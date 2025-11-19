from pathlib import Path

import polars as pl
from pheval.post_processing.post_processing import SortOrder, generate_gene_result
from pheval.utils.file_utils import all_files
from polars.polars import ColumnNotFoundError


def read_gado_result(gado_result: Path) -> pl.DataFrame:
    """Read GADO tab separated result output."""
    return pl.read_csv(gado_result, separator="\t")


def extract_gene_results(raw_results: pl.DataFrame) -> pl.DataFrame:
    """
    Extract gene results from GADO result.
    Args:
        raw_results (pl.DataFrame): GADO results.
    Returns:
        pl.DataFrame: The extracted gene results.
    """
    return raw_results.select(
        [
            pl.col("Ensg").alias("gene_identifier").cast(pl.String),
            pl.col("Hgnc").alias("gene_symbol").cast(pl.String),
            pl.col("Zscore").fill_null(0).round(4).alias("score").cast(pl.Float64),
        ]
    )


def create_standardised_results(results_dir: Path, output_dir: Path, phenopacket_dir: Path) -> None:
    """Create PhEval gene results from GADO raw result directory."""
    for result in all_files(results_dir):
        gado_result = read_gado_result(result)
        try:
            pheval_gene_result = extract_gene_results(gado_result)
            generate_gene_result(
                results=pheval_gene_result,
                output_dir=output_dir,
                sort_order=SortOrder.DESCENDING,
                result_path=result,
                phenopacket_dir=phenopacket_dir,
            )
        except ColumnNotFoundError:
            pass
