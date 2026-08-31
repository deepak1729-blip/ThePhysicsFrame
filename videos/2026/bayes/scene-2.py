"""
The Physics Frame — Bayes / base rate.
Scene 2 (lecture cut): "Count actual people."

    manim -ql --disable_caching scene-2.py Scene2_CountActualPeople

CONTINUITY
    This scene's FIRST frame reproduces scene-1.py's LAST frame exactly — the
    town at BOARD_DIM, the census and badge, the 99 % plate, both rules, the
    question, and the five choice cards.  Cut the two clips together and there
    is no seam: the cards are still on screen for the first half-second and
    then leave under the first line of narration.

    Everything above the SCENE SEAM banner is duplicated VERBATIM from
    scene-1.py and must stay byte-identical to it, including the order in which
    RNG is consumed.  That is the series convention (see shorts/2026) — these
    files are standalone, never imported, because a scene you cannot render on
    its own is a scene you cannot fix on its own.

THE ARITHMETIC IS REAL
    Nothing in this scene is hand-posed.  N_FALSE_POS is round(999 * 1%), the
    counter counts the glyphs that actually changed colour, and the eleven in
    the final row are the eleven mobjects that actually travelled there.  If a
    number is on screen, something below computed it.
"""

from manim import *
from manim.utils.rate_functions import (
    ease_out_cubic,
    ease_in_out_sine,
    there_and_back,
    rush_from,
    linear,
)
import numpy as np
import math


# ═════════════════════════════════════════════════════════════════════════
#  OBSERVATORY BASE  (series design system — do not reassign)
# ═════════════════════════════════════════════════════════════════════════
VOID      = "#000C10"   # background
PANEL     = "#0A141A"   # lifted surface
STARLIGHT = "#F7F6F1"   # the figure · facts · headline text
DUST      = "#8792A0"   # labels, metadata, structure

# ── BAYES PIGMENTS (locked for the whole video) ──────────────────────────
C_SICK    = "#FFA540"   # AMBER — has the disease
C_FALSE   = "#35E0F2"   # CYAN  — the false alarm.  Planted in scene 1, paid here.
C_CLEARED = "#7C98BD"   # the 999 who are fine — present, receded
C_MISSED  = "#84786B"   # the miss: dim amber, an absence
WAN       = "#A79E92"   # the colour of feeling off

MONO = "Space Mono"

TEXT_Z, ART_Z = 100, 10

config.background_color = VOID
RNG = np.random.default_rng(7)


# ═════════════════════════════════════════════════════════════════════════
#  THE PERSON GLYPH   (verbatim from scene-1.py)
# ═════════════════════════════════════════════════════════════════════════
P_HEAD_R  = 0.307
P_HEAD_Y  = 0.300
P_BODY_H  = 0.554
P_BODY_RT = 0.270          # shoulder radius
P_BODY_RB = 0.140          # hem radius
P_BODY_Y  = -0.330
P_TOTAL_H = 1.214

_K = 0.5522847498307936   # circle-to-cubic magic constant


def _torso_path(w, h, rt, rb):
    """Closed rounded rectangle centred on the origin, with independent top and
    bottom corner radii.  8 Bezier segments: 4 edges, 4 single-cubic quarters."""
    hw, hh = w / 2.0, h / 2.0
    kt, kb = _K * rt, _K * rb
    m = VMobject()
    m.start_new_path(np.array([-hw + rt, hh, 0.0]))
    m.add_line_to(np.array([hw - rt, hh, 0.0]))
    m.add_cubic_bezier_curve_to(
        np.array([hw - rt + kt, hh, 0.0]),
        np.array([hw, hh - rt + kt, 0.0]),
        np.array([hw, hh - rt, 0.0]),
    )
    m.add_line_to(np.array([hw, -hh + rb, 0.0]))
    m.add_cubic_bezier_curve_to(
        np.array([hw, -hh + rb - kb, 0.0]),
        np.array([hw - rb + kb, -hh, 0.0]),
        np.array([hw - rb, -hh, 0.0]),
    )
    m.add_line_to(np.array([-hw + rb, -hh, 0.0]))
    m.add_cubic_bezier_curve_to(
        np.array([-hw + rb - kb, -hh, 0.0]),
        np.array([-hw, -hh + rb - kb, 0.0]),
        np.array([-hw, -hh + rb, 0.0]),
    )
    m.add_line_to(np.array([-hw, hh - rt, 0.0]))
    m.add_cubic_bezier_curve_to(
        np.array([-hw, hh - rt + kt, 0.0]),
        np.array([-hw + rt - kt, hh, 0.0]),
        np.array([-hw + rt, hh, 0.0]),
    )
    return m


def person_glyph(body_width=1.0, color=STARLIGHT, opacity=1.0, detail="lo"):
    """The icon, solid-filled.  detail='hi' for a hero, 'lo' for the crowd."""
    w = body_width
    head = Circle(
        radius=P_HEAD_R * w,
        num_components=17 if detail == "hi" else 5,
    ).move_to(np.array([0.0, P_HEAD_Y * w, 0.0]))
    torso = _torso_path(w, P_BODY_H * w, P_BODY_RT * w, P_BODY_RB * w)
    torso.move_to(np.array([0.0, P_BODY_Y * w, 0.0]))
    g = VGroup(head, torso)
    g.set_fill(color, opacity).set_stroke(width=0)
    g.set_z_index(ART_Z)
    return g


# ═════════════════════════════════════════════════════════════════════════
#  LOCKED GEOMETRY   (verbatim from scene-1.py — the inherited frame)
# ═════════════════════════════════════════════════════════════════════════
ROWS, COLS = 25, 40
GLYPH_W  = 0.110
PITCH_X  = GLYPH_W * 1.45
PITCH_Y  = GLYPH_W * P_TOTAL_H + 0.040
CROWD_C  = np.array([-3.35, 0.62, 0.0])

HERO_SLOT = 233   # never marked — see scene-1.py for why
SICK_IDX  = 487   # row 12, col 7

HEADER_Y   = 3.35
CENSUS_C   = np.array([-3.35, HEADER_Y, 0.0])
BADGE_C    = np.array([3.75, HEADER_Y, 0.0])
PLATE_C    = np.array([3.75, 2.15, 0.0])
RULE1_C    = np.array([3.75, 0.35, 0.0])
RULE2_C    = np.array([3.75, -1.15, 0.0])
COL_R_W    = 6.20
RULE_ROW_W = 4.40

QUESTION_C = np.array([0.00, 2.45, 0.0])
CARD_W, CARD_H   = 5.00, 1.15
CARD_GX, CARD_GY = 0.45, 0.40
GRID_C     = np.array([0.00, -0.95, 0.0])
BOARD_DIM  = 0.10

CELL, CELL_GAP = 0.066, 0.022


def slot(index):
    """World position of crowd member `index`, row-major from the top-left."""
    r, c = divmod(index, COLS)
    return CROWD_C + np.array([
        (c - (COLS - 1) / 2.0) * PITCH_X,
        -(r - (ROWS - 1) / 2.0) * PITCH_Y,
        0.0,
    ])


def fit_width(mob, max_w):
    if mob.width > max_w:
        mob.scale_to_fit_width(max_w)
    return mob


# ═════════════════════════════════════════════════════════════════════════
#  INHERITED BUILDERS   (verbatim from scene-1.py)
# ═════════════════════════════════════════════════════════════════════════
def build_positive_badge():
    cap = Text("TEST RESULT", font=MONO, font_size=18, color=DUST)
    box = RoundedRectangle(
        width=2.30, height=0.62, corner_radius=0.06,
        stroke_color=C_SICK, stroke_width=1.3,
        fill_color=C_SICK, fill_opacity=0.07,
    )
    val = Text("POSITIVE", font=MONO, font_size=22, color=C_SICK).move_to(box.get_center())
    badge = VGroup(cap, VGroup(box, val)).arrange(RIGHT, buff=0.30)
    badge.set_z_index(TEXT_Z)
    return badge


def build_census():
    a = VGroup(
        Text("1", font=MONO, font_size=27, color=C_SICK),
        Text("HAS IT", font=MONO, font_size=18, color=DUST),
    ).arrange(RIGHT, buff=0.17, aligned_edge=DOWN)
    sep = Text("/", font=MONO, font_size=22, color=DUST).set_opacity(0.35)
    b = VGroup(
        Text("999", font=MONO, font_size=27, color=C_CLEARED),
        Text("DON'T", font=MONO, font_size=18, color=DUST),
    ).arrange(RIGHT, buff=0.17, aligned_edge=DOWN)
    g = VGroup(a, sep, b).arrange(RIGHT, buff=0.42, aligned_edge=DOWN)
    g.set_z_index(TEXT_Z)
    return g


def build_accuracy_plate(value="99%", value_color=STARLIGHT):
    cap = Text("TEST ACCURACY", font=MONO, font_size=18, color=DUST)
    rule = Line(
        ORIGIN, RIGHT * (cap.width + 0.30),
        stroke_color=DUST, stroke_width=1.2,
    ).set_opacity(0.30)
    val = Text(value, font=MONO, font_size=54, color=value_color)
    plate = VGroup(cap, rule, val).arrange(DOWN, buff=0.18)
    plate.set_z_index(TEXT_Z)
    return plate, val


def build_rule(kicker, verdict, verdict_color, lit_color, odd_color, odd_index, odd_lit):
    """One 99-out-of-100 rule: the words on the left, the count on the right."""
    words = VGroup(
        Text(kicker, font=MONO, font_size=18, color=DUST),
        Text(verdict, font=MONO, font_size=24, color=verdict_color),
    ).arrange(DOWN, aligned_edge=LEFT, buff=0.17)

    block = VGroup()
    for i in range(100):
        r, c = divmod(i, 10)
        odd = i == odd_index
        sq = Square(
            side_length=CELL,
            stroke_width=1.0,
            stroke_color=odd_color if odd else lit_color,
            fill_color=odd_color if odd else lit_color,
            fill_opacity=(1.0 if odd_lit else 0.0) if odd else 0.85,
        )
        if odd and not odd_lit:
            sq.set_stroke(opacity=0.75)
        sq.move_to(np.array([c * (CELL + CELL_GAP), -r * (CELL + CELL_GAP), 0.0]))
        block.add(sq)
    block.move_to(ORIGIN)

    cap = Text("99 of 100", font=MONO, font_size=17, color=DUST)
    right = VGroup(block, cap).arrange(DOWN, buff=0.20)

    words.move_to(LEFT * RULE_ROW_W / 2, aligned_edge=LEFT)
    right.move_to(RIGHT * RULE_ROW_W / 2, aligned_edge=RIGHT)
    row = VGroup(words, right)
    fit_width(row, COL_R_W)
    row.set_z_index(TEXT_Z)
    return row, block


OPTIONS = [
    ("Under 5%",   "probably fine"),
    ("Around 10%", "it is rare, after all"),
    ("Around 50%", "a coin flip"),
    ("Around 90%", "probably sick"),
    ("Around 99%", "as accurate as the test"),
]


def build_option_card(headline, subtitle):
    box = RoundedRectangle(
        width=CARD_W, height=CARD_H, corner_radius=0.12,
        stroke_color=DUST, stroke_width=1.3,
        fill_color=PANEL, fill_opacity=1.0,
    ).set_stroke(opacity=0.32)
    head = Text(headline, font=MONO, font_size=28, color=STARLIGHT)
    sub = Text(subtitle, font=MONO, font_size=17, color=DUST)
    text = VGroup(head, sub).arrange(DOWN, buff=0.13)
    fit_width(text, CARD_W - 0.60)
    text.move_to(box.get_center())
    card = VGroup(box, text)
    card.set_z_index(TEXT_Z + 10)
    return card


def build_option_grid():
    dx = (CARD_W + CARD_GX) / 2.0
    dy = CARD_H + CARD_GY
    cards = VGroup()
    for k, (headline, subtitle) in enumerate(OPTIONS):
        r, c = divmod(k, 2)
        card = build_option_card(headline, subtitle)
        card.move_to(GRID_C + np.array([-dx + c * 2 * dx, dy - r * dy, 0.0]))
        cards.add(card)
    return cards


# ═════════════════════════════════════════════════════════════════════════
# ── SCENE SEAM ───────────────────────────────────────────────────────────
#  Everything below is new to scene 2.
# ═════════════════════════════════════════════════════════════════════════

# ═════════════════════════════════════════════════════════════════════════
#  THE COUNT
#  Every number that reaches the screen comes from here.  The scene performs
#  an expected-value count, not a random draw: with a 1 % false-positive rate
#  a random sample of 999 would land somewhere near ten and the narration
#  would be wrong about half the time.  round(9.99) = 10 is the honest,
#  reproducible figure, and "about ten people" is exactly how the script says
#  it.  The one sick person is caught with probability 0.99, which rounds to
#  the one flag the scene draws.
# ═════════════════════════════════════════════════════════════════════════
N_TOTAL   = 1000
N_SICK    = 1
N_HEALTHY = N_TOTAL - N_SICK                       # 999
SENSITIVITY = 0.99                                 # catches the sick
SPECIFICITY = 0.99                                 # clears the healthy

N_TRUE_POS  = int(round(N_SICK * SENSITIVITY))            # 1
N_FALSE_POS = int(round(N_HEALTHY * (1.0 - SPECIFICITY))) # 10
N_POSITIVE  = N_TRUE_POS + N_FALSE_POS                    # 11
FALSE_PCT   = int(round((1.0 - SPECIFICITY) * 100))       # 1

assert (N_TRUE_POS, N_FALSE_POS, N_POSITIVE) == (1, 10, 11)


def pick_false_positives(n=N_FALSE_POS, seed=32, min_sep=1.05, min_from_sick=1.30):
    """Which healthy people the test wrongly flags.

    Rejection-sampled with a minimum separation so no two land adjacent and
    none lands next to the genuinely sick one.  A clustered draw would read as
    a defective batch — as if the machine failed in one corner of town — and
    the whole point is the opposite: these are ordinary people scattered
    through an ordinary population, and the test is working as specified.

    Seed 32 puts them on rows 4 to 24 across 39 of the 40 columns, with no
    empty band wider than four rows.  The asserts below hold the guarantee, so
    a future edit to the grid cannot silently break the picture.
    """
    rng = np.random.default_rng(seed)
    pool = [i for i in range(N_TOTAL) if i != SICK_IDX]
    chosen = []
    for _ in range(40000):
        if len(chosen) == n:
            break
        cand = int(rng.choice(pool))
        p = slot(cand)
        if np.linalg.norm(p - slot(SICK_IDX)) < min_from_sick:
            continue
        if any(np.linalg.norm(p - slot(c)) < min_sep for c in chosen):
            continue
        chosen.append(cand)
    if len(chosen) != n:
        raise RuntimeError("could not place the false positives with this spacing")
    chosen.sort()
    rows = [i // COLS for i in chosen]
    assert max(rows) - min(rows) >= 19, "false positives clustered vertically"
    assert max(b - a for a, b in zip(rows, rows[1:])) <= 5, "empty band too wide"
    return chosen


FALSE_POS_IDX = pick_false_positives()


# ═════════════════════════════════════════════════════════════════════════
#  SCENE 2 GEOMETRY
# ═════════════════════════════════════════════════════════════════════════
# The tray — the running tally of everyone the test has flagged.  Fixed width,
# filled left to right, so nothing already in it ever shifts when someone new
# arrives.  Its empty right-hand half is an open loop: the count is not done.
TRAY_C      = np.array([-0.30, -2.80, 0.0])
TRAY_W      = 5.10
TRAY_H      = 1.00
TRAY_TITLE_Y = -2.05
TRAY_X0     = -2.50          # centre of the first occupant
TRAY_PITCH  = 0.44
TRAY_GW     = 0.26           # glyph width inside the tray

ARITH_C = np.array([4.30, -2.60, 0.0])   # 1% of 999 = <counter>

# Phase C — the payoff.  The eleven promote out of the tray to the middle of
# the frame at more than five times their size in the town.
ROW_C     = np.array([0.00, 0.45, 0.0])
ROW_GW    = 0.58
ROW_PITCH = 0.92
BADGE_DOWN_C = np.array([0.00, 2.45, 0.0])

# The payoff needs a clean plate.  0.10 was a fine ghost in scene 1, where
# nothing bright sat on top of it; here the labels, the braces and the sum all
# cross it, and legible ghost text behind legible real text reads as a printing
# fault.  0.05 keeps the town as a trace of where these eleven came from and
# lets everything else disappear.
PAYOFF_DIM = 0.05


def tray_slot(k):
    return TRAY_C + np.array([TRAY_X0 - TRAY_C[0] + k * TRAY_PITCH, 0.0, 0.0])


def row_slot(k):
    return ROW_C + np.array([(k - (N_POSITIVE - 1) / 2.0) * ROW_PITCH, 0.0, 0.0])


def build_tray():
    box = RoundedRectangle(
        width=TRAY_W, height=TRAY_H, corner_radius=0.10,
        stroke_color=DUST, stroke_width=1.2, fill_opacity=0.0,
    ).set_stroke(opacity=0.26).move_to(TRAY_C)
    title = Text("TESTED POSITIVE", font=MONO, font_size=18, color=DUST)
    title.move_to(np.array([TRAY_C[0] - 0.55, TRAY_TITLE_Y, 0.0]))
    # The running tally.  edge_to_fix=RIGHT because it grows from one digit to
    # two: anchored on its right edge it stays put over the end of the tray
    # instead of shuffling sideways when it reaches ten.
    count = DecimalNumber(
        0, num_decimal_places=0, font_size=30, color=STARLIGHT, edge_to_fix=RIGHT,
    )
    count.move_to(np.array([TRAY_C[0] + TRAY_W / 2 - 0.20, TRAY_TITLE_Y, 0.0]))
    box.set_z_index(ART_Z + 2)
    title.set_z_index(TEXT_Z)
    count.set_z_index(TEXT_Z)
    return box, title, count


def build_sum_line():
    """1 + 10 = 11, coloured to match the figures it counts.  The equation is
    the picture: amber is the one who is sick, cyan are the ones who are not."""
    parts = VGroup(
        Text(str(N_TRUE_POS), font=MONO, font_size=46, color=C_SICK),
        Text("+", font=MONO, font_size=34, color=DUST),
        Text(str(N_FALSE_POS), font=MONO, font_size=46, color=C_FALSE),
        Text("=", font=MONO, font_size=34, color=DUST),
        Text(str(N_POSITIVE), font=MONO, font_size=54, color=STARLIGHT),
    ).arrange(RIGHT, buff=0.30, aligned_edge=DOWN)
    parts.set_z_index(TEXT_Z + 20)
    return parts


def tick_label(text, color, size=19):
    t = Text(text, font=MONO, font_size=size, color=color)
    t.set_stroke(VOID, 5, background=True)
    t.set_z_index(TEXT_Z + 20)
    return t


# ═════════════════════════════════════════════════════════════════════════
#  DIMMING WITHOUT DESTROYING THE DESIGN
#
#  VMobject.set_opacity() is destructive: it overwrites every part's own
#  opacity with one number.  The badge's box is a 7 % amber wash behind solid
#  text, and rule 1's hundredth cell is a deliberately EMPTY outline standing
#  for the miss.  Dim that group to 0.10 and back to 1.0 with set_opacity and
#  the wash comes back as a solid amber slab that swallows the word POSITIVE,
#  and the empty cell fills in — the picture quietly stops being true.
#
#  So a Layer remembers what each part was designed to be and scales it.
#  `at(f)` means "every part at f times its intended opacity", which is the
#  thing that was actually wanted everywhere set_opacity was reached for.
# ═════════════════════════════════════════════════════════════════════════
class Layer:
    def __init__(self, *mobs):
        self.group = VGroup(*mobs)
        self.design = [
            (m, m.get_fill_opacity(), m.get_stroke_opacity())
            for m in self.group.family_members_with_points()
        ]

    def at(self, factor):
        """Animation: every part back to `factor` x its designed opacity."""
        return AnimationGroup(*[
            m.animate.set_fill(opacity=f * factor).set_stroke(opacity=s * factor)
            for m, f, s in self.design
        ])

    def set(self, factor):
        for m, f, s in self.design:
            m.set_fill(opacity=f * factor)
            m.set_stroke(opacity=s * factor)


def dim_live(mobs, factor):
    """One-way proportional dim from whatever is on screen right now.

    Used where the group has been deliberately restyled since it was built —
    the flipped rule block, for instance — and a Layer would helpfully restore
    it to a state the scene has already argued its way out of."""
    return AnimationGroup(*[
        m.animate
         .set_fill(opacity=m.get_fill_opacity() * factor)
         .set_stroke(opacity=m.get_stroke_opacity() * factor)
        for m in VGroup(*mobs).family_members_with_points()
    ])


# ═════════════════════════════════════════════════════════════════════════
#  SCENE
# ═════════════════════════════════════════════════════════════════════════
class Scene2_CountActualPeople(Scene):

    # ─────────────────────────────────────────────────────────────────────
    #  NARRATION-LOCKED TIMING
    #  The script is the clock.  `beat()` opens a line and records how long it
    #  takes to say; `rest()` pads whatever is left after the animations have
    #  run.  Hand-tuned trailing waits drift — the first cut of this scene came
    #  out 63 s against 80 s of narration, which would have left the voice
    #  track hanging off the end.  This way a beat cannot be shorter than its
    #  own sentence, and re-timing a line means editing one number.
    # ─────────────────────────────────────────────────────────────────────
    def beat(self, text, seconds):
        self.add_subcaption(text, duration=seconds)
        self._t0 = self.renderer.time
        self._len = seconds

    def rest(self, tail=0.0):
        """Pad out to the declared narration length, plus any breath after."""
        pad = self._len + tail - (self.renderer.time - self._t0)
        if pad > 0.04:
            self.wait(pad)

    def construct(self):
        self.camera.background_color = VOID

        # ═════════════════════════════════════════════════════════════════
        #  SEAM — rebuild scene 1's closing frame, exactly
        # ═════════════════════════════════════════════════════════════════
        # RNG must be consumed in scene 1's order or the town is a different
        # town.  This loop is the first and only consumer, as it is there.
        glyphs = []
        for i in range(N_TOTAL):
            g = person_glyph(GLYPH_W, color=C_CLEARED, detail="lo")
            g.move_to(slot(i))
            g.set_fill(C_CLEARED, float(RNG.uniform(0.58, 0.86)))
            glyphs.append(g)

        sick_g = glyphs[SICK_IDX]
        sick_g.set_fill(C_SICK, 1.0).scale(1.40)      # as scene 1 left it
        false_g = [glyphs[i] for i in FALSE_POS_IDX]

        hero_pos = slot(HERO_SLOT)
        order = sorted(range(N_TOTAL), key=lambda i: np.linalg.norm(slot(i) - hero_pos))
        crowd = VGroup(*[glyphs[i] for i in order])

        census = build_census().move_to(CENSUS_C)
        badge = build_positive_badge().move_to(BADGE_C)
        plate, plate_val = build_accuracy_plate()
        plate.move_to(PLATE_C)
        rule1, block1 = build_rule(
            "IF YOU ARE SICK", "-> FLAGGED", C_SICK,
            lit_color=C_SICK, odd_color=C_MISSED, odd_index=46, odd_lit=False,
        )
        rule1.move_to(RULE1_C)
        rule2, block2 = build_rule(
            "IF YOU ARE HEALTHY", "-> CLEARED", C_CLEARED,
            lit_color=C_CLEARED, odd_color=C_FALSE, odd_index=63, odd_lit=True,
        )
        rule2.move_to(RULE2_C)

        # Snapshot the designed opacities BEFORE scene 1's flat dim is applied,
        # so bringing the board back restores the design rather than a flat 1.0.
        L_census = Layer(census)
        L_badge = Layer(badge)
        L_plate = Layer(plate)
        L_rule1 = Layer(rule1)
        L_rule2 = Layer(rule2)

        board = VGroup(crowd, census, badge, plate, rule1, rule2)
        board.set_opacity(BOARD_DIM)     # exactly how scene 1 left it

        question = Text(
            "How likely is it that you actually have the disease?",
            font=MONO, font_size=32, color=STARLIGHT,
        )
        fit_width(question, 11.4)
        question.move_to(QUESTION_C).set_z_index(TEXT_Z + 20)
        question.set_stroke(VOID, 6, background=True)

        cards = build_option_grid()

        self.add(board, question, cards)
        self.wait(0.5)          # the cut lands here; nothing has moved yet

        # ═════════════════════════════════════════════════════════════════
        #  BEAT A — THE BOARD COMES BACK
        # ═════════════════════════════════════════════════════════════════
        # ── A1  The decision layer leaves; the evidence layer returns.  A2's
        #        line ("the only trick to this") is gone from the script, so
        #        the instrument restore it used to carry is folded in here — the
        #        crowd comes up and the panels come back in one exchange.
        self.beat("Okay, Now we are just going to count actual people.", 3.0)
        self.play(
            LaggedStart(
                *[FadeOut(c, shift=DOWN * 0.16) for c in cards],
                lag_ratio=0.08,
            ),
            FadeOut(question, shift=UP * 0.20),
            run_time=1.1,
        )
        self.play(
            AnimationGroup(*[
                g.animate.set_fill(opacity=float(op))
                for g, op in zip(crowd, self._crowd_opacities(crowd))
            ]),
            LaggedStart(
                L_census.at(1.0), L_badge.at(1.0), L_plate.at(1.0),
                L_rule1.at(1.0), L_rule2.at(1.0),
                lag_ratio=0.28,
            ),
            run_time=1.9, rate_func=ease_in_out_sine,
        )
        sick_g.set_fill(C_SICK, 1.0)
        self.rest(tail=0.4)          # paragraph break

        # ── A3  The scan is the same instrument that read your result in
        #        scene 1 — same colour, same speed — only now it reads a town.
        #        This is the scene's one long continuous motion.
        self.beat("let's run that exact same test on all the thousand people.", 4.0)
        block_top = crowd.get_top()[1] + 0.16
        block_bot = crowd.get_bottom()[1] - 0.16
        scan = Line(
            np.array([crowd.get_left()[0] - 0.10, block_top, 0.0]),
            np.array([crowd.get_right()[0] + 0.10, block_top, 0.0]),
            stroke_color=C_SICK, stroke_width=2.4,
        ).set_opacity(0.55).set_z_index(ART_Z + 6)
        self.add(scan)
        self.play(
            scan.animate.move_to(np.array([scan.get_center()[0], block_bot, 0.0])),
            run_time=2.6, rate_func=linear,
        )
        self.play(FadeOut(scan), run_time=0.35)
        self.rest(tail=0.4)          # paragraph break

        # ═════════════════════════════════════════════════════════════════
        #  BEAT B — THE ONE WHO IS ACTUALLY SICK
        # ═════════════════════════════════════════════════════════════════
        town = VGroup(*[g for g in crowd if g is not sick_g])

        # ── B1  the base rate, recalled from the header
        self.beat("Since the disease affects one in a thousand,", 3.0)
        self.play(
            town.animate.set_opacity(0.22),
            L_plate.at(0.35), L_rule2.at(0.35),
            run_time=0.9, rate_func=ease_in_out_sine,
        )
        self.play(
            Indicate(census[0], scale_factor=1.16, color=C_SICK,
                     rate_func=there_and_back),
            run_time=0.8,
        )
        self.rest()

        # ── B2  the amber one lifts clear of the grid.  Lifting beats a ring
        #        or a caption: it makes an individual out of a pixel without
        #        claiming anything at all about the other 999.
        self.beat("we start with our one genuinely sick person.", 3.0)
        lift_pos = slot(SICK_IDX) + np.array([0.0, 0.62, 0.0])
        self.play(
            sick_g.animate.scale_to_fit_width(0.34).move_to(lift_pos),
            run_time=1.0, rate_func=ease_out_cubic,
        )
        self.play(
            Flash(sick_g, color=C_SICK, line_length=0.16, num_lines=14,
                  flash_radius=0.42, line_stroke_width=1.6),
            run_time=0.5,
        )
        self.rest()

        # ── B3  the mechanism fires and the tally opens.  B4's line is gone
        #        from the script, so rule 1's focus-handoff (its recede to 0.45)
        #        is folded onto the end of this beat instead of getting its own.
        self.beat(
            "The test is 99% accurate, so it easily catches them. "
            "They get flagged.",
            5.4,
        )
        self.play(L_rule1.at(1.0), run_time=0.4)
        self.play(block1.animate.scale(1.06), rate_func=there_and_back, run_time=0.5)

        tray_box, tray_title, tray_count = build_tray()
        self.play(Create(tray_box), FadeIn(tray_title), FadeIn(tray_count), run_time=0.7)
        self.play(
            sick_g.animate.scale_to_fit_width(TRAY_GW).move_to(tray_slot(0)),
            ChangeDecimalToValue(tray_count, N_TRUE_POS),
            run_time=1.0, rate_func=ease_in_out_sine,
        )
        self.play(
            Indicate(tray_count, scale_factor=1.16, color=STARLIGHT,
                     rate_func=there_and_back),
            L_rule1.at(0.45),
            run_time=0.8,
        )
        self.rest(tail=0.4)          # paragraph break

        # ═════════════════════════════════════════════════════════════════
        #  BEAT C — THE FLIP
        # ═════════════════════════════════════════════════════════════════
        # ── C1  attention goes back to the 999.  The town comes up as a wave
        #        rather than a switch, so the sentence has motion under it.
        self.beat(
            "But now, look at the other nine hundred ninety-nine "
            "- the perfectly healthy people.",
            5.0,
        )
        town_rows = [
            VGroup(*[glyphs[r * COLS + c] for c in range(COLS)
                     if glyphs[r * COLS + c] is not sick_g])
            for r in range(ROWS)
        ]
        self.play(
            LaggedStart(
                *[row.animate.set_opacity(0.72) for row in town_rows],
                lag_ratio=0.04,
            ),
            L_rule2.at(1.0),
            run_time=1.9,
        )
        self.play(
            Indicate(census[2], scale_factor=1.14, color=C_CLEARED,
                     rate_func=there_and_back),
            run_time=0.7,
        )
        self.rest()

        # ── C2  the reassuring reading of the block: 99 cells lit
        self.beat("The test correctly clears 99 out of every 100 of them.", 4.0)
        cleared_cells = VGroup(*[sq for i, sq in enumerate(block2) if i != 63])
        self.play(
            LaggedStart(
                *[sq.animate.set_fill(C_CLEARED, 1.0) for sq in cleared_cells],
                lag_ratio=0.010,
            ),
            run_time=1.6,
        )
        self.rest()

        # ── C3  THE HINGE OF THE WHOLE VIDEO.
        #        The same hundred cells, reinterpreted.  Nothing is added and
        #        nothing is taken away: the 99 recede and the 1 that was always
        #        sitting there takes the frame.  "Flip the phrasing", literally.
        #        The script dropped "incredibly" — subtitle follows it exactly.
        self.beat(
            "That sounds reassuring, until you flip the phrasing.",
            3.0,
        )
        self.wait(1.0)                      # the breath before the reveal

        false_cell = block2[63]
        verdict_old = rule2[0][1]
        cap_old = rule2[1][1]
        verdict_new = Text("-> FLAGGED", font=MONO, font_size=24, color=C_FALSE)
        verdict_new.move_to(verdict_old, aligned_edge=LEFT)
        cap_new = Text(f"{FALSE_PCT} of 100", font=MONO, font_size=17, color=C_FALSE)
        cap_new.move_to(cap_old)

        self.play(
            cleared_cells.animate.set_fill(C_CLEARED, 0.12).set_stroke(opacity=0.12),
            false_cell.animate.set_fill(C_FALSE, 1.0).scale(1.9),
            ReplacementTransform(verdict_old, verdict_new),
            ReplacementTransform(cap_old, cap_new),
            run_time=1.2, rate_func=ease_in_out_sine,
        )
        # keep the group honest: what it holds must be what is on screen, or a
        # later group-wide opacity change resurrects the old text
        rule2[0].remove(verdict_old); rule2[0].add(verdict_new)
        rule2[1].remove(cap_old);     rule2[1].add(cap_new)
        self.rest()

        # ── C4  the sentence has two clauses, so the block gets two gestures:
        #        the 99 answer to "right 99 times", the 1 to "wrong one time".
        self.beat(
            "If it is right 99 times, it is wrong one time out of a hundred.",
            5.0,
        )
        self.play(
            cleared_cells.animate.set_fill(C_CLEARED, 0.40),
            run_time=0.6, rate_func=there_and_back,
        )
        self.wait(1.1)
        self.play(
            Flash(false_cell, color=C_FALSE, line_length=0.16, num_lines=12,
                  flash_radius=0.34, line_stroke_width=1.6),
            false_cell.animate.scale(1.15),
            run_time=0.6,
        )
        self.play(false_cell.animate.scale(1 / 1.15), run_time=0.35)

        # The sum arrives with nothing in it, while the line that motivates it
        # is still being spoken.  Same move as scene 1's accuracy plate: put
        # the instrument on screen empty, then let the next beat fill it.
        self.wait(0.5)
        arith_lhs = Text(
            f"{FALSE_PCT}% of {N_HEALTHY}", font=MONO, font_size=20, color=DUST
        )
        arith_eq = Text("=", font=MONO, font_size=20, color=DUST).set_opacity(0.6)
        counter = DecimalNumber(
            0, num_decimal_places=0, font_size=34, color=C_FALSE, edge_to_fix=LEFT,
        )
        counter.set_value(N_FALSE_POS)          # lay out at the widest value
        arith = VGroup(arith_lhs, arith_eq, counter).arrange(RIGHT, buff=0.22)
        arith.move_to(ARITH_C).set_z_index(TEXT_Z)
        counter.set_value(0)
        self.play(FadeIn(arith), run_time=0.6)
        self.rest(tail=0.4)          # paragraph break

        # ═════════════════════════════════════════════════════════════════
        #  BEAT D — TEN REAL PEOPLE
        # ═════════════════════════════════════════════════════════════════
        # ── D1  One play per person, each ignition carrying its own tick of
        #        the counter: the state change and its cause in the same
        #        breath.  They land scattered on purpose — a cluster would read
        #        as a broken machine instead of a working one.
        self.beat(
            f"And {FALSE_PCT}% of {N_HEALTHY} healthy people is about ten people.",
            4.0,
        )
        self.wait(0.4)
        for k, g in enumerate(false_g, start=1):
            self.play(
                g.animate.set_fill(C_FALSE, 1.0).scale(1.40),
                ChangeDecimalToValue(counter, k),
                run_time=0.34 if k <= 3 else 0.22,   # the pattern is learned
            )
        self.rest()

        # ── D2  ten real people, all at once
        self.beat(
            "Ten completely healthy people just got told they tested positive.",
            3.7,
        )
        self.play(
            LaggedStart(
                *[Flash(g, color=C_FALSE, line_length=0.10, num_lines=10,
                        flash_radius=0.24, line_stroke_width=1.3)
                  for g in false_g],
                lag_ratio=0.05,
            ),
            run_time=1.1,
        )
        self.wait(0.5)
        self.play(
            Indicate(counter, scale_factor=1.20, color=C_FALSE,
                     rate_func=there_and_back),
            run_time=0.7,
        )
        self.rest(tail=0.4)          # paragraph break

        # ═════════════════════════════════════════════════════════════════
        #  BEAT E — EVERYONE HOLDING A POSITIVE REPORT
        # ═════════════════════════════════════════════════════════════════
        # ── E1  They leave the town, and the town really does lose them:
        #        these are the same eleven mobjects throughout, so the holes
        #        left in the grid are real and the row is not a re-drawing.
        self.beat(
            "So, let's look at everyone who is holding a positive report "
            "right now.",
            4.5,
        )
        self.play(
            LaggedStart(*[
                g.animate.scale_to_fit_width(TRAY_GW).move_to(tray_slot(k))
                for k, g in enumerate(false_g, start=N_TRUE_POS)
            ], lag_ratio=0.09),
            ChangeDecimalToValue(tray_count, N_POSITIVE),
            run_time=2.2, rate_func=ease_in_out_sine,
        )
        # "...right now" — the tray count is the answer to the sentence, so it
        # gets the punctuation.  Keeps the 5.4 s narration hold alive.
        self.wait(1.0)
        self.play(
            Indicate(tray_count, scale_factor=1.18, color=STARLIGHT,
                     rate_func=there_and_back),
            run_time=0.7,
        )
        self.rest()

        # ── E2  the promotion: out of the tally and into the frame
        self.beat("Who is in that group?", 1.5)
        positives = [sick_g] + list(false_g)
        rest_of_board = [
            census, badge, plate, rule1, rule2, arith, tray_box, tray_title, tray_count
        ]
        self.play(
            town.animate.set_opacity(PAYOFF_DIM),
            # dim_live scales what is ON SCREEN, and most of this column is at
            # full strength right now — so the factor IS the target, not a
            # ratio against BOARD_DIM.
            dim_live(rest_of_board, PAYOFF_DIM),
            LaggedStart(*[
                g.animate.scale_to_fit_width(ROW_GW).move_to(row_slot(k))
                for k, g in enumerate(positives)
            ], lag_ratio=0.05),
            run_time=1.8, rate_func=ease_in_out_sine,
        )
        self.rest()

        # ── E3  who they are
        self.beat(
            "One person who is actually sick, and ten people who aren't.", 4.0
        )
        brace_sick = Brace(sick_g, DOWN, buff=0.22, color=C_SICK).set_opacity(0.75)
        lab_sick = tick_label(f"{N_TRUE_POS} ACTUALLY SICK", C_SICK)
        lab_sick.next_to(brace_sick, DOWN, buff=0.16)

        well_group = VGroup(*false_g)
        brace_well = Brace(well_group, DOWN, buff=0.22, color=C_FALSE).set_opacity(0.75)
        lab_well = tick_label(f"{N_FALSE_POS} PERFECTLY HEALTHY", C_FALSE)
        lab_well.next_to(brace_well, DOWN, buff=0.16)

        self.play(GrowFromCenter(brace_sick), FadeIn(lab_sick), run_time=0.8)
        self.wait(0.5)
        self.play(GrowFromCenter(brace_well), FadeIn(lab_well), run_time=0.8)
        self.rest()

        # ── E4  the sum, assembled out of the two labels that earned it
        self.beat("That is eleven in total.", 1.5)
        summ = build_sum_line()
        summ.move_to(np.array([0.0, -2.55, 0.0]))
        self.play(
            TransformFromCopy(lab_sick, summ[0]),
            TransformFromCopy(lab_well, summ[2]),
            FadeIn(summ[1]),
            run_time=0.9,
        )
        self.play(FadeIn(summ[3]), FadeIn(summ[4], shift=RIGHT * 0.12), run_time=0.5)
        self.play(summ[4].animate.scale(1.10), rate_func=there_and_back, run_time=0.45)
        self.rest()

        # ── E5  Your result comes down off the shelf and turns out to belong
        #        to all eleven.  It is the same badge object from scene 1, so
        #        the callback is literal rather than a lookalike.
        self.beat(
            "And every single one of them heard exactly the same words as you did.",
            3.8,
        )
        row_group = VGroup(*positives)
        span = Brace(row_group, UP, buff=0.26, color=DUST).set_opacity(0.45)
        # L_badge.at() and badge.animate both target the same mobject family, and
        # two animations on one mobject in a single play do not compose — one is
        # silently dropped, which is how the badge arrived here still a ghost.
        # Restore first, then move.
        self.play(L_badge.at(1.0), run_time=0.4)
        self.play(
            badge.animate.scale(1.22).move_to(BADGE_DOWN_C),
            run_time=1.0, rate_func=ease_in_out_sine,
        )

        self.play(GrowFromCenter(span), run_time=0.7)
        self.wait(0.6)
        self.play(
            LaggedStart(*[
                Flash(g, color=C_SICK if g is sick_g else C_FALSE,
                      line_length=0.18, num_lines=12, flash_radius=0.52,
                      line_stroke_width=1.5)
                for g in positives
            ], lag_ratio=0.07),
            run_time=1.3,
        )
        self.rest()

        # ── E6  the hold.  Eleven people, one of them sick, all of them told
        #        the same thing.  Scene 3 asks which one you are.
        self.wait(1.8)

        # >>> POST: hard cut to Scene 3.  The row of eleven, the descended
        # badge and both braces survive the cut.

    # ─────────────────────────────────────────────────────────────────────
    @staticmethod
    def _crowd_opacities(crowd):
        """Scene 1 flattened every glyph to BOARD_DIM for its closing frame.
        Bringing the town back needs the per-person variation again, or a
        thousand identical figures read as printed wallpaper rather than a
        crowd.  Drawn from a private generator so the shared RNG stream, which
        scene 1 also consumes, is left exactly where it was."""
        rng = np.random.default_rng(7)
        return [float(rng.uniform(0.58, 0.86)) for _ in range(len(crowd))]
