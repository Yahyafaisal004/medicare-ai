import pandas as pd
from .load import load_labs, load_lab_lookup

IMPORTANT_LABS = [
    "Hemoglobin",
    "White Blood Cells",
    "Creatinine",
    "Glucose"
]

ABNORMAL_THRESHOLDS = {
    "Hemoglobin": (12, 17),
    "White Blood Cells": (4, 11),
    "Creatinine": (0.6, 1.3),
    "Glucose": (70, 140)
}

def build_lab_summary():

    labs = load_labs()
    lab_lookup = load_lab_lookup()

    labs = labs.merge(lab_lookup, on="itemid", how="left")

    labs = labs[labs["label"].isin(IMPORTANT_LABS)]

    labs = labs.dropna(subset=["valuenum", "hadm_id"])

    summaries = []

    for hadm_id, group in labs.groupby("hadm_id"):

        abnormal = []

        for lab_name in IMPORTANT_LABS:
            lab_vals = group[group["label"] == lab_name]["valuenum"]

            if len(lab_vals) == 0:
                continue

            mean_val = lab_vals.mean()
            low, high = ABNORMAL_THRESHOLDS[lab_name]

            if mean_val < low or mean_val > high:
                abnormal.append(f"{lab_name} {mean_val:.2f}")

        summaries.append({
            "hadm_id": hadm_id,
            "abnormal_labs_summary": ", ".join(abnormal)
        })

    lab_df = pd.DataFrame(summaries)

    lab_df.to_csv("data/interim/admission_labs.csv", index=False)

    return lab_df
