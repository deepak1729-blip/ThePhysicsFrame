from manim import *
import numpy as np

# ── BRAND PALETTE (series canvas, verbatim) ──
COLOR_BG        = "#0E1117"
COLOR_GROUND    = "#8E8E93"
COLOR_WHITE     = "#E5E5EA"
COLOR_DIM       = "#3A3F47"
COLOR_VEC_V     = "#32ADE6"   # cyan — velocity (series-locked)
COLOR_AMBER     = "#FFCC00"   # amber — the connector / handshake motif
COLOR_ORANGE    = "#FF9500"   # the struck ball + its mass m
COLOR_BLUE_BALL = "#007AFF"   # series blue

# ── new constants for the momentum scene ──
COLOR_WHITE_BALL  = COLOR_WHITE      # the cue ball
COLOR_ORANGE_BALL = COLOR_ORANGE     # the object ball
COLOR_MOMENTUM    = COLOR_BLUE_BALL  # the real thing — deep blue
COLOR_PARTIAL     = "#B5C94A"        # yellow-green: "feels right, isn't quite"
COLOR_PARTIAL_DIM = "#8A8763"        # greyed-yellow: "not wrong, just incomplete"
COLOR_XMARK       = "#FF6B3D"        # soft red-orange: "this never happens"

FONT = "Segoe UI"
config.background_color = COLOR_BG

# ── overlay assets (drop these next to the script; degrade to placeholders) ──
POOL_TABLE = "table.png"        # landscape felt
CUE_STICK  = "stick.png"         # horizontal, tip on the RIGHT (toward ball)


# ═══════════════════════════════════════════════════════════════════════════
#  HELPERS — same construction vocabulary as the rest of the series
# ═══════════════════════════════════════════════════════════════════════════
def build_grid():
    grid = VGroup()
    max_x, max_y, spacing = 12, 8, 0.5

    def fading_line(start, end, peak_op):
        segs = VGroup()
        vec = end - start
        N = 30
        for i in range(N):
            p1 = start + vec * (i / N)
            p2 = start + vec * ((i + 1) / N)
            t  = (i + 0.5) / N
            op = peak_op * 0.35 * (1 - (2 * t - 1) ** 2)
            segs.add(Line(p1, p2, stroke_opacity=op,
                          stroke_width=1, color=COLOR_WHITE))
        return segs

    for x in np.arange(-max_x, max_x + 0.1, spacing):
        peak = 0.30 * (1 - (abs(x) / max_x) ** 1.5)
        if peak > 0:
            grid.add(fading_line(UP * max_y + RIGHT * x,
                                 DOWN * max_y + RIGHT * x, peak))
    for y in np.arange(-max_y, max_y + 0.1, spacing):
        peak = 0.30 * (1 - (abs(y) / max_y) ** 1.5)
        if peak > 0:
            grid.add(fading_line(LEFT * max_x + UP * y,
                                 RIGHT * max_x + UP * y, peak))
    return grid


def make_ball(color, radius=0.30):
    """Shaded sphere (carried verbatim from the centripetal series)."""
    g = VGroup()
    sphere = Circle(radius=radius)
    sphere.set_fill(color, opacity=1.0)
    sphere.set_sheen(-0.45, DR)
    sphere.set_stroke(color=COLOR_WHITE, width=1.5, opacity=0.22)
    g.add(sphere)
    rim = Circle(radius=radius)
    rim.set_fill(opacity=0)
    rim.set_stroke(color=color, width=3, opacity=0.50)
    g.add(rim)
    spec = Ellipse(width=radius * 0.52, height=radius * 0.34)
    spec.set_fill(COLOR_WHITE, opacity=0.62)
    spec.set_stroke(width=0)
    spec.move_to(np.array([-radius * 0.28, radius * 0.30, 0]))
    spec.rotate(-20 * DEGREES)
    g.add(spec)
    return g


def safe_image(path, width, fallback_label, ratio=0.6):
    """ImageMobject with a labelled placeholder so the scene always renders
    even before the real asset is dropped next to the script (series rule)."""
    try:
        return ImageMobject(path).scale_to_fit_width(width)
    except Exception:
        box = Rectangle(width=width, height=max(width * ratio, 0.2),
                        color=COLOR_GROUND, stroke_width=1.5,
                        fill_color=COLOR_BG, fill_opacity=0.85)
        lbl = Text(fallback_label, font=FONT, font_size=18, color=COLOR_GROUND)
        lbl.scale_to_fit_width(min(width * 0.7, max(lbl.width, 0.1))).move_to(box)
        return VGroup(box, lbl)


def check_mark(color=COLOR_PARTIAL, scale=0.5):
    """The series' satisfying tick (from scene_0/5/6)."""
    m = VMobject(stroke_color=color, stroke_width=6)
    m.set_points_as_corners([
        LEFT * 0.18 + DOWN * 0.02, DOWN * 0.20, RIGHT * 0.30 + UP * 0.26,
    ])
    return m.scale(scale)


def cross_mark(color=COLOR_XMARK, scale=0.6):
    """A soft red-orange X — 'this outcome never happens'."""
    g = VGroup(
        Line(UL, DR, color=color, stroke_width=7),
        Line(UR, DL, color=color, stroke_width=7),
    ).scale(scale)
    return g


def p_arrow(tail, vec, color=COLOR_MOMENTUM, sw=6):
    """Momentum arrow — same stroke vocabulary as the series force/velocity arrows."""
    tail = np.array(tail, dtype=float)
    return Arrow(tail, tail + np.array(vec, dtype=float), buff=0, color=color,
                 stroke_width=sw, max_tip_length_to_length_ratio=0.26)


def energy_bar(value, max_value=1.0, color=COLOR_PARTIAL, width=0.55, full_h=1.7):
    """A vertical KE bar: track + proportional fill. Handles on .track/.fill."""
    track = RoundedRectangle(width=width, height=full_h, corner_radius=0.10,
                             stroke_color=COLOR_GROUND, stroke_width=1.5,
                             fill_opacity=0)
    h = max(full_h * value / max_value, 0.05)
    fill = RoundedRectangle(width=width * 0.78, height=h, corner_radius=0.08,
                            stroke_width=0, fill_color=color, fill_opacity=0.85)
    fill.move_to(track.get_bottom() + UP * h / 2)
    g = VGroup(track, fill)
    g.track, g.fill = track, fill
    return g


# ═══════════════════════════════════════════════════════════════════════════
class Scene_0_WhatStaysConstant(MovingCameraScene):

    # ── locked geometry (Act 1 / Act 2 share this line) ──
    Y0          = -0.2
    BALL_R      = 0.30
    WHITE_START = np.array([-3.4, -0.2, 0.0])
    ORANGE_REST = np.array([1.4, -0.2, 0.0])
    WHITE_STOP  = np.array([0.8, -0.2, 0.0])   # 2·radius left of the object ball
    ORANGE_END  = np.array([2.9, -0.2, 0.0])

    def construct(self):
        self.camera.background_color = COLOR_BG
        self.camera.frame.save_state()
        grid = build_grid()
        grid.set_z_index(-10)
        self.add(grid)
        self.grid = grid

        self.act1_break()
        self.act2_what_happened()
        self.act3_energy_candidate()
        self.act5_momentum()

    def _clear_to_grid(self, run_time=1.0):
        clear = Group(*[m for m in self.mobjects if m is not self.grid])
        if len(clear):
            self.play(FadeOut(clear), run_time=run_time,
                      rate_func=rate_functions.ease_in_out_sine)

    # ===================================================================== A1
    def act1_break(self):
        # ── The break. Cue ball in, object ball out; the cue ball halts. ──
        table = safe_image(POOL_TABLE, 11.0, "pool_table.png", ratio=0.52)
        table.move_to(ORIGIN).set_z_index(-5)
        self.play(FadeIn(table), run_time=0.9, rate_func=smooth)

        white  = make_ball(COLOR_WHITE_BALL,  self.BALL_R).move_to(self.WHITE_START).set_z_index(3)
        orange = make_ball(COLOR_ORANGE_BALL, self.BALL_R).move_to(self.ORANGE_REST).set_z_index(3)
        self.play(LaggedStart(FadeIn(white, scale=0.7),
                              FadeIn(orange, scale=0.7), lag_ratio=0.2),
                  run_time=0.7)

        # Cue stick parked just behind the cue ball, tip pointing right.
        cue = safe_image(CUE_STICK, 4.6, "cue_stick.png", ratio=0.10)
        cue.move_to(self.WHITE_START + LEFT * (self.BALL_R + cue.width / 2 + 0.15))
        cue.set_z_index(4)
        self.play(FadeIn(cue, shift=RIGHT * 0.2), run_time=0.5)
        self.wait(0.3)

        # The strike: a short, sharp thrust into the ball.
        self.play(cue.animate.shift(RIGHT * 0.30), run_time=0.14,
                  rate_func=rate_functions.ease_in_quad)

        # Cue ball runs at constant speed (linear — the physics demands it);
        # the stick withdraws and fades as the ball leaves.
        self.play(
            white.animate.move_to(self.WHITE_STOP),
            cue.animate.shift(LEFT * 1.3).set_opacity(0.0),
            run_time=1.3, rate_func=linear,
        )
        self.remove(cue)

        # The transfer: one clean spark; the cue ball stops dead, the other goes.
        contact = (self.WHITE_STOP + self.ORANGE_REST) / 2
        self.play(Flash(contact, color=COLOR_WHITE, line_length=0.14,
                        num_lines=10, flash_radius=0.34, line_stroke_width=2.2),
                  run_time=0.32)
        self.play(orange.animate.move_to(self.ORANGE_END),
                  run_time=1.2, rate_func=rate_functions.ease_out_sine)  # rolls to rest
        self.wait(0.6)

        self.table, self.white, self.orange = table, white, orange

    # ===================================================================== A2
    def act2_what_happened(self):
        # ── Make the familiar strange. Lean in on the gap; ask, on the viewer's
        #    behalf, the one question nobody stops to ask. ──
        white, orange = self.white, self.orange
        focus = (white.get_center() + orange.get_center()) / 2

        self.play(self.camera.frame.animate.scale(0.72).move_to(focus),
                  run_time=1.6, rate_func=rate_functions.ease_in_out_sine)  # a thoughtful lean
        self.wait(0.4)

        # The handshake line — a geometric suggestion that something crossed.
        shake = DashedLine(white.get_right(), orange.get_left(),
                           color=COLOR_AMBER, stroke_width=2.4,
                           dash_length=0.10, stroke_opacity=0.0).set_z_index(2)
        self.add(shake)
        self.play(shake.animate.set_stroke(opacity=0.55), run_time=0.5)
        # one opacity pulse
        self.play(shake.animate.set_stroke(opacity=0.95), run_time=0.40,
                  rate_func=rate_functions.there_and_back)

        # A single mote rides the line — "something passed", shown not told.
        mote = Dot(white.get_right(), radius=0.06, color=COLOR_AMBER).set_z_index(4)
        self.add(mote)
        self.play(MoveAlongPath(mote, Line(white.get_right(), orange.get_left())),
                  run_time=0.7, rate_func=rate_functions.ease_in_out_sine)
        self.play(FadeOut(mote, scale=0.5), run_time=0.3)
        self.wait(0.2)

        # The question the camera asks for us — a clean serif ?, dim, small.
        qmark = MathTex("?", color=COLOR_WHITE, font_size=46
                        ).move_to(focus + UP * 0.95).set_opacity(0.0).set_z_index(6)
        self.add(qmark)
        self.play(qmark.animate.set_opacity(0.7), run_time=0.5)
        self.wait(2.0)
        self.play(qmark.animate.set_opacity(0.0), run_time=0.6)
        self.remove(qmark)

        # Settle back to a medium shot.
        self.play(Restore(self.camera.frame),
                  run_time=1.3, rate_func=rate_functions.ease_in_out_sine)
        self.play(FadeOut(shake), run_time=0.4)
        self.wait(0.3)

    # ===================================================================== A3
    def act3_energy_candidate(self):
        # ── The tempting wrong answer. Dress it up; let the viewer nod. ──
        self.play(FadeOut(self.table), FadeOut(self.white), FadeOut(self.orange),
                  run_time=0.9, rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.2)

        line1 = Text("something must have stayed constant...", font=FONT,
                     slant=ITALIC, color=COLOR_WHITE, font_size=30)
        line1.to_edge(UP, buff=0.7).set_z_index(5)
        self.play(FadeIn(line1, shift=DOWN * 0.12), run_time=0.8)
        self.wait(0.8)

        # The candidate arrives like a thought, not a typed line.
        cand = Text("Total Energy", font=FONT, weight=BOLD,
                    color=COLOR_PARTIAL, font_size=46)
        cand.next_to(line1, DOWN, buff=0.45).set_z_index(5)
        self.play(FadeIn(cand, scale=0.7), run_time=0.8,
                  rate_func=rate_functions.ease_out_cubic)
        self.wait(0.6)

        # KE = ½mv², built term by term. m carries the moving ball's orange.
        ke = MathTex("KE", "=", r"\frac{1}{2}", "m", "v^2", font_size=52)
        ke[3].set_color(COLOR_ORANGE_BALL)
        ke.next_to(cand, DOWN, buff=0.55).set_z_index(5)
        self.play(FadeIn(ke[0], shift=RIGHT * 0.1),
                  FadeIn(ke[1], shift=RIGHT * 0.1), run_time=0.4)
        self.play(FadeIn(ke[2], shift=UP * 0.12), run_time=0.4)   # the ½ first
        self.play(FadeIn(ke[3], scale=0.6), run_time=0.4)         # m (orange)
        self.play(FadeIn(ke[4], shift=UP * 0.12), run_time=0.4)   # v²
        self.wait(0.5)

        # Two equal bars: KE before / KE after, with a quiet tick between.
        bar_b = energy_bar(1.0, color=COLOR_PARTIAL)
        bar_a = energy_bar(1.0, color=COLOR_PARTIAL)
        lab_b = Text("before", font=FONT, font_size=20, color=COLOR_GROUND)
        lab_a = Text("after",  font=FONT, font_size=20, color=COLOR_GROUND)
        bb = VGroup(bar_b, lab_b).arrange(DOWN, buff=0.18)
        ba = VGroup(bar_a, lab_a).arrange(DOWN, buff=0.18)
        pair = VGroup(bb, ba).arrange(RIGHT, buff=1.6)
        pair.next_to(ke, DOWN, buff=0.5).set_z_index(5)

        self.play(Create(bar_b.track), Create(bar_a.track),
                  FadeIn(lab_b), FadeIn(lab_a), run_time=0.5)
        self.play(GrowFromEdge(bar_b.fill, DOWN), GrowFromEdge(bar_a.fill, DOWN),
                  run_time=0.7, rate_func=rate_functions.ease_out_cubic)

        tick = check_mark(COLOR_PARTIAL).move_to(
            (bar_b.get_center() + bar_a.get_center()) / 2).set_z_index(6)
        self.play(Create(tick), run_time=0.45, rate_func=rate_functions.ease_out_back)
        self.wait(1.3)   # let the viewer agree — this agreement is the trap

        self.line1, self.cand, self.ke = line1, cand, ke
        self.real_pair, self.real_tick = pair, tick    

    # ===================================================================== A5
    def act5_momentum(self):
        # ── The promise. Show the conserved quantity geometrically, then name
        #    it — in blue, the colour of the real thing. ──
        self._clear_to_grid(run_time=1.0)
        self.wait(0.2)

        L = 1.35   # the shared momentum-arrow length

        # AFTER (top): cue ball stopped, object ball moving right.
        yA = 1.25
        wA = make_ball(COLOR_WHITE_BALL,  self.BALL_R).move_to([-2.2, yA, 0]).set_z_index(3)
        oA = make_ball(COLOR_ORANGE_BALL, self.BALL_R).move_to([2.2, yA, 0]).set_z_index(3)
        tagA = Text("after", font=FONT, font_size=20, color=COLOR_GROUND).move_to([-5.0, yA, 0])
        self.play(FadeIn(wA, scale=0.7), FadeIn(oA, scale=0.7),
                  FadeIn(tagA), run_time=0.8)
        self.wait(0.3)

        # The quantity, unnamed: an arrow for the mover, a still dot for the stopped.
        oA_arr = p_arrow(oA.get_right() + RIGHT * 0.05, RIGHT * L).set_z_index(4)
        wA_dot = Dot(wA.get_right() + RIGHT * 0.05, radius=0.07,
                     color=COLOR_MOMENTUM).set_z_index(4)
        self.play(GrowArrow(oA_arr), run_time=0.6)
        self.play(FadeIn(wA_dot, scale=0.5), run_time=0.4)
        self.wait(0.6)

        # BEFORE (bottom): cue ball moving right, object ball at rest.
        yB = -1.4
        wB = make_ball(COLOR_WHITE_BALL,  self.BALL_R).move_to([-2.2, yB, 0]).set_z_index(3)
        oB = make_ball(COLOR_ORANGE_BALL, self.BALL_R).move_to([2.2, yB, 0]).set_z_index(3)
        tagB = Text("before", font=FONT, font_size=20, color=COLOR_GROUND).move_to([-5.0, yB, 0])
        wB_arr = p_arrow(wB.get_right() + RIGHT * 0.05, RIGHT * L).set_z_index(4)
        oB_dot = Dot(oB.get_right() + RIGHT * 0.05, radius=0.07,
                     color=COLOR_MOMENTUM).set_z_index(4)
        self.play(FadeIn(wB, scale=0.7), FadeIn(oB, scale=0.7),
                  FadeIn(tagB), run_time=0.7)
        self.play(GrowArrow(wB_arr), FadeIn(oB_dot, scale=0.5), run_time=0.6)
        self.wait(0.8)

        # The reveal: the after-arrow slides over the before-arrow. Same length.
        target_start = wB_arr.get_start() + UP * 0.45
        target_end   = wB_arr.get_end()   + UP * 0.45
        self.play(oA_arr.animate.put_start_and_end_on(target_start, target_end),
                  run_time=1.2, rate_func=rate_functions.ease_in_out_cubic)
        # a faint glow as they match — symmetry felt before it's understood
        self.play(oA_arr.animate.set_stroke(width=10),
                  wB_arr.animate.set_stroke(width=10),
                  run_time=0.32, rate_func=rate_functions.there_and_back)
        self.wait(1.0)

        # Everything clears; the word lands, dressed in blue.
        stage = Group(wA, oA, tagA, oA_arr, wA_dot,
                      wB, oB, tagB, wB_arr, oB_dot)
        self.play(FadeOut(stage, shift=DOWN * 0.2), run_time=0.9,
                  rate_func=rate_functions.ease_in_out_sine)

        bloom = Dot(ORIGIN, radius=1.7, color=COLOR_MOMENTUM,
                    fill_opacity=0.0, stroke_width=0).set_z_index(-1)
        self.add(bloom)
        word = Text("MOMENTUM", font=FONT, weight=BOLD,
                    color=COLOR_MOMENTUM, font_size=78).move_to(ORIGIN).set_z_index(5)
        self.play(FadeIn(word, scale=0.85),
                  bloom.animate.set_opacity(0.10),
                  run_time=1.1, rate_func=rate_functions.ease_out_cubic)
        self.wait(3.0)   # hold the name

        # Fade to black — a chapter closing, not an ending.
        self.play(FadeOut(Group(*self.mobjects)), run_time=1.6,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.8)
