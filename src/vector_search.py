import os

from neo4j import GraphDatabase

from src.embeddings import create_query_embedding


# ==================================================
# NEO4J CONNECTION
# ==================================================

URI = "bolt://localhost:7687"

USERNAME = "neo4j"

PASSWORD = os.getenv("NEO4J_PASSWORD")


if not PASSWORD:
    raise ValueError(
        "NEO4J_PASSWORD environment variable is not set."
    )


# ==================================================
# VECTOR SEARCH
# ==================================================

def search_similar_passages(query, top_k=5):

    query_embedding = create_query_embedding(query)

    query_embedding = query_embedding.cpu().tolist()

    cypher_query = """
    MATCH (node:Passage)

    SEARCH node IN (
        VECTOR INDEX passage_embedding_index
        FOR $query_embedding
        LIMIT $top_k
    )
    SCORE AS score

    MATCH (work:Work)-[:HAS_SECTION]->(section:Section)
          -[:HAS_PASSAGE]->(node)

    MATCH (node)-[:MENTIONS]->(word:Word)

    MATCH (node)-[:HAS_CATEGORY]->(category:Category)

    RETURN
        node.text AS passage,
        work.title AS source,
        word.text AS word,
        category.name AS category,
        score

    ORDER BY score DESC
    """

    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD)
    )

    try:

        driver.verify_connectivity()

        print("Connected to Neo4j successfully!")

        with driver.session() as session:

            result = session.run(
                cypher_query,
                top_k=top_k,
                query_embedding=query_embedding
            )

            records = []

            for record in result:

                records.append({
                    "passage": record["passage"],
                    "source": record["source"],
                    "word": record["word"],
                    "category": record["category"],
                    "similarity": float(record["score"])
                })

            return records

    finally:

        driver.close()


# ==================================================
# TEST
# ==================================================

if __name__ == "__main__":

    query = "பாசம்"

    print("\n========================================")
    print("       NEO4J SEMANTIC SEARCH")
    print("========================================")

    print("\nQuery:", query)

    results = search_similar_passages(
        query,
        top_k=5
    )

    print("\nResults:\n")

    for result in results:

        print(result)