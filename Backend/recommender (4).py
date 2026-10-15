import os
import re
from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(os.environ.get("DATA_DIR", Path(__file__).resolve().parents[1] / "Data"))

AREAS = ["D1", "D2", "D3", "D6", "D7", "D8", "D9", "D10", "D11", "D12", "D13", "D14"]
RTB_FILES = ["RTB_Clean.csv", "RTB_Clean1.csv", "RTB_Clean2.csv", "RTB_Clean3.csv"]
UNIVERSITY_NAME = "TU Dublin - Grangegorman"
MIN_DAFT_LISTINGS = 3 

FACTORS = [
    {"name": "Rent", "column": "Rent", "kind": "rent"},
    {"name": "Commute", "column": "Commute Minutes", "kind": "commute"},
    {"name": "Shopping & Groceries", "column": "Shopping & Groceries", "kind": "group",
     "columns": ["Supermarkets", "Groceries", "Shopping_Malls"], "noun": "shopping and grocery options"},
    {"name": "Restaurants", "column": "Restaurants", "kind": "count", "noun": "restaurants"},
    {"name": "Healthcare", "column": "Healthcare", "kind": "group",
     "columns": ["Hospitals", "Pharmacies"], "noun": "healthcare amenities"},
    {"name": "Recreation & Wellness", "column": "Recreation & Wellness", "kind": "group",
     "columns": ["Gyms", "Parks"], "noun": "recreation and wellness amenities"},
]
FACTOR_LOOKUP = {f["name"]: f for f in FACTORS}

RATING_LABELS = {1: "Very important", 2: "Important", 3: "Slightly important", 4: "Not important"}
RATING_TO_WEIGHT = {1: 3, 2: 2, 3: 1, 4: 0}


class RecommendationError(ValueError):
    pass


def clean_columns(df):
    df.columns = df.columns.str.strip()
    return df


def read_if_exists(path, reader):
    if path.exists():
        return clean_columns(reader(path))
    return None


# loading data

def load_data(data_dir=DATA_DIR):
    d = Path(data_dir)

    raw = clean_columns(pd.read_csv(d / "Dublin_D1_D24_All_University_Commutes_clean_updated.csv"))
    commute = raw.groupby(["District", "University"]).agg(
        commute_min=("Travel_Time_Min", "mean"),
        dist_km=("Distance_km", "mean"),
    ).reset_index()
    commute = commute.rename(columns={"District": "Area", "commute_min": "Commute Minutes"})
    commute["Commute Minutes"] = commute["Commute Minutes"].round()
    commute["Distance"] = commute["dist_km"].round(1).astype(str) + " km"

    walking = clean_columns(pd.read_excel(d / "Dublin_D1_D24_Walking_Distance_and_Time_to_University.xlsx"))
    walking = walking.rename(columns={"District": "Area",
                                      "Walking_Distance_to_University_km": "Walk km",
                                      "Walking_Time_to_University_Min": "Walk Minutes"})
    walk_avg = walking.groupby(["Area", "University"])[["Walk km", "Walk Minutes"]].mean().reset_index()

    commute = commute.merge(walk_avg, on=["Area", "University"], how="left")
    commute = commute[["Area", "University", "Commute Minutes", "Distance", "Walk km", "Walk Minutes"]]
    universities = sorted(commute["University"].unique())

    amenity_files = [read_if_exists(d / f"{a}_Amenities_Counts.csv", pd.read_csv) for a in AREAS]
    amenities = pd.concat([x for x in amenity_files if x is not None], ignore_index=True)

    room_files = [read_if_exists(d / f"{a}.xlsx", pd.read_excel) for a in AREAS]
    room_data = pd.concat([x for x in room_files if x is not None], ignore_index=True)
    room_data["Room type"] = room_data["Room type"].astype(str).str.strip().str.lower()

    rtb = pd.concat([clean_columns(pd.read_csv(d / f)) for f in RTB_FILES], ignore_index=True)
    rtb["Area"] = "D" + rtb["Location"].astype(str).str.extract(r"Dublin\s*(\d+W?)", flags=re.I, expand=False).str.upper()
    rtb["VALUE"] = pd.to_numeric(rtb["VALUE"], errors="coerce")
    beds = rtb["Number of Bedrooms"].astype(str).str.strip().str.lower()

    census = clean_columns(pd.read_excel(d / "Dublin_Census_Filled.xlsx"))
    ethnicity = clean_columns(pd.read_excel(d / "Dublin_Ethnicity_D1_D24.xlsx"))

    def daft_rent(room_type):
        rent = room_data[room_data["Room type"] == room_type].groupby("Area")["Rent"].mean()
        return rent, pd.Series("Daft.ie", index=rent.index)

    def daft_or_rtb(room_type, rtb_beds):
        listings = room_data[room_data["Room type"] == room_type].groupby("Area")["Rent"]
        daft = listings.mean()[listings.count() >= MIN_DAFT_LISTINGS]
        rtb_avg = rtb[beds == rtb_beds].groupby("Area")["VALUE"].mean()
        rtb_avg = rtb_avg.drop(daft.index, errors="ignore")
        rent = pd.concat([daft, rtb_avg])
        source = pd.concat([pd.Series("Daft.ie", index=daft.index), pd.Series("RTB", index=rtb_avg.index)])
        return rent, source

    rent_tables = {
        "single_room": ("Single Room", *daft_rent("single")),
        "double_room": ("Double Room", *daft_rent("double")),
        "studio": ("Studio", *daft_rent("studio")),
        "one_bed": ("1 Bed Apartment", *daft_or_rtb("1 bed", "one bed")),
        "two_bed": ("2 Bed Apartment", *daft_or_rtb("2 bed", "two bed")),
        "three_bed": ("3 Bed House/Apartment", *daft_rent("3 bed")),
    }

    area_data = pd.DataFrame({"Area": AREAS})
    area_data = (area_data.merge(amenities, on="Area", how="left")
                          .merge(census, on="Area", how="left")
                          .merge(ethnicity, on="Area", how="left"))

    for f in FACTORS:
        if f["kind"] == "group":
            area_data[f["column"]] = area_data[f["columns"]].sum(axis=1, skipna=False)

    return {"area_data": area_data, "commute": commute, "walking": walking, "universities": universities,
            "rent_tables": rent_tables, "census": census, "ethnicity": ethnicity}


#  explanation text 

def join_words(items):
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + " and " + items[-1]


def is_important(rating):
    return rating <= 2


def better_or_worse(name, row, averages):
    f = FACTOR_LOOKUP[name]
    value, avg = row[f["column"]], averages[f["column"]]
    if avg == 0 or abs(value - avg) / abs(avg) < 0.10:  
        return 0
    if f["kind"] in ("rent", "commute"): 
        return 1 if value < avg else -1
    return 1 if value > avg else -1


def good_phrase(name, row, ranked, acc_name):
    f = FACTOR_LOOKUP[name]
    col = f["column"]
    value = row[col]
    if f["kind"] == "commute":
        if value == ranked[col].min():
            return f"is the closest to {row['University']} only {value:.0f} minutes away"
        return f"has a short commute to {row['University']} about {value:.0f} minutes"
    if f["kind"] == "rent":
        if value == ranked[col].min():
            return f"is the cheapest area for a {acc_name.lower()}, €{value:,.0f} a month"
        return f"has lower rent than most areas, €{value:,.0f} a month"
    if value == ranked[col].max():
        return f"has the most {f['noun']} {value:.0f}"
    return f"has more {f['noun']} than most areas {value:.0f}"


def bad_sentence(name, row, ranked):
    f = FACTOR_LOOKUP[name]
    col = f["column"]
    value = row[col]
    if f["kind"] == "commute":
        return f"the commute is longer, about {value:.0f} minutes to {row['University']}."
    if f["kind"] == "rent":
        return f"the rent is higher than in most areas, €{value:,.0f} a month."
    if value == ranked[col].min():
        return f"it has the fewest {f['noun']} of all the areas {value:.0f}."
    return f"it has fewer {f['noun']} than most areas {value:.0f}."


def short_name(name):
    kind = FACTOR_LOOKUP[name]["kind"]
    if kind == "commute":
        return "a shorter commute"
    if kind == "rent":
        return "cheaper rent"
    return "more " + FACTOR_LOOKUP[name]["noun"]


def why_ahead(a, b, active):
    gaps = []
    for name in active:
        gap = a[name + " Contribution"] - b[name + " Contribution"]
        if gap > 0.05:
            gaps.append((gap, name))
    gaps.sort(reverse=True)
    return [short_name(name) for _, name in gaps[:2]]


def explain(position, row, ranked, averages, ratings, active, acc_name):
    lines = []
    n = len(ranked)

    good = [x for x in active if better_or_worse(x, row, averages) == 1]
    good = sorted(good, key=lambda x: ratings[x])[:3]
    if good:
        sentence = row["Area"] + " " + join_words([good_phrase(x, row, ranked, acc_name) for x in good])
        if all(is_important(ratings[x]) for x in good):
            sentence += ", which are all things you said matter to you" if len(good) > 1 else ", which you said matters to you"
        lines.append(sentence + ".")

    diff = row["Budget Difference"]
    if diff <= 0:
        lines.append(f"The average rent is €{row['Rent']:,.0f} a month, which is €{abs(diff):,.0f} less than your budget.")
    else:
        lines.append(f"The average rent is €{row['Rent']:,.0f} a month, which is €{diff:,.0f} more than your budget.")
    if row["Rent Source"] == "RTB":
        lines.append("This is the RTB average, as there weren't enough current listings on Daft for this area.")

    if position < n:
        below = ranked.iloc[position]
        reasons = why_ahead(row, below, active)
        if reasons:
            lines.append(f"It ranked higher than {below['Area']} because it has {join_words(reasons)}.")
    if position > 1:
        above = ranked.iloc[position - 2]
        reasons = why_ahead(above, row, active)
        if reasons:
            lines.append(f"It ranked lower than {above['Area']} because {above['Area']} has {join_words(reasons)}.")

    bad = [x for x in active if is_important(ratings[x]) and better_or_worse(x, row, averages) == -1]
    bad = sorted(bad, key=lambda x: ratings[x])[:2]
    for i, x in enumerate(bad):
        start = "One downside is that " if i == 0 else "Another downside is that "
        lines.append(start + bad_sentence(x, row, ranked))

    if not good and n > 1:
        lines.insert(0, "This area is about average on the things you care about.")
    return " ".join(lines)


def compare_word(value, average):
    if abs(value - average) < 1:
        return "about the same as"
    return "more than" if value > average else "less than"


def area_profile(row, census, ethnicity):
    lines = []
    if pd.notna(row.get("Population")) and row["Population"] > 0:
        students = row["Students"] / row["Population"] * 100
        young = row["Age_20_29"] / row["Population"] * 100
        dub_students = census["Students"].sum() / census["Population"].sum() * 100
        dub_young = census["Age_20_29"].sum() / census["Population"].sum() * 100
        lines.append(f"About {row['Population']:,.0f} people live here.")
        lines.append(f"{students:.0f}% of people are students – {compare_word(students, dub_students)} the Dublin average ({dub_students:.0f}%).")
        lines.append(f"{young:.0f}% of people are aged 20–29 – {compare_word(young, dub_young)} the Dublin average ({dub_young:.0f}%).")
    if pd.notna(row.get("Non_Irish_%")):
        groups = [c for c in ethnicity.columns if c != "Area" and pd.notna(row.get(c))]
        top2 = sorted(groups, key=lambda c: row[c], reverse=True)[:2]
        text = " and ".join(f"{c.replace(' (%)', '')} ({row[c]:.1f}%)" for c in top2)
        lines.append(f"{row['Non_Irish_%']:.0f}% of people are not Irish. The biggest groups are {text}.")
    if pd.notna(row.get("Apartments_%")):
        lines.append(f"{row['Apartments_%']:.0f}% of homes are apartments.")
    return " ".join(lines)


def to_number(x, digits=0):
    if pd.isna(x):
        return None
    return round(float(x), digits)


def factor_columns(f):
    return f.get("columns", [f["column"]])


def walking_info(walking, area, university):
    rows = walking[(walking["Area"] == area) & (walking["University"] == university)]
    places = []
    for _, w in rows.iterrows():
        places.append({
            "landmark": w["Landmark"],
            "direction": w["Direction"],
            "km": to_number(w["Walk km"], 2),
            "minutes": to_number(w["Walk Minutes"]),
        })
    return places


def budget_warning(ranked, budget, acc_name, top_n):
    if not (ranked.head(top_n)["Budget Status"] == "Above budget").all():
        return None
    text = f"None of the top {min(top_n, len(ranked))} areas fit your €{budget:,.0f} budget for a {acc_name.lower()}."
    affordable = ranked[ranked["Budget Status"] == "Within budget"]
    if not affordable.empty:
        best = affordable.iloc[0]
        text += (f" {best['Area']} does fit your budget (€{best['Rent']:,.0f} a month) but ranked lower overall"
                 f" (match score {best['Match Score']:.1f}%) because of your other preferences.")
    else:
        cheapest = ranked.loc[ranked["Rent"].idxmin()]
        text += (f" No area we compared fits this budget. The cheapest is {cheapest['Area']}"
                 f" at €{cheapest['Rent']:,.0f} a month (€{cheapest['Rent'] - budget:,.0f} over budget).")
    return text


# main function

def recommend(data, budget, accommodation, ratings, university=UNIVERSITY_NAME, top_n=3):
    if accommodation not in data["rent_tables"]:
        raise RecommendationError(f"accommodation must be one of {list(data['rent_tables'])}")
    if university not in data["universities"]:
        raise RecommendationError(f"university must be one of {data['universities']}")
    unknown = set(ratings) - set(FACTOR_LOOKUP)
    if unknown:
        raise RecommendationError(f"Unknown factors: {sorted(unknown)}")

    # anything the user didn't rate counts as not important
    ratings = {f["name"]: int(ratings.get(f["name"], 4)) for f in FACTORS}
    weights = {name: RATING_TO_WEIGHT[r] for name, r in ratings.items()}
    active = [name for name, w in weights.items() if w > 0]
    if not active:
        raise RecommendationError("Every factor is rated 'Not important', so there is nothing to rank on.")

    acc_name, selected_rent, rent_source = data["rent_tables"][accommodation]

    uni_commute = data["commute"][data["commute"]["University"] == university]
    areas = data["area_data"].merge(uni_commute, on="Area", how="left")
    areas["University"] = university
    areas["Rent"] = areas["Area"].map(selected_rent)
    areas["Rent Source"] = areas["Area"].map(rent_source)
    areas["Budget Difference"] = areas["Rent"] - budget
    areas["Budget Status"] = np.select(
        [areas["Rent"].isna(), areas["Rent"] <= budget],
        ["Rent data unavailable", "Within budget"],
        default="Above budget",
    )

    needed = []
    for x in active:
        needed += factor_columns(FACTOR_LOOKUP[x])
    needed = list(dict.fromkeys(needed + ["Rent"]))
    has_data = areas[needed].notna().all(axis=1)
    candidates = areas[has_data].copy()

    excluded = []
    for _, row in areas[~has_data].iterrows():
        missing = []
        if pd.isna(row["Rent"]):
            missing.append(acc_name.lower() + " rent")
        if any(pd.isna(row[c]) for c in needed if c not in ("Rent", "Commute Minutes")):
            missing.append("amenity counts")
        if pd.isna(row["Commute Minutes"]):
            missing.append("commute time")
        excluded.append({"area": row["Area"], "reason": "No data for " + " and ".join(missing)})

    if candidates.empty:
        return {"compared": 0, "university": university, "accommodation": acc_name, "budget": budget,
                "warning": None, "recommendations": [], "excluded": excluded}

    candidates["Rent Score"] = (budget / candidates["Rent"]).clip(upper=1)
    max_commute = candidates["Commute Minutes"].max()
    candidates["Commute Score"] = (1 - candidates["Commute Minutes"] / max_commute).clip(lower=0) if max_commute > 0 else 1
    for f in FACTORS:
        if f["kind"] in ("count", "group"):
            for col in factor_columns(f):
                top = candidates[col].max()
                candidates[col + " Score"] = candidates[col] / top if top > 0 else 0
        if f["kind"] == "group":
            # average of the parts so one big number doesnt take over the group
            candidates[f["name"] + " Score"] = candidates[[c + " Score" for c in f["columns"]]].mean(axis=1)

    total = sum(weights.values())
    for name in active:
        f = FACTOR_LOOKUP[name]
        if f["kind"] == "rent":
            score_col = "Rent Score"
        elif f["kind"] == "commute":
            score_col = "Commute Score"
        elif f["kind"] == "group":
            score_col = f["name"] + " Score"
        else:
            score_col = f["column"] + " Score"
        candidates[name + " Contribution"] = candidates[score_col] * weights[name] / total * 100

    candidates["Match Score"] = candidates[[x + " Contribution" for x in active]].sum(axis=1)
    ranked = candidates.sort_values("Match Score", ascending=False).reset_index(drop=True)
    averages = ranked[[f["column"] for f in FACTORS if f["column"] in ranked]].mean()

    results = []
    for i, row in ranked.head(top_n).iterrows():
        position = i + 1
        results.append({
            "rank": position,
            "area": row["Area"],
            "lea": row["LEA"] if pd.notna(row.get("LEA")) else None,
            "rent": to_number(row["Rent"]),
            "rent_source": row["Rent Source"],
            "budget_status": row["Budget Status"],
            "budget_difference": to_number(row["Budget Difference"]),
            "commute_minutes": to_number(row["Commute Minutes"]),
            "distance": row["Distance"],
            "walk_km": to_number(row["Walk km"], 2),
            "walk_minutes": to_number(row["Walk Minutes"]),
            "walking_by_place": walking_info(data["walking"], row["Area"], university),
            "match_score": to_number(row["Match Score"], 1),
            "why": explain(position, row, ranked, averages, ratings, active, acc_name),
            "about": area_profile(row, data["census"], data["ethnicity"]),
        })

    return {"compared": len(ranked), "university": university, "accommodation": acc_name, "budget": budget,
            "warning": budget_warning(ranked, budget, acc_name, top_n),
            "recommendations": results, "excluded": excluded}
