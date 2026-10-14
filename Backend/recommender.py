import os
import re
from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(os.environ.get("DATA_DIR", Path(__file__).resolve().parents[1] / "Data"))

AREAS = ["D1", "D2", "D3", "D6", "D7", "D8", "D9", "D10"]
RTB_FILES = ["RTB_Clean.csv", "RTB_Clean1.csv", "RTB_Clean2.csv", "RTB_Clean3.csv"]
UNIVERSITY_NAME = "TU Dublin Grangegorman"

FACTORS = [
    {"name": "Rent",              "column": "Rent",              "kind": "rent"},
    {"name": "Commute",           "column": "Commute Minutes",   "kind": "commute"},
    {"name": "Supermarkets",      "column": "Supermarkets",      "kind": "count", "noun": "supermarkets"},
    {"name": "Groceries",         "column": "Groceries",         "kind": "count", "noun": "grocery shops"},
    {"name": "Restaurants",       "column": "Restaurants",       "kind": "count", "noun": "restaurants"},
    {"name": "Asian Restaurants", "column": "Asian_Restaurants", "kind": "count", "noun": "Asian restaurants"},
    {"name": "Cafes",             "column": "Cafes",             "kind": "count", "noun": "cafes"},
    {"name": "Gyms",              "column": "Gyms",              "kind": "count", "noun": "gyms"},
    {"name": "Parks",             "column": "Parks",             "kind": "count", "noun": "parks"},
    {"name": "Pharmacies",        "column": "Pharmacies",        "kind": "count", "noun": "pharmacies"},
    {"name": "Hospitals",         "column": "Hospitals",         "kind": "count", "noun": "hospitals"},
    {"name": "Shopping Malls",    "column": "Shopping_Malls",    "kind": "count", "noun": "shopping malls"},
]
FACTOR_LOOKUP = {f["name"]: f for f in FACTORS}

RATING_LABELS = {1: "Very important", 2: "Important", 3: "Slightly important", 4: "Not important"}
RATING_TO_WEIGHT = {1: 3, 2: 2, 3: 1, 4: 0}


def is_important(rating):
    """'Very important' or 'Important'."""
    return rating <= 2


# ---------------------------------------------------------------------------
# 1. LOAD DATA (runs once at start-up)
# ---------------------------------------------------------------------------
def _clean(df):
    df.columns = df.columns.str.strip()
    return df


def _minutes(value):
    value = str(value).lower().strip()
    hours = re.search(r"(\d+)\s*hr", value)
    minutes = re.search(r"(\d+)\s*min", value)
    return (int(hours.group(1)) * 60 if hours else 0) + (int(minutes.group(1)) if minutes else 0)


def load_data(data_dir=DATA_DIR):
    d = Path(data_dir)

    if (d / "TUD G.xlsx").exists():
        commute = _clean(pd.read_excel(d / "TUD G.xlsx"))
        commute["Commute Minutes"] = commute["Commute time"].apply(_minutes)
    else:
        raw = _clean(pd.read_csv(d / "Commute_TUD_Grangegorman.csv"))
        commute = (raw.groupby("District")
                      .agg(**{"Commute Minutes": ("Travel_Time_Min", "mean"),
                              "Distance_km": ("Distance_km", "mean")})
                      .reset_index().rename(columns={"District": "Area"}))
        commute["University"] = UNIVERSITY_NAME
        commute["Commute Minutes"] = commute["Commute Minutes"].round()
        commute["Distance"] = commute["Distance_km"].round(1).astype(str) + " km"
    commute = commute[["Area", "University", "Commute Minutes", "Distance"]]

    amenities = pd.concat([_clean(pd.read_csv(d / f"{a}_Amenities_Counts.csv")) for a in AREAS], ignore_index=True)

    room_data = pd.concat([_clean(pd.read_excel(d / f"{a}.xlsx")) for a in AREAS], ignore_index=True)
    room_data["Room type"] = room_data["Room type"].astype(str).str.strip().str.lower()

    rtb = pd.concat([_clean(pd.read_csv(d / f)) for f in RTB_FILES], ignore_index=True)
    rtb["Area"] = "D" + rtb["Location"].astype(str).str.extract(
        r"Dublin\s*(\d+W?)", flags=re.IGNORECASE, expand=False).str.upper()
    rtb["VALUE"] = pd.to_numeric(rtb["VALUE"], errors="coerce")
    bedrooms = rtb["Number of Bedrooms"].astype(str).str.strip().str.lower()

    census = _clean(pd.read_excel(d / "Dublin_Census_Filled.xlsx"))
    ethnicity = _clean(pd.read_excel(d / "Dublin_Ethnicity_D1_D24.xlsx"))

    rent_tables = {
        # Room data: double = Shared Room, single = Private Room
        "shared_room":  ("Shared Room",           room_data[room_data["Room type"] == "double"].groupby("Area")["Rent"].mean()),
        "private_room": ("Private Room",          room_data[room_data["Room type"] == "single"].groupby("Area")["Rent"].mean()),
        "one_bed":      ("One Bedroom Apartment", rtb[bedrooms == "one bed"].groupby("Area")["VALUE"].mean()),
        "two_bed":      ("Two Bedroom Apartment", rtb[bedrooms == "two bed"].groupby("Area")["VALUE"].mean()),
    }

    area_data = (commute.merge(amenities, on="Area", how="left")
                        .merge(census, on="Area", how="left")
                        .merge(ethnicity, on="Area", how="left"))

    return {"area_data": area_data, "rent_tables": rent_tables, "census": census, "ethnicity": ethnicity}


# ---------------------------------------------------------------------------
# 2. EXPLANATION HELPERS (same wording as the notebook)
# ---------------------------------------------------------------------------
def _join(items):
    return "".join(items) if len(items) <= 1 else ", ".join(items[:-1]) + " and " + items[-1]


def _better_or_worse(name, row, averages):
    f = FACTOR_LOOKUP[name]
    value, avg = row[f["column"]], averages[f["column"]]
    if avg == 0 or abs(value - avg) / abs(avg) < 0.10:
        return 0
    lower_is_better = f["kind"] in ("rent", "commute")
    better = value < avg if lower_is_better else value > avg
    return 1 if better else -1


def _good_phrase(name, row, ranked, acc_name):
    f = FACTOR_LOOKUP[name]
    value, col = row[f["column"]], f["column"]
    if f["kind"] == "commute":
        if value == ranked[col].min():
            return f"is the closest to {UNIVERSITY_NAME} (only {value:.0f} minutes away)"
        return f"has a short commute to {UNIVERSITY_NAME} (about {value:.0f} minutes)"
    if f["kind"] == "rent":
        if value == ranked[col].min():
            return f"is the cheapest area for a {acc_name.lower()} (€{value:,.0f} a month)"
        return f"has lower rent than most areas (€{value:,.0f} a month)"
    if value == ranked[col].max():
        return f"has the most {f['noun']} ({value:.0f})"
    return f"has more {f['noun']} than most areas ({value:.0f})"


def _bad_sentence(name, row, ranked):
    f = FACTOR_LOOKUP[name]
    value, col = row[f["column"]], f["column"]
    if f["kind"] == "commute":
        return f"the commute is longer – about {value:.0f} minutes to {UNIVERSITY_NAME}."
    if f["kind"] == "rent":
        return f"the rent is higher than in most areas (€{value:,.0f} a month)."
    if value == ranked[col].min():
        return f"it has the fewest {f['noun']} of all the areas ({value:.0f})."
    return f"it has fewer {f['noun']} than most areas ({value:.0f})."


def _short_name(name):
    f = FACTOR_LOOKUP[name]
    if f["kind"] == "commute":
        return "a shorter commute"
    if f["kind"] == "rent":
        return "cheaper rent"
    return f"more {f['noun']}"


def _why_ahead(a, b, active, top_n=2):
    gaps = [(n, a[f"{n} Contribution"] - b[f"{n} Contribution"]) for n in active]
    gaps = sorted([g for g in gaps if g[1] > 0.05], key=lambda g: g[1], reverse=True)
    return [_short_name(n) for n, _ in gaps[:top_n]]


def _explain(position, row, ranked, averages, ctx):
    ratings, active, acc_name = ctx["ratings"], ctx["active"], ctx["acc_name"]
    lines, n = [], len(ranked)

    good = [nm for nm in active if _better_or_worse(nm, row, averages) == 1]
    good.sort(key=lambda nm: ratings[nm])
    good = good[:3]
    if good:
        sentence = f"{row['Area']} " + _join([_good_phrase(nm, row, ranked, acc_name) for nm in good])
        if all(is_important(ratings[nm]) for nm in good):
            sentence += ", which are all things you said matter to you" if len(good) > 1 else ", which you said matters to you"
        lines.append(sentence + ".")

    diff = row["Budget Difference"]
    if diff <= 0:
        lines.append(f"The average rent is €{row['Rent']:,.0f} a month, which is €{abs(diff):,.0f} less than your budget.")
    else:
        lines.append(f"The average rent is €{row['Rent']:,.0f} a month, which is €{diff:,.0f} more than your budget.")

    if n > 1:
        if position < n:
            below = ranked.iloc[position]
            reasons = _why_ahead(row, below, active)
            if reasons:
                lines.append(f"It ranked higher than {below['Area']} because it has {_join(reasons)}.")
        if position > 1:
            above = ranked.iloc[position - 2]
            reasons = _why_ahead(above, row, active)
            if reasons:
                lines.append(f"It ranked lower than {above['Area']} because {above['Area']} has {_join(reasons)}.")

    bad = [nm for nm in active if is_important(ratings[nm]) and _better_or_worse(nm, row, averages) == -1]
    bad.sort(key=lambda nm: ratings[nm])
    for i, nm in enumerate(bad[:2]):
        lines.append(("One downside is that " if i == 0 else "Another downside is that ") + _bad_sentence(nm, row, ranked))

    if not good and n > 1:
        lines.insert(0, "This area is about average on the things you care about.")
    return " ".join(lines)


def _compare_word(value, average):
    if abs(value - average) < 1:
        return "about the same as"
    return "more than" if value > average else "less than"


def _profile(row, census, ethnicity):
    lines = []
    if pd.notna(row.get("Population")) and row["Population"] > 0:
        students = row["Students"] / row["Population"] * 100
        young = row["Age_20_29"] / row["Population"] * 100
        dub_students = census["Students"].sum() / census["Population"].sum() * 100
        dub_young = census["Age_20_29"].sum() / census["Population"].sum() * 100
        lines.append(f"About {row['Population']:,.0f} people live here.")
        lines.append(f"{students:.0f}% of people are students – {_compare_word(students, dub_students)} the Dublin average ({dub_students:.0f}%).")
        lines.append(f"{young:.0f}% of people are aged 20–29 – {_compare_word(young, dub_young)} the Dublin average ({dub_young:.0f}%).")
    if pd.notna(row.get("Non_Irish_%")):
        groups = [c for c in ethnicity.columns if c != "Area" and pd.notna(row.get(c))]
        largest = sorted(groups, key=lambda c: row[c], reverse=True)[:2]
        text = " and ".join(f"{c.replace(' (%)', '')} ({row[c]:.1f}%)" for c in largest)
        lines.append(f"{row['Non_Irish_%']:.0f}% of people are not Irish. The biggest groups are {text}.")
    if pd.notna(row.get("Apartments_%")):
        lines.append(f"{row['Apartments_%']:.0f}% of homes are apartments.")
    return " ".join(lines)


def _num(x, digits=0):
    return None if pd.isna(x) else round(float(x), digits)


# ---------------------------------------------------------------------------
# 3. MAIN ENTRY POINT
# ---------------------------------------------------------------------------
class RecommendationError(ValueError):
    pass


def recommend(data, budget, accommodation, ratings, top_n=3):
    """
    budget:        monthly budget in euro (number > 0)
    accommodation: "shared_room" | "private_room" | "one_bed" | "two_bed"
    ratings:       {"Rent": 1, "Commute": 2, ...}  1 = Very important ... 4 = Not important.
                   Factors left out count as 4 (Not important).
    """
    if accommodation not in data["rent_tables"]:
        raise RecommendationError(f"accommodation must be one of {list(data['rent_tables'])}")
    unknown = set(ratings) - set(FACTOR_LOOKUP)
    if unknown:
        raise RecommendationError(f"Unknown factors: {sorted(unknown)}")
    ratings = {f["name"]: int(ratings.get(f["name"], 4)) for f in FACTORS}

    acc_name, selected_rent = data["rent_tables"][accommodation]
    weights = {nm: RATING_TO_WEIGHT[r] for nm, r in ratings.items()}
    active = [nm for nm, w in weights.items() if w > 0]
    if not active:
        raise RecommendationError("Every factor is rated 'Not important', so there is nothing to rank on.")

    area_data = data["area_data"].copy()
    area_data["Rent"] = area_data["Area"].map(selected_rent)
    area_data["Budget Difference"] = area_data["Rent"] - budget
    area_data["Budget Status"] = np.select(
        [area_data["Rent"].isna(), area_data["Rent"] <= budget],
        ["Rent data unavailable", "Within budget"], default="Above budget")

    needed = list(dict.fromkeys([FACTOR_LOOKUP[nm]["column"] for nm in active] + ["Rent"]))
    has_data = area_data[needed].notna().all(axis=1)
    candidates = area_data[has_data].copy()
    excluded = area_data[~has_data]

    def missing_reason(row):
        missing = []
        if pd.isna(row["Rent"]):
            missing.append(f"{acc_name.lower()} rent")
        if any(pd.isna(row[c]) for c in needed if c not in ("Rent", "Commute Minutes")):
            missing.append("amenity counts")
        if pd.isna(row["Commute Minutes"]):
            missing.append("commute time")
        return "No data for " + " and ".join(missing)

    excluded_list = [{"area": r["Area"], "reason": missing_reason(r)}
                     for _, r in excluded.iterrows() if r["Area"] in AREAS]

    if candidates.empty:
        return {"compared": 0, "accommodation": acc_name, "budget": budget,
                "recommendations": [], "excluded": excluded_list}

    candidates["Rent Score"] = (budget / candidates["Rent"]).clip(upper=1)
    max_commute = candidates["Commute Minutes"].max()
    candidates["Commute Score"] = (1 - candidates["Commute Minutes"] / max_commute).clip(lower=0) if max_commute > 0 else 1
    for f in FACTORS:
        if f["kind"] == "count":
            mx = candidates[f["column"]].max()
            candidates[f"{f['column']} Score"] = candidates[f["column"]] / mx if mx > 0 else 0

    def score_col(nm):
        k = FACTOR_LOOKUP[nm]["kind"]
        return "Rent Score" if k == "rent" else "Commute Score" if k == "commute" else f"{FACTOR_LOOKUP[nm]['column']} Score"

    total = sum(weights.values())
    for nm in active:
        candidates[f"{nm} Contribution"] = candidates[score_col(nm)] * weights[nm] / total * 100
    candidates["Match Score"] = candidates[[f"{nm} Contribution" for nm in active]].sum(axis=1)
    ranked = candidates.sort_values("Match Score", ascending=False).reset_index(drop=True)

    averages = ranked[[f["column"] for f in FACTORS if f["column"] in ranked]].mean()
    ctx = {"ratings": ratings, "active": active, "acc_name": acc_name}

    results = []
    for i, row in ranked.head(top_n).iterrows():
        pos = i + 1
        results.append({
            "rank": pos,
            "area": row["Area"],
            "lea": row["LEA"] if pd.notna(row.get("LEA")) else None,
            "rent": _num(row["Rent"]),
            "budget_status": row["Budget Status"],
            "budget_difference": _num(row["Budget Difference"]),
            "commute_minutes": _num(row["Commute Minutes"]),
            "distance": row["Distance"],
            "match_score": _num(row["Match Score"], 1),
            "why": _explain(pos, row, ranked, averages, ctx),
            "about": _profile(row, data["census"], data["ethnicity"]),
        })

    return {"compared": len(ranked), "accommodation": acc_name, "budget": budget,
            "recommendations": results, "excluded": excluded_list}
