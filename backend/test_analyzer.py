from analyzer import extract_skills, compare_skills

resume = """
I have experience with Java, Python, React,
PostgreSQL, Git and REST APIs.
"""

job_description = """
Looking for a developer with Java, Python, React,
Docker, AWS and PostgreSQL experience.
"""

result = compare_skills(resume, job_description)

print("Analysis Result:")
print(result)