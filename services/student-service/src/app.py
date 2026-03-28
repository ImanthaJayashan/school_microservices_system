from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


app = FastAPI(
    title="Student Service",
    version="1.0.0",
    description="CRUD API for students",
)


class StudentCreate(BaseModel):
    name: str
    age: int = Field(ge=1)
    grade: str


class Student(StudentCreate):
    id: int


students: dict[int, Student] = {}
next_id = 1


@app.post("/students", response_model=Student)
def create_student(payload: StudentCreate) -> Student:
    global next_id
    student = Student(id=next_id, **payload.model_dump())
    students[next_id] = student
    next_id += 1
    return student


@app.get("/students", response_model=list[Student])
def list_students() -> list[Student]:
    return list(students.values())


@app.get("/students/{student_id}", response_model=Student)
def get_student(student_id: int) -> Student:
    student = students.get(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@app.put("/students/{student_id}", response_model=Student)
def update_student(student_id: int, payload: StudentCreate) -> Student:
    if student_id not in students:
        raise HTTPException(status_code=404, detail="Student not found")

    student = Student(id=student_id, **payload.model_dump())
    students[student_id] = student
    return student


@app.delete("/students/{student_id}")
def delete_student(student_id: int) -> dict[str, str]:
    if student_id not in students:
        raise HTTPException(status_code=404, detail="Student not found")

    del students[student_id]
    return {"message": "Student deleted"}
