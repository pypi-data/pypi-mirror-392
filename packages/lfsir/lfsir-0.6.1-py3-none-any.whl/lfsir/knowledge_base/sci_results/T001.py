import pandas as pd
import numpy as np

from ...api import api

columns = [
    ("Sum", "Sum"),
    ("Sum", "Male"),
    ("Sum", "Female"),
    ("Urban", "Sum"),
    ("Urban", "Male"),
    ("Urban", "Female"),
    ("Rural", "Sum"),
    ("Rural", "Male"),
    ("Rural", "Female"),
]

index = [
    "Sum",
    "0-4",
    "5-9",
    "10-14",
    "15-19",
    "20-24",
    "25-29",
    "30-34",
    "35-39",
    "40-44",
    "45-49",
    "50-54",
    "55-59",
    "60-64",
    "65-69",
    "70-74",
    "75-79",
    "80>=",
]


def create_annual_table(year: int) -> pd.DataFrame:
    df = (
        api.load_table(table_name="data", years=year)
        .pipe(api.add_attribute, name="Urban_Rural")
        .assign(
            Age_Group=lambda df: pd.cut(
                df["Age"],
                bins=list(range(0, 81, 5)) + [np.inf],
                labels=[f"{age}-{age+4}" for age in list(range(0, 81, 5))[:-1]]
                + ["80>="],
                right=False,
            )
        )
        .groupby(["Sex", "Urban_Rural", "Age_Group"], observed=True)["Weight"]
        .sum()
    )

    age_sum = df.groupby("Age_Group", observed=True).sum()
    age_sum.index = pd.MultiIndex.from_product(
        [["Sum"], ["Sum"], age_sum.index], names=df.index.names
    )

    age_sex_sum = df.groupby(["Sex", "Age_Group"], observed=True).sum()
    age_sex_sum = pd.concat(
        [age_sex_sum], keys=["Sum"], names=["Urban_Rural", "Sex", "Age_Group"]
    )
    age_sex_sum.index = age_sex_sum.index.reorder_levels(
        ["Sex", "Urban_Rural", "Age_Group"]
    )

    age_urban_rural = df.groupby(["Urban_Rural", "Age_Group"], observed=True).sum()
    age_urban_rural = pd.concat(
        [age_urban_rural], keys=["Sum"], names=["Sex", "Urban_Rural", "Age_Group"]
    )

    table = (
        pd.concat([df, age_sum, age_sex_sum, age_urban_rural])
        .unstack(["Urban_Rural", "Sex"])
        .sort_index(axis="columns")
    )
    table.loc["Sum"] = table.sum()

    table = table.loc[index, columns]
    return table


def main(years: list[int]) -> pd.DataFrame:
    if len(years) == 1:
        return create_annual_table(year=years[0])
    return pd.concat(
        [create_annual_table(year=year) for year in years],
        keys=years,
        names=["Year", "Sex", "Urban_Rural", "Age_Group"],
    )
