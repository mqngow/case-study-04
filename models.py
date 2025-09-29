from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, validator
import hashlib
import secrets

class SurveySubmission(BaseModel)
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(..., ge=13, le=120)
    consent: bool = Field(..., description="Must be true to accept")
    rating: int = Field(..., ge=1, le=5)
    comments: Optional[str] = Field(None, max_length=1000)
    user_agent: Optional[str] = Field(None, max_length=1000)

    @validator("comments")
    def _strip_comments(cls, v):
        return v.strip() if isinstance(v, str) else v

    @validator("consent")
    def _must_consent(cls, v):
        if v is not True:
            raise ValueError("consent must be true")
        return v

    def _sha256(self, value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    def to_storable_record(self, *, received_at: datetime, ip: str) -> "StoredSurveyRecord":
        email_hash = self._sha256(self.email)
        age_hash = self._sha256(str(self.age))
        submission_id = self._sha256(secrets.token_hex(32))
        return StoredSurveyRecord(
            name=self.name,
            email_hash=email_hash,
            age_hash=age_hash,
            consent=self.consent,
            rating=self.rating,
            comments=self.comments,
            user_agent=self.user_agent,
            submission_id=submission_id,
            received_at=received_at,
            ip=ip,
        )


class StoredSurveyRecord(BaseModel):
    name: str
    email_hash: str
    age_hash: str
    consent: bool
    rating: int
    comments: Optional[str] = None
    user_agent: Optional[str] = None
    submission_id: str
    received_at: datetime
    ip: str