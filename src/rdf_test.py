from rdflib import Graph, Namespace

graph = Graph()

graph.parse(
    "rdf/tamil_wordnet.ttl",
    format="turtle"
)

TW = Namespace(
    "http://example.org/tamilwordnet/"
)

query = """
SELECT ?workTitle
WHERE {
    TW:Anbu TW:appearsIn ?work .
    ?work TW:title ?workTitle .
}
"""

results = graph.query(
    query,
    initNs={"TW": TW}
)

print("Where does அன்பு appear?\n")

for row in results:
    print(row.workTitle)