from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from ytmusicapi import YTMusic

app = FastAPI()

# CORS setup (allow all for now)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ytmusic = YTMusic()  # anonymous auth

@app.get("/api/search")
def search(q: str = Query(..., description="Search query")):
    try:
        results = ytmusic.search(q, filter="songs")
        return {"results": results}
    except Exception as e:
        return {"error": str(e)}
