from pathlib import Path

import pandas as pd
import streamlit as st

from src.scrape import PremScraper

PREDICTIONS_DIR = Path("predictions/prem")

st.set_page_config(
    page_title="Premier League Predictions",
    page_icon="⚽",
)

st.markdown(
    """
    <style>
        .stApp {
            background-color: #080b14;
        }
        .block-container {
            max-width: 1200px;
            padding-top: 2rem;
        }
        .hero {
            padding: 2.5rem;
            border-radius: 24px;
            background: linear-gradient(135deg, #37003c, #210024);
            border: 1px solid #4b1452;
            margin-bottom: 1.5rem;
        }
        .hero h1 {
            font-size: 3rem;
            margin: 0;
            color: white;
        }
        .hero p {
            color: #c9b8cc;
            font-size: 1.1rem;
            margin-top: 0.6rem;
        }
        .green {
            color: #00ff85;
        }
        .card {
            background: #111622;
            border: 1px solid #202737;
            border-radius: 16px;
            padding: 1.2rem;
        }
        .small-label {
            color: #737d90;
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            font-weight: 700;
        }
        .big-value {
            color: white;
            font-size: 1.8rem;
            font-weight: 800;
            margin-top: 0.2rem;
        }
        .leader {
            background: linear-gradient(
                90deg,
                rgba(0, 255, 133, 0.10),
                #111622
            );
            border: 1px solid rgba(0, 255, 133, 0.25);
        }
        .muted {
            color: #737d90;
        }
        .exact {
            color: #00ff85;
            font-weight: 700;
        }
        .close {
            color: #f6c945;
            font-weight: 700;
        }
        .bad {
            color: #ff657d;
            font-weight: 700;
        }
        .team {
            color: white;
            font-weight: 650;
        }
        hr {
            border-color: #202737;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

def parse_prediction_file(path: Path) -> list[str]:
    """
    Prediction files contain one team per line, in predicted order.
    """
    return [
        line
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def load_predictions() -> dict[str, list[str]]:
    if not PREDICTIONS_DIR.exists():
        return {}

    return {
        path.stem.capitalize(): parse_prediction_file(path)
        for path in sorted(PREDICTIONS_DIR.glob("*.txt"))
    }


@st.cache_data(ttl=3600)
def get_standings():
    scraper = PremScraper()
    return scraper.scrape_standings()


def build_comparison(standings, predictions):
    actual_rank = {
        row["Team"]: int(row["Rk"])
        for _, row in standings.iterrows()
    }

    comparisons = {}

    for person, teams in predictions.items():
        rows = []

        for predicted, team in enumerate(teams, start=1):
            actual = actual_rank.get(team)

            rows.append(
                {
                    "team": team,
                    "predicted": predicted,
                    "actual": actual,
                    "error": (
                        abs(predicted - actual)
                        if actual is not None
                        else None
                    ),
                }
            )

        comparisons[person] = rows

    return comparisons


def build_leaderboard(comparisons):
    leaderboard = []

    for person, rows in comparisons.items():
        valid = [r for r in rows if r["actual"] is not None]

        if not valid:
            continue

        errors = [r["error"] for r in valid]

        leaderboard.append(
            {
                "person": person,
                "total_error": sum(errors),
                "avg_error": sum(errors) / len(errors),
                "exact": sum(e == 0 for e in errors),
            }
        )

    return sorted(
        leaderboard,
        key=lambda x: (
            x["total_error"],
            x["avg_error"],
            -x["exact"],
        ),
    )

try:
    standings = get_standings()
except Exception as e:
    st.error(f"Could not retrieve standings: {e}")
    st.stop()

predictions = load_predictions()

if not predictions:
    st.error("No predictions found.")
    st.stop()

comparisons = build_comparison(standings, predictions)
leaderboard = build_leaderboard(comparisons)

st.markdown(
    """
    <div class="hero">
        <h1>
            Premier League <span class="green">Predictions</span>
        </h1>
        <p>
            Who knows ball?
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

if leaderboard:
    leader = leaderboard[0]

    c1, c2, c3, c4 = st.columns(4)

    metrics = [
        ("Predictors", len(leaderboard)),
        ("Current leader", leader["person"]),
        ("Best error", leader["total_error"]),
        ("Exact hits", sum(x["exact"] for x in leaderboard)),
    ]

    for col, (label, value) in zip(
        [c1, c2, c3, c4],
        metrics,
    ):
        with col:
            st.markdown(
                f"""
                <div class="card">
                    <div class="small-label">{label}</div>
                    <div class="big-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

st.subheader("Prediction leaderboard")

for i, row in enumerate(leaderboard):
    if i == 0:
        medal = "🥇"
        border = "leader"
    elif i == 1:
        medal = "🥈"
        border = ""
    elif i == 2:
        medal = "🥉"
        border = ""
    else:
        medal = f"#{i + 1}"
        border = ""

    with st.container(border=True):
        cols = st.columns(
            [0.6, 3, 1.2, 1.2, 1.2, 1.2]
        )

        cols[0].markdown(
            f"### {medal}"
        )

        cols[1].markdown(
            f"**{row['person']}**"
        )

        cols[2].markdown(
            f"""
            <div class="small-label">Error</div>
            <div class="big-value">{row['total_error']}</div>
            """,
            unsafe_allow_html=True,
        )

        cols[3].markdown(
            f"""
            <div class="small-label">Avg error</div>
            <div class="big-value">{row['avg_error']:.2f}</div>
            """,
            unsafe_allow_html=True,
        )

        cols[4].markdown(
            f"""
            <div class="small-label">Exact</div>
            <div class="big-value">{row['exact']}</div>
            """,
            unsafe_allow_html=True,
        )

        # cols[5].markdown(
        #     f"""
        #     <div class="small-label">Within 2</div>
        #     <div class="big-value">{row['within_two']}</div>
        #     """,
        #     unsafe_allow_html=True,
        # )


# =============================================================================
# PERSON DETAIL
# =============================================================================

st.subheader("📊 Prediction breakdown")

selected_person = st.selectbox(
    "Select predictor",
    list(comparisons.keys()),
)

rows = comparisons[selected_person]

valid = [
    r for r in rows
    if r["actual"] is not None
]

if valid:
    total_error = sum(r["error"] for r in valid)
    average_error = total_error / len(valid)
    exact = sum(r["error"] == 0 for r in valid)
    within_two = sum(r["error"] <= 2 for r in valid)

    c1, c2, c3, c4 = st.columns(4)

    stats = [
        ("Total error", total_error),
        ("Average error", f"{average_error:.2f}"),
        ("Exact positions", exact),
        ("Within 2", within_two),
    ]

    for col, (label, value) in zip(
        [c1, c2, c3, c4],
        stats,
    ):
        with col:
            st.markdown(
                f"""
                <div class="card">
                    <div class="small-label">{label}</div>
                    <div class="big-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


st.write("")

# Header
cols = st.columns([0.7, 3, 1, 1])

cols[0].markdown("**Pred**")
cols[1].markdown("**Team**")
cols[2].markdown("**Actual**")
cols[3].markdown("**Difference**")

st.divider()

for row in rows:
    predicted = row["predicted"]
    team = row["team"]
    actual = row["actual"]
    error = row["error"]

    if actual is None:
        actual_display = "—"
        difference = "Not found"
        css_class = "bad"

    elif error == 0:
        actual_display = str(actual)
        difference = "🎯 Exact"
        css_class = "exact"

    elif error <= 2:
        actual_display = str(actual)
        difference = f"↕ {error}"
        css_class = "close"

    else:
        actual_display = str(actual)
        difference = f"↕ {error}"
        css_class = "bad"

    cols = st.columns([0.7, 3, 1, 1])

    cols[0].markdown(
        f"<span class='muted'>{predicted}</span>",
        unsafe_allow_html=True,
    )

    cols[1].markdown(
        f"<span class='team'>{team}</span>",
        unsafe_allow_html=True,
    )

    cols[2].markdown(
        f"**{actual_display}**"
    )

    cols[3].markdown(
        f"<span class='{css_class}'>{difference}</span>",
        unsafe_allow_html=True,
    )