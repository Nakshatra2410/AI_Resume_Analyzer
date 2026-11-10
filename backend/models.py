from sqlalchemy import (
    BigInteger,
    String,
    Text,
    TIMESTAMP,
    ForeignKey,
    Numeric,
    text
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    created_at = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
    )

class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    uploaded_at = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
    )

class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    resume_id: Mapped[int] = mapped_column(
        BigInteger, 
        ForeignKey("resumes.id", ondelete="CASCADE"), 
        nullable=False
    )
    job_description: Mapped[str] = mapped_column(Text, nullable=False)
    ats_score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    matched_skills = mapped_column(
        JSONB, server_default=text("'[]'::jsonb")
    )
    missing_skills = mapped_column(
        JSONB, server_default=text("'[]'::jsonb")   
    )
    suggestions = mapped_column(
        JSONB, server_default=text("'[]'::jsonb")   
    )
    created_at = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP") 
    )