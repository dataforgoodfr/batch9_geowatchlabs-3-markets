import pandas as pd
import numpy as np


def build_and_clean_df(original_df, sub_features):
    df = original_df[sub_features].copy()
    df = df.replace({np.nan: None})
    df = df.astype(
        {
            "commune": "category",
            "enqu": "category",
            "wilaya": "category",
            "ident": "category",
            "numquest": "category",
        }
    )
    df["TxDep"] = df["TxDep"].fillna(0)
    return df


def label_encoders_generator(df, list_of_columns_to_encode):
    label_encoders = []
    for col in list_of_columns_to_encode:
        le = pd.DataFrame(df[col].unique()).reset_index()
        label_encoders.append(le)
    return label_encoders


def encode_df(df, list_of_cols, list_of_label_encoded_features):
    for k in range(len(list_of_label_encoded_features)):
        col_name = list_of_cols[k]
        label_encoded_features = list_of_label_encoded_features[k]
        df = df.merge(
            label_encoded_features,
            how="left",
            left_on=col_name,
            right_on=0,
            suffixes=("", "_right"),
        ).drop(columns=[0, col_name])
        df = df.rename(columns={"index": col_name})
    return df


def decode_df(df, list_of_cols, list_of_label_encoded_features):
    for k in range(len(list_of_label_encoded_features)):
        col_name = list_of_cols[k]
        label_encoded_features = list_of_label_encoded_features[k]
        df[col_name] = df[col_name].astype("int")
        df = df.merge(
            label_encoded_features,
            how="left",
            left_on=col_name,
            right_on="index",
            suffixes=("", "_right"),
        ).drop(columns=["index", col_name])
        df = df.rename(columns={0: col_name})
    return df
