import json


def load_literary_data():

    with open(
        "data/literary_data.json",
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    return data


# Test
data = load_literary_data()

print("Number of records:", len(data))

for item in data:
    print(item["word"], "→", item["text"])