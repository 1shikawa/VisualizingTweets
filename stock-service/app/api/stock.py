from typing import List
from fastapi import APIRouter, HTTPException

from app.api.models import StockIn, StockOut, StockUpdate
from app.api import crud

stock = APIRouter()

@stock.get('/', response_model=List[StockOut])
async def get_all_stock():
    return await crud.get_all_stock()


@stock.get('/{id}/', response_model=StockOut)
async def get_stock(id):
    stock = await crud.get_stock(id)
    if not stock:
        raise HTTPException(status_code=404, detail='stock not found')
    return stock


@stock.delete('/{id}/')
async def delete_stock(id):
    stock = await crud.get_stock(id)
    if not stock:
        raise HTTPException(status_code=404, detail='stock not found')
    await crud.delete_stock(id)
    return {"result": "delete success"}


@stock.post('/', response_model=StockOut, status_code=201)
async def create_stcok(payload: StockIn):
    stock_id = await crud.create_stock(payload)
    response = {
        'id': stock_id,
        **payload.dict()
    }

    return response

@stock.put('/{id}/', response_model=StockOut, status_code=201)
async def update_stock(id: int, payload: StockUpdate):
    stock = await crud.get_stock(id)
    if not stock:
        raise HTTPException(status_code=404, detail='stock not found')

    update_data = payload.dict(exclude_unset=True)

    stock_in_db = StockIn(**stock)

    updated_stock = stock_in_db.copy(update=update_data)
    await crud.update_stock(id, updated_stock)

    response = {
        'id': id,
        **update_data
    }

    return response
