"""
Main API module
"""
from datetime import timedelta
from typing import Dict, List

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from . import models
from .database import Base, engine
from .deps import get_db
from .routers import users, sectors
from .schemas import Activity
from .security import JwtToken, authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
def home():
    """
    Basis route
    """
    return "Welcome to the API!"


@app.post("/login", response_model=JwtToken)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user: models.User = authenticate_user(db, form_data.username, form_data.password)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/activity")
def create_activity(activity: Activity):
    print(activity)

    return "Activity created!"


@app.get("/activities/list", response_model=List[Activity])
def list_activities(db: Session = Depends(get_db)):
    return db.query(models.Activity).all()


# TODO proper model
@app.post("/impact", response_model=Dict[int, float])
def get_impact(values: Dict[int, float], db: Session = Depends((get_db))):
    coefs = db.query(models.LeontiefCoefficient).filter(
        models.LeontiefCoefficient.source_id.in_(values.keys())
    ).all()
    response: Dict[int, float] = dict()
    for coef in coefs:
        if coef.target_id not in response:
            response[coef.target_id] = 0
        response[coef.target_id] += coef.value * values[coef.source_id]
    return response


@app.post("/activity/{sector_id}/{sector_value}", response_model=Activity)
def get_results(sector_id: int, sector_value: float, db: Session = Depends(get_db)):
    coefs = db.query(models.ActivityCoefficient).filter(
        models.ActivityCoefficient.sector_id == sector_id
    ).all()
    props = {coef.activity.name: sector_value * coef.value for coef in coefs}
    return Activity(**props)


app.include_router(users.router, prefix='/users')
app.include_router(sectors.router, prefix='/sectors')


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
