import json

from src.ai_pipeline import analyze_tamil_sentence


if __name__ == "__main__":

    print("\n========================================")
    print("       TAMIL CONTEXT SEARCH AI")
    print("========================================")

    query = input("\nEnter Tamil sentence: ")

    result = analyze_tamil_sentence(query)

    print("\n========================================")
    print("           AI JSON RESULT")
    print("========================================")

    print(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=4
        )
    )