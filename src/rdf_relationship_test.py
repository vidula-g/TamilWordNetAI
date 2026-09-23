from rdflib import Graph, Namespace

from rdflib.namespace import RDF


RDF_FILE = "rdf/tamil_wordnet_generated.ttl"

TW = Namespace(
    "http://example.org/tamilwordnet/"
)


def load_rdf():

    print("\nLoading Tamil WordNet RDF...")

    graph = Graph()

    graph.parse(
        RDF_FILE,
        format="turtle"
    )

    print("RDF loaded successfully!")
    print("Total triples:", len(graph))

    return graph


def test_relationships(graph):

    query = """
    SELECT
        ?child
        ?childLabel
        ?relation
        ?parent
        ?parentLabel

    WHERE {

        ?child rdf:type tw:Word .

        ?child tw:label ?childLabel .

        ?child tw:parent ?parent .

        ?parent tw:label ?parentLabel .

        OPTIONAL {
            ?child tw:relationName ?relation .
        }
    }

    LIMIT 20
    """

    results = graph.query(
        query,
        initNs={
            "rdf": RDF,
            "tw": TW
        }
    )

    print("\n========================================")
    print("       WORDNET RELATIONSHIP TEST")
    print("========================================")

    count = 0

    for row in results:

        count += 1

        print("\nRelationship", count)
        print("----------------------------")

        print("Parent word :", row.parentLabel)
        print("Child word  :", row.childLabel)
        print("Relation    :", row.relation)

        print("Parent URI  :", row.parent)
        print("Child URI   :", row.child)

    print("\nTotal relationships shown:", count)


if __name__ == "__main__":

    print("========================================")
    print("    RDF WORDNET RELATIONSHIP TEST")
    print("========================================")

    graph = load_rdf()

    test_relationships(graph)