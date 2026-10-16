from pydantic import BaseModel, field_validator, ValidationError


class Car(BaseModel):
    id: int
    make: str
    model: str
    year: int
    color: str


class CarInput(BaseModel):
    make: str
    model: str
    year: int
    color: str

    @field_validator("make", "model", "color")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()

    @field_validator("model")
    @classmethod
    def model_must_not_be_blank(cls, value: str) -> str:
        if value == "":
            raise ValueError("model must not be blank")
        return value

    @field_validator("year")
    @classmethod
    def year_must_be_reasonable(cls, value: int) -> int:
        if value < 1900 or value > 2100:
            raise ValueError("year must be between 1900 and 2100")
        return value
