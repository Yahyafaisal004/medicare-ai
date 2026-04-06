import pandas as pd
import ast
from faker import Faker
import random

def refine_dataset():

    df = pd.read_csv("data/processed/admissions_clean.csv")
    # ----------------------------
    # Add Deterministic Fake Names
    # ----------------------------

    fake = Faker("en_IN")

    # Fix random seed for reproducibility
    Faker.seed(42)
    random.seed(42)

    patient_name_map = {}

    # We generate one name per subject_id
    for sid in df["subject_id"].unique():

        # Get gender of this patient
        gender = df[df["subject_id"] == sid]["gender"].iloc[0]

        if gender == "male":
            name = fake.name_male()
        elif gender == "female":
            name = fake.name_female()
        else:
            name = fake.name()

        patient_name_map[sid] = name

    df["patient_name"] = df["subject_id"].map(patient_name_map)

    # Convert string list → proper text
    def clean_diagnosis_list(x):
        try:
            parsed = ast.literal_eval(x)
            return ", ".join(parsed[:3])  # keep max 3
        except:
            return ""

    df["diagnosis_list"] = df["diagnosis_list"].apply(clean_diagnosis_list)

    # Clean abnormal labs text
    df["abnormal_labs_summary"] = df["abnormal_labs_summary"].fillna("None")

    def normalize_admission_type(x):

        x = str(x).upper()

        if "EMER" in x:
            return "emergency"
        
        if "SURGICAL SAME DAY" in x:
            return "elective"
    
        if "OBSERV" in x:
            return "observation"

        if "ELECT" in x:
            return "elective"

        if "URGENT" in x:
            return "urgent"

        return "other"


    df["admission_type"] = df["admission_type"].apply(normalize_admission_type)
    
    df.loc[
        df["abnormal_labs_summary"] == "",
        "abnormal_labs_summary"
    ] = "None"

    df["los_days"] = df["length_of_stay"].round().astype(int)

    df["los_days"] = df["los_days"].apply(lambda x: 1 if x < 1 else x) #ensure minimum of 1 day

    # Remove extreme LOS outliers (> 60 days)
    df = df[df["length_of_stay"] < 60]

    # Remove unrealistic ages
    df = df[df["age"] < 100]
    def normalize_gender(x):
        x = str(x).strip().upper()
        if x == "M":
            return "male"
        if x == "F":
            return "female"
        return "other"

    df["gender"] = df["gender"].apply(normalize_gender)

    def compute_severity(row):

        score = 0
        diagnosis = str(row["primary_diagnosis"]).lower()
        labs = str(row["abnormal_labs_summary"]).lower()

        # -------------------------
        # 1️⃣ High-risk diagnoses
        # -------------------------

        high_risk_keywords = [
            "respiratory failure",
            "sepsis",
            "septic",
            "heart failure",
            "acute kidney failure",
            "renal failure",
            "stroke",
            "cerebral",
            "embolism",
            "thrombosis",
            "necrosis",
            "leukemia",
            "malignant",
            "severe"
        ]

        if any(k in diagnosis for k in high_risk_keywords):
            score += 2

        # -------------------------
    # 2️⃣ Lab value severity scoring
    # -------------------------

        if row["abnormal_labs_summary"] != "None":

            for lab in row["abnormal_labs_summary"].split(", "):

                parts = lab.split()
                value = float(parts[-1])
                lab_name = " ".join(parts[:-1]).lower()

                # Hemoglobin severity
                if "hemoglobin" in lab_name:
                    if value < 8:
                        score += 2
                    elif value < 10:
                        score += 1

                # Creatinine severity
                if "creatinine" in lab_name:
                    if value > 3:
                        score += 2
                    elif value > 1.5:
                        score += 1

                # WBC severity
                if "white blood cells" in lab_name:
                    if value > 20 or value < 3:
                        score += 2
                    elif value > 12:
                        score += 1

                # Glucose severity
                if "glucose" in lab_name:
                    if value > 300 or value < 50:
                        score += 2
                    elif value > 180:
                        score += 1

        # -------------------------
        # 3️⃣ Length of stay
        # -------------------------

        if row["los_days"] >= 14:
            score += 2
        elif row["los_days"] >= 7:
            score += 1

        # -------------------------
        # 4️⃣ Emergency context
        # -------------------------

        if row["admission_type"] == "EMERGENCY":
            score += 1

        # -------------------------
        # Final classification
        # -------------------------

        if score >= 4:
            return "severe"
        elif score >= 2:
            return "moderate"
        else:
            return "mild"


    df["severity_level"] = df.apply(compute_severity, axis=1)
    def age_bucket(age):

        age = int(age)

        if age < 18:
            return "pediatric"
        elif age <= 40:
            return "young adult"
        elif age <= 65:
            return "middle-aged"
        else:
            return "elderly"

    df["age_group"] = df["age"].apply(age_bucket)

    df["abnormal_labs_summary"] = df["abnormal_labs_summary"].fillna("None")
    df.loc[df["abnormal_labs_summary"] == "", "abnormal_labs_summary"] = "None"

    def generate_symptoms(row):

        diagnosis = str(row["primary_diagnosis"]).lower()

        # --------------------
        # Cardiac
        # --------------------
        if any(x in diagnosis for x in [
            "atrial", "heart failure", "coronary", "angina",
            "myocardial", "pericard", "ischemic", "embolism",
            "thrombosis", "pacemaker"
        ]):
            return "chest discomfort, shortness of breath, palpitations"

        # --------------------
        # Respiratory
        # --------------------
        if any(x in diagnosis for x in [
            "pneumonia", "respiratory", "copd",
            "asthma", "pulmonary", "lung"
        ]):
            return "cough, shortness of breath, fever"

        # --------------------
        # Renal
        # --------------------
        if any(x in diagnosis for x in [
            "kidney", "renal", "chronic kidney", "dialysis"
        ]):
            return "reduced urine output, swelling, fatigue"

        # --------------------
        # Diabetes / Endocrine
        # --------------------
        if any(x in diagnosis for x in [
            "diabetes", "hyperglycemia", "hypoglycemia",
            "thyroid", "glucose"
        ]):
            return "fatigue, increased thirst, frequent urination"

        # --------------------
        # Infection
        # --------------------
        if any(x in diagnosis for x in [
            "sepsis", "infection", "pneumonia",
            "abscess", "clostridium", "streptococ"
        ]):
            return "fever, chills, generalized weakness"

        # --------------------
        # Hematologic
        # --------------------
        if any(x in diagnosis for x in [
            "anemia", "thrombocytopenia", "pancytopenia"
        ]):
            return "fatigue, dizziness, pallor"

        # --------------------
        # Neurological
        # --------------------
        if any(x in diagnosis for x in [
            "stroke", "encephalopathy", "delirium",
            "epilepsy", "multiple sclerosis", "cerebral"
        ]):
            return "weakness, confusion, dizziness"

        # --------------------
        # Gastrointestinal
        # --------------------
        if any(x in diagnosis for x in [
            "ulcer", "reflux", "varices", "pancreatitis",
            "cholecystitis", "abdominal", "ibs"
        ]):
            return "abdominal pain, nausea, vomiting"

        # --------------------
        # Psychiatric
        # --------------------
        if any(x in diagnosis for x in [
            "anxiety", "bipolar", "depress",
            "schizo", "suicidal", "alcohol"
        ]):
            return "low mood, anxiety, sleep disturbance"

        # --------------------
        # Trauma
        # --------------------
        if any(x in diagnosis for x in [
            "fracture", "injury", "contusion"
        ]):
            return "localized pain, swelling, limited movement"

        # --------------------
        # Default
        # --------------------
        return "generalized weakness and fatigue"

    df["symptoms"] = df.apply(generate_symptoms, axis=1)

    def generate_doctor_notes(row):

        diagnosis = str(row["primary_diagnosis"]).lower()
        doctor_notes = []

        # ============================
        # Diagnosis-based reasoning
        # ============================

        # Cardiac
        if any(x in diagnosis for x in [
            "atrial", "heart failure", "coronary",
            "angina", "myocardial", "pericard",
            "ischemic", "embolism", "thrombosis"
        ]):
            doctor_notes.append("Cardiology evaluation was conducted and cardiac monitoring was maintained.")

        # Respiratory
        elif any(x in diagnosis for x in [
            "pneumonia", "respiratory", "copd",
            "asthma", "pulmonary", "lung"
        ]):
            doctor_notes.append("Respiratory function was closely monitored and supportive therapy was provided.")

        # Renal
        elif any(x in diagnosis for x in [
            "kidney", "renal", "chronic kidney", "dialysis"
        ]):
            doctor_notes.append("Renal function and fluid balance were carefully managed.")

        # Diabetes / Endocrine
        elif any(x in diagnosis for x in [
            "diabetes", "hyperglycemia", "hypoglycemia", "thyroid"
        ]):
            doctor_notes.append("Metabolic parameters were monitored and glycemic control was optimized.")

        # Infection
        elif any(x in diagnosis for x in [
            "sepsis", "infection", "abscess",
            "clostridium", "streptococ"
        ]):
            doctor_notes.append("Infectious workup was performed and antimicrobial therapy was initiated.")

        # Hematologic
        elif any(x in diagnosis for x in [
            "anemia", "thrombocytopenia", "pancytopenia"
        ]):
            doctor_notes.append("Hematologic parameters were monitored and supportive management was provided.")

        # Neurological
        elif any(x in diagnosis for x in [
            "stroke", "encephalopathy", "delirium",
            "epilepsy", "multiple sclerosis", "cerebral"
        ]):
            doctor_notes.append("Neurological status was assessed regularly with serial evaluations.")

        # Gastrointestinal
        elif any(x in diagnosis for x in [
            "ulcer", "reflux", "varices",
            "pancreatitis", "cholecystitis", "abdominal"
        ]):
            doctor_notes.append("Gastrointestinal symptoms were managed with appropriate medical therapy.")

        # Psychiatric
        elif any(x in diagnosis for x in [
            "anxiety", "bipolar", "depress",
            "schizo", "suicidal", "alcohol"
        ]):
            doctor_notes.append("Psychiatric evaluation was conducted and supportive counseling was provided.")

        # Trauma
        elif any(x in diagnosis for x in [
            "fracture", "injury", "contusion"
        ]):
            doctor_notes.append("Orthopedic assessment was completed and mobility was monitored.")

        else:
            doctor_notes.append("Comprehensive inpatient evaluation and management were performed.")

        # ============================
        # Admission type context
        # ============================

        if row["admission_type"] == "EMERGENCY":
            doctor_notes.append("Patient required urgent evaluation on admission.")
        elif row["admission_type"] == "ELECTIVE":
            doctor_notes.append("Admission was planned for further evaluation and management.")
        elif row["admission_type"] == "OBSERVATION":
            doctor_notes.append("Patient was admitted for short-term monitoring.")
        else:
            doctor_notes.append("Standard inpatient admission process was followed.")

        # ============================
        # Severity context
        # ============================

        if row["severity_level"] == "severe":
            doctor_notes.append("Clinical course was complex and required close monitoring.")
        elif row["severity_level"] == "moderate":
            doctor_notes.append("Active inpatient management was required.")
        else:
            doctor_notes.append("Clinical condition remained stable during hospitalization.")

        # ============================
        # Length of stay nuance
        # ============================

        if row["los_days"] > 14:
            doctor_notes.append("Extended hospitalization was necessary due to ongoing medical needs.")
        elif row["los_days"] <= 3:
            doctor_notes.append("Patient demonstrated rapid clinical improvement.")

        # ============================
        # Lab context
        # ============================

        if row["abnormal_labs_summary"] != "None":
            doctor_notes.append("Laboratory abnormalities were addressed appropriately.")
        else:
            doctor_notes.append("Laboratory parameters remained within acceptable limits.")

        return " ".join(doctor_notes)   
    df["doctor_notes"] = df.apply(generate_doctor_notes, axis=1)
    def clean_diagnosis_list(row):

        try:
            parsed = ast.literal_eval(row["diagnosis_list"])
            primary = row["primary_diagnosis"]

            filtered = [d for d in parsed if d != primary]

            return ", ".join(filtered[:3])
        except:
            return ""

    df["diagnosis_list"] = df.apply(clean_diagnosis_list, axis=1)
    def format_lab_summary(x):

        if x == "None":
            return "None"

        formatted = []

        for lab in x.split(", "):

            parts = lab.strip().split()

            # Last element is numeric value
            value = float(parts[-1])

            # Everything before that is lab name
            lab_name = " ".join(parts[:-1])

            formatted.append(f"{lab_name} {value:.1f}")

        return ", ".join(formatted)
    
    df["diagnosis_list"] = df["diagnosis_list"].fillna("")
    df["diagnosis_list"] = df["diagnosis_list"].replace("nan", "")


    df["abnormal_labs_summary"] = df["abnormal_labs_summary"].apply(format_lab_summary)
    

    df_rag = df[[
        "hadm_id",
        "subject_id",
        "patient_name",
        "age",
        "age_group",
        "gender",
        "severity_level",
        "admission_type",
        "los_days",
        "symptoms",
        "primary_diagnosis",
        "diagnosis_list",
        "abnormal_labs_summary",
        "doctor_notes"
    ]]

    df_rag.to_csv("data/processed/admissions_rag_ready.csv", index=False)

    return df_rag


if __name__ == "__main__":
    refine_dataset()
