from fastapi import FastAPI
from pydantic import BaseModel, ValidationError
from settings import Settings
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
settings = None

try:
    settings = Settings()
    logger.info(f"Settings loaded: {settings}")
except ValidationError as e:
    logger.error("Validation error ", exc_info=e)
    for error in e.errors():
        logger.error(error["message"], exc_info=error["exc_info"])
    raise SystemExit(1)

app = FastAPI(title="DC25_bobry Dummy API")

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float

@app.get("/")
async def read_root():
    return {"message": "Hello from FastAPI!"}

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id, "name": f"Item {item_id}"}

@app.post("/items/")
async def create_item(item: Item):
    return {"message": "Item received", "item": item}

