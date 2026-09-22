import stanza

from src.vector_search import search_similar_passages


# ==================================================
# SETTINGS
# ==================================================

MIN_SIMILARITY = 0.0


# ==================================================
# LOAD TAMIL NLP MODEL
# ==================================================

print("Loading Tamil NLP model...")

nlp = stanza.Pipeline(
    lang="ta",
    processors="tokenize,pos,lemma"
)

print("Tamil NLP model loaded!")


# ==================================================
# MORPHOLOGICAL ANALYSIS
# ==================================================

def analyze_morphology(text):

    doc = nlp(text)

    results = []

    for sentence in doc.sentences:

        for word in sentence.words:

            results.append({

                "word": word.text,

                "lemma": word.lemma,

                "pos": word.upos

            })

    return results


# ==================================================
# GET LEMMAS
# ==================================================

def get_lemmas(text):

    morphology = analyze_morphology(text)

    lemmas = []

    for item in morphology:

        if item["lemma"]:

            lemmas.append(
                item["lemma"]
            )

    return lemmas


# ==================================================
# SEMANTIC RETRIEVAL FROM NEO4J
# ==================================================

def find_similar_contexts(
    query,
    top_k=3
):

    # Analyze the query using Tamil morphology
    query_lemmas = get_lemmas(query)

    # Search Neo4j using the query embedding
    neo4j_results = search_similar_passages(
        query,
        top_k=top_k
    )

    results = []

    for item in neo4j_results:

        similarity = item["similarity"]

        if similarity < MIN_SIMILARITY:
            continue

        results.append({

            "text": item["passage"],

            "source": item["source"],

            "category": item["category"],

            "word": item["word"],

            "similarity": similarity

        })

    return results