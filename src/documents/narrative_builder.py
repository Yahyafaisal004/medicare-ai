from src.preprocessing import labs


def format_admission_type(x):

    x = str(x).upper()

    if x == "EMERGENCY":
        return "on an emergency basis"
    if x == "URGENT":
        return "on an urgent basis"
    if x == "ELECTIVE":
        return "for elective management"
    if x == "OBSERVATION":
        return "for observation"

    return "for inpatient care"

def build_narrative(row):

    # Format admission phrase
    admission_phrase = format_admission_type(row["admission_type"])

    # Lab sentence
    labs = row["abnormal_labs_summary"]

    if isinstance(labs, str) and labs.lower() != "nan":
        lab_sentence = f"Laboratory investigations revealed abnormalities including {labs}."
    else:
        lab_sentence = "Laboratory parameters remained within acceptable limits."
    # Additional diagnoses sentence
    if isinstance(row["diagnosis_list"], str) and row["diagnosis_list"].strip() != "":
        additional_diag = (
            f"Additional associated diagnoses included {row['diagnosis_list']}. "
        )
    else:
        additional_diag = ""
    # Severity sentence
    if row["severity_level"] == "severe":
        severity_sentence = "The clinical course was severe and required intensive management. "
    elif row["severity_level"] == "moderate":
        severity_sentence = "The clinical course was of moderate severity and required active inpatient management. "
    else:
        severity_sentence = "The clinical course remained mild and stable during admission. "
    # Final narrative
    narrative = (
        f"{row['patient_name']} is a {row['age']}-year-old "
        f"{row['age_group']} {row['gender']} patient "
        f"admitted {admission_phrase}. "
        f"The patient presented with {row['symptoms']}. "
        f"Clinical evaluation led to a primary diagnosis of "
        f"{row['primary_diagnosis']}. "
        f"{additional_diag}"
        f"The hospital stay lasted {row['los_days']} days. "
        f"{severity_sentence}"
        f"{lab_sentence} "
        f"Physician documentation noted: {row['doctor_notes']}"
    )

    return narrative

