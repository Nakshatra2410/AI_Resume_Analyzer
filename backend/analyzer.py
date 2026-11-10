import re

# Canonical skill names and their commonly used variations
SKILL_ALIASES = {
    "Java": ["java"],
    "Python": ["python"],
    "C++": ["c++", "cpp"],
    "JavaScript": ["javascript", "js"],
    "TypeScript": ["typescript", "ts"],
    "React": ["react", "react.js", "reactjs"],
    "Node.js": ["node.js", "nodejs"],
    "Express.js": ["express", "express.js"],
    "FastAPI": ["fastapi"],
    "Django": ["django"],
    "Spring Boot": ["spring boot"],
    "HTML": ["html"],
    "CSS": ["css"],
    "Tailwind CSS": ["tailwind", "tailwind css"],
    "SQL": ["sql"],
    "PostgreSQL": ["postgresql", "postgres"],
    "MySQL": ["mysql"],
    "MongoDB": ["mongodb", "mongo db"],
    "Redis": ["redis"],
    "REST API": ["rest api", "restful api"],
    "GraphQL": ["graphql"],
    "Git": ["git"],
    "GitHub": ["github"],
    "Docker": ["docker"],
    "Kubernetes": ["kubernetes", "k8s"],
    "AWS": ["aws", "amazon web services"],
    "Azure": ["azure", "microsoft azure"],
    "Google Cloud": ["google cloud", "gcp"],
    "Linux": ["linux"],
    "CI/CD": ["ci/cd", "continuous integration"],
    "Machine Learning": ["machine learning", "ml"],
    "Deep Learning": ["deep learning", "dl"],
    "NLP": ["natural language processing", "nlp"],
    "Pandas": ["pandas"],
    "NumPy": ["numpy"],
    "Scikit-learn": ["scikit-learn", "sklearn"],
}

def extract_skills(text: str) -> list[str]:
    """
    Extract recognized skills from resume or jd.
    Returns canonical skill names without duplicates.
    """

    if not text:
        return []

    found_skills = []

    normalized_text = text.casefold()

    for skill, aliases in SKILL_ALIASES.items():
        for alias in aliases:
            pattern = (
                r"(?<![a-z0-9])"
                + re.escape(alias.casefold())
                + r"(?![s-z0-9])"
            )

            if re.search(pattern, normalized_text):
                found_skills.append(skill)
            break

    return found_skills

def compare_skills(resume_text: str, job_description: str) -> dict:
    """
    Compare resume skills with job description skills.
    """
    resume_skills = set(extract_skills(resume_text))
    required_skills = set(extract_skills(job_description))

    matched_skills = sorted(resume_skills & required_skills)
    missing_skills = sorted(required_skills - resume_skills)

    total_required = len(required_skills)

    if total_required == 0:
        skill_match_score = 0.0
    else:
        skill_match_score = round(
            len(matched_skills) / total_required * 100, 2
        )

    return {
        "resume_skills": sorted(resume_skills),
        "required_skills": sorted(required_skills),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "skill_match_score": skill_match_score
    }

def calculate_experience_score(resume_text: str) -> float:
    if not resume_text:
        return 0.0

    text = resume_text.casefold()

    experience_keywords = [
        "internship",
        "intern",
        "work experience",
        "professional experience",
        "years of experience",
        "months of experience",
        "worked as",
        "employment"
    ]

    found_keywords = [
        keyword
        for keyword in experience_keywords
        if keyword in text
    ]

    if len(found_keywords) >= 2:
        return 20.0

    if len(found_keywords) == 1:
        return 10.0

    return 0.0