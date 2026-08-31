"""
The Physics Frame — Bayes / base rate.
Scene 1 (lecture cut): "You tested positive."

One continuous canvas, ~74 s.  Nothing is ever cleared: the single person we
draw in the first two seconds becomes one glyph inside a crowd of a thousand,
and every later object is derived on screen from the object before it.

See plan.md for the beat graph, the object ledger and the layout IR.

    manim -ql --disable_caching scene-1.py Scene1_YouTestedPositive
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
PANEL     = "#0A141A"   # lifted surface — the result card only
STARLIGHT = "#F7F6F1"   # the figure · facts · headline text
DUST      = "#8792A0"   # labels, metadata, structure

# ── BAYES PIGMENTS (locked for the whole video) ──────────────────────────
C_SICK    = "#FFA540"   # AMBER — has the disease, and the live question
C_FALSE   = "#35E0F2"   # CYAN  — the false alarm.  Planted here, paid off later.
C_CLEARED = "#7C98BD"   # the 999 who are fine — present, receded
C_MISSED  = "#84786B"   # the miss: dim amber, an absence
WAN       = "#A79E92"   # the colour of feeling off

MONO = "Space Mono"

TEXT_Z, ART_Z = 100, 10

config.background_color = VOID
RNG = np.random.default_rng(7)


# ═════════════════════════════════════════════════════════════════════════
#  THE PERSON GLYPH
#  Proportions measured off the reference icon (440 px canvas) and
#  normalised to body width = 1.0, origin at the glyph's bounding-box centre.
#
#      head   circle,  r = 0.307,  centre y = +0.300
#      torso  1.000 x 0.554, centre y = -0.330,
#             shoulder radius 0.270, hem radius 0.140  (the reference has
#             near-semicircular shoulders over a long flat hem; one uniform
#             corner radius reads as a pill and loses the silhouette)
#      gap between head and shoulders = 0.045
#      total height = 1.214
#
#  The torso is built as 4 straight edges + 4 single-cubic quarter arcs
#  (32 points).  That is exact to ~0.03 % of the radius and cheap enough that
#  a thousand of them render, which is the whole point of the scene.
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
    m.add_cubic_bezier_curve_to(                       # top right shoulder
        np.array([hw - rt + kt, hh, 0.0]),
        np.array([hw, hh - rt + kt, 0.0]),
        np.array([hw, hh - rt, 0.0]),
    )
    m.add_line_to(np.array([hw, -hh + rb, 0.0]))
    m.add_cubic_bezier_curve_to(                       # bottom right hem
        np.array([hw, -hh + rb - kb, 0.0]),
        np.array([hw - rb + kb, -hh, 0.0]),
        np.array([hw - rb, -hh, 0.0]),
    )
    m.add_line_to(np.array([-hw + rb, -hh, 0.0]))
    m.add_cubic_bezier_curve_to(                       # bottom left hem
        np.array([-hw + rb - kb, -hh, 0.0]),
        np.array([-hw, -hh + rb - kb, 0.0]),
        np.array([-hw, -hh + rb, 0.0]),
    )
    m.add_line_to(np.array([-hw, hh - rt, 0.0]))
    m.add_cubic_bezier_curve_to(                       # top left shoulder
        np.array([-hw, hh - rt + kt, 0.0]),
        np.array([-hw + rt - kt, hh, 0.0]),
        np.array([-hw + rt, hh, 0.0]),
    )
    return m


def person_glyph(body_width=1.0, color=STARLIGHT, opacity=1.0, detail="lo"):
    """The icon, solid-filled.  detail='hi' for the hero, 'lo' for the crowd."""
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


def shimmer_mark(height, amp, cycles=1.6, samples=22, color=DUST):
    """A vertical squiggle — the iconography of not feeling right."""
    pts = [
        np.array([amp * math.sin(TAU * cycles * k / (samples - 1)),
                  height * (k / (samples - 1) - 0.5), 0.0])
        for k in range(samples)
    ]
    m = VMobject(stroke_color=color, stroke_width=2.4)
    m.set_points_smoothly(pts)
    m.set_z_index(ART_Z)
    return m


# ═════════════════════════════════════════════════════════════════════════
#  LOCKED GEOMETRY  (Layout Motion IR, plan.md §5)
# ═════════════════════════════════════════════════════════════════════════
HERO_C   = np.array([0.00, 0.35, 0.0])     # beat 1 — dead centre
HERO_W   = 2.28                            # hero body width
HERO_L   = np.array([-3.55, 0.35, 0.0])    # beat 2 — the clinic

CARD_C   = np.array([3.75, 0.45, 0.0])

ROWS, COLS = 25, 40
GLYPH_W  = 0.110
PITCH_X  = GLYPH_W * 1.45
PITCH_Y  = GLYPH_W * P_TOTAL_H + 0.040
CROWD_C  = np.array([-3.35, 0.62, 0.0])

# The slot the figure lands in when it joins the town.  It is NEVER marked.
# Ringing "you" would tell the viewer they are not the amber one, which is a
# claim the scene has no right to make and which quietly answers the question
# the video is about to ask.  The figure lands here and then dissolves into the
# population: after that, you could be any of the thousand, including the sick
# one.  That uncertainty is the entire subject.
HERO_SLOT = 233   # row 5,  col 33
SICK_IDX  = 487   # row 12, col 7

HEADER_Y   = 3.35
CENSUS_C   = np.array([-3.35, HEADER_Y, 0.0])
BADGE_C    = np.array([3.75, HEADER_Y, 0.0])
PLATE_C    = np.array([3.75, 2.15, 0.0])
RULE1_C    = np.array([3.75, 0.35, 0.0])
RULE2_C    = np.array([3.75, -1.15, 0.0])
COL_R_W    = 6.20                          # right-column width budget
RULE_ROW_W = 4.40                          # both rule rows share this width

# Phase C — the decision.  The board recedes to 0.16 and the question moves to
# the header, so the five choices own the middle of the frame.
QUESTION_C = np.array([0.00, 2.45, 0.0])
CARD_W, CARD_H   = 5.00, 1.15
CARD_GX, CARD_GY = 0.45, 0.40
GRID_C     = np.array([0.00, -0.95, 0.0])
# The board goes to a ghost rather than out.  At 0.16 the leftover rule labels
# poked out around the card edges as legible fragments and read as clutter; at
# 0.10 the town survives as texture and the numbers survive as shape, which is
# all the recall the decision frame needs.
BOARD_DIM  = 0.10


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


def plated(mob, pad_x=0.16, pad_y=0.10):
    """Opaque backing plate — for the one label that sits over the crowd."""
    plate = RoundedRectangle(
        width=mob.width + 2 * pad_x, height=mob.height + 2 * pad_y,
        corner_radius=0.06, fill_color=VOID, fill_opacity=1.0, stroke_width=0,
    ).move_to(mob.get_center())
    plate.set_z_index(TEXT_Z)
    mob.set_z_index(TEXT_Z + 1)
    return VGroup(plate, mob).set_z_index(TEXT_Z)


# ═════════════════════════════════════════════════════════════════════════
#  SHARED BUILDERS
# ═════════════════════════════════════════════════════════════════════════
def build_result_card():
    """The doctor never appears.  The doctor speaks through instruments."""
    frame = RoundedRectangle(
        width=4.70, height=2.70, corner_radius=0.10,
        stroke_color=DUST, stroke_width=1.4,
        fill_color=PANEL, fill_opacity=1.0,
    ).set_stroke(opacity=0.45)
    cap = Text("TEST RESULT", font=MONO, font_size=18, color=DUST)
    cap.move_to(frame.get_corner(UL) + np.array([0.36, -0.42, 0.0]), aligned_edge=LEFT)
    rule = Line(
        ORIGIN, RIGHT * (frame.width - 0.72),
        stroke_color=DUST, stroke_width=1.2,
    ).set_opacity(0.28)
    rule.next_to(cap, DOWN, buff=0.24).align_to(cap, LEFT)
    card = VGroup(frame, cap, rule)
    card.set_z_index(ART_Z)
    cap.set_z_index(TEXT_Z)
    return card


def build_dashes(n=8, w=0.22, gap=0.13):
    """The empty value row — a measurement that has not resolved yet."""
    g = VGroup(*[
        Line(ORIGIN, RIGHT * w, stroke_color=DUST, stroke_width=3.0).set_opacity(0.40)
        for _ in range(n)
    ])
    g.arrange(RIGHT, buff=gap)
    g.set_z_index(TEXT_Z)
    return g


def build_positive_badge():
    """What the card demotes into once its news has landed."""
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
    """1 has it, 999 do not — the town's hidden truth, stated once."""
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


def build_accuracy_plate():
    """TEST ACCURACY / ?  — the value mobject is returned separately so the
    '?' can be swapped for '99%' in place, at the same size and baseline."""
    cap = Text("TEST ACCURACY", font=MONO, font_size=18, color=DUST)
    rule = Line(
        ORIGIN, RIGHT * (cap.width + 0.30),
        stroke_color=DUST, stroke_width=1.2,
    ).set_opacity(0.30)
    val = Text("?", font=MONO, font_size=54, color=C_SICK)
    plate = VGroup(cap, rule, val).arrange(DOWN, buff=0.18)
    plate.set_z_index(TEXT_Z)
    return plate, val


CELL, CELL_GAP = 0.066, 0.022


def build_rule(kicker, verdict, verdict_color, lit_color, odd_color, odd_index, odd_lit):
    """One 99-out-of-100 rule: the words on the left, the count on the right.

    The block is the argument.  The caption underneath only labels it.
    `odd_index` is the hundredth cell — the miss, or the false alarm."""
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

    # Both rules are laid out inside the same fixed width, words flush left and
    # block flush right, so the two 100-blocks form one column.  Arranging with
    # a buff instead would put them at different x, because "IF YOU ARE SICK"
    # and "IF YOU ARE HEALTHY" are different lengths.
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
    """One choice.  The subtitle is the intuition behind the guess — it is what
    makes a viewer commit to a number instead of waiting to be told one."""
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
    """Two columns, wrapping — so the fifth choice sits alone on the last row.
    A 2-2-1 wrap reads as a list of things to pick from; five in a rigid row
    reads as a scale, which is the thing we just decided not to draw."""
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
#  SCENE
# ═════════════════════════════════════════════════════════════════════════
class Scene1_YouTestedPositive(Scene):

    def construct(self):
        self.camera.background_color = VOID

        # ═════════════════════════════════════════════════════════════════
        #  BEAT 1 — WAKE          0.0 → 8.4 s
        # ═════════════════════════════════════════════════════════════════
        self.wait(0.8)

        # One clock drives the figure's whole life: breath, tremor, entrance,
        # pallor.  Nothing about the figure is posed — it is evaluated.
        clk = ValueTracker(0.0)
        clk.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clk)

        reveal   = ValueTracker(0.0)   # 0 asleep, 1 upright
        sickness = ValueTracker(0.0)   # 0 fine,   1 off

        def hero_pose():
            t, rv, sk = clk.get_value(), reveal.get_value(), sickness.get_value()
            breath = 0.011 * math.sin(TAU * t / 4.4)
            tremor = sk * 0.005 * math.sin(TAU * t / 0.29)
            g = person_glyph(
                HERO_W,
                color=interpolate_color(ManimColor(STARLIGHT), ManimColor(WAN), sk),
                opacity=rv,
                detail="hi",
            )
            g.stretch(1.0 + breath + tremor, 1)
            g.stretch(1.0 - 0.45 * (breath + tremor), 0)
            g.move_to(HERO_C + DOWN * (0.45 * (1.0 - rv) + 0.10 * sk))
            g.rotate(-4.2 * DEGREES * sk, about_point=g.get_bottom())
            return g

        hero = always_redraw(hero_pose)

        # a floor to rise off — it reads as "sitting up", then it goes
        ground = Line(
            HERO_C + np.array([-1.85, -1.42, 0.0]),
            HERO_C + np.array([1.85, -1.42, 0.0]),
            stroke_color=DUST, stroke_width=1.4,
        ).set_opacity(0.0).set_z_index(ART_Z)
        self.add(ground, hero)

        # ── 1a  "Picture this."
        self.add_subcaption("Picture this.", duration=2.2)
        self.play(
            ground.animate.set_opacity(0.22),
            reveal.animate.set_value(1.0),
            run_time=2.2, rate_func=ease_out_cubic,
        )

        # ── 1b  "You wake up one morning"
        self.add_subcaption("You wake up one morning", duration=1.6)
        self.play(ground.animate.set_opacity(0.0), run_time=1.0)
        self.wait(0.6)

        # ── 1c  "and you just feel... off."
        self.add_subcaption("and you just feel... off.", duration=2.6)
        self.play(sickness.animate.set_value(1.0), run_time=1.5, rate_func=ease_in_out_sine)

        head_top = HERO_C[1] + (P_HEAD_Y + P_HEAD_R) * HERO_W
        marks = VGroup(*[
            shimmer_mark(0.52, 0.085).move_to(
                np.array([HERO_C[0] + dx, head_top + 0.42 + dy, 0.0])
            )
            for dx, dy in ((-0.34, 0.0), (0.0, 0.13), (0.34, 0.02))
        ]).set_opacity(0.55)
        self.play(
            LaggedStart(
                *[
                    Succession(
                        Create(m, run_time=0.55),
                        FadeOut(m, shift=UP * 0.16, run_time=0.50),
                    )
                    for m in marks
                ],
                lag_ratio=0.30,
            ),
            run_time=1.1,
        )

        # ── 1d  breath alone
        self.wait(1.2)

        # ═════════════════════════════════════════════════════════════════
        #  BEAT 2 — THE DIAGNOSIS   8.4 → 26.2 s
        # ═════════════════════════════════════════════════════════════════
        # The figure stops being redrawn here and becomes an ordinary mobject:
        # it is about to be transformed, and an updater-driven target would
        # churn its submobjects mid-interpolation.
        hero.clear_updaters()
        clk.clear_updaters()
        self.remove(clk)

        card = build_result_card().move_to(CARD_C)
        frame = card[0]

        # ── 2a  "So, you go to the doctor"
        self.add_subcaption("So, you go to the doctor", duration=2.0)
        self.play(
            hero.animate.scale_to_fit_height(2.42).move_to(HERO_L),
            Create(frame),
            run_time=1.4, rate_func=ease_in_out_sine,
        )
        self.play(FadeIn(card[1]), Create(card[2]), run_time=0.6)

        # ── 2b  "and they run some tests"
        self.add_subcaption("and they run some tests", duration=2.6)
        dashes = build_dashes().move_to(CARD_C + DOWN * 0.42)
        self.play(FadeIn(dashes), run_time=0.4)

        scan = Line(
            frame.get_left() + RIGHT * 0.10, frame.get_right() + LEFT * 0.10,
            stroke_color=C_SICK, stroke_width=2.4,
        ).set_opacity(0.50).set_z_index(ART_Z + 5)
        scan.move_to(np.array([CARD_C[0], frame.get_top()[1] - 0.16, 0.0]))
        self.add(scan)
        self.play(
            scan.animate.move_to(np.array([CARD_C[0], frame.get_bottom()[1] + 0.16, 0.0])),
            run_time=0.85, rate_func=linear,
        )
        self.play(
            scan.animate.move_to(np.array([CARD_C[0], frame.get_top()[1] - 0.16, 0.0])),
            run_time=0.85, rate_func=linear,
        )
        self.play(FadeOut(scan), run_time=0.3)
        self.wait(0.2)

        # ── 2c  "...you've tested positive"   ← first landing
        self.add_subcaption(
            "and your doctor tells you that you've tested positive", duration=3.2
        )
        positive = Text("POSITIVE", font=MONO, font_size=46, color=C_SICK)
        positive.move_to(dashes.get_center()).set_z_index(TEXT_Z)
        underline = Line(
            ORIGIN, RIGHT * (positive.width + 0.18),
            stroke_color=C_SICK, stroke_width=2.0,
        ).set_opacity(0.55)
        underline.next_to(positive, DOWN, buff=0.22).set_z_index(TEXT_Z)

        self.play(ReplacementTransform(dashes, positive), run_time=0.9, rate_func=rush_from)
        self.play(
            Flash(positive, color=C_SICK, line_length=0.22, num_lines=16,
                  flash_radius=1.55, line_stroke_width=1.8),
            Create(underline),
            run_time=0.7,
        )
        self.wait(1.6)

        # ── 2d  "for a very rare disease."   — the card demotes
        self.add_subcaption("for a very rare disease.", duration=2.4)
        badge = build_positive_badge().move_to(BADGE_C)
        self.play(
            FadeOut(VGroup(frame, card[1], card[2], underline), scale=0.85),
            ReplacementTransform(positive, badge),
            run_time=1.1, rate_func=ease_in_out_sine,
        )
        self.wait(1.3)

        # ── 2e  "It only affects about one in a thousand people," ─────────
        #        THE BLOOM.  The one long continuous motion of the scene.
        # ═════════════════════════════════════════════════════════════════
        self.add_subcaption(
            "It only affects about one in a thousand people,", duration=3.6
        )

        glyphs = []
        for i in range(1000):
            g = person_glyph(GLYPH_W, color=C_CLEARED, detail="lo")
            g.move_to(slot(i))
            g.set_fill(C_CLEARED, float(RNG.uniform(0.58, 0.86)))
            glyphs.append(g)
        hero_g, sick_g = glyphs[HERO_SLOT], glyphs[SICK_IDX]
        hero_op = hero_g.get_fill_opacity()   # its anonymous, in-the-crowd look

        hero_pos = slot(HERO_SLOT)
        order = sorted(range(1000), key=lambda i: np.linalg.norm(slot(i) - hero_pos))
        crowd = VGroup(*[glyphs[i] for i in order])   # submobject order == bloom order

        for g in crowd:
            g.save_state()
            g.scale(0.30).set_opacity(0.0)
        self.add(crowd)

        # Two moves, not one.  If the hero is still in flight while the crowd
        # blooms, the ripple appears to start from an empty patch of screen and
        # the whole point of the shot is lost.  So: the figure arrives first,
        # holds alone for a beat as a single speck, and only then do the other
        # nine hundred and ninety-nine radiate out of it.
        self.play(
            hero.animate.scale_to_fit_width(GLYPH_W).move_to(hero_pos).set_fill(
                STARLIGHT, 1.0
            ),
            run_time=1.1, rate_func=ease_in_out_sine,
        )
        self.wait(0.3)

        # the hero and its slot are now pixel-identical; swap silently
        hero_g.restore()
        hero_g.set_fill(STARLIGHT, 1.0)       # still lit — still identifiably you
        self.remove(hero)
        self.play(
            LaggedStart(
                *[Restore(g) for g in crowd if g is not hero_g],
                lag_ratio=0.0035,
            ),
            run_time=2.6, rate_func=linear,
        )
        self.wait(0.4)

        # ── 2f  you dissolve into the population.
        #        This is the beat that used to ring and label "YOU", and it was
        #        wrong: a ring says which one you are, and therefore says you
        #        are not the amber one.  The honest gesture is the reverse —
        #        the one lit figure gives up its identity and becomes
        #        indistinguishable from the other 999.  From here on, you could
        #        be any of them.
        self.play(
            hero_g.animate.set_fill(C_CLEARED, hero_op),
            run_time=1.1, rate_func=ease_in_out_sine,
        )
        self.wait(0.3)

        # ── 2g  "but it's serious."  — one of them really has it
        self.add_subcaption("but it's serious.", duration=2.6)
        self.play(
            sick_g.animate.set_fill(C_SICK, 1.0).scale(1.40),
            run_time=0.5, rate_func=ease_out_cubic,
        )
        self.play(
            Flash(sick_g, color=C_SICK, line_length=0.11, num_lines=12,
                  flash_radius=0.26, line_stroke_width=1.5),
            run_time=0.5,
        )
        census = build_census().move_to(CENSUS_C)
        self.play(FadeIn(census), run_time=0.7)
        self.wait(0.9)

        # ═════════════════════════════════════════════════════════════════
        #  BEAT 3 — THE PANIC       26.2 → 35.0 s
        # ═════════════════════════════════════════════════════════════════
        # ── 3a  "Obviously, you panic."  Attention hands off in one play:
        #        the town dims, you brighten.
        self.add_subcaption("Obviously, you panic.", duration=2.4)
        # The eye hands off to the badge: the result is what causes the panic,
        # and the badge is also where the next twenty-five seconds live.
        context = VGroup(*[g for g in crowd if g is not sick_g])
        self.play(
            context.animate.set_opacity(0.30),
            sick_g.animate.set_fill(C_SICK, 0.75),
            run_time=0.9, rate_func=ease_in_out_sine,
        )
        self.play(
            Indicate(badge, scale_factor=1.10, color=C_SICK, rate_func=there_and_back),
            run_time=0.6,
        )
        self.wait(0.9)

        # ── 3b  "You ask the doctor, how sure are we about this?"
        #        The instrument arrives empty, on the question — not after it.
        #        Otherwise the right half of the frame is dead for three seconds.
        self.add_subcaption(
            "You ask the doctor, \"How sure are we about this?\"", duration=2.8
        )
        plate, plate_val = build_accuracy_plate()
        plate.move_to(PLATE_C)
        self.play(FadeIn(plate[0]), Create(plate[1]), run_time=0.9)
        self.wait(1.9)

        # ── 3c  "How accurate is this test?"  — the question lands in the slot
        self.add_subcaption("\"How accurate is this test?\"", duration=3.4)
        self.play(FadeIn(plate_val, shift=DOWN * 0.16), run_time=0.7)
        self.play(
            plate_val.animate.scale(1.12),
            rate_func=there_and_back, run_time=0.5,
        )
        self.wait(2.2)

        # ═════════════════════════════════════════════════════════════════
        #  BEAT 4 — THE ANSWER      35.0 → 51.0 s
        # ═════════════════════════════════════════════════════════════════
        # ── 4a  "It's 99% accurate."   ← second landing
        self.add_subcaption(
            "And they tell you: the test is excellent. It's 99% accurate.",
            duration=3.0,
        )
        ninetynine = Text("99%", font=MONO, font_size=54, color=STARLIGHT)
        ninetynine.move_to(plate_val.get_center()).set_z_index(TEXT_Z)
        self.play(FadeTransform(plate_val, ninetynine), run_time=1.0)
        plate.remove(plate_val)           # the '?' is off screen; drop the
        plate.add(ninetynine)             # reference or a later group animation
                                          # on `plate` would resurrect it
        self.play(
            ninetynine.animate.scale(1.09),
            rate_func=there_and_back, run_time=0.5,
        )
        self.wait(1.5)

        # ── 4b  "it correctly catches the disease 99 times out of 100"
        self.add_subcaption(
            "It correctly catches the disease 99 times out of 100,", duration=6.0
        )
        rule1, block1 = build_rule(
            "IF YOU ARE SICK", "-> FLAGGED", C_SICK,
            lit_color=C_SICK, odd_color=C_MISSED, odd_index=46, odd_lit=False,
        )
        rule1.move_to(RULE1_C)
        self.play(FadeIn(rule1[0], shift=RIGHT * 0.18), run_time=0.9)
        self.play(
            LaggedStart(*[FadeIn(sq) for sq in block1], lag_ratio=0.011),
            run_time=2.4,                 # first instance: the slow tier
        )
        self.play(FadeIn(rule1[1][1]), run_time=0.5)
        self.play(
            block1.animate.scale(1.05),
            rate_func=there_and_back, run_time=0.5,
        )
        self.wait(1.7)

        # ── 4c  "and if you're healthy, it correctly clears you 99 times
        #        out of 100."   The hundredth cell is cyan.  Nobody mentions it.
        self.add_subcaption(
            "and if you're healthy, it correctly clears you 99 times out of 100.",
            duration=7.0,
        )
        rule2, block2 = build_rule(
            "IF YOU ARE HEALTHY", "-> CLEARED", C_CLEARED,
            lit_color=C_CLEARED, odd_color=C_FALSE, odd_index=63, odd_lit=True,
        )
        rule2.move_to(RULE2_C)
        self.play(FadeIn(rule2[0], shift=RIGHT * 0.18), run_time=0.9)
        self.play(
            LaggedStart(*[FadeIn(sq) for sq in block2], lag_ratio=0.011),
            run_time=1.5,                 # the pattern is learned: run it faster
        )
        self.play(FadeIn(rule2[1][1]), run_time=0.5)
        self.wait(1.6)

        # ═════════════════════════════════════════════════════════════════
        #  BEAT 5 — THE QUESTION    49.1 → end
        # ═════════════════════════════════════════════════════════════════
        board = VGroup(crowd, census, badge, plate, rule1, rule2)

        # ── 5a  "So —"  the whole board recedes.  It has said what it knows;
        #        what is left is a decision, and the decision needs the frame.
        self.add_subcaption("So...", duration=2.5)
        self.play(
            board.animate.set_opacity(BOARD_DIM),
            run_time=1.2, rate_func=ease_in_out_sine,
        )
        self.wait(1.3)

        # ── 5b  the question moves to the header   ← the promise
        self.add_subcaption(
            "How likely is it that you actually have the disease?", duration=4.0
        )
        question = Text(
            "How likely is it that you actually have the disease?",
            font=MONO, font_size=32, color=STARLIGHT,
        )
        fit_width(question, 11.4)
        question.move_to(QUESTION_C).set_z_index(TEXT_Z + 20)
        # the board behind sits at 0.16, but a backstroke costs nothing and
        # guarantees the line stays clean over the dimmed town
        question.set_stroke(VOID, 6, background=True)
        self.play(Write(question), run_time=1.8)
        self.wait(2.2)

        # ── 5c  "Pause the video and pick a number,"  — the five choices
        self.add_subcaption("Pause the video and pick a number,", duration=3.4)
        cards = build_option_grid()
        self.play(
            LaggedStart(
                *[FadeIn(c, shift=UP * 0.14) for c in cards],
                lag_ratio=0.16,
            ),
            run_time=2.0,
        )
        self.wait(1.4)

        # ── 5d/5e  the scan.  One highlight visits every choice in turn, so no
        #        card is privileged and none is pre-selected.  It is also the
        #        ambient life of the longest hold in the scene: a decision
        #        frame that never moves reads as a slide, not a question.
        self.add_subcaption("don't just wait for me to solve it.", duration=3.2)
        scan = RoundedRectangle(
            width=CARD_W, height=CARD_H, corner_radius=0.12,
            stroke_color=C_SICK, stroke_width=2.4, fill_opacity=0.0,
        ).move_to(cards[0].get_center()).set_z_index(TEXT_Z + 30)
        self.play(Create(scan), run_time=0.7)
        self.wait(1.5)
        self.play(scan.animate.move_to(cards[1].get_center()), run_time=0.4)
        self.wait(0.6)

        self.add_subcaption(
            "In about two minutes I'll show you the real number, "
            "and I am almost sure that you will be surprised.",
            duration=10.5,
        )
        for k in (2, 3, 4):
            self.wait(1.1)
            self.play(scan.animate.move_to(cards[k].get_center()), run_time=0.4)
        self.wait(1.3)

        # It leaves without landing anywhere.  Resting the highlight on a card
        # would read as the answer, and the answer is two minutes away.
        self.play(FadeOut(scan), run_time=0.6)
        self.wait(2.6)

        # >>> POST: hard cut to Scene 2.  The dimmed board is still underneath —
        # crowd, the amber one, the plate and both rules — so Scene 2 can bring
        # it back up rather than rebuilding it.
