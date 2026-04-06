def detect_query_type(query):

    query = query.lower()

    cohort_keywords = [
        "all", "which", "list", "show me", "find all",
        "patients with", "cases of", "how many"
    ]

    for kw in cohort_keywords:
        if kw in query:
            return "cohort"

    return "specific"