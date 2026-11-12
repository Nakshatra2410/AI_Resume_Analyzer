from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from models import User, Resume, Analysis
from schemas import UserCreate, UserLogin, AnalysisCreate
from security import hash_password, create_access_token, verify_password
from dependencies import get_current_user
from analyzer import calculate_ats_score, generate_suggestions
from ai_service import generate_ai_suggestions

import uuid
import fitz

from pathlib import Path
from sqlalchemy.exc import SQLAlchemyError

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE = 5 * 1024 * 1024 #5MB

app = FastAPI(
    title="AI Resume Analyzer",
    description="Backend API for analyzing resumes",
    version="1.0.0"
)

class JobDescription(BaseModel):
    job_title: str
    job_description: str

@app.get("/")
def home():
    return {
        "message": "Welcome to AI Resume Analyzer!",
        "status": "Backend is running successfully"
    }

@app.get("/health")
def heath_check():
    return {
        "status": "healthy",
        "service": "AI Resume Analyzer Backend"
    }

@app.post("/analyze-job")
def analyze_job(job: JobDescription):
    return {
        "message": "Job description received successfully",
        "job_title": job.job_title,
        "job_description": job.job_description
    }

@app.post("/api/v1/users/register", status_code=201)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hash_password(user_data.password)
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {
            "message": "User registered successfully",
            "user_id": new_user.id,
            "name": new_user.name,
            "email": new_user.email
        }

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Could not register user"
        )

@app.post("/api/v1/users/login")
def login_user(user_data: UserLogin, db: Session = Depends(get_db)):

    user = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if not user or not verify_password(
        user_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token(user.id)

    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.get("/api/v1/users/me")
def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    return {
        "message": "Authenticated successfully",
        "user_id": current_user.id,
        "name": current_user.name,
        "email": current_user.email
    }

@app.post("/api/v1/resumes", status_code=201)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Validate file extension
    if Path(file.filename or "").suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    # 2. Read uploaded file
    file_content = await file.read()

    if not file_content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty"
        )

    # 3. Validate file size
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File size must not exceed 5MB"
        )

    # 4. Validate PDF content and extract text
    try:
        with fitz.open(stream=file_content, filetype="pdf") as pdf:
            if pdf.is_encrypted:
                raise HTTPException(
                    status_code=400,
                    detail="Password-protected PDFs are not supported"
                )

            extracted_text = "\n".join(
                page.get_text() for page in pdf
            ).strip()

    except HTTPException:
        raise 
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid or corrupted PDF file"
        )

    if not extracted_text:
        raise HTTPException(
            status_code=400,
            detail="No readable text found in PDF"
        )

    # 5. Generate unique filename
    unique_filename = f"{uuid.uuid4().hex}.pdf"
    file_path = UPLOAD_DIR / unique_filename

    # 6. Save PDF Locally
    try:
        file_path.write_bytes(file_content)

        #7. Save resume details in PostgreSQL
        new_resume = Resume(
            user_id = current_user.id,
            filename=Path(file.filename).name,
            file_path=str(file_path),
            extracted_text=extracted_text
        )

        db.add(new_resume)
        db.commit()
        db.refresh(new_resume)

        return {
            "message": "Resume uploaded successfully",
            "resume_id": new_resume.id,
            "filename": new_resume.filename,
            "extracted_text": extracted_text
        }

    except SQLAlchemyError:
        db.rollback()

        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=500,
            detail="Could not save resume details"
        )

    except OSError:
        db.rollback()

        if file_path.exists():
            file_path.unlink()
            
        raise HTTPException(
            status_code=500,
            detail="Could not save uploaded file"
        )

@app.get("/api/v1/resumes")
def get_my_resumes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    resumes = db.query(Resume).filter(
        Resume.user_id == current_user.id
    ).order_by(
        Resume.uploaded_at.desc()
    ).all()

    return {
        "total_resumes": len(resumes),
        "resumes": [
            {
                "resume_id": resume.id,
                "filename": resume.filename,
                "uploaded_at": resume.uploaded_at
            }
            for resume in resumes
        ]
    }

@app.post("/api/v1/analyses", status_code=201)
def create_analysis(
    analysis_data: AnalysisCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Find requested resume belonging to logged-in user
    resume = db.query(Resume).filter(
        Resume.id == analysis_data.resume_id,
        Resume.user_id == current_user.id
    ).first()

    if not resume:
        raise HTTPException(
            status_code=404,
            detail="Resume not found"
        )

    # 2. Compare resume skills with job requirements
    result = calculate_ats_score(
        resume.extracted_text,
        analysis_data.job_description
    )

    rule_based_suggestions = generate_suggestions(result)

    suggestions = generate_ai_suggestions(
        resume_text=resume.extracted_text,
        job_description=analysis_data.job_description,
        rule_based_suggestions=rule_based_suggestions
    )

    # 3. Save analysis in PostgreSQL
    new_analysis = Analysis(
        resume_id=resume.id,
        job_description=analysis_data.job_description,
        ats_score=result["ats_score"],
        matched_skills=result["matched_skills"],
        missing_skills=result["missing_skills"],
        suggestions=suggestions,
        score_breakdown=result["score_breakdown"]
    )

    try:
        db.add(new_analysis)
        db.commit()
        db.refresh(new_analysis)

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Could not save analysis"
        )

    # 4. Return analysis result
    return {
        "message": "Resume analyzed successfully",
        "analysis_id": new_analysis.id,
        "resume_id": resume.id,
        "ats_score": result["ats_score"],
        "score_breakdown": result["score_breakdown"],
        "resume_skills": result["resume_skills"],
        "required_skills": result["required_skills"],
        "matched_skills": result["matched_skills"],
        "missing_skills": result["missing_skills"],
        "suggestions": suggestions,
    }

@app.get("/api/v1/analyses/{analysis_id}")
def get_analysis(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    analysis = db.query(Analysis).join(
        Resume,
        Analysis.resume_id == Resume.id
    ).filter(
        Analysis.id == analysis_id,
        Resume.user_id == current_user.id
    ).first()

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="Analysis not found"
        )

    return {
        "analysis_id": analysis.id,
        "resume_id": analysis.resume_id,
        "job_description": analysis.job_description,
        "skill_match_score": float(analysis.ats_score or 0),
        "score_breakdown": analysis.score_breakdown,
        "matched_skills": analysis.matched_skills,
        "missing_skills": analysis.missing_skills,
        "suggestions": analysis.suggestions,
        "created_at": analysis.created_at
    }

@app.get("/api/v1/analyses")
def get_my_analyses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    results = db.query(
        Analysis,
        Resume.filename
    ).join(
        Resume,
        Analysis.resume_id == Resume.id
    ).filter(
        Resume.user_id == current_user.id
    ).order_by(
        Analysis.created_at.desc()
    ).all()

    return {
        "total_analyses": len(results),
        "analyses": [
            {
                "analysis_id": analysis.id,
                "resume_id": analysis.resume_id,
                "resume_filename": filename,
                "skill_match_score": float(analysis.ats_score or 0),
                "score_breakdown": analysis.score_breakdown,
                "matched_skills": analysis.matched_skills,
                "missing_skills": analysis.missing_skills,
                "created_at": analysis.created_at
            }
            for analysis, filename in results
        ]
    }