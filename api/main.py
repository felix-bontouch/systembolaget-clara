from fastapi import FastAPI
from config.settings_config import settings
from .llm_operations.agent import chain

app = FastAPI()

@app.get("/test")
def test():
    reponse = chain.invoke({})
    return {"status" : reponse}