from typing import Any, Iterator, Optional

import deltalake as dl
import polars as pl
import pyarrow as pa
import pyarrow.parquet as pq

from .schema import Schema
from .slicing import HyperSlice


def _dnf_to_sql(dnf: list[tuple]) -> str:
    """Convert DNF expression to SQL expression."""
    if len(dnf) == 0:
        return "1=1"

    sql_parts = []
    for col, op, val in dnf:
        if op == "in":
            assert isinstance(val, list)
            lst = ", ".join([f"'{item}'" for item in val])
            sql_parts.append(f"{col} IN ({lst})")
        elif op in [">=", "<=", ">", "<", "="]:
            sql_parts.append(f"{col} {op} '{val}'")
        else:
            raise ValueError(f"Unsupported operation: {op}")

    return " AND ".join(sql_parts)


class Table:
    def __init__(
        self,
        delta_table: dl.DeltaTable,
    ):
        """Class representing a dataset

        Args:
            delta_table (dl.DeltaTable): Delta table
        """
        self.delta_table = delta_table
        self.table_name = self.delta_table.table_uri.split("/")[-1]

    def __repr__(self):
        return f"Table('{self.table_name}')"

    def partition_cols(self) -> list[str]:
        """Get the partition columns of the table"""
        return self.delta_table.metadata().partition_columns

    def schema(self) -> Schema:
        """Get the schema of the table"""
        pa_schema = pa.schema(self.delta_table.schema())
        return Schema.from_arrow(pa_schema)

    def source(self, hyper_slice: Optional[HyperSlice] = None) -> pl.LazyFrame:
        """Source (lazy) from Delta table

        Args:
            hyper_slice (HyperSlice): Hyper sliced used to filter data
        """
        if hyper_slice is None:
            hyper_slice = []

        # add generated filters to hyperslice
        hyper_slice = self.schema().add_generated_filters(hyper_slice)

        partition_cols = self.delta_table.metadata().partition_columns

        if len(hyper_slice) == 0:
            file_filters = None
            partition_filters = None
        else:
            file_filters = pq.filters_to_expression(hyper_slice)
            partition_filters = [f for f in hyper_slice if f[0] in partition_cols]

        pyarrow_dataset = self.delta_table.to_pyarrow_dataset(partition_filters)

        if file_filters is not None:
            pyarrow_dataset = pyarrow_dataset.filter(file_filters)

        return pl.scan_pyarrow_dataset(pyarrow_dataset)

    def read(self, hyper_slice: Optional[HyperSlice] = None) -> pl.DataFrame:
        """Read (eager) from Delta table

        Args:
            hyper_slice (HyperSlice): Hyper sliced used to filter data
        """
        return self.source(hyper_slice).collect()

    def sink(self, df: pl.LazyFrame, hyper_slice: HyperSlice):
        """Sink (lazy) to Delta Lake

        Args:
            df (pl.LazyFrame): LazyFrame to sink
            table (dl.DeltaTable): Delta table
            hyper_slice (HyperSlice): Hyper slice to overwrite in existing data.
                If None, all data will be overwritten.
        """
        schema = self.schema()

        # add generated filters to hyperslice
        hyper_slice = schema.add_generated_filters(hyper_slice)

        df = schema.add_generated_columns(df)

        pa_schema = schema.to_arrow()

        # make batch generator for stream writing
        def record_batches() -> Iterator[pa.RecordBatch]:
            for batch in df.collect_batches():
                pyarrow_table = batch.to_arrow()
                # we need to cast the incoming data to the
                # table schema. In theory, this should automatically
                # be casted, but it seems that metadata on fields
                # gets removed otherwise.
                casted_pyarrow_table = pyarrow_table.select(pa_schema.names).cast(
                    pa_schema
                )
                yield from casted_pyarrow_table.to_batches()

        record_batch_reader = pa.RecordBatchReader.from_batches(
            pa_schema, record_batches()
        )

        if len(hyper_slice) == 0:
            predicate = None
        else:
            predicate = _dnf_to_sql(hyper_slice)

        dl.write_deltalake(
            table_or_uri=self.delta_table,
            data=record_batch_reader,
            mode="overwrite",
            predicate=predicate,
            schema_mode="merge",
        )

    def write(self, df: pl.DataFrame, hyper_slice: HyperSlice):
        """Write (eager) to Delta Lake

        Args:
            df (pl.LazyFrame): DataFrame to write
            table (dl.DeltaTable): Delta table
            hyper_slice (HyperSlice): Hyper slice to overwrite in existing data.
                If None, all data will be overwritten.
        """
        self.sink(df.lazy(), hyper_slice)

    def optimize(self) -> list[str]:
        """Optimize Delta table by compacting and vacuuming

        Returns:
            list[str]: List of removed files
        """
        metrics = self.delta_table.optimize.compact()

        vacuumed_files = self.delta_table.vacuum(
            dry_run=False,
        )

        metrics["numFilesVacuumed"] = len(vacuumed_files)

        return metrics

    def delete(self, hyper_slice: HyperSlice) -> dict[str, Any]:
        """Delete data from Delta table

        Args:
            hyper_slice (HyperSlice): Hyper slice to delete.
            If None, all data will be deleted.

        Returns:
            dict[str, any]: Delete metrics.

            https://docs.databricks.com/gcp/en/delta/history#operation-metrics-keys
        """
        if hyper_slice is None or hyper_slice == [()]:
            predicate = None
        else:
            predicate = _dnf_to_sql(hyper_slice)

        return self.delta_table.delete(predicate)
