import yake
import spacy
from storage.redis_store import RedisStore
kw_extractor = yake.KeywordExtractor()

# content = None
# with open("./samples/big_sample.txt") as f:
#     content = f.read()
#

content = "How should I create a new class that manages the profiles of the user?"

nlp = spacy.load("en_core_web_sm")
extracted_expr = [(kw, w) for kw, w in kw_extractor.extract_keywords(content)]
# extracted_expr.sort(key=lambda x: x[1], reverse=True)

wbow = {}
for kw, w in extracted_expr:
    doc = nlp(kw.lower())
    # remove the stop words from the given text for greater quality embeddings and faster outputs
    lemmas = [token.lemma_ for token in doc if not (token.is_punct or token.is_stop or token.like_num or token.like_url or token.like_email or token.is_currency)]
    w_len = w / len(lemmas)

    for word in lemmas:
        if not wbow.get(word):
            wbow[word] = (0, 0)
        wbow[word] = (wbow[word][0] + w_len, wbow[word][1] + 1)

    # print(f"Weight of phrase {w} with lemmas: {lemmas}")

wbow = sorted([(k, w / c) for k, (w, c) in wbow.items()], key=lambda x: x[1], reverse=True)
print(wbow)

# develop an algorithm for optimizing data retrieval
tree_id = "d05ff527-61ce-42bc-ad0b-439ac5511dde"
print(RedisStore.get(tree_id))
