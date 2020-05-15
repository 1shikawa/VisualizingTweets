import os

# モデル定義とクエリ生成
from sqlalchemy import (Column, DateTime, Integer, MetaData, String, Table,
                        create_engine, ARRAY)
# DBアクセス
from databases import Database

# 環境変数から取得
DATABASE_URI = os.getenv('DATABASE_URI')

engine = create_engine(DATABASE_URI, encoding="utf-8",  echo=True)
# 既存DB反映
metadata = MetaData(bind=engine, reflect=True)

stock = Table(
    # MySQL上のテーブル名
    'VisualizingTweets_stock',
    metadata
)

database = Database(DATABASE_URI)
