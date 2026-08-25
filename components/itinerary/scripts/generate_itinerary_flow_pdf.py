"""Generate a PDF explaining how Tour Ceylon builds an itinerary — from sign-in to save."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

OUT = Path(__file__).resolve().parents[3] / "docs" / "itinerary" / "How_Itinerary_Is_Generated.pdf"

TEAL = colors.HexColor("#0A4A52")
INK = colors.HexColor("#1A2332")
MUTED = colors.HexColor("#5A6570")
LINE = colors.HexColor("#D0DCE0")
ROW_ALT = colors.HexColor("#F5FAFA")
HEAD_BG = colors.HexColor("#0A4A52")


def styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "T",
            parent=base["Title"],
            fontSize=20,
            textColor=TEAL,
            spaceAfter=4,
            alignment=TA_CENTER,
        ),
        "sub": ParagraphStyle(
            "S",
            parent=base["Normal"],
            fontSize=11,
            textColor=MUTED,
            alignment=TA_CENTER,
            spaceAfter=14,
        ),
        "h1": ParagraphStyle(
            "H1",
            parent=base["Heading1"],
            fontSize=13,
            textColor=TEAL,
            spaceBefore=12,
            spaceAfter=6,
        ),
        "h2": ParagraphStyle(
            "H2",
            parent=base["Heading2"],
            fontSize=11,
            textColor=INK,
            spaceBefore=8,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "B",
            parent=base["Normal"],
            fontSize=10,
            textColor=INK,
            leading=14,
            spaceAfter=6,
        ),
        "note": ParagraphStyle(
            "N",
            parent=base["Normal"],
            fontSize=9,
            textColor=MUTED,
            leading=12,
            spaceAfter=6,
        ),
        "li": ParagraphStyle(
            "LI",
            parent=base["Normal"],
            fontSize=10,
            textColor=INK,
            leading=13,
        ),
        "cell": ParagraphStyle(
            "Cell",
            parent=base["Normal"],
            fontSize=8.5,
            textColor=INK,
            leading=11.5,
        ),
        "cellh": ParagraphStyle(
            "CellH",
            parent=base["Normal"],
            fontSize=8.5,
            textColor=colors.white,
            leading=11.5,
            fontName="Helvetica-Bold",
        ),
        "callout": ParagraphStyle(
            "Callout",
            parent=base["Normal"],
            fontSize=10,
            textColor=TEAL,
            leading=14,
            spaceAfter=6,
            leftIndent=4,
        ),
    }


def table(rows, col_widths):
    t = Table(rows, colWidths=col_widths)
    cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), HEAD_BG),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    for i in range(1, len(rows)):
        if i % 2 == 1:
            cmds.append(("BACKGROUND", (0, i), (-1, i), ROW_ALT))
    t.setStyle(TableStyle(cmds))
    return t


def bullets(items, s):
    return ListFlowable(
        [ListItem(Paragraph(item, s["li"])) for item in items],
        bulletType="bullet",
        leftIndent=12,
        bulletFontSize=8,
    )


def numbered(items, s):
    return ListFlowable(
        [ListItem(Paragraph(item, s["li"])) for item in items],
        bulletType="1",
        start=1,
        leftIndent=16,
    )


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(TEAL)
    canvas.rect(0, A4[1] - 8 * mm, A4[0], 8 * mm, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(16 * mm, A4[1] - 5.5 * mm, "Tour Ceylon  |  How an itinerary is generated")
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(A4[0] - 16 * mm, 10 * mm, f"Page {doc.page}")
    canvas.setStrokeColor(LINE)
    canvas.line(16 * mm, 14 * mm, A4[0] - 16 * mm, 14 * mm)
    canvas.restoreState()


def build():
    s = styles()
    story = []

    story.append(Paragraph("Tour Ceylon", s["title"]))
    story.append(
        Paragraph(
            "How an itinerary is generated — from sign-in to the day-by-day plan",
            s["sub"],
        )
    )
    story.append(HRFlowable(width="100%", thickness=1, color=LINE, spaceAfter=10))

    story.append(
        Paragraph(
            "This document follows one traveller from the public home page through "
            "sign-in, attraction picks, budget, hotels, and the rule engine that "
            "stamps clock times. The itinerary is <b>not</b> written by ChatGPT. "
            "It is built from what the user already saved in the database.",
            s["body"],
        )
    )

    # ---------- Journey map ----------
    story.append(Paragraph("The journey at a glance", s["h1"]))
    story.append(
        Paragraph(
            "Planning is a six-step wizard. Sign-in sits in front of it. "
            "Generation happens on step 4 when the Itinerary page opens.",
            s["body"],
        )
    )
    journey = [
        [
            Paragraph("<b>Step</b>", s["cellh"]),
            Paragraph("<b>Screen</b>", s["cellh"]),
            Paragraph("<b>What the user does</b>", s["cellh"]),
            Paragraph("<b>What is saved</b>", s["cellh"]),
        ],
        [
            Paragraph("0", s["cell"]),
            Paragraph("Home / Login", s["cell"]),
            Paragraph("Opens Travel, signs in or registers", s["cell"]),
            Paragraph("JWT in the browser; user row in the database", s["cell"]),
        ],
        [
            Paragraph("1", s["cell"]),
            Paragraph("Attractions", s["cell"]),
            Paragraph("Picks 1–3 moods, trip length, and places", s["cell"]),
            Paragraph("<b>user_trip_input</b> (trip_id, days, moods, attraction IDs)", s["cell"]),
        ],
        [
            Paragraph("2", s["cell"]),
            Paragraph("Budget", s["cell"]),
            Paragraph("Sets total spend and optional custom split", s["cell"]),
            Paragraph("<b>budget_split</b> (food / stay / shopping / transport)", s["cell"]),
        ],
        [
            Paragraph("3", s["cell"]),
            Paragraph("Stay", s["cell"]),
            Paragraph("Chooses one hotel per destination city", s["cell"]),
            Paragraph("Hotels written onto the same trip", s["cell"]),
        ],
        [
            Paragraph("4", s["cell"]),
            Paragraph("Itinerary", s["cell"]),
            Paragraph("Page opens (or user clicks Generate)", s["cell"]),
            Paragraph("<b>generated_itinerary</b> JSON with days and times", s["cell"]),
        ],
        [
            Paragraph("5–6", s["cell"]),
            Paragraph("Discover / Export", s["cell"]),
            Paragraph("Guides, agencies, download PDF", s["cell"]),
            Paragraph("Same itinerary; optional saved references", s["cell"]),
        ],
    ]
    story.append(table(journey, [18 * mm, 32 * mm, 64 * mm, 64 * mm]))
    story.append(Spacer(1, 3 * mm))
    story.append(
        Paragraph(
            "Rule: unique locations on the trip cannot exceed the number of days. "
            "Generation is refused until attractions, budget split, and one hotel per city exist.",
            s["note"],
        )
    )

    # ---------- 1. Home ----------
    story.append(Paragraph("1. Home page (before login)", s["h1"]))
    story.append(
        Paragraph(
            "The Travel app home is public. Anyone can browse featured attractions. "
            "The Itinerary card and “Get in touch” send a signed-in user to "
            "<b>/attractions</b>. If they are not signed in, they go to <b>/login</b>.",
            s["body"],
        )
    )
    story.append(
        bullets(
            [
                "Home also links Wellness, SOS, and Live Data (other Tour Ceylon modules).",
                "Featured photos load from <b>GET /api/attractions</b> (no login required).",
                "Planning screens after login sit behind a protected route.",
            ],
            s,
        )
    )

    # ---------- 2. Sign in ----------
    story.append(Paragraph("2. Sign in", s["h1"]))
    story.append(
        Paragraph(
            "The login card title is “Sign in to plan your trip”. After a successful "
            "sign-in the browser is sent to <b>/attractions</b> and the wizard starts.",
            s["body"],
        )
    )
    story.append(Paragraph("Ways to get an account", s["h2"]))
    story.append(
        numbered(
            [
                "<b>Email + password Sign In</b> — <b>POST /api/auth/login</b>. "
                "Looks up the user, checks the password, returns a JWT.",
                "<b>Register</b> — <b>POST /api/auth/register</b>. Creates a new user "
                "(password at least 6 characters) and returns a JWT immediately.",
                "<b>Continue with Google</b> — Google Identity Services on the page; "
                "the ID token is sent to <b>POST /api/auth/google</b>. A travel user is "
                "created or linked by email / Google ID.",
                "<b>SOS fallback</b> — if travel login fails, the app tries Tourist SOS "
                "login, then <b>POST /api/auth/link-account</b> so one email can work in both apps.",
            ],
            s,
        )
    )
    story.append(Paragraph("What is stored in the browser", s["h2"]))
    story.append(
        bullets(
            [
                "<b>access_token</b> — JWT with identity = user id and role <b>travel_user</b>.",
                "<b>user</b> — JSON profile (email, name, picture).",
                "Every later API call sends <b>Authorization: Bearer …</b>.",
                "On load, the app checks expiry and calls <b>GET /api/auth/me</b>. "
                "A stale or invalid token is cleared and the user is sent back to login.",
            ],
            s,
        )
    )
    story.append(
        Paragraph(
            "Google-only accounts cannot use a password until they set one via link-account. "
            "Police officers use a different username login; that path is not used for itinerary planning.",
            s["note"],
        )
    )

    # ---------- 3. Protected shell ----------
    story.append(Paragraph("3. After login: the planning shell", s["h1"]))
    story.append(
        Paragraph(
            "Routes under Attractions, Budget, Stay, Itinerary, Discover, Export, History, "
            "and Profile require a valid token. Without one, the user is redirected to login. "
            "The sidebar lists the six wizard steps. Progress in the top bar is about 25% → "
            "45% → 65% → 80% → 90% → 100% as they move forward.",
            s["body"],
        )
    )
    story.append(
        bullets(
            [
                "Trip state (trip_id, moods, days, budget, hotels, itinerary) lives in "
                "browser memory (<b>TripContext</b>) for this session.",
                "The durable copy is in PostgreSQL, keyed by the logged-in user.",
                "The top-bar search jumps back to Attractions and filters the catalogue.",
            ],
            s,
        )
    )

    # ---------- 4. Attractions ----------
    story.append(Paragraph("4. Attractions — create the trip", s["h1"]))
    story.append(
        Paragraph(
            "This is the first planning screen. The catalogue loads from "
            "<b>GET /api/attractions</b>. Live Data risk badges may overlay from "
            "<b>/api/risk</b> (optional; generation does not depend on risk).",
            s["body"],
        )
    )
    story.append(Paragraph("What the user chooses", s["h2"]))
    story.append(
        numbered(
            [
                "<b>Trip length</b> — number of days (default 7).",
                "<b>Moods</b> — 1 to 3 pills: Adventure, Authentic, Curious, Excited, "
                "Explore, Happy, Healing, Peaceful, Relaxed, Spiritual. "
                "These later drive Auto start time.",
                "<b>Category filter</b> — Wild, Scenic, Pristine, Heritage, Essence, Thrills (or All).",
                "<b>Places</b> — at least one attraction. Search matches name, city, or details.",
            ],
            s,
        )
    )
    story.append(Paragraph("Hard rules before Confirm", s["h2"]))
    story.append(
        bullets(
            [
                "At least one mood and one attraction.",
                "Number of <b>distinct destination cities</b> must be between 1 and the number of days "
                "(a 7-day trip can visit at most 7 cities; several places in the same city is fine).",
            ],
            s,
        )
    )
    story.append(
        Paragraph(
            "Confirm calls <b>POST /api/trip-input</b> with days, selected_moods, and "
            "finalized_attractions (IDs in pick order). The server:",
            s["body"],
        )
    )
    story.append(
        numbered(
            [
                "Checks the user from the JWT and validates IDs exist.",
                "Merges moods from the chosen places with the pills (max 3 stored).",
                "Creates a <b>user_trip_input</b> row (status in_progress).",
                "Builds a day/city skeleton (<b>get_day_plan()</b>) and returns trip_id.",
            ],
            s,
        )
    )
    story.append(
        Paragraph(
            "The browser stores trip_id and goes to Budget. Without this save, later pages "
            "cannot allocate money or list hotels.",
            s["note"],
        )
    )

    # ---------- 5. Budget ----------
    story.append(Paragraph("5. Budget — split the spend", s["h1"]))
    story.append(
        Paragraph(
            "The user sets a total budget (default 2500, treated as USD in the UI). "
            "Default split is 25% food, 35% stay, 15% shopping, 25% transport. "
            "Turning on Manual Adjustment lets them move sliders; they must still sum to 100%. "
            "Turning it off resets to those defaults.",
            s["body"],
        )
    )
    story.append(
        Paragraph(
            "Confirm calls <b>POST /api/budget/split</b> with trip_id, budget, and "
            "optional custom percentages. The server writes <b>budget_split</b> amounts "
            "and percentages, and stores the total on the trip. Then the browser goes to Stay.",
            s["body"],
        )
    )
    story.append(
        Paragraph(
            "Accommodation search uses the stay slice of this split (per night, converted "
            "with LKR_TO_USD_RATE, default 300) to hide hotels that are over budget.",
            s["note"],
        )
    )

    # ---------- 6. Accommodation ----------
    story.append(Paragraph("6. Stay — one hotel per city", s["h1"]))
    story.append(
        Paragraph(
            "The page loads <b>GET /api/accommodation?trip_id=…&amp;room_type=…</b>. "
            "Room type is single, double (default), or family. Hotels are grouped by the "
            "destination cities already implied by the selected attractions.",
            s["body"],
        )
    )
    story.append(
        bullets(
            [
                "Budget split must already exist; otherwise the API refuses the list.",
                "The user must pick <b>one hotel for every destination</b>.",
                "If a city has no hotel in budget, they must raise the stay budget or change places.",
            ],
            s,
        )
    )
    story.append(
        Paragraph(
            "Continue calls <b>PATCH /api/trip-input/{trip_id}</b> with "
            "accommodations_by_destination. The trip now has attractions, budget, and hotels. "
            "The browser goes to Itinerary.",
            s["body"],
        )
    )

    # ---------- 7. Itinerary page ----------
    story.append(Paragraph("7. Itinerary page — when generation runs", s["h1"]))
    story.append(
        Paragraph(
            "This is the moment the day-by-day schedule is created. The page does not wait "
            "for a special “AI” product. It calls the generate API with the trip already saved.",
            s["body"],
        )
    )
    story.append(
        numbered(
            [
                "If hotels are missing, the page asks the user to go back to Stay.",
                "If a plan already exists for this trip, it loads <b>GET /api/itinerary/{trip_id}</b>.",
                "If none exists (404), it automatically calls "
                "<b>POST /api/itinerary/generate</b> with trip_id and optional day_start.",
                "The user can change start time (or Auto by mood) and click Generate again; "
                "the old JSON for that trip is deleted and replaced.",
            ],
            s,
        )
    )
    story.append(
        Paragraph(
            "The server refuses generate unless: (1) at least one attraction, "
            "(2) one hotel per destination, (3) a budget split. All of those were collected "
            "in steps 4–6 after sign-in.",
            s["note"],
        )
    )

    story.append(PageBreak())

    # ---------- Engine ----------
    story.append(Paragraph("8. What the generator does with that saved trip", s["h1"]))
    story.append(
        Paragraph(
            "Main files: <b>routes/itinerary.py</b> (API) → <b>ai_service.py</b> "
            "(times and day JSON) → <b>trip_plan_service.py</b> (city/day split and hotels). "
            "The JSON is stored in <b>generated_itinerary</b> with source “database”.",
            s["body"],
        )
    )
    story.append(
        numbered(
            [
                "Split destination cities across the trip days.",
                "Assign each selected attraction to a day.",
                "Choose the day’s start hour (user time, or Auto by mood).",
                "Stamp clock times on each stop, with lunch and evening limits.",
                "Attach the hotel already chosen for that city, then save JSON.",
            ],
            s,
        )
    )

    story.append(Paragraph("8.1 Split cities across days", s["h2"]))
    story.append(
        Paragraph(
            "Places are grouped by destination, in the <b>order the user picked them</b>. "
            "Total days are shared as evenly as possible. The trip never bounces back to a "
            "city after it has moved on.",
            s["body"],
        )
    )
    story.append(
        Paragraph(
            "Example: 7 days, Colombo → Kandy → Galle. Base days = 7 ÷ 3 = 2, remainder 1 "
            "goes to later cities → about 2 days Colombo, 2 Kandy, 3 Galle. "
            "Function: <b>get_day_plan()</b>.",
            s["body"],
        )
    )

    story.append(Paragraph("8.2 Put attractions on those days", s["h2"]))
    story.append(
        bullets(
            [
                "<b>One day in a city</b> — all of that city’s selected places go on that day.",
                "<b>Several days in a city</b> — one place per day; extras are stacked on the last day of that block.",
                "<b>Extra days with no leftover places</b> — a leisure slot: “Explore {city}” (free time, not a repeat visit).",
            ],
            s,
        )
    )
    story.append(
        Paragraph("Function: <b>attractions_grouped_by_day()</b>.", s["note"])
    )

    story.append(Paragraph("8.3 Choose the start time", s["h2"]))
    story.append(
        Paragraph(
            "The Itinerary page can send a clock time, or leave it empty for Auto.",
            s["body"],
        )
    )
    mood_rows = [
        [Paragraph("<b>Mood saved on the trip</b>", s["cellh"]), Paragraph("<b>Start hour</b>", s["cellh"])],
        [Paragraph("Spiritual", s["cell"]), Paragraph("6:30 AM", s["cell"])],
        [Paragraph("Adventure", s["cell"]), Paragraph("7:30 AM", s["cell"])],
        [Paragraph("Explore / Excited", s["cell"]), Paragraph("8:00 AM", s["cell"])],
        [Paragraph("Curious", s["cell"]), Paragraph("8:30 AM", s["cell"])],
        [Paragraph("Happy / Authentic", s["cell"]), Paragraph("9:00 AM", s["cell"])],
        [Paragraph("Healing", s["cell"]), Paragraph("9:30 AM", s["cell"])],
        [Paragraph("Peaceful", s["cell"]), Paragraph("10:00 AM", s["cell"])],
        [Paragraph("Relaxed", s["cell"]), Paragraph("10:30 AM", s["cell"])],
        [Paragraph("No moods (fallback)", s["cell"]), Paragraph("8:30 AM", s["cell"])],
    ]
    story.append(table(mood_rows, [90 * mm, 70 * mm]))
    story.append(Spacer(1, 4 * mm))
    story.append(
        bullets(
            [
                "User chose a time (for example <b>8:30 AM</b>) → that hour is used.",
                "<b>Auto (by mood)</b> or empty → average of the mood hours above. "
                "Spiritual (6:30) + Relaxed (10:30) → 8:30.",
                "The <b>first place of the day</b> can push the start later, never earlier: "
                "Wild / safari / temple earlier; beach / spa later. Start is clamped between 5:00 AM and 2:00 PM.",
            ],
            s,
        )
    )

    cat_rows = [
        [Paragraph("<b>Category or name hint</b>", s["cellh"]), Paragraph("<b>Bias</b>", s["cellh"])],
        [Paragraph("Wild", s["cell"]), Paragraph("6:30 AM", s["cell"])],
        [Paragraph("Heritage / temple / religious", s["cell"]), Paragraph("6:30–7:00 AM", s["cell"])],
        [Paragraph("Thrills / hiking", s["cell"]), Paragraph("7:00–7:30 AM", s["cell"])],
        [Paragraph("Scenic / waterfall", s["cell"]), Paragraph("8:00–8:30 AM", s["cell"])],
        [Paragraph("Essence / market", s["cell"]), Paragraph("9:00 AM", s["cell"])],
        [Paragraph("Pristine / beach", s["cell"]), Paragraph("9:30 AM", s["cell"])],
        [Paragraph("Museum / spa", s["cell"]), Paragraph("10:00–10:30 AM", s["cell"])],
    ]
    story.append(table(cat_rows, [90 * mm, 70 * mm]))
    story.append(Spacer(1, 3 * mm))
    story.append(
        Paragraph(
            "Functions: <b>_parse_day_start()</b>, <b>_mood_start_hour()</b>, "
            "<b>_category_bias()</b> in ai_service.py.",
            s["note"],
        )
    )

    story.append(Paragraph("8.4 Stamp clock times on each stop", s["h2"]))
    story.append(
        Paragraph(
            "Once the start hour is fixed, stops on that day are spaced with simple gaps. "
            "This is not driving time from a map.",
            s["body"],
        )
    )
    gap_rows = [
        [Paragraph("<b>Stops that day</b>", s["cellh"]), Paragraph("<b>Gap between stops</b>", s["cellh"])],
        [Paragraph("1 place", s["cell"]), Paragraph("Only the start time", s["cell"])],
        [Paragraph("2 places", s["cell"]), Paragraph("About 3 hours apart", s["cell"])],
        [Paragraph("3 places", s["cell"]), Paragraph("About 2.5 hours apart", s["cell"])],
        [Paragraph("4 or more", s["cell"]), Paragraph("About 2 hours apart", s["cell"])],
    ]
    story.append(table(gap_rows, [70 * mm, 90 * mm]))
    story.append(Spacer(1, 4 * mm))
    story.append(
        bullets(
            [
                "If the next slot falls in <b>12:00–1:00 PM</b>, it jumps to <b>1:00 PM</b> (lunch).",
                "Nothing is planned after about <b>8:00 PM</b> (late slots are pulled back to 7:30 PM).",
                "Example: start 8:00 AM, three places → about 8:00 AM, 10:30 AM, 1:00 PM.",
            ],
            s,
        )
    )
    story.append(Paragraph("Function: <b>_build_day_times()</b> in ai_service.py.", s["note"]))

    story.append(Paragraph("8.5 Attach hotel and save", s["h2"]))
    story.append(
        bullets(
            [
                "Each day gets the hotel already chosen for that city (<b>hotel_for_day()</b>).",
                "The builder returns one JSON object: title, summary, route (for example Kandy → Galle), "
                "highlights, days (activities + times + stay), and <b>source: database</b>.",
                "That JSON is stored in <b>generated_itinerary</b>. The Itinerary page reads it.",
            ],
            s,
        )
    )

    # ---------- After ----------
    story.append(Paragraph("9. After the plan exists", s["h1"]))
    story.append(
        bullets(
            [
                "<b>Discover</b> — businesses, agencies, and guides near the trip; user can save references.",
                "<b>Export</b> — download a trip PDF from the same JSON "
                "(<b>GET /api/itinerary/{trip_id}/pdf</b>).",
                "<b>History</b> — lists generated plans for this signed-in user "
                "(<b>GET /api/itinerary/history</b>); opening one reloads that trip on the Itinerary page.",
                "<b>Log out</b> — clears the JWT; planning routes require sign-in again.",
            ],
            s,
        )
    )

    # ---------- APIs ----------
    story.append(Paragraph("10. API chain (signed-in user)", s["h1"]))
    api_rows = [
        [
            Paragraph("<b>When</b>", s["cellh"]),
            Paragraph("<b>Method</b>", s["cellh"]),
            Paragraph("<b>Purpose</b>", s["cellh"]),
        ],
        [
            Paragraph("Sign in / register / Google", s["cell"]),
            Paragraph("POST /api/auth/login | register | google", s["cell"]),
            Paragraph("Issue travel JWT", s["cell"]),
        ],
        [
            Paragraph("Refresh session", s["cell"]),
            Paragraph("GET /api/auth/me", s["cell"]),
            Paragraph("Confirm token still valid", s["cell"]),
        ],
        [
            Paragraph("Catalogue", s["cell"]),
            Paragraph("GET /api/attractions", s["cell"]),
            Paragraph("List places (public)", s["cell"]),
        ],
        [
            Paragraph("Confirm attractions", s["cell"]),
            Paragraph("POST /api/trip-input", s["cell"]),
            Paragraph("Create trip for this user", s["cell"]),
        ],
        [
            Paragraph("Confirm budget", s["cell"]),
            Paragraph("POST /api/budget/split", s["cell"]),
            Paragraph("Save percentages and amounts", s["cell"]),
        ],
        [
            Paragraph("Open Stay", s["cell"]),
            Paragraph("GET /api/accommodation", s["cell"]),
            Paragraph("Hotels in budget per city", s["cell"]),
        ],
        [
            Paragraph("Confirm hotels", s["cell"]),
            Paragraph("PATCH /api/trip-input/{id}", s["cell"]),
            Paragraph("Attach one hotel per city", s["cell"]),
        ],
        [
            Paragraph("Open Itinerary / Generate", s["cell"]),
            Paragraph("POST /api/itinerary/generate", s["cell"]),
            Paragraph("Build and save day JSON", s["cell"]),
        ],
        [
            Paragraph("Reload plan", s["cell"]),
            Paragraph("GET /api/itinerary/{id}", s["cell"]),
            Paragraph("Read saved JSON", s["cell"]),
        ],
    ]
    story.append(table(api_rows, [48 * mm, 70 * mm, 60 * mm]))
    story.append(Spacer(1, 4 * mm))

    # ---------- Not ----------
    story.append(Paragraph("11. What this generator does not do", s["h1"]))
    story.append(
        bullets(
            [
                "It does not call OpenAI (OPENAI_API_KEY can stay empty).",
                "It does not use live maps, road times, or opening hours.",
                "It does not reorder cities geographically — it keeps pick order from Attractions.",
                "It does not invent hotels; it only attaches stays the user confirmed after sign-in.",
                "It does not run until the user is authenticated and the trip has attractions, budget, and hotels.",
            ],
            s,
        )
    )

    story.append(Spacer(1, 8 * mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=LINE, spaceAfter=6))
    story.append(
        Paragraph(
            "Tour Ceylon — sign in → pick places and moods → split budget → choose hotels → "
            "generate: city blocks → assign places → start hour from user or mood → spaced times + hotel.",
            s["note"],
        )
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title="Tour Ceylon — How an itinerary is generated (from sign-in)",
        author="Tour Ceylon",
    )
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    build()
