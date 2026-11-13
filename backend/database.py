
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

# Database location
DATABASE_URL = "sqlite:///./ppt_validator.db"

# Create database connection
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Create database session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


# Presentation table
class PresentationRecord(Base):
    __tablename__ = "presentations"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    total_slides = Column(Integer, nullable=False)
    slides_json = Column(Text, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)


# Create tables
Base.metadata.create_all(bind=engine)
