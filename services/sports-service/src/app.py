from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI(
    title="Sports Service",
    version="1.0.0",
    description="CRUD API for sports activities",
)


class SportCreate(BaseModel):
    sport_name: str
    coach_name: str
    practice_day: str


class Sport(SportCreate):
    id: int


sports: dict[int, Sport] = {}
next_id = 1


@app.post("/sports", response_model=Sport)
def create_sport(payload: SportCreate) -> Sport:
    global next_id
    sport = Sport(id=next_id, **payload.model_dump())
    sports[next_id] = sport
    next_id += 1
    return sport


@app.get("/sports", response_model=list[Sport])
def list_sports() -> list[Sport]:
    return list(sports.values())


@app.get("/sports/{sport_id}", response_model=Sport)
def get_sport(sport_id: int) -> Sport:
    sport = sports.get(sport_id)
    if not sport:
        raise HTTPException(status_code=404, detail="Sport not found")
    return sport


@app.put("/sports/{sport_id}", response_model=Sport)
def update_sport(sport_id: int, payload: SportCreate) -> Sport:
    if sport_id not in sports:
        raise HTTPException(status_code=404, detail="Sport not found")

    sport = Sport(id=sport_id, **payload.model_dump())
    sports[sport_id] = sport
    return sport


@app.delete("/sports/{sport_id}")
def delete_sport(sport_id: int) -> dict[str, str]:
    if sport_id not in sports:
        raise HTTPException(status_code=404, detail="Sport not found")

    del sports[sport_id]
    return {"message": "Sport deleted"}
