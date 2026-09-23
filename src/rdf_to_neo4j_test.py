import os

from rdflib import Graph, Namespace
from rdflib.namespace import RDF
from neo4j import GraphDatabase


# ========================================
# CONFIGURATION
# ========================================

RDF_FILE = "rdf/tamil_wordnet_generated.ttl"

URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = os.getenv("NEO4J_PASSWORD")

TW = Namespace("http://example.org/tamilwordnet/")

TEST_LIMIT = 10


# ========================================
# CHECK PASSWORD
# ========================================

if not PASSWORD:
    raise ValueError(
        "NEO4J_PASSWORD environment variable is not set."
    )


# ========================================
# LOAD RDF
# ========================================

def load_rdf():

    print("\nLoading actual Tamil WordNet RDF...")

    graph = Graph()

    graph.parse(
        RDF_FILE,
        format="turtle"
    )

    print("RDF loaded successfully!")
    print("Total RDF triples:", len(graph))

    return graph


# ========================================
# GET WORDNET RECORDS
# ========================================

def get_wordnet_records(graph):

    query = """
    SELECT ?node ?label ?nodeindex ?pos ?relationCode ?relationName
    WHERE {

        ?node rdf:type tw:Word .

        OPTIONAL {
            ?node tw:label ?label .
        }

        OPTIONAL {
            ?node tw:nodeIndex ?nodeindex .
        }

        OPTIONAL {
            ?node tw:pos ?pos .
        }

        OPTIONAL {
            ?node tw:relationCode ?relationCode .
        }

        OPTIONAL {
            ?node tw:relationName ?relationName .
        }
    }

    LIMIT 10
    """

    results = graph.query(
        query,
        initNs={
            "rdf": RDF,
            "tw": TW
        }
    )

    records = []

    for row in results:

        records.append({
            "node_uri": str(row.node),
            "label": str(row.label) if row.label else "",
            "nodeindex": str(row.nodeindex) if row.nodeindex else "",
            "pos": str(row.pos) if row.pos else "",
            "relationCode": (
                str(row.relationCode)
                if row.relationCode
                else ""
            ),
            "relationName": (
                str(row.relationName)
                if row.relationName
                else ""
            )
        })

    return records


# ========================================
# INSERT WORDNET NODE
# ========================================

def insert_wordnet_node(tx, record):

    query = """
    MERGE (w:WordNetWord {
        nodeindex: $nodeindex
    })

    SET
        w.label = $label,
        w.pos = $pos,
        w.relationCode = $relationCode,
        w.relationName = $relationName

    RETURN w
    """

    tx.run(
        query,
        nodeindex=record["nodeindex"],
        label=record["label"],
        pos=record["pos"],
        relationCode=record["relationCode"],
        relationName=record["relationName"]
    )


# ========================================
# IMPORT TEST
# ========================================

def import_test():

    graph = load_rdf()

    print("\nExtracting test records...")

    records = get_wordnet_records(graph)

    print(
        f"Records selected for test: {len(records)}"
    )

    print("\nConnecting to Neo4j...")

    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD)
    )

    try:

        driver.verify_connectivity()

        print("Connected to Neo4j successfully!")

        with driver.session() as session:

            for record in records:

                session.execute_write(
                    insert_wordnet_node,
                    record
                )

                print(
                    f"Imported: "
                    f"{record['label']} "
                    f"({record['nodeindex']})"
                )

        print("\n========================================")
        print("       TEST IMPORT COMPLETED")
        print("========================================")

    except Exception as error:

        print("\nImport failed.")
        print("Error:", error)

    finally:

        driver.close()


# ========================================
# MAIN
# ========================================

if __name__ == "__main__":

    print("========================================")
    print("   RDF → NEO4J WORDNET TEST IMPORT")
    print("========================================")

    import_test()