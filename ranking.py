from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from database import get_keywords_for_role

def rank_by_job_role(resumes, job_role_name):
    """
    Ranks resumes based on predefined job role keywords and weights.
    Args:
        resumes: List of tuples (resume_id, file_name, text_content).
        job_role_name: Name of the selected job role.
    Returns:
        List of tuples (resume_id, file_name, score) sorted by score descending.
    """
    # Fetch keywords and their weights for the job role
    keywords = {kw: w for kw, w in get_keywords_for_role(job_role_name)}
    rankings = []

    # Calculate score for each resume
    for resume_id, file_name, text in resumes:
        score = 0
        text_lower = text.lower()  # Case-insensitive matching
        for keyword, weight in keywords.items():
            # Count occurrences of each keyword and multiply by weight
            occurrences = text_lower.count(keyword.lower())
            score += weight * occurrences  # Point-wise scoring
        # Normalize score to a maximum of 100 (optional, adjust as needed)
        max_possible_score = sum(keywords.values()) * 10  # Assuming max 10 occurrences per keyword
        normalized_score = min((score / max_possible_score) * 100, 100) if max_possible_score > 0 else 0
        rankings.append((resume_id, file_name, normalized_score))
    
    # Sort by score in descending order
    return sorted(rankings, key=lambda x: x[2], reverse=True)

def rank_by_description(resumes, description):
    """
    Ranks resumes based on similarity to a custom job description using TF-IDF.
    Args:
        resumes: List of tuples (resume_id, file_name, text_content).
        description: Custom job description entered by the user.
    Returns:
        List of tuples (resume_id, file_name, score) sorted by score descending.
    """
    # Prepare text data for TF-IDF vectorization
    texts = [text if text else "" for _, _, text in resumes]  # Handle empty texts
    texts.append(description)

    # Vectorize texts using TF-IDF with English stop words removal
    try:
        vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
        tfidf_matrix = vectorizer.fit_transform(texts)
        
        # Calculate cosine similarity between description (last row) and resumes
        cosine_sim = cosine_similarity(tfidf_matrix[-1:], tfidf_matrix[:-1])[0]
        
        # Create rankings list with scores scaled to 0-100
        rankings = [(resumes[i][0], resumes[i][1], score * 100) for i, score in enumerate(cosine_sim)]
    except ValueError:
        # Handle case where no valid features are extracted
        rankings = [(resume[0], resume[1], 0.0) for resume in resumes]
    
    # Sort by score in descending order
    return sorted(rankings, key=lambda x: x[2], reverse=True)