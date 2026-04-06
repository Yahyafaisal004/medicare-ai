import pandas as pd
from .load import load_diagnoses, load_diagnosis_lookup

def build_diagnosis_table():

    diagnoses = load_diagnoses()
    lookup = load_diagnosis_lookup()

    diag = diagnoses.merge(
        lookup,
        on=["icd_code", "icd_version"],
        how="left"
    )

    diag_grouped = (
        diag.groupby("hadm_id")["long_title"]
        .apply(lambda x: list(x.dropna())[:5])
        .reset_index()
    )

    diag_grouped["primary_diagnosis"] = diag_grouped["long_title"].apply(
        lambda x: x[0] if len(x) > 0 else "Unknown"
    )

    diag_grouped = diag_grouped.rename(
        columns={"long_title": "diagnosis_list"}
    )

    diag_grouped.to_csv("data/interim/admission_diagnoses.csv", index=False)

    return diag_grouped
