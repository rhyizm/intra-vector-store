from sentence_transformers import SentenceTransformer

def create_embeddings(documents, model="stsb-xlm-r-multilingual"):
    sentence_transformers = SentenceTransformer(model)
    embeddings = sentence_transformers.encode(documents)

    return embeddings.tolist()