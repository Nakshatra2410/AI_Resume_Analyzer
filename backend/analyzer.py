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

    experience_headers = [
        "work experience",
        "professional experience",
        "employment history",
        "internship experience",
        "experience:"
    ]

    experience_indicators = [
        "internship",
        "intern",
        "worked as",
        "employed as",
        "software developer",
        "software engineer",
        "developer",
        "engineer"
    ]

    duration_patterns = [
        r"\b\d+\s+years?\b",
        r"\b\d+\s+months?\b",
        r"\bjan(?:uary)?\s*[-–to]+\s*\w+\b",
        r"\b20\d{2}\s*[-–to]+\s*20\d{2}\b"
    ]

    has_experience_header = any(
        header in text for header in experience_headers
    )

    opportunity_phrases = [
        "looking for an internship",
        "seeking an internship",
        "looking for work experience",
        "seeking work experience",
        "interested in internship opportunities",
        "seeking job opportunities"
    ]

    if any(phrase in text for phrase in opportunity_phrases):
        return 0.0

    has_experience_indicator = any(
        indicator in text for indicator in experience_indicators
    )

    has_duration = any(
        re.search(pattern, text)
        for pattern in duration_patterns
    )

    if has_experience_header and has_experience_indicator and has_duration:
        return 20.0

    if has_experience_header and has_experience_indicator:
        return 10.0

    return 0.0

def calculate_project_score(
        resume_text: str,
        required_skills: list[str]
) -> float:

    if not resume_text:
        return 0.0

    text = resume_text.casefold()

    project_headers = [
        "projects:",
        "academic projects:",
        "personal projects:",
        "key projects:",
        "project experience:"
    ]

    project_text = ""

    for header in project_headers:
        position = text.find(header)

        if position != -1:
            project_text = text[position + len(header):]
            break

    if not project_text:
        return 0.0

    project_skills = set(extract_skills(project_text))
    required_skills_set = set(required_skills)

    matched_project_skills = (
        project_skills & required_skills_set
    )

    if len(matched_project_skills) >= 2:
        return 15.0

    elif len(matched_project_skills) == 1:
        return 10.0

    return 5.0

def calculate_education_score(resume_text: str) -> float:
    if not resume_text:
        return 0.0

    text = resume_text.casefold()

    # Recognized degree qualifications
    masters_degrees = [
        "master of science",
        "master of technology",
        "master of engineering",
        "master of computer applications",
        "m.tech",
        "mtech",
        "m.sc",
        "msc",
        "mca",
        "mba"
    ]

    bachelors_degrees = [
        "bachelor of",
        "bachelor of technology",
        "bachelor of engineering",
        "bachelor of science",
        "bachelor of computer applications",
        "b.tech",
        "btech",
        "b.e.",
        "b.sc",
        "bsc",
        "bca",
        "b.com",
        "bcom",
        "bachelor's degree"
    ]

    diplomas = [
        "diploma in",
        "associate degree"
    ]

    relevant_fields = [
        "computer science",
        "information technology",
        "software engineering",
        "computer engineering",
        "information systems"
    ]

    # Check master's degree
    if any(degree in text for degree in masters_degrees):
           return 10.0

    # Check bachelor's degree
    if any(degree in text for degree in bachelors_degrees):
        if any(field in text for field in relevant_fields):
            return 10.0

        return 7.0

    # Check for diploma or associate qualification
    if any(diploma in text for diploma in diplomas):
        return 5.0

    return 0.0

def calculate_keyword_score(
        resume_text: str,
        job_description: str
) -> float:

    if not resume_text or not job_description:
        return 0.0

    stop_words = {
        "the", "and", "for", "with", "you", "your",
        "are", "our", "this", "that", "will", "have",
        "has", "from", "into", "who", "what", "their",
        "they", "can", "should", "must", "ability",
        "work", "working", "looking", "experience",
        "years", "year", "using", "use", "good"
    }

    # Remove recognized technical skills to avoid double-counting
    cleaned_description = job_description.casefold()

    for skill, aliases in SKILL_ALIASES.items():
        for alias in [skill] + aliases:
            pattern = r"(?<![a-z0-9])" + re.escape(
                alias.casefold()
            ) + r"(?![a-z0-9])"

            cleaned_description = re.sub(
                pattern, " ",cleaned_description
            )

    job_keywords = {
        word for word in re.findall(
            r"\b[a-zA-Z]{3,}\b", cleaned_description
        )
        if word not in stop_words
    }

    resume_keywords = {
        word for word in re.findall(
            r"\b[a-zA-Z]{3,}\b", resume_text.casefold()
        )
    }

    if not job_keywords:
        return 0.0

    matched_keywords = job_keywords & resume_keywords

    score = (
        len(matched_keywords) / len(job_keywords)
    ) * 15

    return round(score, 2)

def calculate_ats_score(
        resume_text: str,
        job_description: str
) -> dict:

    # 1. Skills score (max 40)
    skill_result = compare_skills(
        resume_text,
        job_description
    )

    skills_score = round(
        skill_result["skill_match_score"] * 0.40,
        2
    )

    # 2. Experience score (max 20)
    experience_score = calculate_experience_score(
        resume_text
    )

    # 3. Project score (max 15)
    project_score = calculate_project_score(
        resume_text,
        skill_result["required_skills"]
    )

    # 4. Education score (max 10)
    education_score = calculate_education_score(
        resume_text
    )

    # 5. Keyword score (max 15)
    keyword_score = calculate_keyword_score(
        resume_text,
        job_description
    )

    total_score = round(
        skills_score
        + experience_score
        + project_score
        + education_score
        + keyword_score,
        2
    )

    return {
        "ats_score": total_score,
        "score_breakdown": {
          "skills_score": skills_score,
            "experience_score": experience_score,
            "project_score": project_score,
            "education_score": education_score,
            "keyword_score": keyword_score
        },
        "matched_skills": skill_result["matched_skills"],
        "missing_skills": skill_result["missing_skills"],
        "resume_skills": skill_result["resume_skills"],
        "required_skills": skill_result["required_skills"]
    }