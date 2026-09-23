RELATION_NAMES = {
    "Noun": {
        "1": "Meronym",
        "2": "Holonym",
        "3": "Hyponym",
        "4": "Synonym",
        "5": "Coterm",
        "7": "RelVerb",
        "8": "RelNoun",
        "9": "RelNoun",
        "10": "RelNoun",
        "11": "RelNoun",
        "12": "RelVerb"
    },

    "Verb": {
        "3": "Troponym",
        "4": "Synonym",
        "7": "Nominal",
        "8": "RelNoun",
        "9": "RelNoun",
        "10": "RelNoun",
        "11": "RelNoun"
    },

    "Adjective": {
        "4": "Synonym",
        "8": "RelNoun",
        "9": "RelNoun",
        "10": "RelNoun",
        "11": "RelNoun"
    },

    "Adverb": {
        "4": "Synonym",
        "8": "RelNoun",
        "9": "RelNoun",
        "10": "RelNoun",
        "11": "RelNoun"
    }
}


def get_relation_name(pos, relation):
    return RELATION_NAMES.get(pos, {}).get(
        relation,
        "Unknown"
    )


if __name__ == "__main__":

    print("Tamil WordNet Relation Mapper")
    print("--------------------------------")

    test_cases = [
        ("Noun", "1"),
        ("Noun", "3"),
        ("Noun", "4"),
        ("Noun", "5"),
        ("Noun", "7"),
        ("Noun", "8"),
        ("Noun", "9"),
        ("Noun", "10"),
        ("Noun", "11"),

        ("Verb", "3"),
        ("Verb", "4"),
        ("Verb", "7"),
        ("Verb", "8"),

        ("Adjective", "4"),
        ("Adverb", "4")
    ]

    for pos, relation in test_cases:

        name = get_relation_name(
            pos,
            relation
        )

        print(
            f"{pos} + relation {relation} → {name}"
        )