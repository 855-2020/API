"""
Main API module
"""
from fastapi import FastAPI
import uvicorn

from .schemas import Activity

app = FastAPI()


@app.get("/")
def home():
    """
    Basis route
    """
    return "Welcome to the API!"


@app.post("/activity")
def create_activity(activity_data: Activity):
    activity = Activity(**activity_data)
    print(activity)

    return "Activity created!"


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
