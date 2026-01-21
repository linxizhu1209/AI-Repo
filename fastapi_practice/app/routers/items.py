from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime
from models.item import ItemCreate, ItemResponse, ItemUpdate

router = APIRouter(prefix="/items", tags=["items"])

fake_items_db = []
item_id_counter = 1

@router.get("/", response_model=List[ItemResponse])
async def get_items():
    return fake_items_db


@router.post("/", response_model=ItemResponse)
async def create_item(item: ItemCreate):
    global item_id_counter

    new_item = {
        "id": item_id_counter,
        "title": item.title,
        "description": item.description,
        "price": item.price,
        "create_at": datetime.now()
    }

    fake_items_db.append(new_item)

    item_id_counter += 1

    return new_item

@router.get("/{item_id}", response_model = ItemResponse)
async def get_item(item_id: int):
    for item in fake_items_db:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")