import pandas as pd
from config.aggregation import month_to_nb


def prices_data_clean(df_prices):
    """Cleans the wfp prices DataFrame.

    Args:
        df_prices (pd.DataFrame): prices DataFrame to clean

    Returns:
        df_prices (pd.DataFrame): cleaned prices DataFrame
    """
    df_prices["date"] = ["-".join(el.split("-")[:2]) for el in df_prices["date"]]
    df_prices["id"] = df_prices["date"] + df_prices["admname"]
    df_prices = df_prices.drop(0)
    df_prices["price"] = pd.to_numeric(df_prices["price"])
    df_prices[["id", "price", "cmname"]].pivot_table(
        index="id", columns="cmname", values="price", aggfunc="mean"
    )
    return df_prices


def import_prices(
    df_aggregated_match_for_FSMS_files_with_yields,
    path_to_wfp_food_prices_mauritania_csv,
    month_to_nb=month_to_nb,
):
    """Reads the prices csv file, cleans it, and merges it with main DataFrame.

    Args:
        df_aggregated_match_for_FSMS_files_with_yields (pd.DataFrame): main DataFrame
        path_to_wfp_food_prices_mauritania_csv (str): path to csv prices.

    Returns:
        aggregated_match_for_FSMS_files_with_yields_with_price (pd.DataFrame):
        main DataFrame with prices
    """
    price_data = pd.read_csv(path_to_wfp_food_prices_mauritania_csv)
    price_data_clean = prices_data_clean(price_data)

    month_to_nb = month_to_nb
    df_aggregated_match_for_FSMS_files_with_yields["id"] = [
        str(df_aggregated_match_for_FSMS_files_with_yields.loc[i, "year"])
        + "-"
        + month_to_nb[
            str(df_aggregated_match_for_FSMS_files_with_yields.loc[i, "month"])
        ]
        + str(df_aggregated_match_for_FSMS_files_with_yields.loc[i, "wilaya"])
        for i in range(df_aggregated_match_for_FSMS_files_with_yields.shape[0])
    ]

    df = pd.merge(
        df_aggregated_match_for_FSMS_files_with_yields,
        price_data_clean,
        left_on="id",
        right_on="id",
        how="inner",
    )
    df = df.drop(columns=["id"])
    return df
