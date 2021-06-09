from preprocessing.utils_communes import (
    build_and_clean_df,
    label_encoders_generator,
    encode_df,
    decode_df,
)
import pandas as pd
from preprocessing.preprocessing import (
    standardize_education_level,
    standardize_date,
    standardize_tailmen,
    standardize_bool_hors_nk,
    standardize_moughataa_commune_float,
)
from config.preprocessing import preprocessing_FSMS_files_with_yields_types
from pathlib import Path
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import BaggingClassifier

feature_cols = [
    "numquest",
    "ident",
    "enqu",
    "wilaya",
    "numen",
    "hors nk",
    "Tailmen",
    "Nb_hom",
    "Nb_fem",
    "TxDep",
    "Equiv_ad",
    "moughataa",
    "commune",
]


def impute_communes(features=feature_cols, aggregated_file=None):
    if aggregated_file is None:
        aggregated_file = (
            str(Path.home()) + "/last_drive_version_standardized_aggregated_dataset.csv"
        )
    df_aggregated_file = pd.read_csv(aggregated_file, low_memory=False)
    df_aggregated_file.drop(columns=["Unnamed: 0"], inplace=True)

    columns = []
    for col in df_aggregated_file.columns.to_list():
        new_col = col.replace("$", "")
        columns.append(new_col)
    df_aggregated_file.columns = columns

    df_aggregated_file = df_aggregated_file.astype(
        preprocessing_FSMS_files_with_yields_types
    )

    df_aggregated_file = df_aggregated_file.rename(columns={"id": "price_id"})
    df_aggregated_file["Scol"] = standardize_education_level(df_aggregated_file["Scol"])
    df_aggregated_file["Tailmen"] = df_aggregated_file["Tailmen"].apply(
        lambda row: standardize_tailmen(row)
    )
    df_aggregated_file["date"] = df_aggregated_file["date"].apply(
        lambda row: standardize_date(row)
    )
    df_aggregated_file["hors nk"] = df_aggregated_file["hors nk"].apply(
        lambda row: standardize_bool_hors_nk(row)
    )
    df_aggregated_file["date"] = pd.to_datetime(
        df_aggregated_file["date"], format="%Y-%m-%d", errors="coerce"
    )
    df_aggregated_file["commune"] = df_aggregated_file["commune"].apply(
        lambda x: standardize_moughataa_commune_float(x)
    )

    # build dataframe
    tmp_df_aggregated_file = build_and_clean_df(df_aggregated_file, features)

    # label encode dataframe
    columns_to_encode = [
        "wilaya",
        "Tailmen",
        "hors nk",
        "moughataa",
        "commune",
        "numquest",
    ]
    label_encoded_features = label_encoders_generator(
        tmp_df_aggregated_file, columns_to_encode
    )
    tmp_df_aggregated_file = encode_df(
        tmp_df_aggregated_file, columns_to_encode, label_encoded_features
    )

    # split into 2 datasets : one which has the predictions, and the other on which we will have to make the predictions
    tmp_df_aggregated_file_predict = (
        tmp_df_aggregated_file[tmp_df_aggregated_file["commune"] == 0]
        .copy()
        .reset_index()
        .drop(columns=["index"])
    )
    tmp_df_aggregated_file = (
        tmp_df_aggregated_file[tmp_df_aggregated_file["commune"] > 0]
        .reset_index()
        .drop(columns=["index"])
    )

    features = list(
        zip(
            tmp_df_aggregated_file["wilaya"],
            tmp_df_aggregated_file["hors nk"],
            tmp_df_aggregated_file["moughataa"],
            tmp_df_aggregated_file["Tailmen"],
            tmp_df_aggregated_file["numquest"],
        )
    )

    label = tmp_df_aggregated_file.commune

    features_predict = list(
        zip(
            tmp_df_aggregated_file_predict["wilaya"],
            tmp_df_aggregated_file_predict["hors nk"],
            tmp_df_aggregated_file_predict["moughataa"],
            tmp_df_aggregated_file_predict["Tailmen"],
            tmp_df_aggregated_file_predict["numquest"],
        )
    )

    # Predict Output
    parameters = {
        "n_neighbors": range(1, 50),
        "weights": ["uniform", "distance"],
    }  # 'algorithm':['auto', 'ball_tree', 'kd_tree', 'brute']
    gridsearch = GridSearchCV(KNeighborsClassifier(), parameters)
    gridsearch.fit(features, label)

    parameters = {
        "n_neighbors": range(1, 50),
        "weights": ["uniform", "distance"],
    }  # 'algorithm':['auto', 'ball_tree', 'kd_tree', 'brute']
    gridsearch = GridSearchCV(KNeighborsClassifier(), parameters)
    gridsearch.fit(features, label)

    best_k = gridsearch.best_params_["n_neighbors"]
    best_weights = gridsearch.best_params_["weights"]
    bagged_knn = KNeighborsClassifier(n_neighbors=best_k, weights=best_weights)
    model = BaggingClassifier(bagged_knn, n_estimators=100)
    model.fit(features, label)

    # Test our model
    predicted = model.predict(features_predict)
    tmp_df_aggregated_file_predict["predicted_commune_num"] = predicted
    tmp_df_aggregated_file_predict[
        "predicted_commune"
    ] = tmp_df_aggregated_file_predict["predicted_commune_num"].astype("int")

    # Decode labels
    columns_to_decode = [
        "wilaya",
        "Tailmen",
        "hors nk",
        "moughataa",
        "predicted_commune",
        "numquest",
    ]
    tmp_df_aggregated_file_predict = decode_df(
        tmp_df_aggregated_file_predict, columns_to_decode, label_encoded_features
    )
    columns_to_decode = [
        "wilaya",
        "Tailmen",
        "hors nk",
        "moughataa",
        "commune",
        "numquest",
    ]
    tmp_df_aggregated_file = decode_df(
        tmp_df_aggregated_file, columns_to_decode, label_encoded_features
    )

    final_df = pd.concat([tmp_df_aggregated_file_predict, tmp_df_aggregated_file]).drop(columns=["predicted_commune_num"])
    return final_df
