import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# Load data once
skills_df = pd.read_csv("dataset/skills.csv")
skill_names = skills_df["skill_name"].tolist()
embeddings = np.load("backend/ml/skill_embeddings.npy")

# Case-insensitive mapping
skill_to_index = {skill.lower(): i for i, skill in enumerate(skill_names)}


def get_embedding(skill_name):
    idx = skill_to_index.get(skill_name.lower())
    if idx is None:
        return None
    return embeddings[idx]


def compute_similarity(skill1, skill2):
    emb1 = get_embedding(skill1)
    emb2 = get_embedding(skill2)

    if emb1 is None or emb2 is None:
        return 0

    sim = cosine_similarity([emb1], [emb2])[0][0]
    return (sim + 1) / 2  # Map to 0-1 range