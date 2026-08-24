import json
from datetime import date, timedelta
from pathlib import Path

import streamlit as st

from src.scrape import PremScraper

PREDICTIONS_DIR = Path("predictions/prem")
HISTORY_PATH = Path(".cache/prem_snapshots.json")
TEAM_NAMES = json.loads(Path("src/abbr.json").read_text())

# Prediction-accuracy color scale: green for a perfect call, yellow at the
# midpoint, red for the worst possible miss (predicted 1st, finished last,
# or vice versa, on a 20-team table).
PRED_GREEN = (0x42, 0xf5, 0x84)
PRED_YELLOW = (0xf5, 0xc5, 0x42)
PRED_RED = (0xf5, 0x42, 0x75)
MAX_ERROR = 19
SEASON_MATCHDAYS = 38

st.set_page_config(
    page_title="Premier League Predictions",
    layout="wide",
)

st.markdown(
    f"""
    <style>
        .stApp {{
            background-color: #080b14;
        }}
        header[data-testid="stHeader"] {{
            background: transparent;
        }}
        .block-container {{
            max-width: 1200px;
            padding-top: 2rem;
        }}
        .hero {{
            padding: 2.5rem;
            border-radius: 24px;
            background: linear-gradient(135deg, #37003c, #210024);
            border: 1px solid #4b1452;
            margin-bottom: 1.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
        }}
        .hero h1 {{
            font-size: 3rem;
            margin: 0;
            color: white;
        }}
        .hero p {{
            color: #c9b8cc;
            font-size: 1.1rem;
            margin-top: 0.6rem;
        }}
        .matchday-pill {{
            background: rgba({", ".join(str(c) for c in PRED_GREEN)}, 0.12);
            border: 1px solid rgba({", ".join(str(c) for c in PRED_GREEN)}, 0.35);
            color: rgb({", ".join(str(c) for c in PRED_GREEN)});
            padding: 0.5rem 1.1rem;
            border-radius: 999px;
            font-weight: 700;
            font-size: 0.9rem;
            white-space: nowrap;
        }}
        .green {{
            color: rgb({", ".join(str(c) for c in PRED_GREEN)});
        }}
        .card {{
            background: #111622;
            border: 1px solid #202737;
            border-radius: 16px;
            padding: 1.2rem;
        }}
        .small-label {{
            color: #737d90;
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            font-weight: 700;
        }}
        .big-value {{
            color: white;
            font-size: 1.8rem;
            font-weight: 800;
            margin-top: 0.2rem;
        }}
        .leader {{
            background: linear-gradient(
                90deg,
                rgba({", ".join(str(c) for c in PRED_GREEN)}, 0.10),
                #111622
            );
            border: 1px solid rgba({", ".join(str(c) for c in PRED_GREEN)}, 0.25);
        }}
        .muted {{
            color: #737d90;
        }}
        .team {{
            color: white;
            font-weight: 650;
        }}
        .move-up {{
            color: rgb({", ".join(str(c) for c in PRED_GREEN)});
            font-weight: 700;
            font-size: 0.85rem;
        }}
        .move-down {{
            color: rgb({", ".join(str(c) for c in PRED_RED)});
            font-weight: 700;
            font-size: 0.85rem;
        }}
        .move-flat {{
            color: #737d90;
            font-weight: 700;
            font-size: 0.85rem;
        }}
        hr {{
            border-color: #202737;
        }}
        table.grid-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.95rem;
        }}
        table.grid-table th {{
            text-align: center;
            color: #737d90;
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            padding: 0.6rem 0.5rem;
            border-bottom: 1px solid #202737;
        }}
        table.grid-table th:first-child {{
            text-align: left;
        }}
        table.grid-table td {{
            text-align: center;
            padding: 0.55rem 0.5rem;
            border-bottom: 1px solid #171c29;
        }}
        table.grid-table td:first-child {{
            text-align: left;
        }}
        table.grid-table tr:hover {{
            background: #0d1220;
        }}
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


@st.cache_data(ttl=3600)
def get_matchday():
    scraper = PremScraper()
    return scraper.scrape_matchday()


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


def build_team_grid(standings, predictions):
    actual_rank = {
        row["Team"]: int(row["Rk"])
        for _, row in standings.iterrows()
    }
    people = list(predictions.keys())

    grid = []
    for team, actual in sorted(actual_rank.items(), key=lambda x: x[1]):
        row = {"team": team, "actual": actual}
        for person in people:
            preds = predictions[person]
            row[person] = preds.index(team) + 1 if team in preds else None
        grid.append(row)

    return grid, people


def _load_history() -> dict:
    if not HISTORY_PATH.exists():
        return {}
    try:
        return json.loads(HISTORY_PATH.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def _save_snapshot(leaderboard: list[dict]) -> None:
    history = _load_history()
    today = date.today().isoformat()

    if today in history:
        return

    history[today] = {
        row["person"]: {"rank": i + 1, "total_error": row["total_error"]}
        for i, row in enumerate(leaderboard)
    }

    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_PATH.write_text(json.dumps(history))


def get_weekly_movement(leaderboard: list[dict]) -> dict[str, int | None]:
    """
    Compares today's leaderboard rank to the most recent snapshot that is
    at least a week old. Snapshots are written locally by this app as it's
    used, so movement stays blank until ~7 days of history accumulate.
    """
    history = _load_history()
    if not history:
        return {}

    cutoff = date.today() - timedelta(days=7)
    candidates = [d for d in history if date.fromisoformat(d) <= cutoff]
    if not candidates:
        return {}

    past = history[max(candidates)]

    movement = {}
    for i, row in enumerate(leaderboard):
        person = row["person"]
        past_rank = past.get(person, {}).get("rank")
        movement[person] = (
            past_rank - (i + 1) if past_rank is not None else None
        )

    return movement


def movement_badge(delta: int | None) -> str:
    if delta is None:
        return "<span class='move-flat'>NEW</span>"
    if delta > 0:
        return f"<span class='move-up'>▲ {delta}</span>"
    if delta < 0:
        return f"<span class='move-down'>▼ {abs(delta)}</span>"
    return "<span class='move-flat'>— steady</span>"


def team_name(abbr: str) -> str:
    return TEAM_NAMES.get(abbr, abbr)


def error_color(error: int | None) -> str:
    """
    Interpolates green -> yellow -> red based on how far off a prediction
    was, from a perfect call (error 0) to the worst possible miss
    (error MAX_ERROR).
    """
    if error is None:
        return "#737d90"

    # Yellow sits early on the scale so green falls off sharply for even
    # small misses, while the long tail out to red stays gradual.
    stops = [(0.0, PRED_GREEN), (0.25, PRED_YELLOW), (1.0, PRED_RED)]
    t = max(0.0, min(1.0, error / MAX_ERROR))

    for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
        if t0 <= t <= t1:
            local_t = (t - t0) / (t1 - t0)
            r, g, b = (
                round(c0[i] + (c1[i] - c0[i]) * local_t) for i in range(3)
            )
            return f"#{r:02x}{g:02x}{b:02x}"

    return f"#{PRED_RED[0]:02x}{PRED_RED[1]:02x}{PRED_RED[2]:02x}"


try:
    standings = get_standings()
    matchday = get_matchday()
except Exception as e:
    st.error(f"Could not retrieve standings: {e}")
    st.stop()

predictions = load_predictions()

if not predictions:
    st.error("No predictions found.")
    st.stop()

comparisons = build_comparison(standings, predictions)
leaderboard = build_leaderboard(comparisons)
weekly_movement = get_weekly_movement(leaderboard)
_save_snapshot(leaderboard)

st.markdown(
    f"""
    <div class="hero">
        <div>
            <h1>
                Premier League <span class="green">Predictions</span>
            </h1>
            <p>
                Who knows ball?
            </p>
        </div>
        <div class="matchday-pill">Matchday {matchday}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.progress(
    matchday / SEASON_MATCHDAYS,
    text=f"Matchday {matchday} of {SEASON_MATCHDAYS}",
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

tab_leaderboard, tab_grid, tab_detail = st.tabs(
    ["Leaderboard", "Head-to-head", "Predictor breakdown"]
)

# =============================================================================
# LEADERBOARD
# =============================================================================

with tab_leaderboard:
    top3 = leaderboard[:3]

    for col, row in zip(st.columns(len(top3)), top3):
        rank = leaderboard.index(row) + 1

        with col:
            with st.container(border=True):
                st.markdown(f"### #{rank}")
                st.markdown(f"**{row['person']}**")

                st.markdown(
                    f"""
                    <div class="small-label">Error</div>
                    <div class="big-value">{row['total_error']}</div>
                    """,
                    unsafe_allow_html=True,
                )

                st.markdown(
                    f"""
                    <div class="small-label">Avg error</div>
                    <div class="big-value">{row['avg_error']:.2f}</div>
                    """,
                    unsafe_allow_html=True,
                )

                st.markdown(
                    f"""
                    <div class="small-label">Exact</div>
                    <div class="big-value">{row['exact']}</div>
                    """,
                    unsafe_allow_html=True,
                )

                st.markdown(
                    f"""
                    <div class="small-label">Vs last week</div>
                    <div class="big-value">{movement_badge(weekly_movement.get(row['person']))}</div>
                    """,
                    unsafe_allow_html=True,
                )

    rest = leaderboard[3:]

    if rest:
        st.caption("The rest of the pack")

        for i, row in enumerate(rest, start=4):
            with st.container(border=True):
                cols = st.columns([0.6, 2.4, 1.2, 1.2, 1.2, 1.2])

                cols[0].markdown(f"### #{i}")
                cols[1].markdown(f"**{row['person']}**")

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

                cols[5].markdown(
                    f"""
                    <div class="small-label">Vs last week</div>
                    <div class="big-value">{movement_badge(weekly_movement.get(row['person']))}</div>
                    """,
                    unsafe_allow_html=True,
                )

# =============================================================================
# HEAD-TO-HEAD GRID
# =============================================================================

with tab_grid:
    st.caption(
        "Every team's actual position next to what each person predicted "
        "for it, colored by accuracy: green is spot on, red is way off. "
        "(+n) means the team finished n spots lower than predicted, "
        "(-n) means it finished n spots higher."
    )

    grid, people = build_team_grid(standings, predictions)

    sort_by = st.selectbox("Sort by", ["Actual", "Team"] + people)

    if sort_by == "Actual":
        grid = sorted(grid, key=lambda r: r["actual"])
    elif sort_by == "Team":
        grid = sorted(grid, key=lambda r: team_name(r["team"]))
    else:
        grid = sorted(
            grid,
            key=lambda r: (r[sort_by] is None, r[sort_by]),
        )

    header_cells = "".join(f"<th>{person}</th>" for person in people)
    rows_html = ""

    for row in grid:
        cells = f"<td class='team'>{team_name(row['team'])}</td><td>{row['actual']}</td>"

        for person in people:
            predicted = row[person]

            if predicted is None:
                cells += "<td class='muted'>—</td>"
                continue

            diff = row["actual"] - predicted
            error = abs(diff)
            color = error_color(error)
            diff_str = f"{diff:+d}" if diff != 0 else "0"

            cells += (
                f"<td style='color:{color}; font-weight:700;'>"
                f"{predicted} <span style='opacity:0.65;'>"
                f"({diff_str})</span></td>"
            )

        rows_html += f"<tr>{cells}</tr>"

    st.markdown(
        f"""
        <table class="grid-table">
            <thead>
                <tr><th>Team</th><th>Actual</th>{header_cells}</tr>
            </thead>
            <tbody>{rows_html}</tbody>
        </table>
        """,
        unsafe_allow_html=True,
    )

# =============================================================================
# PERSON DETAIL
# =============================================================================

with tab_detail:
    people_list = list(comparisons.keys())

    selected_person = st.pills(
        "Select predictor",
        people_list,
        selection_mode="single",
        default=people_list[0],
    )

    if selected_person is None:
        selected_person = people_list[0]

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
            diff_color = error_color(MAX_ERROR)

        else:
            actual_display = str(actual)
            difference = "Exact" if error == 0 else f"↕ {error}"
            diff_color = error_color(error)

        cols = st.columns([0.7, 3, 1, 1])

        cols[0].markdown(
            f"<span class='muted'>{predicted}</span>",
            unsafe_allow_html=True,
        )

        cols[1].markdown(
            f"<span class='team'>{team_name(team)}</span>",
            unsafe_allow_html=True,
        )

        cols[2].markdown(
            f"**{actual_display}**"
        )

        cols[3].markdown(
            f"<span style='color:{diff_color}; font-weight:700;'>"
            f"{difference}</span>",
            unsafe_allow_html=True,
        )
