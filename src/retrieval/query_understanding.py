from openai import OpenAI
import json
import re
import os
from dotenv import load_dotenv

load_dotenv()


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key = os.getenv("OPENROUTER_API_KEY")

)
SYSTEM_PROMPT = """
You analyze search queries for a hospital patient record retrieval system.

The system stores hospital admission narratives containing:
- patient names
- diagnoses
- symptoms
- admission types
- severity levels
- treatments

Your task is to convert the user query into structured JSON.

Rewrite the query so it is optimized for retrieving hospital admission narratives from a medical database.

The rewritten query should:
- include relevant medical context words such as "hospital admission", "diagnosis", "symptoms", "treatment", or "medical report"
- preserve the user's original intent
- not invent new medical facts
- improve semantic retrieval for medical records

Return ONLY raw JSON using this exact schema:

{
 "rewritten_query": string,
 "patient_name": string or null,
 "diagnosis": string or null,
 "severity_level": "mild" | "moderate" | "severe" | null,
 "admission_type": "emergency" | "urgent" | "observation" | "elective" | null
}

Rules:
- Use null if the information is not mentioned
- Do NOT output "None", "", or "unknown"
- Do NOT include explanations
- Do NOT include markdown
- Do NOT include code blocks
- Output must start with { and end with }

Extraction rules:
- Extract patient_name if a person's name is clearly mentioned
- Map severity phrases like "critical", "serious", or "life-threatening" → "severe"
- Map "scheduled" or "planned" admission → "elective"
- Extract diagnosis if a disease, condition, or medical term is mentioned (e.g., diabetes, obesity, cancer, hypertension)
- ALWAYS preserve key medical terms from the user query (e.g., disease names like diabetes, obesity, cancer)
- Map "monitoring" or "short stay" → "observation"
- Map "urgent care" or "immediate admission" → "urgent"
- Map "ER", "accident admission", or "emergency" → "emergency"

Output keys must appear in this exact order:
rewritten_query
patient_name
diagnosis
severity_level
admission_type
"""


def understand_query(query):

    response = client.chat.completions.create(
        model="dstepfun/step-3.5-flash:free",
        max_tokens=100,
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query}
        ]
    )

    import json
    import re

    content = response.choices[0].message.content

    print("\nRAW LLM OUTPUT:\n", content)

    try:

        # remove markdown code blocks
        content = content.replace("```json", "").replace("```", "")

        # extract json
        json_str = re.search(r'\{.*\}', content, re.DOTALL).group()

        parsed = json.loads(json_str)

    except Exception as e:

        print("JSON parse failed:", e)

        parsed = {
            "rewritten_query": query,
            "patient_name": None,
            "diagnosis": None,
            "severity_level": None,
            "admission_type": None
        }

    return parsed