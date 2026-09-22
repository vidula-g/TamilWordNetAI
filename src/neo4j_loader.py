import json
import os

from neo4j import GraphDatabase

from src.embeddings import create_embeddings


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
# LOAD JSON DATA
# ==================================================

def load_json_data():

    with open(
        "data/literary_data.json",
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ==================================================
# INSERT ONE LITERARY RECORD
# ==================================================

def insert_record(tx, item, embedding):

    query = """
    MERGE (w:Work {
        title: $source
    })

    SET w.author = CASE
        WHEN $source = "திருக்குறள்"
        THEN "திருவள்ளுவர்"
        ELSE "Unknown"
    END

    MERGE (s:Section {
        work_title: $source,
        name: "General"
    })

    MERGE (w)-[:HAS_SECTION]->(s)

    MERGE (p:Passage {
        passage_id: $passage_id
    })

    SET p.number = $number,
        p.text = $text,
        p.embedding = $embedding

    MERGE (s)-[:HAS_PASSAGE]->(p)

    MERGE (word:Word {
        text: $word
    })

    SET word.lemma = $word

    MERGE (p)-[:MENTIONS]->(word)

    MERGE (c:Category {
        name: $category
    })

    MERGE (p)-[:HAS_CATEGORY]->(c)
    """

    tx.run(
        query,
        source=item["source"],
        passage_id=f"json_{item['id']}",
        number=item["id"],
        text=item["text"],
        word=item["word"],
        category=item["category"],
        embedding=embedding
    )


# ==================================================
# IMPORT ALL RECORDS
# ==================================================

def import_data():

    data = load_json_data()

    print(
        f"Found {len(data)} records in literary_data.json"
    )


    # ==================================================
    # CREATE EMBEDDINGS
    # ==================================================

    print("\nCreating embeddings for literary passages...")

    texts = [
        item["text"]
        for item in data
    ]

    embeddings = create_embeddings(texts)

    embeddings = embeddings.cpu().tolist()

    print(
        f"Created {len(embeddings)} embeddings."
    )

    print(
        f"Embedding dimension: {len(embeddings[0])}"
    )


    # ==================================================
    # CONNECT TO NEO4J
    # ==================================================

    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD)
    )

    try:

        driver.verify_connectivity()

        print("\nConnected to Neo4j successfully!")


        # ==================================================
        # INSERT RECORDS
        # ==================================================

        with driver.session() as session:

            for index, item in enumerate(data):

                session.execute_write(
                    insert_record,
                    item,
                    embeddings[index]
                )

                print(
                    f"Imported record {item['id']}: "
                    f"{item['word']}"
                )


        print("\nAll records imported successfully!")

        print(
            "Embeddings stored in Neo4j successfully!"
        )


    except Exception as error:

        print("\nImport failed.")

        print("Error:", error)


    finally:

        driver.close()


# ==================================================
# RUN IMPORT
# ==================================================

if __name__ == "__main__":

    import_data()