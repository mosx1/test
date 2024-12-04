from pydantic import BaseModel

class Translate(BaseModel):

    session: str
    user_id: int
    summ: float