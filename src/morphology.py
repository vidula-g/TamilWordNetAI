import stanza

# Load Tamil NLP pipeline
nlp = stanza.Pipeline(
    lang="ta",
    processors="tokenize,pos,lemma"
)


def analyze_text(text):

    doc = nlp(text)

    results = []

    for sentence in doc.sentences:

        for word in sentence.words:

            word_info = {
                "word": word.text,
                "lemma": word.lemma,
                "pos": word.upos
            }

            results.append(word_info)

    return results


# Test
text = "அன்பு மனித வாழ்க்கையின் அடிப்படை பண்பாகும்"

results = analyze_text(text)

for item in results:
    print(item)