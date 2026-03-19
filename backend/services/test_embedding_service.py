from embedding_service import compute_similarity, get_embedding

# Test the service
if __name__ == "__main__":
    test_pairs = [
        ("Python Basics", "Data Structures"),
        ("Machine Learning Fundamentals", "Neural Networks Basics"),
        ("Linear Algebra", "Calculus"),
    ]
    
    for s1, s2 in test_pairs:
        sim = compute_similarity(s1, s2)
        print(f"{s1} vs {s2}: {sim:.3f}")