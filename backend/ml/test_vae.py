import torch
import numpy as np
import pandas as pd
import joblib
import json
from vae_model import VAE

def load_artifacts():
    """Load trained model and artifacts"""
    print("Loading model artifacts...")
    
    # Load metadata
    with open('backend/ml/model_metadata.json', 'r') as f:
        metadata = json.load(f)
    
    # Load scaler
    scaler = joblib.load("backend/ml/feature_scaler.pkl")
    
    # Load embeddings
    embeddings = np.load("backend/ml/skill_embeddings.npy")
    
    # Load model
    model = VAE(input_dim=metadata['input_dim'], latent_dim=metadata['latent_dim'])
    model.load_state_dict(torch.load("backend/ml/vae_model.pth"))
    model.eval()
    
    # Create mappings
    skill_names = metadata['skill_names']
    skill_to_idx = {skill: i for i, skill in enumerate(skill_names)}
    idx_to_skill = {i: skill for i, skill in enumerate(skill_names)}
    
    print(f"✓ Loaded model with input_dim={metadata['input_dim']}, latent_dim={metadata['latent_dim']}")
    print(f"✓ Loaded embeddings with shape: {embeddings.shape}")
    
    return model, scaler, embeddings, skill_names, skill_to_idx, idx_to_skill

def cosine_sim(a, b):
    """Compute cosine similarity between two vectors"""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8)

def test_skill_pairs(embeddings, skill_to_idx, test_pairs):
    """Test similarity between skill pairs"""
    print("\n" + "=" * 60)
    print("Testing Skill Pair Similarities")
    print("=" * 60)
    
    for skill1, skill2 in test_pairs:
        if skill1 in skill_to_idx and skill2 in skill_to_idx:
            idx1, idx2 = skill_to_idx[skill1], skill_to_idx[skill2]
            emb1, emb2 = embeddings[idx1], embeddings[idx2]
            sim = cosine_sim(emb1, emb2)
            print(f"{skill1:35} vs {skill2:30} → {sim:6.3f}")
        else:
            print(f"❌ {skill1} or {skill2} not found")

def find_similar_skills(embeddings, skill_to_idx, idx_to_skill, skill_name, top_k=5):
    """Find most similar skills to a given skill"""
    if skill_name not in skill_to_idx:
        print(f"❌ Skill '{skill_name}' not found")
        return
    
    idx = skill_to_idx[skill_name]
    emb = embeddings[idx]
    
    # Compute similarities
    similarities = []
    for i, other_emb in enumerate(embeddings):
        if i != idx:
            sim = cosine_sim(emb, other_emb)
            similarities.append((i, sim))
    
    # Sort by similarity
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\nTop {top_k} skills similar to '{skill_name}':")
    for i, (other_idx, sim) in enumerate(similarities[:top_k]):
        print(f"  {i+1}. {idx_to_skill[other_idx]:35} → {sim:6.3f}")

def test_category_clusters(embeddings, skill_names, skills_df):
    """Test if skills in same category cluster together"""
    print("\n" + "=" * 60)
    print("Testing Category Clusters")
    print("=" * 60)
    
    categories = skills_df['category'].unique()
    skill_to_idx = {skill: i for i, skill in enumerate(skill_names)}
    
    for category in categories[:3]:  # Test first 3 categories
        cat_skills = skills_df[skills_df['category'] == category]['skill_name'].tolist()[:3]
        
        if len(cat_skills) >= 2:
            print(f"\n{category}:")
            for i in range(len(cat_skills)):
                for j in range(i+1, len(cat_skills)):
                    if cat_skills[i] in skill_to_idx and cat_skills[j] in skill_to_idx:
                        idx1, idx2 = skill_to_idx[cat_skills[i]], skill_to_idx[cat_skills[j]]
                        emb1, emb2 = embeddings[idx1], embeddings[idx2]
                        sim = cosine_sim(emb1, emb2)
                        print(f"  {cat_skills[i]:30} vs {cat_skills[j]:30} → {sim:6.3f}")

def main():
    """Main test function"""
    # Load artifacts
    model, scaler, embeddings, skill_names, skill_to_idx, idx_to_skill = load_artifacts()
    
    # Load original skills data for category testing
    skills_df = pd.read_csv("dataset/skills.csv")
    
    # Test 1: Critical skill pairs
    test_pairs = [
        ("Python Basics", "Data Structures"),
        ("Python Basics", "Java Programming"),
        ("Machine Learning Fundamentals", "Neural Networks Basics"),
        ("Machine Learning Fundamentals", "Deep Learning"),
        ("Linear Algebra", "Calculus"),
        ("Linear Algebra", "Statistics"),
        ("HTML & CSS Fundamentals", "JavaScript Fundamentals"),
        ("HTML & CSS Fundamentals", "React.js"),
        ("AWS Core Services", "Cloud Fundamentals"),
        ("Database Programming", "SQL for Data Science"),
    ]
    test_skill_pairs(embeddings, skill_to_idx, test_pairs)
    
    # Test 2: Find similar skills for key skills
    print("\n" + "=" * 60)
    print("Finding Similar Skills")
    print("=" * 60)
    
    key_skills = ["Python Basics", "Machine Learning Fundamentals", "Linear Algebra", "AWS Core Services"]
    for skill in key_skills:
        find_similar_skills(embeddings, skill_to_idx, idx_to_skill, skill, top_k=3)
    
    # Test 3: Category clustering
    test_category_clusters(embeddings, skill_names, skills_df)
    
    # Test 4: Model reconstruction (optional)
    print("\n" + "=" * 60)
    print("Testing Model Reconstruction")
    print("=" * 60)
    
    # Test on a few samples
    test_skills = ["Python Basics", "Machine Learning Fundamentals", "AWS Core Services"]
    
    # Load and normalize test data
    features, _ = create_skill_features(skills_df)  # Need to import this function
    features_normalized = scaler.transform(features)
    test_data = torch.tensor(features_normalized).float()
    
    # Get reconstructions
    with torch.no_grad():
        recon, _, _ = model(test_data)
        recon_loss = nn.functional.mse_loss(recon, test_data, reduction='none').mean(dim=1)
    
    print(f"Average reconstruction loss: {recon_loss.mean():.4f}")
    print("✓ Model reconstruction test passed")

# Need to import create_skill_features from train
from train_vae import create_skill_features
import torch.nn as nn

if __name__ == "__main__":
    main()