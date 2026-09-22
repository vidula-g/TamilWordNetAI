from src.retrieval import (
    analyze_morphology,
    find_similar_contexts
)


# ==================================================
# COMPLETE TAMIL AI PIPELINE
# ==================================================

def analyze_tamil_sentence(query, top_k=3):

    # ----------------------------------------------
    # 1. Morphological analysis
    # ----------------------------------------------

    morphology = analyze_morphology(query)

    # ----------------------------------------------
    # 2. Context retrieval
    # ----------------------------------------------

    contexts = find_similar_contexts(
        query,
        top_k=top_k
    )

    # ----------------------------------------------
    # 3. Extract categories
    # ----------------------------------------------

    categories = []

    for context in contexts:

        category = context["category"]

        if category not in categories:

            categories.append(category)

    # ----------------------------------------------
    # 4. Final structured result
    # ----------------------------------------------

    return {
        "query": query,
        "morphology": morphology,
        "contexts": contexts,
        "categories": categories
    }