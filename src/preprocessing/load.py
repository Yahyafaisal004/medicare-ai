import pandas as pd
def load_patients():
    return pd.read_csv("data/raw/patients.csv")

def load_admissions():
    return pd.read_csv("data/raw/admissions.csv")

def load_diagnoses():
    return pd.read_csv("data/raw/diagnoses_icd.csv")

def load_diagnosis_lookup():
    return pd.read_csv("data/raw/d_icd_diagnoses.csv")

def load_labs():
    return pd.read_csv("data/raw/labevents.csv")

def load_lab_lookup():
    return pd.read_csv("data/raw/d_labitems.csv")