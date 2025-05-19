"""
Models for the CET Exam App
This module defines the data models for the exam builder and related functionality.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum

class SubjectCategory(str, Enum):
    """Enum for subject categories in the exam."""
    REASONING = "reasoning"
    ENGLISH = "english"
    COMPUTER_CONCEPTS = "computer_concepts"
    PYTHON = "python"

@dataclass
class Option:
    """Represents an option in a multiple choice question."""
    id: str
    text: str
    is_correct: bool = False

@dataclass
class Question:
    """Represents a multiple choice question in the exam."""
    id: str
    text: str
    category: SubjectCategory
    options: List[Option]
    explanation: str
    difficulty_level: int = 1  # 1-Easy, 2-Medium, 3-Hard
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        """Convert question to dictionary for Firestore storage."""
        return {
            "id": self.id,
            "text": self.text,
            "category": self.category.value,
            "options": [
                {
                    "id": opt.id,
                    "text": opt.text,
                    "is_correct": opt.is_correct
                } for opt in self.options
            ],
            "explanation": self.explanation,
            "difficulty_level": self.difficulty_level,
            "created_at": self.created_at,
            "updated_at": self.updated_at or self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Question':
        """Create question from Firestore dictionary."""
        options = [
            Option(
                id=opt["id"],
                text=opt["text"],
                is_correct=opt["is_correct"]
            ) for opt in data.get("options", [])
        ]
        
        return cls(
            id=data.get("id"),
            text=data.get("text"),
            category=SubjectCategory(data.get("category")),
            options=options,
            explanation=data.get("explanation", ""),
            difficulty_level=data.get("difficulty_level", 1),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )

@dataclass
class Exam:
    """Represents an exam with multiple questions."""
    id: str
    title: str
    description: str
    duration_minutes: int
    questions: List[str]  # List of question IDs
    categories: List[SubjectCategory]
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        """Convert exam to dictionary for Firestore storage."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "duration_minutes": self.duration_minutes,
            "questions": self.questions,
            "categories": [cat.value for cat in self.categories],
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at or self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Exam':
        """Create exam from Firestore dictionary."""
        return cls(
            id=data.get("id"),
            title=data.get("title"),
            description=data.get("description"),
            duration_minutes=data.get("duration_minutes", 60),
            questions=data.get("questions", []),
            categories=[SubjectCategory(cat) for cat in data.get("categories", [])],
            is_active=data.get("is_active", True),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )

@dataclass
class ExamResult:
    """Represents a student's exam result."""
    id: str
    user_id: str
    exam_id: str
    answers: Dict[str, str]  # Question ID to selected option ID
    score: float
    max_score: float
    category_scores: Dict[str, float]  # Category to score
    completed_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """Convert exam result to dictionary for Firestore storage."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "exam_id": self.exam_id,
            "answers": self.answers,
            "score": self.score,
            "max_score": self.max_score,
            "category_scores": self.category_scores,
            "completed_at": self.completed_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ExamResult':
        """Create exam result from Firestore dictionary."""
        return cls(
            id=data.get("id"),
            user_id=data.get("user_id"),
            exam_id=data.get("exam_id"),
            answers=data.get("answers", {}),
            score=data.get("score", 0),
            max_score=data.get("max_score", 0),
            category_scores=data.get("category_scores", {}),
            completed_at=data.get("completed_at")
        )
