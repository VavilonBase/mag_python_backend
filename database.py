from datetime import date, timedelta
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

engine = create_async_engine("sqlite+aiosqlite:///tasks.db")
new_session = async_sessionmaker(engine, expire_on_commit=False)


class Model(DeclarativeBase):
   pass

class ProjectOrm(Model):
   __tablename__ = "projects"
   id: Mapped[int] = mapped_column(primary_key=True)
   number: Mapped[int]
   author: Mapped[str]
   description: Mapped[str]
   dt_from: Mapped[date]
   dt_to: Mapped[date]

async def create_tables():
   async with engine.begin() as conn:
       await conn.run_sync(Model.metadata.create_all)

async def delete_tables():
   async with engine.begin() as conn:
       await conn.run_sync(Model.metadata.drop_all)