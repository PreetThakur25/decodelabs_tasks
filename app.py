import os
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify, render_template, send_from_directory
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__, static_folder="static", template_folder="templates")

# Phase 1: Mock Data Generation
def generate_mock_data():
    jobs = [
        {"title": "Frontend Engineer", "skills": ["HTML", "CSS", "JavaScript", "React", "TypeScript", "Webpack"]},
        {"title": "Backend Engineer", "skills": ["Python", "Node.js", "SQL", "PostgreSQL", "APIs", "Docker"]},
        {"title": "Fullstack Engineer", "skills": ["HTML", "CSS", "JavaScript", "React", "Node.js", "SQL", "MongoDB"]},
        {"title": "Data Scientist", "skills": ["Python", "SQL", "Machine Learning", "R", "Pandas", "Statistics"]},
        {"title": "DevOps Engineer", "skills": ["Docker", "Kubernetes", "CI/CD", "AWS", "Linux", "Terraform"]},
        {"title": "iOS Mobile Developer", "skills": ["Swift", "SwiftUI", "Xcode", "iOS", "Objective-C", "Git"]},
        {"title": "Android Mobile Developer", "skills": ["Kotlin", "Java", "Android SDK", "Gradle", "Git", "APIs"]},
        {"title": "Embedded Systems Engineer", "skills": ["C", "C++", "Microcontrollers", "RTOS", "Electronics", "Assembly"]},
        {"title": "Data Engineer", "skills": ["Python", "SQL", "Spark", "Hadoop", "ETL Pipelines", "Scala"]},
        {"title": "Cyber Security Analyst", "skills": ["Firewalls", "Penetration Testing", "Network Security", "Cryptography", "Linux", "Wireshark"]},
        {"title": "QA Automation Engineer", "skills": ["Python", "Selenium", "Cypress", "QA Testing", "Test Automation", "Git"]},
        {"title": "Cloud Architect", "skills": ["AWS", "Azure", "Cloud Architecture", "Terraform", "Security", "Networking"]},
        {"title": "Game Developer", "skills": ["C#", "Unity", "C++", "Unreal Engine", "3D Graphics", "OpenGL"]},
        {"title": "Systems Administrator", "skills": ["Linux", "Windows Server", "Active Directory", "Scripting", "Networking", "PowerShell"]},
        {"title": "Machine Learning Engineer", "skills": ["Python", "PyTorch", "TensorFlow", "Deep Learning", "Machine Learning", "SQL"]},
        {"title": "Database Administrator", "skills": ["SQL", "PostgreSQL", "Oracle", "Database Tuning", "Backup Recovery", "NoSQL"]},
        {"title": "Network Engineer", "skills": ["Cisco", "Routing", "Switching", "TCP/IP", "Firewalls", "VPN"]},
        {"title": "Site Reliability Engineer (SRE)", "skills": ["Python", "Go", "Kubernetes", "Prometheus", "Monitoring", "Linux"]},
        {"title": "Blockchain Developer", "skills": ["Solidity", "Ethereum", "Smart Contracts", "Cryptography", "Rust", "Go"]},
        {"title": "UI/UX Engineer", "skills": ["Figma", "CSS", "HTML", "Design Systems", "Wireframing", "Prototyping"]}
    ]
    # Represent skills as a comma-separated string for vectorization
    df_data = []
    for job in jobs:
        df_data.append({
            "title": job["title"],
            "skills": job["skills"],
            "skills_str": ", ".join(job["skills"])
        })
    df = pd.DataFrame(df_data)
    # Save to CSV to fulfill the Phase 1 requirement
    df.to_csv("job_roles_dataset.csv", index=False)
    return df

# Initialize dataframe and vectors
df_jobs = generate_mock_data()

# Fit vectorizer on startup using a token pattern that preserves C++, C#, .js, etc.
vectorizer = TfidfVectorizer(token_pattern=r'[a-zA-Z0-9+#\.\-]+', lowercase=True)
job_vectors = vectorizer.fit_transform(df_jobs["skills_str"])

# Extract all unique skills to send to frontend for interactive options
def get_all_unique_skills(df):
    unique = set()
    for skills_list in df["skills"]:
        for s in skills_list:
            unique.add(s)
    return sorted(list(unique))

unique_skills = get_all_unique_skills(df_jobs)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/skills", methods=["GET"])
def get_skills():
    return jsonify({"skills": unique_skills})

# Phase 3: The 4-Step Pipeline API Endpoint
@app.route("/api/recommend", methods=["POST"])
def recommend():
    # Step 1: Ingestion
    payload = request.get_json(silent=True)
    if not payload or "skills" not in payload:
        return jsonify({"error": "Invalid request format. Expected JSON containing 'skills' array."}), 400
    
    skills = payload["skills"]
    if not isinstance(skills, list) or len(skills) != 3:
        return jsonify({"error": "Please provide exactly 3 skills."}), 400

    # Step 2: Scoring
    user_input_str = ", ".join(skills)
    user_vector = vectorizer.transform([user_input_str])
    
    # Calculate similarity scores
    similarity_scores = cosine_similarity(user_vector, job_vectors).flatten()
    
    # Add score column to copy of dataframe
    df_scored = df_jobs.copy()
    df_scored["score"] = similarity_scores

    # Step 3: Sorting
    df_sorted = df_scored.sort_values(by="score", ascending=False)

    # Step 4: Filtering
    df_filtered = df_sorted.head(3)

    # Format recommendations for output
    recommendations = []
    for _, row in df_filtered.iterrows():
        # Match percentage rounded to 1 decimal place
        match_percentage = round(float(row["score"]) * 100, 1)
        recommendations.append({
            "title": row["title"],
            "skills": row["skills"],
            "match_percentage": match_percentage
        })

    return jsonify({
        "status": "success",
        "user_input": skills,
        "recommendations": recommendations
    })

if __name__ == "__main__":
    # Standard Flask listener
    app.run(host="127.0.0.1", port=5000, debug=True)
