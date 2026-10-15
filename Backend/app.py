
from typing import Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import recommender

app = FastAPI(title="Crib Crew – Dublin Area Recommender API", version="1.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

DATA = recommender.load_data() 


class RecommendRequest(BaseModel):
    budget: float = Field(..., gt=0, examples=[900])
    university: str = Field(recommender.UNIVERSITY_NAME, examples=["Trinity College Dublin"])
    accommodation: str = Field(..., examples=["single_room"],
                               description="single_room | double_room | studio | one_bed | two_bed | three_bed")
    ratings: Dict[str, int] = Field(
        ..., description="1 = Very important, 2 = Important, 3 = Slightly important, 4 = Not important",
        examples=[{"Rent": 1, "Commute": 2, "Supermarkets": 2, "Groceries": 2, "Restaurants": 3,
                   "Asian Restaurants": 3, "Cafes": 4, "Gyms": 3, "Parks": 4, "Pharmacies": 2,
                   "Hospitals": 4, "Shopping Malls": 3}])


@app.get("/")
def health():
    return {"status": "ok", "areas": recommender.AREAS}


@app.get("/options")
def options():
    """Everything the frontend needs to build the form."""
    return {
        "universities": DATA["universities"],
        "accommodation": {k: v[0] for k, v in DATA["rent_tables"].items()},
        "factors": [f["name"] for f in recommender.FACTORS],
        "ratings": recommender.RATING_LABELS,
    }


@app.post("/recommend")
def recommend(req: RecommendRequest):
    if any(r not in (1, 2, 3, 4) for r in req.ratings.values()):
        raise HTTPException(422, "Each rating must be 1, 2, 3 or 4")
    try:
        return recommender.recommend(DATA, req.budget, req.accommodation, req.ratings, req.university)
    except recommender.RecommendationError as e:
        raise HTTPException(422, str(e))
