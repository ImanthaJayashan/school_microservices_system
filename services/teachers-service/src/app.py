from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


app = FastAPI(
    title="Teachers Service",
    version="1.0.0",
    description="CRUD API for teachers",
)


class TeacherCreate(BaseModel):
    name: str
    subject: str
    years_experience: int = Field(ge=0)


class Teacher(TeacherCreate):
    id: int


teachers: dict[int, Teacher] = {}
next_id = 1


@app.post("/teachers", response_model=Teacher)
def create_teacher(payload: TeacherCreate) -> Teacher:
    global next_id
    teacher = Teacher(id=next_id, **payload.model_dump())
    teachers[next_id] = teacher
    next_id += 1
    return teacher


@app.get("/teachers", response_model=list[Teacher])
def list_teachers() -> list[Teacher]:
    return list(teachers.values())


@app.get("/teachers/{teacher_id}", response_model=Teacher)
def get_teacher(teacher_id: int) -> Teacher:
    teacher = teachers.get(teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return teacher


@app.put("/teachers/{teacher_id}", response_model=Teacher)
def update_teacher(teacher_id: int, payload: TeacherCreate) -> Teacher:
    if teacher_id not in teachers:
        raise HTTPException(status_code=404, detail="Teacher not found")

    teacher = Teacher(id=teacher_id, **payload.model_dump())
    teachers[teacher_id] = teacher
    return teacher


@app.delete("/teachers/{teacher_id}")
def delete_teacher(teacher_id: int) -> dict[str, str]:
    if teacher_id not in teachers:
        raise HTTPException(status_code=404, detail="Teacher not found")

    del teachers[teacher_id]
    return {"message": "Teacher deleted"}
