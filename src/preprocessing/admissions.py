import pandas as pd
from .load import load_patients, load_admissions

def build_admission_base():

    patients = load_patients()
    admissions = load_admissions()

    df = admissions.merge(patients, on="subject_id", how="left")

    df["admittime"] = pd.to_datetime(df["admittime"])
    df["dischtime"] = pd.to_datetime(df["dischtime"])

    df = df.dropna(subset=["dischtime"])

    df["length_of_stay"] = (
        (df["dischtime"] - df["admittime"]).dt.total_seconds() / (24*3600)
    )

    df = df[df["length_of_stay"] > 0]

    df = df[[
        "hadm_id",
        "subject_id",
        "anchor_age",
        "gender",
        "admission_type",
        "length_of_stay",
        "admittime",
        "dischtime"
    ]]

    df = df.rename(columns={"anchor_age": "age"})

    df.to_csv("data/interim/admission_base.csv", index=False)

    return df
