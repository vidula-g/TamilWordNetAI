from sentence_transformers import SentenceTransformer


# ==================================================
# LOAD SENTENCE TRANSFORMER MODEL
# ==================================================

print("Loading Sentence Transformer model...")

model = SentenceTransformer(
    "Tamil-ai/tamil-embed-base"
)

print("Sentence Transformer loaded!")


# ==================================================
# CREATE EMBEDDINGS
# ==================================================

def create_embeddings(texts):

    return model.encode(
        texts,
        convert_to_tensor=True
    )


# ==================================================
# CREATE SINGLE QUERY EMBEDDING
# ==================================================

def create_query_embedding(text):

    return model.encode(
        text,
        convert_to_tensor=True
    )