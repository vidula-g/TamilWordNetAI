import re

from relation_mapper import get_relation_name


SQL_FILE = r"C:\Users\vidul\AppData\Local\Temp\c71e519a-9fb7-4140-b5a9-4826a892e24c_TamilWordnet.tgz.TamilWordnet.tgz\TamilWordnet\tvudump.sql"


def parse_twn_records():

    records = []

    with open(
        SQL_FILE,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as file:

        for line in file:

            if not line.startswith(
                "INSERT INTO twn VALUES"
            ):
                continue

            match = re.search(
                r"INSERT INTO twn VALUES "
                r"\('([^']*)','([^']*)',"
                r"([^,]*),([^,]*),"
                r"'([^']*)','([^']*)',"
                r"([^,]*),'([^']*)','([^']*)'\);",
                line
            )

            if not match:
                continue

            nodeindex = match.group(1)
            label = match.group(2)
            relation = match.group(5)
            pos = match.group(9)

            if "," in nodeindex:
                parent = nodeindex.rsplit(",", 1)[0]
            else:
                parent = None

            relation_name = get_relation_name(
                pos,
                relation
            )

            records.append({
                "nodeindex": nodeindex,
                "label": label,
                "relation": relation,
                "relation_name": relation_name,
                "pos": pos,
                "parent": parent
            })

    return records


if __name__ == "__main__":

    records = parse_twn_records()

    print("========================================")
    print("       TAMIL WORDNET PARSER")
    print("========================================")

    print(
        "\nTotal twn records:",
        len(records)
    )

    print("\nFirst 20 records:\n")

    for record in records[:20]:
        print(record)