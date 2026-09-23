from rdflib import Graph, Namespace, Literal


RDF_FILE = "rdf/tamil_wordnet_generated.ttl"

TW = Namespace(
    "http://example.org/tamilwordnet/"
)


def load_graph():

    graph = Graph()

    graph.parse(
        RDF_FILE,
        format="turtle"
    )

    return graph


def get_relation_counts(graph):

    query = """
    SELECT ?relation (COUNT(?word) AS ?relationCount)
    WHERE {
        ?word tw:relationName ?relation .
    }
    GROUP BY ?relation
    ORDER BY DESC(?relationCount)
    """

    return graph.query(
        query,
        initNs={
            "tw": TW
        }
    )


def get_sample_words(graph, relation):

    query = """
    SELECT ?word ?pos
    WHERE {
        ?node tw:label ?word .
        ?node tw:relationName ?relation .

        OPTIONAL {
            ?node tw:pos ?pos .
        }

        FILTER (?relation = ?searchRelation)
    }
    LIMIT 5
    """

    return graph.query(
        query,
        initNs={
            "tw": TW
        },
        initBindings={
            "searchRelation": Literal(relation)
        }
    )


if __name__ == "__main__":

    print("========================================")
    print("      RDF RELATION TEST")
    print("========================================")

    print("\nLoading RDF...")

    graph = load_graph()

    print(
        "RDF loaded successfully!"
    )

    print(
        "Total triples:",
        len(graph)
    )

    print("\nRelation counts:\n")

    for row in get_relation_counts(graph):

        print(
            f"{row.relation}: "
            f"{row['relationCount']}"
        )

    relations_to_test = [
        "Synonym",
        "Hyponym",
        "Meronym",
        "Troponym",
        "Nominal"
    ]

    for relation in relations_to_test:

        print(
            f"\n--- {relation} ---"
        )

        results = get_sample_words(
            graph,
            relation
        )

        found = False

        for row in results:

            found = True

            print(
                f"{row.word} "
                f"({row.pos})"
            )

        if not found:

            print(
                "No records found."
            )