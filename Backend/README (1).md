# Backend

This folder has the backend for our Dublin area recommender. It takes what the student enters (budget, room type and what matters to them) and returns the top 3 Dublin areas with a short explanation for each.

It is hosted on Azure here:
https://crib-crew-api-bqf2b3b9bea0ada0.germanywestcentral-01.azurewebsites.net/docs

Open that link to test it in the browser.

## Files

- `recommender.py` - loads the data from the Data folder and scores the areas
- `app.py` - makes it a web API so the website can use it
- `Recommendation system.ipynb` - our first prototype in Colab

## How to use it

Send a POST request to `/recommend` like this:

```json
{
  "budget": 900,
  "accommodation": "single_room",
  "ratings": {"Rent": 1, "Commute": 2, "Supermarkets": 2, "Cafes": 4}
}
```

Accommodation can be: `single_room`, `double_room`, `studio`, `one_bed`, `two_bed`, `three_bed`

Ratings go from 1 to 4 (1 = very important, 4 = not important). If a factor is left out it counts as 4.

Factors: Rent, Commute, Supermarkets, Groceries, Restaurants, Asian Restaurants, Cafes, Gyms, Parks, Pharmacies, Hospitals, Shopping Malls

`/options` gives the list of room types and factors, so the frontend doesn't have to hard code them.

## Rent data

Rent comes from Daft.ie listings. For 1 and 2 bed, if an area has less than 3 listings we use the RTB average instead.

Areas covered right now: D1-D3 and D6-D14. To add an area, upload its rent file (e.g. `D15.xlsx`) and amenity file (`D15_Amenities_Counts.csv`) to Data and add it to the `AREAS` list in `recommender.py`.

## Running it locally

```
pip install -r requirements.txt
cd Backend
uvicorn app:app --reload
```

Then go to http://127.0.0.1:8000/docs

## Deployment

Every push to main redeploys it to Azure automatically (GitHub Actions). Startup command on Azure:

```
gunicorn --chdir Backend --bind=0.0.0.0:8000 -w 1 -k uvicorn.workers.UvicornWorker --timeout 120 app:app
```
