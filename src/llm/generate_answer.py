from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key = os.getenv("OPENROUTER_API_KEY")
)
def call_llm(prompt, system_prompt="You are a helpful assistant."):

    response = client.chat.completions.create(
        model="stepfun/step-3.5-flash:free",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=0   # important for deterministic rewriting
    )

    return response.choices[0].message.content.strip()

def rewrite_query(current_query, history):

    if not history:
        return current_query

    history_text = "\n".join([
        f"{h['role']}: {h['content']}" for h in history
    ])

    prompt = f"""
Convert the follow-up medical question into a standalone query.

Conversation:
{history_text}

Follow-up question:
{current_query}

Return ONLY the rewritten query.
"""

    try:
        return call_llm(
            prompt,
            system_prompt="You rewrite medical queries for clarity."
        )
    except:
        return current_query

def generate_answer(query, context, role):

    # ----------------------------
    # QUERY TYPE DETECTION
    # ----------------------------
    query_lower = query.lower()

    if any(x in query_lower for x in ["how many", "count", "number of"]):
        mode = "count"
    elif any(x in query_lower for x in ["list", "which", "show", "find all"]):
        mode = "cohort"
    else:
        mode = "summary"

    # ----------------------------
    # SYSTEM PROMPT
    # ----------------------------
    if role == "doctor":
        system_prompt = "You are a precise clinical assistant." \
        """Return output in clean plain text:
        - Do NOT use *, **, or markdown formatting
        - Use simple bullets and headings
        - Keep it structured and readable
        """
    else:
        system_prompt = """
        You are a medical assistant explaining health information to a patient.

            Rules:
            - Use very simple language (like explaining to a non-medical person)
            - Avoid medical jargon
            - If you must use a medical term, explain it in simple words
            - Be calm and reassuring
            - Keep answers short and clear
            - Do NOT sound like a doctor writing a report
            Return output in clean plain text:
            - Do NOT use *, **, or markdown formatting
            - Use simple bullets and headings
            - Keep it structured and readable
        """

    # ----------------------------
    # PROMPT SELECTION
    # ----------------------------

    if mode == "count":

        prompt = f"""
You are a medical data assistant.

Use ONLY the provided patient records.

Instructions:
- First give the exact count
- Then list matching patients
- Clearly separate included vs excluded cases if relevant
- Be concise and structured
- Do not invent information
Return output in clean plain text:
        - Do NOT use *, **, or markdown formatting
        - Use simple bullets and headings
        - Keep it structured and readable

Records:
{context}

Question:
{query}

Answer:
"""

    elif mode == "cohort":

        prompt = f"""
You are a clinical data assistant.

Use ONLY the provided patient records.

Instructions:
- Identify all relevant patients
- Group similar cases if possible
- Highlight key clinical patterns (severity, diagnosis, complications)
- Keep the answer structured and concise
- Do not list unnecessary details for every patient
Return output in clean plain text:
        - Do NOT use *, **, or markdown formatting
        - Use simple bullets and headings
        - Keep it structured and readable

Records:
{context}

Question:
{query}

Answer:
"""

    else:  # summary mode

        prompt = f"""
You are a clinical assistant helping doctors.

Use ONLY the provided patient records.

Instructions:
- Provide a clear clinical summary
- Focus on the most relevant findings
- Avoid listing every field unless necessary
- Keep the answer concise and readable
Return output in clean plain text:
        - Do NOT use *, **, or markdown formatting
        - Use simple bullets and headings
        - Keep it structured and readable

Records:
{context}

Question:
{query}

Answer:
"""

    # ----------------------------
    # LLM CALL
    # ----------------------------
    answer = None

    for attempt in range(2):

        try:
            response = client.chat.completions.create(
                model="stepfun/step-3.5-flash:free",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
            )

            content = response.choices[0].message.content

            if not content or content.strip() == "":
                raise ValueError("Empty response")

            answer = content.strip()
            break

        except Exception as e:
            print(f"LLM attempt {attempt+1} failed:", e)

    if not answer:
        answer = "Could not generate answer. Showing retrieved records."

    return answer