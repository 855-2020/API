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
from .routers import user, sector, model, role
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


app.include_router(user.router, prefix='/users')
app.include_router(sector.router, prefix='/sectors')
app.include_router(model.router, prefix='/models')
app.include_router(role.router, prefix='/roles')


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
