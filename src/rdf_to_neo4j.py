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

TW = Namespace(
    "http://example.org/tamilwordnet/"
)

BATCH_SIZE = 1000


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

    print("\nLoading Tamil WordNet RDF...")

    graph = Graph()

    graph.parse(
        RDF_FILE,
        format="turtle"
    )

    print("RDF loaded successfully!")
    print(
        "Total RDF triples:",
        len(graph)
    )

    return graph


# ========================================
# EXTRACT WORDNET NODES
# ========================================

def extract_nodes(graph):

    query = """
    SELECT
        ?node
        ?label
        ?nodeindex
        ?pos
        ?relationCode
        ?relationName

    WHERE {

        ?node rdf:type tw:Word .

        ?node tw:label ?label .

        ?node tw:nodeIndex ?nodeindex .

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
    """

    results = graph.query(
        query,
        initNs={
            "rdf": RDF,
            "tw": TW
        }
    )

    nodes = []

    for row in results:

        nodes.append({
            "nodeindex": str(
                row.nodeindex
            ),

            "label": str(
                row.label
            ),

            "pos": (
                str(row.pos)
                if row.pos
                else ""
            ),

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

    return nodes


# ========================================
# EXTRACT RELATIONSHIPS
# ========================================

def extract_relationships(graph):

    query = """
    SELECT
        ?childNodeIndex
        ?parentNodeIndex
        ?relation

    WHERE {

        ?child rdf:type tw:Word .

        ?child tw:nodeIndex ?childNodeIndex .

        ?child tw:parent ?parent .

        ?parent tw:nodeIndex ?parentNodeIndex .

        ?child tw:relationName ?relation .
    }
    """

    results = graph.query(
        query,
        initNs={
            "rdf": RDF,
            "tw": TW
        }
    )

    relationships = []

    for row in results:

        relationships.append({
            "child_nodeindex": str(
                row.childNodeIndex
            ),

            "parent_nodeindex": str(
                row.parentNodeIndex
            ),

            "relation": str(
                row.relation
            )
        })

    return relationships


# ========================================
# RELATIONSHIP TYPE MAPPING
# ========================================

RELATIONSHIP_TYPES = {

    "Synonym": "SYNONYM_OF",

    "Hyponym": "HYPONYM_OF",

    "Meronym": "MERONYM_OF",

    "Troponym": "TROPONYM_OF",

    "RelNoun": "RELATED_NOUN",

    "RelVerb": "RELATED_VERB",

    "Coterm": "COTERM_OF",

    "Nominal": "NOMINAL_OF"
}


# ========================================
# INSERT NODE BATCH
# ========================================

def insert_nodes(tx, nodes):

    query = """
    UNWIND $nodes AS node

    MERGE (w:WordNetWord {
        nodeindex: node.nodeindex
    })

    SET
        w.label = node.label,
        w.pos = node.pos,
        w.relationCode = node.relationCode,
        w.relationName = node.relationName
    """

    tx.run(
        query,
        nodes=nodes
    )


# ========================================
# INSERT RELATIONSHIP BATCH
# ========================================

def insert_relationships(
    tx,
    relationships,
    relation_type
):

    query = f"""
    UNWIND $relationships AS rel

    MATCH (child:WordNetWord {{
        nodeindex: rel.child_nodeindex
    }})

    MATCH (parent:WordNetWord {{
        nodeindex: rel.parent_nodeindex
    }})

    MERGE (
        child
    )-[:{relation_type}]->(
        parent
    )
    """

    tx.run(
        query,
        relationships=relationships
    )


# ========================================
# IMPORT NODES
# ========================================

def import_nodes(
    driver,
    nodes
):

    print("\n========================================")
    print("        IMPORTING WORDNET NODES")
    print("========================================")

    total = len(nodes)

    print(
        f"Total nodes to import: {total}"
    )

    for start in range(
        0,
        total,
        BATCH_SIZE
    ):

        batch = nodes[
            start:start + BATCH_SIZE
        ]

        with driver.session() as session:

            session.execute_write(
                insert_nodes,
                batch
            )

        end = min(
            start + BATCH_SIZE,
            total
        )

        print(
            f"Imported nodes: "
            f"{end}/{total}"
        )


# ========================================
# IMPORT RELATIONSHIPS
# ========================================

def import_relationships(
    driver,
    relationships
):

    print("\n========================================")
    print("     IMPORTING WORDNET RELATIONSHIPS")
    print("========================================")

    grouped = {}

    for relationship in relationships:

        relation_name = relationship[
            "relation"
        ]

        neo4j_type = RELATIONSHIP_TYPES.get(
            relation_name
        )

        if not neo4j_type:

            print(
                "Skipping unknown relation:",
                relation_name
            )

            continue

        if neo4j_type not in grouped:

            grouped[neo4j_type] = []

        grouped[neo4j_type].append(
            relationship
        )

    for relation_type, items in grouped.items():

        print(
            f"\n{relation_type}: "
            f"{len(items)} relationships"
        )

        total = len(items)

        for start in range(
            0,
            total,
            BATCH_SIZE
        ):

            batch = items[
                start:start + BATCH_SIZE
            ]

            with driver.session() as session:

                session.execute_write(
                    insert_relationships,
                    batch,
                    relation_type
                )

            end = min(
                start + BATCH_SIZE,
                total
            )

            print(
                f"  Imported: "
                f"{end}/{total}"
            )


# ========================================
# MAIN IMPORT
# ========================================

def import_wordnet():

    graph = load_rdf()

    print("\nExtracting WordNet nodes...")

    nodes = extract_nodes(graph)

    print(
        "Total WordNet nodes:",
        len(nodes)
    )

    print("\nExtracting relationships...")

    relationships = extract_relationships(
        graph
    )

    print(
        "Total WordNet relationships:",
        len(relationships)
    )

    print("\nConnecting to Neo4j...")

    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD)
    )

    try:

        driver.verify_connectivity()

        print(
            "Connected to Neo4j successfully!"
        )

        import_nodes(
            driver,
            nodes
        )

        import_relationships(
            driver,
            relationships
        )

        print("\n========================================")
        print("      FULL WORDNET IMPORT COMPLETE")
        print("========================================")

    except Exception as error:

        print("\nImport failed.")
        print("Error:", error)

        raise

    finally:

        driver.close()


# ========================================
# RUN
# ========================================

if __name__ == "__main__":

    print("========================================")
    print("     TAMIL WORDNET RDF → NEO4J")
    print("          FULL IMPORT")
    print("========================================")

    import_wordnet()