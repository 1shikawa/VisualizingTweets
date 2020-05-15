from fastapi import FastAPI
from app.api.stock import stock
from app.api.database import metadata, database, engine

app = FastAPI(openapi_url="/api/v1/stock/openapi.json", docs_url="/api/v1/stock/docs")

# 起動時にDBに接続する
@app.on_event("startup")
async def startup():
    await database.connect()

# 終了時にDBを切断する
@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# stock routerを登録する
app.include_router(stock, prefix='/api/v1/stock', tags=['stock'])
