import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="TMDB Clone - MongoDB Atlas Edition")

# Connessione MongoDB Atlas
MONGO_DETAILS = os.getenv("MONGO_DETAILS")
client = AsyncIOMotorClient(MONGO_DETAILS)
db = client.movie_db
movie_collection = db.movies

# Montiamo la cartella static (opzionale per file CSS/JS esterni)
app.mount("/static", StaticFiles(directory="static"), name="static")


def movie_helper(movie) -> dict:
    return {
        "movie_id": movie["movie_id"],
        "title": movie["title"],
        "details": movie["details"],
        "media": movie["media"],
        "cast": movie["cast"],
        "director": movie["director"]
    }

# --- ROTTE FRONTEND ---


@app.get("/")
async def read_index():
    return FileResponse('static/index.html')


@app.get("/movie")
async def read_movie():
    return FileResponse('static/movie.html')

# --- ROTTE API ---


@app.get("/api/movies")
async def get_all_movies():
    movies = []
    async for movie in movie_collection.find():
        movies.append(movie_helper(movie))
    return movies


@app.get("/api/movies/{movie_id}")
async def get_movie_by_id(movie_id: int):
    movie = await movie_collection.find_one({"movie_id": movie_id})
    if movie:
        return movie_helper(movie)
    raise HTTPException(status_code=404, detail="Film non trovato")


@app.get("/api/search/")
async def search_movies(q: str = Query(None, min_length=2)):
    if not q:
        return await get_all_movies()
    query = {"$text": {"$search": q}}
    results = []
    async for movie in movie_collection.find(query):
        results.append(movie_helper(movie))
    return results

# if __name__ == "__main__":
#    import uvicorn
#    uvicorn.run(app, host="0.0.0.0", port=8000)
