# Backend API 


| File | What it does |
|---|---|
| `recommender.py` | Loads the data from `/Data` once and scores the areas |
| `app.py` | The web API (FastAPI) |
| `../../requirements.txt` | Python packages Azure installs |

## Endpoints

| Method | URL | Purpose |
|---|---|---|
| GET | `/` | Health check – returns `{"status": "ok"}` |
| GET | `/options` | Accommodation types, factor names and rating labels for building the form |
| POST | `/recommend` | Returns the top 3 areas with explanations |
| GET | `/docs` | Interactive test page |

### Example request, `POST /recommend`
```json
{
  "budget": 900,
  "accommodation": "private_room",
  "ratings": {"Rent": 1, "Commute": 2, "Supermarkets": 2, "Groceries": 2,
              "Restaurants": 3, "Asian Restaurants": 3, "Cafes": 4, "Gyms": 3,
              "Parks": 4, "Pharmacies": 2, "Hospitals": 4, "Shopping Malls": 3}
}
```
`accommodation`: `shared_room`, `private_room`, `one_bed`, `two_bed`
Ratings: 1 = Very important, 2 = Important, 3 = Slightly important, 4 = Not important, missing factors will be counted as 4.

### Example response
```json
{
  "compared": 6,
  "accommodation": "Private Room",
  "budget": 900,
  "recommendations": [
    {"rank": 1, "area": "D1", "lea": "North Inner City", "rent": 1092.0,
     "budget_status": "Above budget", "commute_minutes": 14.0, "distance": "1.8 km",
     "match_score": 83.2, "why": "D1 has a short commute ...", "about": "About 26,452 people live here ..."}
  ],
  "excluded": [{"area": "D9", "reason": "No data for private room rent"}]
}
```

## Run it on your own computer
```bash
pip install -r requirements.txt 
cd Backend/api
uvicorn app:app --reload
```
open this link-> http://127.0.0.1:8000/docs

## Azure startup command
```
gunicorn --chdir Backend/api --bind=0.0.0.0:8000 -w 1 -k uvicorn.workers.UvicornWorker --timeout 120 app:app
```

## Calling it from the frontend 
```js
const res = await fetch("https://crib-crew-api.azurewebsites.net/recommend", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ budget: 900, accommodation: "private_room", ratings: { Rent: 1, Commute: 2 } })
});
const data = await res.json();
console.log(data.recommendations);
```
