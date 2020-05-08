from app.api.models import StockOut, StockIn
from app.api.database import stock, database

# 全件取得
async def get_all_stock():
    query = stock.select()
    return await database.fetch_all(query=query)

# 指定対象取得
async def get_stock(id: int):
    query = stock.select(stock.c.id == id)
    return await database.fetch_one(query=query)

# 指定対象削除
async def delete_stock(id: int):
    query = stock.delete().where(stock.c.id == id)
    return await database.execute(query=query)

# １件登録
async def create_stock(payload: StockIn):
    query = stock.insert().values(**payload.dict())
    return await database.execute(query=query)

# １件更新
async def update_stock(id: int, payload: StockIn):
    query = (
        stock.update().where(stock.c.id == id).values(**payload.dict())
    )
    return await database.execute(query=query)
