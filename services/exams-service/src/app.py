from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


app = FastAPI(
    title="Exams Service",
    version="1.0.0",
    description="CRUD API for exams",
)


class ExamCreate(BaseModel):
    subject: str
    exam_date: str
    max_marks: int = Field(ge=1)


class Exam(ExamCreate):
    id: int


exams: dict[int, Exam] = {}
next_id = 1


@app.post("/exams", response_model=Exam)
def create_exam(payload: ExamCreate) -> Exam:
    global next_id
    exam = Exam(id=next_id, **payload.model_dump())
    exams[next_id] = exam
    next_id += 1
    return exam


@app.get("/exams", response_model=list[Exam])
def list_exams() -> list[Exam]:
    return list(exams.values())


@app.get("/exams/{exam_id}", response_model=Exam)
def get_exam(exam_id: int) -> Exam:
    exam = exams.get(exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    return exam


@app.put("/exams/{exam_id}", response_model=Exam)
def update_exam(exam_id: int, payload: ExamCreate) -> Exam:
    if exam_id not in exams:
        raise HTTPException(status_code=404, detail="Exam not found")

    exam = Exam(id=exam_id, **payload.model_dump())
    exams[exam_id] = exam
    return exam


@app.delete("/exams/{exam_id}")
def delete_exam(exam_id: int) -> dict[str, str]:
    if exam_id not in exams:
        raise HTTPException(status_code=404, detail="Exam not found")

    del exams[exam_id]
    return {"message": "Exam deleted"}
