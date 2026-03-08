from typing import Union

from pydantic import BaseModel, field_validator, model_validator


class IdentifyRequest(BaseModel):
    email: str | None = None
    phoneNumber: Union[int, str] | None = None

    @field_validator("phoneNumber", mode="before")
    @classmethod
    def coerce_phone_to_str(cls, v):
        if v is None:
            return None
        return str(v).strip() if str(v).strip() else None

    @field_validator("email", mode="before")
    @classmethod
    def coerce_email(cls, v):
        if v is None:
            return None
        s = str(v).strip()
        return s if s else None

    @model_validator(mode="after")
    def at_least_one_identifier(self):
        has_email = bool(self.email and str(self.email).strip())
        has_phone = bool(self.phoneNumber is not None and str(self.phoneNumber).strip())
        if not has_email and not has_phone:
            raise ValueError("At least one of email or phoneNumber must be provided")
        return self


class ContactPayload(BaseModel):
    primaryContatctId: int
    emails: list[str]
    phoneNumbers: list[str]
    secondaryContactIds: list[int]


class ContactResponse(BaseModel):
    contact: ContactPayload
