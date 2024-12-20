import logging
from typing import Type

import polars as pl
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class DataProcessLayer:
    """
    A layer for processing and validating medical data.
    """

    @classmethod
    def process_med_an_name_data(cls, df: pl.DataFrame) -> pl.DataFrame:
        """
        Process the data by modifying the 'is_simple' field and adding a
         'loaded' column.

        Args:
            df (pl.DataFrame): The raw Polars DataFrame.

        Returns:
            pl.DataFrame: The processed Polars DataFrame.
        """
        df = df.with_columns(
            pl.when(df["is_simple"] == "Y")
            .then(0)
            .otherwise(df["min_value"])
            .alias("min_value"),
            pl.when(df["is_simple"] == "Y")
            .then(1)
            .otherwise(df["max_value"])
            .alias("max_value"),
        )
        return df

    @classmethod
    def validate_polars_df(
        cls, df: pl.DataFrame, model: Type[BaseModel]
    ) -> pl.DataFrame:
        """
        Validate a Polars DataFrame against a Pydantic model.

        Args:
            df (pl.DataFrame): Polars DataFrame to validate.
            model (Type[BaseModel]): Pydantic model class for validation.

        Returns:
            pl.DataFrame: Validated Polars DataFrame.
        """
        records = df.to_dicts()
        validated_records = []

        for record in records:
            try:
                validated_data = model(**record).model_dump(by_alias=True)
                validated_records.append(validated_data)
            except Exception as e:
                logger.error(f"Validation error for record {record}: {e}")
                raise

        return pl.DataFrame(validated_records)

    @classmethod
    def get_outliers_with_details(
        cls, results: pl.DataFrame, table2: pl.DataFrame
    ) -> pl.DataFrame:
        """
        Identifies and lists out-of-bound results for each patient.

        Args:
            results (pl.DataFrame): Table with results.
            table2 (pl.DataFrame): Reference table with analysis details.

        Returns:
            pl.DataFrame: A DataFrame containing outlier details.
        """
        results = results.with_columns(pl.col("Значение").cast(pl.Float64))

        joined = results.join(table2, left_on="Анализ", right_on="id", how="inner")
        joined = joined.with_columns(
            pl.when(pl.col("is_simple") == "Y")
            .then(pl.col("Значение") == 1)
            .otherwise(
                (pl.col("Значение") < pl.col("min_value"))
                | (pl.col("Значение") > pl.col("max_value"))
            )
            .alias("is_outlier")
        )

        filtered = joined.filter(pl.col("is_outlier"))
        result = filtered.rename({"name": "Расшифровка анализа"}).select(
            [
                "Код пациента",
                "Анализ",
                "Значение",
                "Расшифровка анализа",
                "min_value",
                "max_value",
                "is_simple",
            ]
        )
        return result

    @classmethod
    def merge_with_patients(
        cls, outliers: pl.DataFrame, patients: pl.DataFrame, min_outliers: int = 2
    ) -> pl.DataFrame:
        """
        Merge the outliers table with the patients table and include a conclusion.

        Args:
            outliers (pl.DataFrame): DataFrame with outlier details.
            patients (pl.DataFrame): DataFrame with patient details.
            min_outliers (int): Minimum number of outliers to consider.

        Returns:
            pl.DataFrame: Merged DataFrame with patient information and conclusions.
        """
        outlier_counts = (
            outliers.group_by("Код пациента")
            .agg(pl.count("Анализ").alias("outlier_count"))
            .filter(pl.col("outlier_count") >= min_outliers)
        )

        filtered_outliers = outliers.join(outlier_counts, on="Код пациента")
        filtered_outliers = filtered_outliers.with_columns(
            pl.when(pl.col("is_simple") == "Y")
            .then(pl.lit("Положительный"))
            .when(pl.col("Значение") > pl.col("max_value"))
            .then(pl.lit("Повышен"))
            .when(pl.col("Значение") < pl.col("min_value"))
            .then(pl.lit("Понижен"))
            .otherwise(pl.lit(None))
            .alias("Заключение")
        )

        result = filtered_outliers.join(
            patients, left_on="Код пациента", right_on="id"
        ).select(
            pl.col("name").alias("Имя"),
            pl.col("phone").alias("Телефон"),
            pl.col("Анализ").alias("Название анализа"),
            pl.col("Расшифровка анализа"),
            pl.col("Значение"),
            pl.col("Заключение"),
            pl.col("is_simple"),
        )
        return result
