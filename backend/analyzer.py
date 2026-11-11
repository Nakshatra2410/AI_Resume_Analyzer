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

    if not resume_text or not required_skills:
        return 0.0

    text = resume_text.casefold()

    project_headers = [
        "projects:",
        "academic projects:",
        "personal projects:",
        "key projects:",
        "project experience:"
    ]

    other_section_headers = [
        "education:",
        "experience:",
        "work experience:",
        "professional experience:",
        "skills:",
        "technical skills:",
        "certifications:",
        "achievements:",
        "summary:",
        "objective:"
    ]

    project_start = -1

    for header in project_headers:
        position = text.find(header)

        if position != -1 and (
            project_start == -1 or position < project_start
        ):
            project_start = position + len(header)

    if project_start == -1:
        return 0.0

    project_text = text[project_start:]

    section_end = len(project_text)

    for header in other_section_headers:
        position = project_text.find(header)

        if position != -1 and position < section_end:
            section_end = position

    project_text = project_text[:section_end]

    if not project_text.strip():
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

def normalize_keyword(word: str) -> str:

    word = word.casefold()

    # Handle common word endings
    if len(word) > 5 and word.endswith("ing"):
        word = word[:-3]

    elif len(word) > 4 and word.endswith("ed"):
        word = word[:-2]

    elif len(word) > 4 and word.endswith("es"):
        word = word[:-2]

    elif len(word) > 3 and word.endswith("s"):
        word = word[:-1]

    return word


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

    # Remove recognized technical skills to avoid double-counting.
    cleaned_description = job_description.casefold()

    for skill, aliases in SKILL_ALIASES.items():
        for alias in [skill] + aliases:
            pattern = (
                r"(?<![a-z0-9])"
                + re.escape(alias.casefold())
                + r"(?![a-z0-9])"
            )

            cleaned_description = re.sub(
                pattern, " ", cleaned_description
            )

    # Extract and normalize job-description keywords.
    job_words = re.findall(
        r"\b[a-zA-Z]{3,}\b",
        cleaned_description
    )

    job_keywords = {
        normalize_keyword(word)
        for word in job_words
        if word not in stop_words
    }

    # Extract and normalize resume keywords.
    resume_words = re.findall(
        r"\b[a-zA-Z]{3,}\b",
        resume_text.casefold()
    )

    resume_keywords = {
        normalize_keyword(word)
        for word in resume_words
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

def generate_suggestions(
        ats_result: dict
) -> list[str]:

    suggestions = []

    missing_skills = ats_result["missing_skills"]
    score_breakdown = ats_result["score_breakdown"]

    # 1. Missing technical skills
    if missing_skills:
        skills = ", ".join(missing_skills)

        suggestions.append(
            f"Consider learning and demonstrating these "
            f"job-required skills: {skills}"
        ) 

    # 2. Experience improvement
    if score_breakdown["experience_score"] < 20:
        suggestions.append(
            "Strengthen your experience section by including "
            "relevant internships, work experience, responsibilities, "
            "and employment durations, if applicable."
        )

    # 3. Project improvement
    if score_breakdown["project_score"] < 15:
        suggestions.append(
            "Add relevant projects that demonstrate the technical "
            "skills required for this role. Describe your contribution "
            "and the technologies used."
        )

    # 4. Education improvement
    if score_breakdown["education_score"] < 10:
        suggestions.append(
            "Clearly mention your educational qualification, "
            "degree, specialization, and institution."
        )

    # 5. Keyword improvement
    if score_breakdown["keyword_score"] < 10:
        suggestions.append(
            "Include relevant technical and role-specific keywords "
            "from the job description naturally in your resume, "
            "where they accurately reflect your experience."
        )

    return suggestions