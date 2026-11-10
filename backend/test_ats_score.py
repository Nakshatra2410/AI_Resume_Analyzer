from analyzer import calculate_ats_score

resume = """
Education:
B.Tech in Computer Science and Engineering.

Experience:
Software development internship.

Projects:
Built a web application using Java and React.
Developed scalable applications and secure systems.

Skills:
Java, Python, React, PostgreSQL, Git.
"""

job_description = """
Looking for a software developer with Java, Python,
React, PostgreSQL, Docker and AWS.

Experienced developer building scalable applications
and secure systems.
"""

result = calculate_ats_score(resume, job_description)

print("ATS Analysis Result:")
print(result)