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

TEST_LIMIT = 20


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
    print("Total RDF triples:", len(graph))

    return graph


# ========================================
# GET RELATIONSHIPS
# ========================================

def get_relationships(graph):

    query = f"""
    SELECT
        ?child
        ?childLabel
        ?childNodeIndex
        ?relation
        ?parent
        ?parentLabel
        ?parentNodeIndex

    WHERE {{

        ?child rdf:type tw:Word .

        ?child tw:label ?childLabel .

        ?child tw:nodeIndex ?childNodeIndex .

        ?child tw:parent ?parent .

        ?parent tw:label ?parentLabel .

        ?parent tw:nodeIndex ?parentNodeIndex .

        ?child tw:relationName ?relation .
    }}

    LIMIT {TEST_LIMIT}
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

            "child_label": str(
                row.childLabel
            ),

            "relation": str(
                row.relation
            ),

            "parent_nodeindex": str(
                row.parentNodeIndex
            ),

            "parent_label": str(
                row.parentLabel
            )
        })

    return relationships


# ========================================
# GET REQUIRED NODES
# ========================================

def get_required_nodes(relationships):

    nodes = {}

    for relationship in relationships:

        child_index = relationship[
            "child_nodeindex"
        ]

        parent_index = relationship[
            "parent_nodeindex"
        ]

        nodes[child_index] = {
            "nodeindex": child_index,
            "label": relationship[
                "child_label"
            ]
        }

        nodes[parent_index] = {
            "nodeindex": parent_index,
            "label": relationship[
                "parent_label"
            ]
        }

    return list(nodes.values())


# ========================================
# INSERT WORDNET NODE
# ========================================

def insert_wordnet_node(tx, node):

    query = """
    MERGE (w:WordNetWord {
        nodeindex: $nodeindex
    })

    SET w.label = $label

    RETURN w
    """

    tx.run(
        query,
        nodeindex=node["nodeindex"],
        label=node["label"]
    )


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
# CREATE RELATIONSHIP
# ========================================

def create_relationship(tx, relationship):

    relation_name = relationship[
        "relation"
    ]

    neo4j_relation = RELATIONSHIP_TYPES.get(
        relation_name
    )

    if not neo4j_relation:

        print(
            f"Skipping unknown relation: "
            f"{relation_name}"
        )

        return

    query = f"""
    MATCH (child:WordNetWord {{
        nodeindex: $child_nodeindex
    }})

    MATCH (parent:WordNetWord {{
        nodeindex: $parent_nodeindex
    }})

    MERGE (child)-[:{neo4j_relation}]->(parent)
    """

    tx.run(
        query,
        child_nodeindex=relationship[
            "child_nodeindex"
        ],

        parent_nodeindex=relationship[
            "parent_nodeindex"
        ]
    )


# ========================================
# IMPORT TEST
# ========================================

def import_relationship_test():

    graph = load_rdf()

    print("\nExtracting relationships...")

    relationships = get_relationships(
        graph
    )

    print(
        f"Relationships selected: "
        f"{len(relationships)}"
    )

    print("\nFinding required WordNet nodes...")

    nodes = get_required_nodes(
        relationships
    )

    print(
        f"Required nodes: {len(nodes)}"
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

        # --------------------------------
        # CREATE REQUIRED NODES
        # --------------------------------

        print(
            "\nCreating required WordNet nodes..."
        )

        with driver.session() as session:

            for node in nodes:

                session.execute_write(
                    insert_wordnet_node,
                    node
                )

                print(
                    f"Node: "
                    f"{node['label']} "
                    f"({node['nodeindex']})"
                )

        # --------------------------------
        # CREATE RELATIONSHIPS
        # --------------------------------

        print(
            "\nCreating WordNet relationships..."
        )

        with driver.session() as session:

            for relationship in relationships:

                session.execute_write(
                    create_relationship,
                    relationship
                )

                print(
                    f"{relationship['child_label']} "
                    f"--["
                    f"{relationship['relation']}"
                    f"]--> "
                    f"{relationship['parent_label']}"
                )

        print("\n========================================")
        print("   RELATIONSHIP TEST COMPLETED")
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
    print(" RDF → NEO4J RELATIONSHIP TEST")
    print("========================================")

    import_relationship_test()