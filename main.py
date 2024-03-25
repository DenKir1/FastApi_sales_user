from tortoise.contrib.fastapi import register_tortoise
import config
# from tortoise import Tortoise
from fastapi import FastAPI
from sales.router import router as router_product
from users.router import router as router_user


app = FastAPI(
    title="SALES"
)

#app.add_middleware(
#            db_url=config.DATABASE_CONFIG,
#        )

app.include_router(router_product)
app.include_router(router_user)

register_tortoise(app=app, config=config.DATABASE_CONFIG)
