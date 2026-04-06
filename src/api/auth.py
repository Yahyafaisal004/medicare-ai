import jwt
from datetime import datetime, timedelta
import pandas as pd

SECRET_KEY = "medicareai"
ALGORITHM = "HS256"

DOCTOR_PASSWORD = "medicareai"

DATA_PATH = "data/processed/admissions_rag_ready.csv"


def subject_exists(subject_id):
    df = pd.read_csv(DATA_PATH)
    return subject_id in df["subject_id"].values


def create_access_token(data: dict):
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(hours=2)

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return token


def decode_token(token: str):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload