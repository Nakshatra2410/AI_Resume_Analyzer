from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class AnalysisCreate(BaseModel):
    resume_id: int
    job_description: str = Field(
        min_length=20,
        description="Job description to compare with resume"
    )