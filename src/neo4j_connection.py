import os

from neo4j import GraphDatabase


# ==================================================
# NEO4J CONNECTION SETTINGS
# ==================================================

URI = "bolt://localhost:7687"

USERNAME = "neo4j"

PASSWORD = os.getenv("NEO4J_PASSWORD")


if not PASSWORD:
    raise ValueError(
        "NEO4J_PASSWORD environment variable is not set."
    )


# ==================================================
# CREATE DRIVER
# ==================================================

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)


# ==================================================
# TEST CONNECTION
# ==================================================

def test_connection():

    driver.verify_connectivity()

    print("Connected to Neo4j successfully!")


# ==================================================
# SEARCH WORD IN NEO4J
# ==================================================

def search_word(word):

    query = """
    MATCH (w:Word)<-[:MENTIONS]-(p:Passage)
    MATCH (work:Work)-[:HAS_SECTION]->(section:Section)
          -[:HAS_PASSAGE]->(p)
    MATCH (p)-[:HAS_CATEGORY]->(c:Category)

    WHERE w.text = $word

    RETURN
        w.text AS word,
        work.title AS source,
        p.text AS passage,
        c.name AS category

    ORDER BY source
    """

    with driver.session() as session:

        result = session.run(
            query,
            word=word
        )

        records = []

        for record in result:

            records.append({
                "word": record["word"],
                "source": record["source"],
                "passage": record["passage"],
                "category": record["category"]
            })

        return records


# ==================================================
# TEST
# ==================================================

if __name__ == "__main__":

    test_connection()

    results = search_word("அன்பு")

    for item in results:

        print(item)

    driver.close()