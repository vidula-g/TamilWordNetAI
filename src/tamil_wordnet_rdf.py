from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF

from tamil_wordnet_parser import parse_twn_records


TW = Namespace(
    "http://example.org/tamilwordnet/"
)


OUTPUT_FILE = "rdf/tamil_wordnet_generated.ttl"


def create_rdf_graph(records):

    graph = Graph()

    graph.bind(
        "tw",
        TW
    )

    for record in records:

        nodeindex = record["nodeindex"]
        label = record["label"]
        relation = record["relation"]
        relation_name = record["relation_name"]
        pos = record["pos"]
        parent = record["parent"]

        word_uri = TW[
            "word_" +
            nodeindex.replace(",", "_")
        ]

        graph.add(
            (
                word_uri,
                RDF.type,
                TW.Word
            )
        )

        graph.add(
            (
                word_uri,
                TW.label,
                Literal(label)
            )
        )

        graph.add(
            (
                word_uri,
                TW.nodeIndex,
                Literal(nodeindex)
            )
        )

        graph.add(
            (
                word_uri,
                TW.pos,
                Literal(pos)
            )
        )

        graph.add(
            (
                word_uri,
                TW.relationCode,
                Literal(relation)
            )
        )

        graph.add(
            (
                word_uri,
                TW.relationName,
                Literal(relation_name)
            )
        )

        if parent:

            parent_uri = TW[
                "word_" +
                parent.replace(",", "_")
            ]

            graph.add(
                (
                    word_uri,
                    TW.parent,
                    parent_uri
                )
            )

    return graph


if __name__ == "__main__":

    print("========================================")
    print("     TAMIL WORDNET RDF CONVERTER")
    print("========================================")

    print("\nParsing Tamil WordNet SQL...")

    records = parse_twn_records()

    print(
        "Total records:",
        len(records)
    )

    print("\nCreating RDF graph...")

    graph = create_rdf_graph(records)

    print(
        "Total RDF triples:",
        len(graph)
    )

    print("\nSaving RDF file...")

    graph.serialize(
        destination=OUTPUT_FILE,
        format="turtle"
    )

    print(
        "\nRDF file created successfully:"
    )

    print(OUTPUT_FILE)