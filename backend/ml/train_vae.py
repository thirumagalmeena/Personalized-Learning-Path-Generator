import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import joblib
import os
import json
from vae_model import VAE

def load_data():
    """Load and prepare skills data"""
    print("Loading skills data...")
    skills_df = pd.read_csv("dataset/skills.csv")
    skill_names = skills_df["skill_name"].tolist()
    num_skills = len(skill_names)
    
    print(f"Number of skills: {num_skills}")
    
    # Create skill to index mapping
    skill_to_idx = {skill: i for i, skill in enumerate(skill_names)}
    idx_to_skill = {i: skill for i, skill in enumerate(skill_names)}
    
    return skills_df, skill_names, skill_to_idx, idx_to_skill

def create_skill_features(skills_df):
    """Create basic features for each skill"""
    features = []
    
    # Get unique categories
    categories = skills_df['category'].unique()
    category_to_idx = {cat: i for i, cat in enumerate(categories)}
    
    # Difficulty mapping
    difficulty_map = {'Beginner': 1, 'Intermediate': 2, 'Advanced': 3}
    
    for _, row in skills_df.iterrows():
        feature = []
        
        # 1. Difficulty (normalized)
        feature.append(difficulty_map[row['difficulty']] / 3.0)
        
        # 2. Learning hours (normalized)
        feature.append(row['estimated_learning_hours'] / 100.0)
        
        # 3. Category (one-hot encoding)
        cat_vector = [0] * len(categories)
        cat_vector[category_to_idx[row['category']]] = 1
        feature.extend(cat_vector)
        
        features.append(feature)
    
    return np.array(features, dtype=np.float32), categories

def normalize_features(features):
    """Normalize features using StandardScaler"""
    print("\nNormalizing features...")
    scaler = StandardScaler()
    features_normalized = scaler.fit_transform(features)
    
    print(f"Normalized - mean: {features_normalized.mean():.3f}, std: {features_normalized.std():.3f}")
    print(f"Range: [{features_normalized.min():.3f}, {features_normalized.max():.3f}]")
    
    return features_normalized, scaler

def train_vae(model, data, epochs=500):
    """Train the VAE model"""
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    print("\n" + "=" * 60)
    print("Starting VAE Training")
    print("=" * 60)
    
    best_loss = float('inf')
    train_losses = []
    
    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()
        
        # Forward pass
        recon, mu, logvar = model(data)
        
        # Reconstruction loss (MSE)
        recon_loss = nn.functional.mse_loss(recon, data, reduction='sum')
        
        # KL divergence
        kl_loss = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())
        
        # Beta annealing
        beta = min(1.0, epoch / 100)
        
        # Total loss
        total_loss = recon_loss + beta * kl_loss
        
        # Backward pass
        total_loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()
        
        # Track loss
        train_losses.append(total_loss.item())
        
        # Track best model
        if total_loss.item() < best_loss:
            best_loss = total_loss.item()
            torch.save(model.state_dict(), "backend/ml/vae_model_best.pth")
        
        # Print progress
        if epoch % 50 == 0:
            print(f"Epoch {epoch:3d} | Total Loss: {total_loss.item():8.2f} | "
                  f"Recon Loss: {recon_loss.item():8.2f} | KL Loss: {kl_loss.item():8.2f} | Beta: {beta:.2f}")
    
    print("=" * 60)
    print(f"Training complete! Best loss: {best_loss:.2f}")
    
    return model, train_losses

def save_artifacts(model, scaler, embeddings, skill_names, categories, input_dim):
    """Save model and all artifacts"""
    print("\nSaving model and artifacts...")
    
    # Save final model
    torch.save(model.state_dict(), "backend/ml/vae_model.pth")
    print("✓ Model saved to: backend/ml/vae_model.pth")
    
    # Save embeddings
    np.save("backend/ml/skill_embeddings.npy", embeddings)
    print("✓ Embeddings saved to: backend/ml/skill_embeddings.npy")
    print(f"  Embedding shape: {embeddings.shape}")
    
    # Save scaler
    joblib.dump(scaler, "backend/ml/feature_scaler.pkl")
    print("✓ Scaler saved to: backend/ml/feature_scaler.pkl")
    
    # Save metadata
    metadata = {
        'skill_names': skill_names,
        'categories': list(categories),
        'input_dim': input_dim,
        'latent_dim': 16,
        'num_skills': len(skill_names)
    }
    
    with open('backend/ml/model_metadata.json', 'w') as f:
        json.dump(metadata, f)
    print("✓ Metadata saved to: backend/ml/model_metadata.json")

def main():
    """Main training function"""
    # Load data
    skills_df, skill_names, skill_to_idx, idx_to_skill = load_data()
    
    # Create features
    print("Creating skill features...")
    features, categories = create_skill_features(skills_df)
    input_dim = features.shape[1]
    print(f"Feature dimension: {input_dim}")
    print(f"Number of categories: {len(categories)}")
    
    # Normalize features
    features_normalized, scaler = normalize_features(features)
    
    # Convert to tensor
    data = torch.tensor(features_normalized).float()
    print(f"Data shape: {data.shape}")
    
    # Initialize model
    print("\nInitializing VAE model...")
    model = VAE(input_dim=input_dim, latent_dim=16)
    total_params = sum(p.numel() for p in model.parameters())
    print(f"Total parameters: {total_params:,}")
    
    # Train model
    model, train_losses = train_vae(model, data, epochs=500)
    
    # Generate embeddings
    model.eval()
    with torch.no_grad():
        embeddings = model.get_embeddings(data).numpy()
    
    # Save artifacts
    save_artifacts(model, scaler, embeddings, skill_names, categories, input_dim)
    
    print("\n✅ Training complete! Files saved in backend/ml/")
    return model, embeddings, skill_to_idx, idx_to_skill

if __name__ == "__main__":
    main()