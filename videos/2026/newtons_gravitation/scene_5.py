from manim import *
import numpy as np

# ─────────────────────────────────────────────────────────────────────────
#  BRAND PALETTE  (carried verbatim from scene_4 / the series canvas)
# ─────────────────────────────────────────────────────────────────────────
COLOR_BG        = "#0E1117"
COLOR_GROUND    = "#8E8E93"
COLOR_WHITE     = "#E5E5EA"
COLOR_VEC_F     = "#FF3B30"   # red    — "broken" / the force we already know
COLOR_GREEN     = "#34C759"   # green  — confirmation / "this is right"
COLOR_AMBER     = "#FFCC00"   # amber  — the connector + thread motif (series)
COLOR_BLUE_BALL = "#007AFF"   # blue   — LOCKED: the big mass M (Earth)
COLOR_CORAL     = "#FF6F61"   # coral  — LOCKED (scene_4): the small mass m (apple)
COLOR_DIM       = "#3A3F47"   # ghost / cancelled stroke

# Semantic aliases (flip COLOR_m -> COLOR_AMBER to match scene_3's amber m).
COLOR_M      = COLOR_BLUE_BALL    # Earth's mass
COLOR_m      = COLOR_CORAL        # apple's mass
COLOR_THREAD = COLOR_AMBER        # the gravitational threads (connector motif)

FONT = "Segoe UI"
config.background_color = COLOR_BG
RNG = np.random.default_rng(7)    # deterministic -> stable render cache


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


def make_stone(radius=0.26):
    """Static, non-random irregular stone (frozen profile -> stable caching).
    Identical construction to scene_1/scene_3 so the callback reads instantly."""
    g = VGroup()
    shape_profile = [1.1, 0.9, 1.15, 0.85, 1.05, 0.95, 1.2, 0.82, 1.08, 0.9, 1.1]
    pts = []
    N = len(shape_profile)
    for i in range(N):
        a = TAU * i / N
        r = radius * shape_profile[i]
        pts.append(np.array([r * np.cos(a), r * np.sin(a), 0]))
    body = Polygon(*pts, color="#3A3A3C")
    body.set_fill("#8E8E93", opacity=1.0)
    body.set_stroke(color="#3A3A3C", width=1.6, opacity=0.9)
    body.set_sheen(-0.35, DR)
    g.add(body)
    spec_data = [(0.3 * radius, 1.2, 0.08 * radius),
                 (0.5 * radius, 3.5, 0.06 * radius),
                 (0.25 * radius, 5.0, 0.09 * radius)]
    for r, a, sr in spec_data:
        spec = Dot(point=np.array([r * np.cos(a), r * np.sin(a), 0]),
                   radius=sr, color="#3A3A3C")
        spec.set_fill("#3A3A3C", opacity=0.75)
        g.add(spec)
    return g


def check_mark(color=COLOR_GREEN, scale=0.5):
    """The series' satisfying tick (from scene_0)."""
    m = VMobject(stroke_color=color, stroke_width=6)
    m.set_points_as_corners([
        LEFT * 0.18 + DOWN * 0.02, DOWN * 0.20, RIGHT * 0.30 + UP * 0.26,
    ])
    return m.scale(scale)


def make_unit(color, radius=0.15):
    """A single 'unit of mass' in the particle world: soft halo + bright core.
    Same halo vocabulary as scene_1's make_particle, but tinted by identity."""
    g = VGroup()
    for r_mult, op in [(3.4, 0.06), (2.2, 0.12), (1.5, 0.22)]:
        g.add(Dot(ORIGIN, radius=radius * r_mult, color=color,
                  fill_opacity=op, stroke_width=0))
    g.add(Dot(ORIGIN, radius=radius, color=color, fill_opacity=1.0, stroke_width=0))
    g.add(Dot(ORIGIN, radius=radius * 0.42, color=COLOR_WHITE,
              fill_opacity=0.85, stroke_width=0))
    return g


def thread(p1, p2, amp=0.0, color=COLOR_THREAD, sw=2.6, op=0.95):
    """A luminous gravitational thread (glow underlay + core).
    `amp` bows the midpoint perpendicular to the span; amp=0 is dead straight.
    Bowed and straight versions share structure, so Transform interpolates the
    'pluck-and-settle' twang cleanly."""
    p1 = np.asarray(p1, float)
    p2 = np.asarray(p2, float)
    d = p2 - p1
    perp = np.array([-d[1], d[0], 0.0])
    n = np.linalg.norm(perp)
    perp = perp / n if n > 1e-6 else np.array([0.0, 1.0, 0.0])
    mid = (p1 + p2) / 2 + perp * amp

    core = VMobject(stroke_color=color, stroke_width=sw, stroke_opacity=op)
    core.set_points_smoothly([p1, mid, p2])
    glow = VMobject(stroke_color=color, stroke_width=sw * 3.4, stroke_opacity=0.10)
    glow.set_points_smoothly([p1, mid, p2])
    return VGroup(glow, core)


def frac(num, den, pad=0.22, sw=3):
    """A fraction bar laid between an already-built numerator and denominator.
    Returns a VGroup with .num/.den/.bar handles so glyphs stay addressable."""
    bar_w = max(num.width, den.width) + pad
    bar = Line(LEFT * bar_w / 2, RIGHT * bar_w / 2, stroke_width=sw, color=COLOR_WHITE)
    num.next_to(bar, UP, buff=0.10)
    den.next_to(bar, DOWN, buff=0.10)
    g = VGroup(num, bar, den)
    g.num, g.bar, g.den = num, bar, den
    return g


def col_positions(x, n, sp=1.1):
    """Vertical column of n slots at column-x, ordered TOP -> BOTTOM."""
    return [np.array([x, ((n - 1) / 2 - i) * sp, 0.0]) for i in range(n)]


# ═══════════════════════════════════════════════════════════════════════════
class Scene_5_WhyMultiply(MovingCameraScene):

    # ── locked geometry ──
    L_X      = -3.4                      # left algebra-panel anchor x
    BIG_X    =  2.2                      # right demo: heavy-stone lane
    SMALL_X  =  3.8                      # right demo: light-stone lane
    Y0       =  2.0                      # drop height (demo)
    BL       = -2.4                      # demo baseline
    REST_C   = -2.4 + 0.30               # landed centre y
    E_X      = -3.8                      # particle world: Earth column
    A_X      =  3.8                      # particle world: apple column
    SP       =  1.1                      # column / grid spacing

    def construct(self):
        self.camera.frame.save_state()
        grid = build_grid()
        grid.set_z_index(-10)
        self.add(grid)
        self.grid = grid

        self.act1_temptation()
        self.act2_break()
        self.act3_fix()
        self.act4_threads()
        self.act5_resolution()

    # ===================================================================== A1
    def act1_temptation(self):
        # ── "Toh fir add kyun nahi?" — let the wrong answer feel reasonable. ──
        M = MathTex("M", color=COLOR_M, font_size=120).move_to(LEFT * 1.7 + UP * 0.35)
        m = MathTex("m", color=COLOR_m, font_size=76).move_to(RIGHT * 1.7 + UP * 0.35)
        # Size encodes mass: a big M, a small m. Pure symbols — no bodies yet.
        self.play(FadeIn(M, shift=RIGHT * 0.3),
                  FadeIn(m, shift=LEFT * 0.3),
                  run_time=1.1, rate_func=rate_functions.ease_out_cubic)
        self.wait(0.7)

        # The "+" is written in, unhurried, like chalk on a board.
        plus = MathTex("+", color=COLOR_WHITE, font_size=84).move_to(UP * 0.35)
        self.play(FadeIn(plus, shift=DOWN * 0.35), run_time=0.6,
                  rate_func=rate_functions.ease_out_cubic)
        # Tighten M + m into one confident expression about the centre.
        self.play(M.animate.move_to(LEFT * 0.95 + UP * 0.35),
                  m.animate.move_to(RIGHT * 0.85 + UP * 0.35),
                  run_time=0.6, rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.5)

        # Units materialise — the seductive "but the units match!" beat.
        kg_M = Tex("kg", color=COLOR_GROUND, font_size=34).next_to(M, DOWN, buff=0.55).set_opacity(0.55)
        kg_m = Tex("kg", color=COLOR_GROUND, font_size=34).next_to(m, DOWN, buff=0.55).set_opacity(0.55)
        self.play(FadeIn(kg_M, shift=UP * 0.08), FadeIn(kg_m, shift=UP * 0.08),
                  run_time=0.6)

        brace = Brace(VGroup(kg_M, kg_m), DOWN, color=COLOR_GROUND).set_opacity(0.5)
        cap = Text("same units", font=FONT, slant=ITALIC, color=COLOR_GROUND,
                   font_size=24).next_to(brace, DOWN, buff=0.18)
        self.play(GrowFromCenter(brace), FadeIn(cap), run_time=0.7)

        tick = check_mark(COLOR_GREEN).next_to(VGroup(M, plus, m), RIGHT, buff=0.55)
        self.play(Create(tick), run_time=0.4, rate_func=rate_functions.ease_out_back)
        self.play(tick.animate.scale(1.18), run_time=0.5,
                  rate_func=rate_functions.there_and_back)
        self.wait(1.2)   # hold — let the viewer agree with the wrong thing

        # Clear the props but KEEP M, +, m: the sum becomes a claim about force.
        self.play(FadeOut(kg_M), FadeOut(kg_m), FadeOut(brace), FadeOut(cap),
                  FadeOut(tick), run_time=0.5)
        self._a1 = dict(M=M, plus=plus, m=m)

    # ===================================================================== A2
    def act2_break(self):
        M, plus, m = self._a1["M"], self._a1["plus"], self._a1["m"]

        # ── "Yaad karo, har cheez same rate se girti hai." ──
        # Establish the right-hand demo first: the equal-falling AXIOM.
        guide_b = DashedLine([self.BIG_X, self.Y0 + 0.4, 0], [self.BIG_X, self.BL, 0],
                             color=COLOR_WHITE, stroke_opacity=0.18, dash_length=0.12)
        guide_s = DashedLine([self.SMALL_X, self.Y0 + 0.4, 0], [self.SMALL_X, self.BL, 0],
                             color=COLOR_WHITE, stroke_opacity=0.18, dash_length=0.12)
        base = Line([self.BIG_X - 0.7, self.BL, 0], [self.SMALL_X + 0.7, self.BL, 0],
                    color=COLOR_GROUND, stroke_width=2, stroke_opacity=0.5)
        big   = make_stone(0.34).move_to([self.BIG_X, self.Y0, 0])
        small = make_stone(0.22).move_to([self.SMALL_X, self.Y0, 0])
        self.play(Create(guide_b), Create(guide_s), Create(base),
                  FadeIn(big, shift=DOWN * 0.15), FadeIn(small, shift=DOWN * 0.15),
                  run_time=0.9)

        # The amber connector — the lie-detector motif from scene_3. Flat = true.
        self._drop_together(big, small, T=1.1, tilt=False)
        flash_grp = VGroup(big, small)
        self.play(Flash([self.BIG_X, self.BL, 0], color=COLOR_GROUND,
                        line_length=0.16, num_lines=8, flash_radius=0.36),
                  Flash([self.SMALL_X, self.BL, 0], color=COLOR_GROUND,
                        line_length=0.14, num_lines=8, flash_radius=0.30),
                  run_time=0.45)
        self.wait(0.7)

        # Soft split: a faint seam, and the masses fly left to BECOME the formula.
        seam = DashedLine([0, 3.4, 0], [0, -3.4, 0], color=COLOR_WHITE,
                          stroke_opacity=0.12, dash_length=0.14)
        L1_ref = MathTex("F", "=", "M", "+", "m",
                         font_size=48).move_to(self.L_X * RIGHT + UP * 1.55)
        F1  = MathTex("F", color=COLOR_WHITE, font_size=48).move_to(L1_ref[0])
        eq1 = MathTex("=", color=COLOR_WHITE, font_size=48).move_to(L1_ref[1])
        self.play(
            Create(seam),
            big.animate.move_to([self.BIG_X, self.Y0, 0]),       # lift stones back
            small.animate.move_to([self.SMALL_X, self.Y0, 0]),
            M.animate.scale(48 / 120).move_to(L1_ref[2]),
            plus.animate.scale(48 / 84).move_to(L1_ref[3]),
            m.animate.scale(48 / 76).move_to(L1_ref[4]),
            FadeIn(F1, shift=RIGHT * 0.12), FadeIn(eq1, shift=RIGHT * 0.12),
            run_time=1.3, rate_func=rate_functions.ease_in_out_sine)
        L1 = VGroup(F1, eq1, M, plus, m)   # the additive hypothesis
        self.wait(0.4)

        # ── Derive the broken acceleration, one form morphing into the next. ──
        a_anchor = self.L_X * RIGHT + DOWN * 0.55

        # a = F / m
        formA = VGroup(
            MathTex("a", "=", color=COLOR_WHITE, font_size=46),
            frac(MathTex("F", color=COLOR_WHITE, font_size=46),
                 MathTex("m", color=COLOR_m, font_size=46)),
        ).arrange(RIGHT, buff=0.18).move_to(a_anchor)
        self.play(Write(formA), run_time=0.8)
        self.wait(0.4)

        # = (M + m) / m
        numB = VGroup(MathTex("M", color=COLOR_M, font_size=46),
                      MathTex("+", color=COLOR_WHITE, font_size=46),
                      MathTex("m", color=COLOR_m, font_size=46)).arrange(RIGHT, buff=0.10)
        formB = VGroup(
            MathTex("a", "=", color=COLOR_WHITE, font_size=46),
            frac(numB, MathTex("m", color=COLOR_m, font_size=46)),
        ).arrange(RIGHT, buff=0.18).move_to(a_anchor)
        self.play(ReplacementTransform(formA, formB), run_time=0.9)
        self.wait(0.4)

        # = M/m + 1   (built with an addressable denominator m)
        den_glyph = MathTex("m", color=COLOR_m, font_size=46)
        formC = VGroup(
            MathTex("a", "=", color=COLOR_WHITE, font_size=46),
            frac(MathTex("M", color=COLOR_M, font_size=46), den_glyph),
            MathTex("+", "1", color=COLOR_WHITE, font_size=46),
        ).arrange(RIGHT, buff=0.18).move_to(a_anchor)
        self.play(ReplacementTransform(formB, formC), run_time=0.9)
        self.wait(0.5)

        # The problem in one ring: the apple's own mass survives in the answer.
        ring = Circle(radius=0.30, color=COLOR_m, stroke_width=4).move_to(den_glyph)
        arrow = Arrow(ring.get_right(), small.get_left() + LEFT * 0.05, buff=0.12,
                      color=COLOR_m, stroke_width=3,
                      max_tip_length_to_length_ratio=0.12)
        self.play(Create(ring), run_time=0.4)
        self.play(ring.animate.scale(1.18), run_time=0.6,
                  rate_func=rate_functions.there_and_back)
        self.play(GrowArrow(arrow), small.animate.set_color(COLOR_m), run_time=0.6)
        self.wait(0.6)
        self.play(FadeOut(arrow), FadeOut(ring), run_time=0.4)

        # ── The falsification: under this rule the stones must DIVERGE. ──
        self.play(small.animate.set_color(COLOR_GROUND), run_time=0.3)  # back to stone
        self._drop_together(big, small, T=1.3, tilt=True)   # connector now tilts

        # POST: one-frame faint-red pulse behind the broken formula (sub-bass cue).
        redflash = RoundedRectangle(width=formC.width + 0.5, height=formC.height + 0.4,
                                    corner_radius=0.12, stroke_width=0,
                                    fill_color=COLOR_VEC_F, fill_opacity=0.18)
        redflash.move_to(formC).set_z_index(-1)
        self.add(redflash)
        self.play(redflash.animate.set_opacity(0.0), run_time=0.18)
        self.remove(redflash)
        self.wait(0.9)   # let the wrongness sit, unresolved

        self._a2 = dict(L1=L1, plus=plus, formC=formC, den_glyph=den_glyph,
                        big=big, small=small, seam=seam,
                        guides=VGroup(guide_b, guide_s, base), a_anchor=a_anchor)

    # ===================================================================== A3
    def act3_fix(self):
        s = self._a2
        L1, plus, formC = s["L1"], s["plus"], s["formC"]
        big, small, a_anchor = s["big"], s["small"], s["a_anchor"]

        # ── "Ab multiply karke dekho." The + becomes a · in place. ──
        dot_glyph = MathTex(r"\cdot", color=COLOR_WHITE, font_size=48).move_to(plus)
        self.play(plus.animate.scale(1.3).set_color(COLOR_GREEN), run_time=0.3)
        self.play(Transform(plus, dot_glyph), run_time=0.5,
                  rate_func=rate_functions.ease_in_out_cubic)   # + -> ·
        self.wait(0.4)

        # Re-derive with the fixed force: a = (M · m) / m, handles on both m's.
        M_num = MathTex("M", color=COLOR_M, font_size=46)
        dot_num = MathTex(r"\cdot", color=COLOR_WHITE, font_size=46)
        m_num = MathTex("m", color=COLOR_m, font_size=46)
        num = VGroup(M_num, dot_num, m_num).arrange(RIGHT, buff=0.10)
        m_den = MathTex("m", color=COLOR_m, font_size=46)
        formD = VGroup(
            MathTex("a", "=", color=COLOR_WHITE, font_size=46),
            frac(num, m_den),
        ).arrange(RIGHT, buff=0.18).move_to(a_anchor)
        self.play(ReplacementTransform(formC, formD), run_time=0.9)
        self.wait(0.4)

        # The cancellation — the quiet heart of the act.
        self.play(m_num.animate.set_color(COLOR_m).scale(1.28),
                  m_den.animate.set_color(COLOR_m).scale(1.28),
                  run_time=0.5, rate_func=rate_functions.ease_out_cubic)
        sl_n = Line(m_num.get_corner(UL) + UL * 0.04, m_num.get_corner(DR) + DR * 0.04,
                    color=COLOR_VEC_F, stroke_width=3)
        sl_d = Line(m_den.get_corner(UL) + UL * 0.04, m_den.get_corner(DR) + DR * 0.04,
                    color=COLOR_VEC_F, stroke_width=3)
        self.play(Create(sl_n), Create(sl_d), run_time=0.45)   # the teacher's pen
        self.play(VGroup(m_num, m_den, sl_n, sl_d).animate
                  .set_color(COLOR_DIM).set_opacity(0.4), run_time=0.5)
        self.wait(0.3)

        # What remains: a = M, clean white, alone.
        aM = MathTex("a", "=", "M", color=COLOR_WHITE, font_size=52).move_to(a_anchor)
        self.play(ReplacementTransform(VGroup(formD, sl_n, sl_d), aM), run_time=0.8,
                  rate_func=rate_functions.ease_in_out_cubic)
        self.play(aM.animate.scale(1.1), run_time=0.5,
                  rate_func=rate_functions.there_and_back)
        self.wait(0.5)

        # ── Confirmation: the stones fall together again. Knot untied. ──
        self._drop_together(big, small, T=1.2, tilt=False)
        pulse = check_mark(COLOR_GREEN, scale=0.6).next_to(
            VGroup(big, small), DOWN, buff=0.45)
        self.play(Create(pulse), run_time=0.4, rate_func=rate_functions.ease_out_back)
        self.wait(1.0)

        # Dissolve the algebra + lab world; keep only the grid for the threads.
        keep = self.grid
        clear = Group(*[mo for mo in self.mobjects if mo is not keep])
        self.play(FadeOut(clear, shift=DOWN * 0.2), run_time=1.0,
                  rate_func=rate_functions.ease_in_out_sine)

    # ===================================================================== A4
    def act4_threads(self):
        # ── "Dhaageon wali duniya." Multiplication, made geometric. ──
        e_pts = col_positions(self.E_X, 1, self.SP)
        a_pts = col_positions(self.A_X, 1, self.SP)
        self.e_dots = [make_unit(COLOR_M).move_to(p) for p in e_pts]
        self.a_dots = [make_unit(COLOR_m).move_to(p) for p in a_pts]

        e_lab = Text("Earth", font=FONT, color=COLOR_M, font_size=24
                     ).next_to(self.e_dots[0], DOWN, buff=0.35)
        a_lab = Text("apple", font=FONT, color=COLOR_m, font_size=24
                     ).next_to(self.a_dots[0], DOWN, buff=0.35)
        self.play(FadeIn(self.e_dots[0], scale=0.5), FadeIn(self.a_dots[0], scale=0.5),
                  FadeIn(e_lab, shift=UP * 0.1), FadeIn(a_lab, shift=UP * 0.1),
                  run_time=0.9)
        self.wait(0.4)

        # Force counter (top centre, world-space so it scales with the dolly-back).
        f_label = MathTex(r"\text{Force} =", color=COLOR_WHITE, font_size=40
                          ).move_to(UP * 3.0 + LEFT * 0.5)
        self.f_val = MathTex("1", color=COLOR_AMBER, font_size=44
                             ).next_to(f_label, RIGHT, buff=0.18)
        self.play(FadeIn(f_label), run_time=0.4)

        # The first thread — one luminous span. "Force = 1."
        self.threads = VGroup()
        self._rebuild_threads(twang=True, run_time=0.9)
        self.play(FadeIn(self.f_val, scale=0.5), run_time=0.4)
        self.wait(0.9)

        # Step 1 — double the apple (1 x 2 = 2).
        self._grow_column(self.a_dots, self.A_X, 2, COLOR_m, FadeOut(a_lab))
        self._rebuild_threads(twang=True, run_time=1.0, cam_scale=1.05)
        self._set_force("2")
        self.wait(0.6)

        # Step 2 — double the Earth (2 x 2 = 4).
        self._grow_column(self.e_dots, self.E_X, 2, COLOR_M, FadeOut(e_lab))
        self._rebuild_threads(twang=True, run_time=1.2, cam_scale=1.05)
        self._set_force("4")
        self.wait(0.6)

        # Step 3 — apple becomes 3 (2 x 3 = 6). Pause: let the viewer count.
        self._grow_column(self.a_dots, self.A_X, 3, COLOR_m)
        self._rebuild_threads(twang=True, run_time=1.5)
        self._set_force("6")
        self.wait(1.0)

        # Step 4 — Earth becomes 3 (3 x 3 = 9).
        self._grow_column(self.e_dots, self.E_X, 3, COLOR_M)
        self._rebuild_threads(twang=True, run_time=2.0, cam_scale=1.08)
        self._set_force("9")
        self.wait(1.0)

        # ── The revelation: every thread collapses to a node of a 3x3 array. ──
        # Threads were built top->bottom Earth (rows) x top->bottom apple (cols),
        # so node (i,j) maps straight onto a clean matrix. The grid IS the table.
        grid_dots = VGroup()
        transforms = []
        for i in range(3):
            for j in range(3):
                tgt = np.array([(j - 1) * self.SP, (1 - i) * self.SP, 0.0])
                node = make_unit(COLOR_AMBER, radius=0.10).move_to(tgt)
                grid_dots.add(node)
                transforms.append(ReplacementTransform(self.threads[i * 3 + j], node))
        self.play(
            LaggedStart(*transforms, lag_ratio=0.05),
            FadeOut(VGroup(*self.e_dots), shift=LEFT * 0.3),
            FadeOut(VGroup(*self.a_dots), shift=RIGHT * 0.3),
            self.camera.frame.animate.scale(0.95).move_to(ORIGIN),
            run_time=1.8, rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.6)
        self.grid_dots = grid_dots

        # Ghost multiplication table — felt, not read (left of the array).
        facts = VGroup(*[
            MathTex(f, color=COLOR_WHITE, font_size=30)
            for f in (r"1\times1=1", r"1\times2=2", r"2\times2=4",
                      r"2\times3=6", r"3\times3=9")
        ]).arrange(DOWN, buff=0.26, aligned_edge=LEFT)
        facts.to_edge(LEFT, buff=0.9).set_opacity(0.32)
        facts[-1].set_color(COLOR_AMBER)   # the count we just built
        self.play(LaggedStart(*[FadeIn(f, shift=RIGHT * 0.1) for f in facts],
                              lag_ratio=0.12), run_time=1.4)
        self.wait(0.8)

        # ── The formula crystallises from the grid: F ∝ M × m. ──
        F   = MathTex("F", color=COLOR_WHITE, font_size=60)
        prop = MathTex(r"\propto", color=COLOR_WHITE, font_size=60)
        Msym = MathTex("M", color=COLOR_M, font_size=60)
        tim = MathTex(r"\times", color=COLOR_WHITE, font_size=54)
        msym = MathTex("m", color=COLOR_m, font_size=60)
        law = VGroup(F, prop, Msym, tim, msym).arrange(RIGHT, buff=0.22)
        law.move_to(DOWN * 2.7)

        for sym in (F, prop, Msym, tim, msym):
            self.play(FadeIn(sym, shift=UP * 0.12), run_time=0.32,
                      rate_func=rate_functions.ease_out_cubic)
        # Honour the operator: a soft amber glow blooms behind the ×.
        glow = Dot(tim.get_center(), radius=0.34, color=COLOR_AMBER,
                   fill_opacity=0.0, stroke_width=0).set_z_index(-1)
        self.add(glow)
        self.play(glow.animate.set_opacity(0.5), run_time=0.4)
        self.play(glow.animate.set_opacity(0.22), run_time=0.4)
        self.wait(0.8)

        self._a4 = dict(law=law, times=tim, facts=facts, glow=glow)

    # ===================================================================== A5
    def act5_resolution(self):
        s = self._a4
        law, times = s["law"], s["times"]

        # A landing, not a launch. Fade the scaffolding; keep the glowing array.
        self.play(FadeOut(s["facts"]), FadeOut(s["glow"]), run_time=0.7)

        # Scratch-pad × matures into physics-notation ·, and the law grows.
        dot = MathTex(r"\cdot", color=COLOR_WHITE, font_size=60).move_to(times)
        self.play(Transform(times, dot), run_time=0.6,
                  rate_func=rate_functions.ease_in_out_cubic)
        self.play(law.animate.scale(1.4).move_to(UP * 0.2), run_time=1.0,
                  rate_func=rate_functions.ease_in_out_sine)
        # Settle the array gently below the law.
        self.play(self.grid_dots.animate.move_to(DOWN * 2.0).scale(0.9),
                  run_time=0.9, rate_func=rate_functions.ease_in_out_sine)
        self.wait(1.5)

        # Visual tail: the nodes drift like particles — a clean handoff to Premiere.
        drifts = []
        for node in self.grid_dots:
            v = np.array([float(RNG.uniform(-1.0, 1.0)),
                          float(RNG.uniform(-0.6, 0.6)), 0.0])
            drifts.append(node.animate.shift(v).set_opacity(0.0))
        self.play(LaggedStart(*drifts, lag_ratio=0.04),
                  run_time=2.2, rate_func=rate_functions.ease_in_sine)
        self.play(law.animate.set_opacity(0.0), self.grid.animate.set_opacity(0.0),
                  run_time=1.2)
        self.wait(0.5)

    # ═══════════════════════════════════════════════════════════ INTERNALS
    def _drop_together(self, big, small, T, tilt):
        """Run a synchronised drop with the amber connector between centres.
        tilt=False -> both share one y(t) (flat connector = equal falling).
        tilt=True  -> light accelerates harder (broken rule; connector tilts)."""
        fall = self.Y0 - self.REST_C
        a_main = 2 * fall / T ** 2
        a_heavy = a_main * 0.55 if tilt else a_main   # heavy lags under the lie

        def y_small(t):
            return max(self.Y0 - 0.5 * a_main * t * t, self.REST_C)

        def y_big(t):
            return max(self.Y0 - 0.5 * a_heavy * t * t, self.REST_C)

        t = ValueTracker(0.0)
        big.add_updater(lambda mo: mo.move_to([self.BIG_X, y_big(t.get_value()), 0]))
        small.add_updater(lambda mo: mo.move_to([self.SMALL_X, y_small(t.get_value()), 0]))
        conn = always_redraw(lambda: DashedLine(
            big.get_center(), small.get_center(),
            color=COLOR_AMBER, stroke_width=2.5, dash_length=0.12))
        self.add(conn)

        # Strobe afterimages — spacing grows with speed (the series' acceleration tell).
        stamps = VGroup()
        last = 0.0
        for tp in [0.45 * T, 0.75 * T]:
            self.play(t.animate.set_value(tp), run_time=(tp - last), rate_func=linear)
            stamps.add(
                Dot([self.BIG_X, y_big(tp), 0], radius=0.045, color=COLOR_WHITE,
                    fill_opacity=0.22, stroke_width=0),
                Dot([self.SMALL_X, y_small(tp), 0], radius=0.045, color=COLOR_WHITE,
                    fill_opacity=0.22, stroke_width=0))
            self.add(stamps)
            last = tp
        self.play(t.animate.set_value(T), run_time=(T - last), rate_func=linear)

        big.clear_updaters()
        small.clear_updaters()
        self.remove(conn)
        final = DashedLine(big.get_center(), small.get_center(),
                           color=COLOR_AMBER, stroke_width=2.5, dash_length=0.12)
        self.add(final)
        self.play(FadeOut(stamps), run_time=0.3)
        self.play(FadeOut(final), run_time=0.3)

    def _grow_column(self, dots, x, n, color, *extra_anims):
        """Animate a column of unit-dots to n slots (existing slide, new divide in)."""
        new_pts = col_positions(x, n, self.SP)
        moves = []
        for d, p in zip(dots, new_pts[:len(dots)]):
            moves.append(d.animate.move_to(p))
        born = []
        for p in new_pts[len(dots):]:
            child = make_unit(color).move_to(dots[-1].get_center()).scale(0.4)
            dots.append(child)
            self.add(child)
            born.append(child.animate.move_to(p).scale(1 / 0.4))
        self.play(*moves, *born, *[a for a in extra_anims],
                  run_time=0.9, rate_func=rate_functions.ease_out_cubic)

    def _rebuild_threads(self, twang, run_time, cam_scale=None):
        """Redraw the complete bipartite web for the current dot layout.
        Drawing every thread (not just the new ones) lets the eye re-count the
        web at each step — the count is the whole point."""
        old = self.threads
        new_bowed = VGroup()
        targets = []
        k = 0
        for e in self.e_dots:                 # rows: top -> bottom
            for a in self.a_dots:             # cols: top -> bottom
                p1, p2 = e.get_center(), a.get_center()
                amp = 0.22 * (1 if k % 2 == 0 else -1) if twang else 0.0
                new_bowed.add(thread(p1, p2, amp=amp))
                targets.append(thread(p1, p2, amp=0.0))
                k += 1

        if len(old):
            self.play(FadeOut(old), run_time=0.25)
        self.add(new_bowed)
        anims = [LaggedStart(*[Transform(new_bowed[i], targets[i])
                               for i in range(len(targets))],
                             lag_ratio=0.10)]
        if cam_scale is not None:
            anims.append(self.camera.frame.animate.scale(cam_scale))
        self.play(*anims, run_time=run_time,
                  rate_func=rate_functions.ease_out_back if twang
                  else rate_functions.ease_in_out_sine)
        self.threads = new_bowed   # now straightened; keep ordered refs

    def _set_force(self, value):
        """Pop the force counter to a new value."""
        new = MathTex(value, color=COLOR_AMBER, font_size=44).move_to(self.f_val)
        self.play(ReplacementTransform(self.f_val, new), run_time=0.4,
                  rate_func=rate_functions.ease_out_back)
        self.f_val = new
        self.play(self.f_val.animate.scale(1.18), run_time=0.3,
                  rate_func=rate_functions.there_and_back)