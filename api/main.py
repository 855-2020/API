"""
Main API module
"""
from typing import Dict

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import uvicorn

from . import models
from .deps import get_db
from .schemas import Activity
from .database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
def home():
    """
    Basis route
    """
    return "Welcome to the API!"


@app.post("/activity")
def create_activity(activity: Activity):
    print(activity)

    return "Activity created!"


# TODO proper model
@app.post("/impact", response_model=Dict[int, float])
def get_impact(values: Dict[int, float], db: Session = Depends((get_db))):
    coefs = db.query(models.Coefficient).filter(
        models.Coefficient.source_id.in_(values.keys())
    ).all()
    response: Dict[int, float] = dict()
    for coef in coefs:
        if coef.target_id not in response:
            response[coef.target_id] = 0
        response[coef.target_id] += coef.value * values[coef.source_id]
    return response


@app.post("/activity/{sector_id}/{sector_value}", response_model=Activity)
def get_results(sector_id: int, sector_value: float, db: Session = Depends(get_db)):
    coefs = db.query(models.CoefficientActivity).filter(
        models.CoefficientActivity.sector_id == sector_id
    ).all()
    props = {coef.activity.name: sector_value * coef.value for coef in coefs}
    return Activity(**props)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
