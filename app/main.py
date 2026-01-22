from fastapi import Depends, FastAPI
from app.database import get_db

app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/health")
def health_check(db=Depends(get_db)):
    db.execute("SELECT 1")
    return {"status": "ok"}