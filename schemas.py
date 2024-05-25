from pydantic import BaseModel
from pydantic import ConfigDict
from datetime import date

class SProjectAdd(BaseModel):
   number: int
   author: str
   description: str

   
class SProjectFullAdd(BaseModel):
   number: int
   author: str
   description: str
   dt_from: date
   dt_to: date


class SProject(SProjectFullAdd):
   id: int
   model_config = ConfigDict(from_attributes=True)

class SProjectId(BaseModel):
   id: int