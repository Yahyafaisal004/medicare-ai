import pandas as pd

def build_final_dataset():

    base = pd.read_csv("data/interim/admission_base.csv")
    diag = pd.read_csv("data/interim/admission_diagnoses.csv")
    labs = pd.read_csv("data/interim/admission_labs.csv")

    df = base.merge(diag, on="hadm_id", how="left")
    df = df.merge(labs, on="hadm_id", how="left")

    df["abnormal_labs_summary"] = df["abnormal_labs_summary"].fillna("None")

    df.to_csv("data/processed/admissions_clean.csv", index=False)

    return df
