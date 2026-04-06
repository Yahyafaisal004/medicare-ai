import pandas as pd
import json
from src.documents.narrative_builder import build_narrative


def export_rag_json():

    df = pd.read_csv("data/processed/admissions_rag_ready.csv")

    records = []

    for _, row in df.iterrows():

        document = {
            "id": f"hadm_{int(row['hadm_id'])}",
            "metadata": {
                "hadm_id": int(row["hadm_id"]),
                "subject_id": int(row["subject_id"]),
                "patient_name": row["patient_name"],
                "admission_type": row["admission_type"],
                "severity_level": row["severity_level"],
                "los_days": int(row["los_days"]),
                "primary_diagnosis": row["primary_diagnosis"]
            },
            "page_content": build_narrative(row),
            "type": "Document"
        }

        records.append(document)

    with open("data/processed/admissions_rag_documents.json", "w") as f:
        json.dump(records, f, indent=4)

    print("RAG JSON export complete.")


if __name__ == "__main__":
    export_rag_json()
