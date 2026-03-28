from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


app = FastAPI(
    title="Subjects Service",
    version="1.0.0",
    description="CRUD API for subjects",
)


class SubjectCreate(BaseModel):
    name: str
    code: str
    credits: int = Field(ge=1)


class Subject(SubjectCreate):
    id: int


subjects: dict[int, Subject] = {}
next_id = 1


@app.post("/subjects", response_model=Subject)
def create_subject(payload: SubjectCreate) -> Subject:
    global next_id
    subject = Subject(id=next_id, **payload.model_dump())
    subjects[next_id] = subject
    next_id += 1
    return subject


@app.get("/subjects", response_model=list[Subject])
def list_subjects() -> list[Subject]:
    return list(subjects.values())


@app.get("/subjects/{subject_id}", response_model=Subject)
def get_subject(subject_id: int) -> Subject:
    subject = subjects.get(subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject


@app.put("/subjects/{subject_id}", response_model=Subject)
def update_subject(subject_id: int, payload: SubjectCreate) -> Subject:
    if subject_id not in subjects:
        raise HTTPException(status_code=404, detail="Subject not found")

    subject = Subject(id=subject_id, **payload.model_dump())
    subjects[subject_id] = subject
    return subject


@app.delete("/subjects/{subject_id}")
def delete_subject(subject_id: int) -> dict[str, str]:
    if subject_id not in subjects:
        raise HTTPException(status_code=404, detail="Subject not found")

    del subjects[subject_id]
    return {"message": "Subject deleted"}
