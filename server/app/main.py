from fastapi import FastAPI
app = FastAPI(title="Bank Assistant API")

@app.get("/")
async def root():
    return {"message" : "welcome"}

