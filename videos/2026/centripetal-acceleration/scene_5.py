from manim import *
import numpy as np
import math

# ─────────────────────────────────────────────
#  BRAND PALETTE  (consistent with the series)
# ─────────────────────────────────────────────
COLOR_BG        = "#0E1117"
COLOR_GROUND    = "#8E8E93"
COLOR_GREY_BALL = "#E5E5EA"
COLOR_BLUE_BALL = "#007AFF"
COLOR_VEC_F     = "#FF3B30"   # red — force / acceleration / "the quantity"
COLOR_VEC_V     = "#32ADE6"   # cyan — the hypothetical / ghost timeline
COLOR_GREEN     = "#34C759"   # right angles
COLOR_AMBER     = "#FFCC00"   # yellow — AB·measured length (v·t)
COLOR_PINK      = "#FF2D55"
COLOR_PURPLE    = "#AF52DE"
COLOR_ORANGE    = "#FF9500"   # the doomed cancellation pair
COLOR_WHITE     = "#E5E5EA"
COLOR_CYAN      = "#32ADE6"
COLOR_INDIGO    = "#5856D6"   # NEW slot — AD = 2r, a structural constant


# ═══════════════════════════════════════════════════════════════════
#  HELPERS  (carried over verbatim from the rest of the series)
# ═══════════════════════════════════════════════════════════════════
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


def pill_bg(text_mob, buff=0.18, fill=COLOR_BG, fill_opacity=0.82,
            stroke=COLOR_GROUND, stroke_w=1.0, stroke_op=0.45):
    h = text_mob.height + buff * 1.6
    w = text_mob.width + buff * 2.4
    bg = RoundedRectangle(
        corner_radius=min(h * 0.5, 0.22),
        height=h, width=w,
        stroke_color=stroke, stroke_width=stroke_w, stroke_opacity=stroke_op,
        fill_color=fill, fill_opacity=fill_opacity,
    ).move_to(text_mob.get_center())
    return bg


def make_liquid_glass_card(width, height):
    """Glassmorphism card with iridescent rim and glossy sheen (series-wide)."""
    card = VGroup()
    base = RoundedRectangle(corner_radius=0.3, width=width, height=height,
                            fill_color=COLOR_GREY_BALL, fill_opacity=0.12,
                            stroke_width=0)
    highlight = RoundedRectangle(corner_radius=0.3, width=width, height=height,
                                 fill_color=COLOR_WHITE, fill_opacity=0.08,
                                 stroke_width=0)
    highlight.set_sheen(-0.5, UL)
    rim = RoundedRectangle(corner_radius=0.3, width=width, height=height,
                           stroke_width=2.5, fill_opacity=0)
    rim.set_color([COLOR_PURPLE, COLOR_CYAN, COLOR_GREEN, COLOR_PINK])
    rim.set_stroke(opacity=0.85)
    card.add(base, highlight, rim)
    return card


def make_center_point(scale=1.0):
    g = VGroup()
    dot = Dot(point=ORIGIN, radius=0.05 * scale, color=COLOR_GREY_BALL)
    dot.set_fill(COLOR_GREY_BALL, opacity=1.0)
    shimmer = Circle(radius=0.18 * scale, stroke_color=COLOR_VEC_F,
                     stroke_width=3, stroke_opacity=0.0, fill_opacity=0)
    g.add(shimmer, dot)
    g.shimmer = shimmer
    return g


def make_stone(radius=0.26):
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
    for r, a, sr in [(0.3 * radius, 1.2, 0.08 * radius),
                     (0.5 * radius, 3.5, 0.06 * radius),
                     (0.25 * radius, 5.0, 0.09 * radius)]:
        spec = Dot(point=np.array([r * np.cos(a), r * np.sin(a), 0]),
                   radius=sr, color="#3A3A3C")
        spec.set_fill("#3A3A3C", opacity=0.75)
        g.add(spec)
    return g


def orbit_point(center, radius, angle):
    return center + radius * np.array([np.cos(angle), np.sin(angle), 0])


def right_angle_marker(vertex, p1, p2, size=0.3, color=COLOR_GREEN,
                       stroke_width=4):
    """A square corner tick at `vertex`, oriented toward p1 and p2."""
    d1 = (p1 - vertex); d1 = d1 / np.linalg.norm(d1)
    d2 = (p2 - vertex); d2 = d2 / np.linalg.norm(d2)
    a = vertex + d1 * size
    b = vertex + d1 * size + d2 * size
    c = vertex + d2 * size
    m = VMobject(color=color, stroke_width=stroke_width)
    m.set_points_as_corners([a, b, c])
    return m


# ═══════════════════════════════════════════════════════════════════
#  SCENE 5
# ═══════════════════════════════════════════════════════════════════
class Scene5_TheCollapse(MovingCameraScene):
    def construct(self):
        self.camera.background_color = COLOR_BG
        grid = build_grid()
        grid.set_z_index(-10)
        self.add(grid)
        self.camera.frame.save_state()

        # ── shared geometry (identical to Scenes 3 & 4) ───────────
        O = np.array([0.0, 0.0, 0.0])
        R = 2.5
        A = O + R * UP                                   # (0, 2.5) — frozen stone
        D = O - R * UP                                   # (0, -2.5)
        PHI0 = math.radians(37)                            # the "cartoon" angle
        # BC kept strictly vertical for every phi (C sits directly below B),
        # exactly as Scene 4 left it after the tighten-to-limit move.

        phi = ValueTracker(PHI0)
        # drives line stroke + right-angle-mark size so detail stays crisp
        # as the camera dives in on corner A (1.0 = full-frame, smaller = zoomed)
        zoom = ValueTracker(1.0)

        def Pb():
            d = R * math.tan(phi.get_value())
            return A + LEFT * d

        def Pc():
            b = Pb()
            cx = b[0]
            cy = math.sqrt(max(R * R - cx * cx, 0.0))
            return np.array([cx, cy, 0.0])

        B0, C0 = Pb(), Pc()   # the values at PHI0 (== Scene 4's B and C_clean)

        # ══════════════════════════════════════════════════════════
        #  RE-ESTABLISH SCENE 4's CLOSING FRAME  (hard cut, no entrance)
        # ══════════════════════════════════════════════════════════
        orbit = Circle(radius=R, color=COLOR_GREY_BALL, stroke_width=1.5,
                       stroke_opacity=0.18).move_to(O)
        hand = make_center_point(scale=0.8).move_to(O).set_z_index(2)
        lineAD = Line(A, D, color=COLOR_GREY_BALL, stroke_width=2.6).set_z_index(1)
        string = Line(O, C0, color=COLOR_GREY_BALL, stroke_width=2.6).set_z_index(1)

        lineAB = Line(A, B0, color=COLOR_CYAN, stroke_width=4).set_z_index(4)
        lineBC = Line(B0, C0, color=COLOR_AMBER, stroke_width=4).set_z_index(8)
        lineAC = Line(A, C0, color=COLOR_WHITE, stroke_width=2.4,
                      stroke_opacity=0.9).set_z_index(3)
        lineCD = Line(C0, D, color=COLOR_PURPLE, stroke_width=4).set_z_index(4)

        small_fill = Polygon(A, B0, C0, stroke_width=0, fill_color=COLOR_CYAN,
                             fill_opacity=0.14).set_z_index(0)
        big_fill = Polygon(A, C0, D, stroke_width=0, fill_color=COLOR_PURPLE,
                           fill_opacity=0.10).set_z_index(0)

        sq_B = right_angle_marker(B0, A, C0, size=0.26).set_z_index(9)
        sq_C = right_angle_marker(C0, A, D, size=0.26).set_z_index(9)

        A_label = MathTex("A", font_size=40, color=COLOR_WHITE
                          ).next_to(A, UP, buff=0.22).set_z_index(9)
        b_lbl = MathTex("B", font_size=40, color=COLOR_WHITE
                        ).next_to(B0, UP, buff=0.22).set_z_index(9)
        C_label = MathTex("C", font_size=40, color=COLOR_WHITE
                          ).next_to(C0, LEFT, buff=0.20).set_z_index(9)
        D_label = MathTex("D", font_size=40, color=COLOR_WHITE
                          ).next_to(D, DOWN, buff=0.22).set_z_index(9)

        ghost_stone = make_stone(radius=0.2).move_to(B0).set_z_index(6).set_opacity(0.10)
        real_stone = make_stone(radius=0.2).move_to(C0).set_z_index(6).set_opacity(0.10)

        # docked facts, rebuilt exactly as Scene 4 parked them (upper-left)
        eq_ab = MathTex("AB", "=", "v", r"\cdot", "t", font_size=40)
        eq_ab[0].set_color(COLOR_VEC_V); eq_ab[2].set_color(COLOR_VEC_V)
        ab_fact = VGroup(pill_bg(eq_ab), eq_ab).scale(0.78).to_corner(UL, buff=0.55)
        ab_fact.set_z_index(9)

        eq_bc = MathTex("BC", "=", r"\frac{1}{2}", "a", "t^2", font_size=42)
        eq_bc[0].set_color(COLOR_AMBER)
        bc_fact = VGroup(pill_bg(eq_bc), eq_bc).scale(0.78)
        bc_fact.next_to(ab_fact, DOWN, buff=0.22, aligned_edge=LEFT)
        bc_fact.set_z_index(9)

        # the AD = 2r fact docks here later (Act 1) in the same pill format as the
        # two above — its slot is reserved now so the dock target is fixed.
        eq_ad = MathTex("AD", "=", "2r", font_size=42)
        eq_ad[0].set_color(COLOR_INDIGO); eq_ad[2].set_color(COLOR_INDIGO)
        ad_fact = VGroup(pill_bg(eq_ad), eq_ad).scale(0.78)
        ad_fact.next_to(bc_fact, DOWN, buff=0.22, aligned_edge=LEFT)
        ad_fact.set_z_index(9)

        # the golden equation, still inside Scene 4's glass card
        golden_eq = MathTex("AC^2", "=", "BC", r"\cdot", "AD", font_size=52
                            ).set_z_index(14)
        golden_eq.move_to(ORIGIN)
        dark_card = Rectangle(width=24, height=14, fill_color=COLOR_BG,
                              fill_opacity=0.55, stroke_width=0).set_z_index(12)
        glass_card = make_liquid_glass_card(width=5.0, height=2.6).set_z_index(13)

        self.add(orbit, hand, lineAD, string, small_fill, big_fill,
                 lineAB, lineCD, lineAC, lineBC, sq_B, sq_C,
                 A_label, b_lbl, C_label, D_label, ghost_stone, real_stone,
                 ab_fact, bc_fact, dark_card, glass_card, golden_eq)

        self.wait(0.6)   # half-beat of recognition before anything moves

        # ── dissolve the hero card, brighten the working figure, dock AC² ──
        golden_dock = golden_eq.copy().scale(0.62).to_edge(UP, buff=0.35)
        self.play(
            FadeOut(dark_card),
            FadeOut(glass_card, scale=0.9),
            Transform(golden_eq, golden_dock),
            orbit.animate.set_stroke(opacity=0.40),
            big_fill.animate.set_fill(opacity=0.08),
            run_time=1.1, rate_func=rate_functions.ease_in_out_sine,
        )
        self.wait()

        r_up = Line(O, A, color=COLOR_INDIGO, stroke_width=5).set_z_index(6)
        r_dn = Line(O, D, color=COLOR_INDIGO, stroke_width=5).set_z_index(6)
        r_up_lbl = MathTex("r", font_size=34, color=COLOR_INDIGO
                           ).next_to(r_up, RIGHT, buff=0.12).set_z_index(7)
        r_dn_lbl = MathTex("r", font_size=34, color=COLOR_INDIGO
                           ).next_to(r_dn, RIGHT, buff=0.12).set_z_index(7)
        self.play(
            golden_eq[4].animate.set_color(COLOR_INDIGO),
            Create(r_up), Create(r_dn),
            FadeIn(r_up_lbl), FadeIn(r_dn_lbl),
            run_time=0.9,
        )

        ad = VGroup(A_label, D_label).copy().set_z_index(15)
        r = VGroup(r_up_lbl, r_dn_lbl)
        adr = VGroup(ad, r)
        self.play(
            FadeIn(ad_fact[0]),                              # the pill
            # ReplacementTransform consumes `adr` so no stray copies of the A/D
            # labels linger on top of the fact (which used to surface a phantom
            # "D" later, when the figure stripped down for a = v²/r).
            ReplacementTransform(adr, eq_ad),            # A,D + r,r → "AD = 2r"
            FadeOut(VGroup(r_up, r_dn)),                  # only the indigo diameter lines
            run_time=1.0, rate_func=rate_functions.ease_in_out_sine,
        )
        self.add(ad_fact)   # re-assert as a single group (eq_ad now lives in it)

        # ══════════════════════════════════════════════════════════
        #  ACT 1
        # ══════════════════════════════════════════════════════════

        # the honest, apologetic wobble as we call it a cartoon (static triangle)
        self.play(Wiggle(small_fill, scale_value=1.04, rotation_angle=0.012 * TAU),
                  run_time=0.9)

        # attach the live updaters to the inherited figure (draw nothing new)
        string.add_updater(lambda m: m.put_start_and_end_on(O, Pc()))
        lineAB.add_updater(lambda m: m.put_start_and_end_on(A, Pb()))
        lineBC.add_updater(lambda m: m.put_start_and_end_on(Pb(), Pc()))
        lineAC.add_updater(lambda m: m.put_start_and_end_on(A, Pc()))
        lineCD.add_updater(lambda m: m.put_start_and_end_on(Pc(), D))
        small_fill.add_updater(lambda m: m.set_points_as_corners([A, Pb(), Pc(), A]))
        big_fill.add_updater(lambda m: m.set_points_as_corners([A, Pc(), D, A]))

        A_label._base_h = A_label.height
        b_lbl._base_h   = b_lbl.height
        C_label._base_h = C_label.height

        def _dock(label, point, direction, buff_base):
            z = zoom.get_value()
            label.set(height=max(label._base_h * z, 1e-3))
            label.next_to(point, direction, buff=buff_base * z)

        A_label.add_updater(lambda m: _dock(m, A,    UP,   0.22))
        b_lbl.add_updater(  lambda m: _dock(m, Pb(), UP,   0.22))
        C_label.add_updater(lambda m: _dock(m, Pc(), LEFT, 0.20))
        ghost_stone.add_updater(lambda m: m.move_to(Pb()))
        real_stone.add_updater(lambda m: m.move_to(Pc()))
        sq_B.add_updater(lambda m: m.become(
            right_angle_marker(Pb(), A, Pc(), size=0.26 * zoom.get_value(),
                               stroke_width=4 * zoom.get_value()
                               ).set_z_index(9)))
        sq_C.add_updater(lambda m: m.become(
            right_angle_marker(Pc(), A, D, size=0.26 * zoom.get_value(),
                               stroke_width=4 * zoom.get_value()
                               ).set_z_index(9)))

        for ln, base_w in ((lineAB, 4.0), (lineBC, 4.0), (lineAC, 2.4),
                           (lineCD, 4.0), (string, 2.6),
                           (orbit, 1.5), (lineAD, 2.6)):
            ln._base_w = base_w
            ln.add_updater(lambda m: m.set_stroke(
                width=max(m._base_w * zoom.get_value(), 0.08)))

        # shrink the triangle down — POST: pitch slides DOWN as t drops
        self.play(
            phi.animate.set_value(math.radians(14)),
            run_time=3.0, rate_func=rate_functions.ease_in_out_sine,
        )
        self.wait(1.0)   # stop small-but-visible; let it sit

        # ══════════════════════════════════════════════════════════
        #  ACT 2 · WHEN TIME VANISHES, B AND C BECOME A   (hero beat)
        # ══════════════════════════════════════════════════════════

        self.play(
            self.camera.frame.animate.move_to(A + DOWN * 0.35).set(width=4.2),
            zoom.animate.set_value(4.2 / 14),
            run_time=1.3, rate_func=rate_functions.ease_in_out_cubic,
        )

        self.play(
            phi.animate.set_value(math.radians(0.8)),
            self.camera.frame.animate.move_to(A + DOWN * 0.06).set(width=0.7),
            zoom.animate.set_value(0.7 / 14),
            run_time=3.6, rate_func=rate_functions.ease_in_out_sine,
        )

        ghost_stone.clear_updaters()
        grid.save_state()   # remember the exact per-line fade so we can restore it
        self.play(
            grid.animate.set_opacity(0.0),
            FadeOut(ghost_stone),
            run_time=0.8, rate_func=rate_functions.ease_in_out_sine,
        )

        self.play(
            phi.animate.set_value(math.radians(0.12)),
            self.camera.frame.animate.move_to(A + DOWN * 0.012).set(width=0.14),
            zoom.animate.set_value(0.14 / 14),
            run_time=2.2, rate_func=rate_functions.ease_in_out_sine,
        )

        # freeze the live figure at the limit
        for m in (string, lineAB, lineBC, lineAC, lineCD, small_fill, big_fill,
                  A_label, b_lbl, C_label, ghost_stone, real_stone, sq_B, sq_C,
                  orbit, lineAD):
            m.clear_updaters()

        self.wait()

        # everything below happens at deep zoom — size text to the frame
        fw = self.camera.frame.get_width()   # current frame width (~0.14)

        # AC's identity dissolves into AB — one line where there were two
        self.play(FadeOut(lineAC), run_time=0.5)
        self.wait()

        chords_and_orbit = VGroup(
            orbit, string, lineAB, lineBC, lineCD, small_fill, big_fill,
            b_lbl, C_label, D_label, hand, real_stone, sq_B, sq_C,
        )
        self.play(
            Restore(self.camera.frame),
            Restore(grid),
            FadeOut(chords_and_orbit),
            run_time=1.3, rate_func=rate_functions.ease_in_out_cubic,
        )
        eq_center = golden_eq.copy().scale(1 / 0.62).move_to(ORIGIN)
        self.play(Transform(golden_eq, eq_center),
                  run_time=0.9, rate_func=rate_functions.ease_in_out_sine)
        self.wait()

        # the substitution: the C in AC² physically melts into B → AB² = BC·AD
        # colours match the docked facts top-left: AB→cyan, BC→amber, AD→indigo
        eq_sub = MathTex("AB^2", "=", "BC", r"\cdot", "AD", font_size=52
                         ).move_to(ORIGIN).set_z_index(14)
        eq_sub[0].set_color(COLOR_VEC_V)        # AB²  (cyan, == eq_ab's AB)
        eq_sub[2].set_color(COLOR_AMBER)        # BC   (amber, == eq_bc's BC)
        eq_sub[4].set_color(COLOR_INDIGO)       # AD   (indigo, == eq_ad's AD)
        self.play(
            ReplacementTransform(golden_eq[0][0], eq_sub[0][0]),   # A → A
            ReplacementTransform(golden_eq[0][1], eq_sub[0][1]),   # C → B (the melt)
            ReplacementTransform(golden_eq[0][2], eq_sub[0][2]),   # ² → ²
            ReplacementTransform(golden_eq[1], eq_sub[1]),
            ReplacementTransform(golden_eq[2], eq_sub[2]),
            ReplacementTransform(golden_eq[3], eq_sub[3]),
            ReplacementTransform(golden_eq[4], eq_sub[4]),
            run_time=1.2, rate_func=rate_functions.ease_in_out_sine,
        )
        # POST: a clean bell resolves here — "we arrived somewhere."
        self.play(Indicate(eq_sub, color=COLOR_WHITE, scale_factor=1.12),
                  run_time=0.7)
        self.wait(0.8)

        # dock the equation up top; the orbit and triangle are already gone
        # (faded on the zoom-out), so only the AD diameter is dimmed back here.
        self.play(
            lineAD.animate.set_stroke(opacity=0.45),
            run_time=1.0, rate_func=rate_functions.ease_in_out_sine,
        )
        self.wait()

        # ══════════════════════════════════════════════════════════
        #  ACT 3 · GEOMETRY BECOMES PHYSICS   (clean substitution)
        # ══════════════════════════════════════════════════════════
        
        # 1. Flip the equation so the left/right sides align with the upcoming physics formula.
        # AB² = BC · AD  -->  BC · AD = AB²
        eq_flipped = MathTex("BC", r"\cdot", "AD", "=", "AB^2", font_size=52
                             ).move_to(ORIGIN).set_z_index(14)
        eq_flipped[0].set_color(COLOR_AMBER)    # BC
        eq_flipped[2].set_color(COLOR_INDIGO)   # AD
        eq_flipped[4].set_color(COLOR_VEC_V)    # AB² (cyan)

        self.play(
            ReplacementTransform(eq_sub[0], eq_flipped[4]), # AB² -> AB²
            ReplacementTransform(eq_sub[1], eq_flipped[3]), # = -> =
            ReplacementTransform(eq_sub[2], eq_flipped[0]), # BC -> BC
            ReplacementTransform(eq_sub[3], eq_flipped[1]), # · -> ·
            ReplacementTransform(eq_sub[4], eq_flipped[2]), # AD -> AD
            run_time=0.8, rate_func=rate_functions.ease_in_out_sine
        )
        self.wait(0.4)

        # 2. Setup the target assembled equation
        assembled = MathTex(
            r"\left(\tfrac{1}{2}\,a\,t^2\right)", r"\cdot", r"\left(2r\right)",
            "=", r"\left(v\cdot t\right)^2", font_size=48,
        ).move_to(ORIGIN).set_z_index(14)
        assembled[0].set_color(COLOR_VEC_F)     # ½at²  (red)
        assembled[2].set_color(COLOR_INDIGO)    # 2r    (indigo)
        assembled[4].set_color(COLOR_AMBER)     # (v·t)² (yellow)

        # Morph the structural glue right away so the slots are ready
        self.play(
            ReplacementTransform(eq_flipped[1], assembled[1]),  # · -> ·
            ReplacementTransform(eq_flipped[3], assembled[3]),  # = -> =
            run_time=0.4
        )

        # 3. Clean, in-place substitution function
        def clean_substitute(source_token, target_token, source_pill):
            """Pulse the docked fact to draw the eye, then smoothly morph the term in-place."""
            self.play(
                Indicate(source_pill, color=COLOR_WHITE, scale_factor=1.06),
                run_time=0.5
            )
            self.play(
                ReplacementTransform(source_token, target_token),
                run_time=0.7, rate_func=rate_functions.ease_in_out_sine
            )

        # Execute the substitutions one by one
        clean_substitute(eq_flipped[0], assembled[0], bc_fact)  # BC -> ½at²
        clean_substitute(eq_flipped[2], assembled[2], ad_fact)  # AD -> 2r
        clean_substitute(eq_flipped[4], assembled[4], ab_fact)  # AB² -> (v·t)²

        # POST: Three clean, in-place morphs. Let it sit before the demolition.
        self.wait(1.2)

        # ══════════════════════════════════════════════════════════
        #  ACT 4 · THE COLLAPSE   (everything cancels)
        # ══════════════════════════════════════════════════════════
        # Expand the right so the symmetry is visible, then demolish.
        expanded = MathTex(
            r"\tfrac{1}{2}", "a", "t^2", r"\cdot", "2", "r", "=", "v^2", "t^2",
            font_size=48,
        ).move_to(ORIGIN).set_z_index(14)
        # recolor for the demolition: doomed pairs glow, the survivor 'a' is red
        expanded[0].set_color(COLOR_ORANGE)   # ½  ┐ annihilate
        expanded[4].set_color(COLOR_ORANGE)   # 2  ┘
        expanded[1].set_color(COLOR_VEC_F)    # a  (the survivor)
        expanded[5].set_color(COLOR_INDIGO)   # r
        expanded[7].set_color(COLOR_AMBER)    # v²
        expanded[2].set_color(COLOR_CYAN)     # t² ┐ cancel across "="
        expanded[8].set_color(COLOR_CYAN)     # t² ┘

        self.play(ReplacementTransform(assembled, expanded),
                  run_time=1.1, rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.6)

        # ½ and 2 drift together and pop out of existence
        half_tok, two_tok = expanded[0], expanded[4]
        mid = (half_tok.get_center() + two_tok.get_center()) / 2 + UP * 0.6
        self.play(half_tok.animate.move_to(mid + LEFT * 0.18),
                  two_tok.animate.move_to(mid + RIGHT * 0.18),
                  run_time=0.7, rate_func=rate_functions.ease_in_out_sine)
        self.play(
            Flash(mid, color=COLOR_ORANGE, line_length=0.18, num_lines=12,
                  flash_radius=0.3, line_stroke_width=2.5),
            FadeOut(half_tok, scale=0.0), FadeOut(two_tok, scale=0.0),
            run_time=0.6,
        )
        # POST: an ascending "pip" — the sound of simplification.
        step2 = MathTex("a", "t^2", r"\cdot", "r", "=", "v^2", "t^2", font_size=48
                        ).move_to(ORIGIN).set_z_index(14)
        step2[0].set_color(COLOR_VEC_F)
        step2[1].set_color(COLOR_CYAN); step2[6].set_color(COLOR_CYAN)
        step2[3].set_color(COLOR_INDIGO); step2[5].set_color(COLOR_AMBER)
        self.play(
            ReplacementTransform(expanded[1], step2[0]),   # a
            ReplacementTransform(expanded[2], step2[1]),   # t²
            ReplacementTransform(expanded[3], step2[2]),   # ·
            ReplacementTransform(expanded[5], step2[3]),   # r
            ReplacementTransform(expanded[6], step2[4]),   # =
            ReplacementTransform(expanded[7], step2[5]),   # v²
            ReplacementTransform(expanded[8], step2[6]),   # t²
            run_time=0.8, rate_func=rate_functions.ease_in_out_sine,
        )
        self.wait(0.5)

        # t² cancels across the equals sign — one from each side, meeting in the middle
        tL, tR = step2[1], step2[6]
        eq_center_pt = step2[4].get_center()
        self.play(tL.animate.move_to(eq_center_pt + LEFT * 0.35),
                  tR.animate.move_to(eq_center_pt + RIGHT * 0.35),
                  run_time=0.7, rate_func=rate_functions.ease_in_out_sine)
        self.play(
            Flash(eq_center_pt, color=COLOR_CYAN, line_length=0.18, num_lines=12,
                  flash_radius=0.3, line_stroke_width=2.5),
            FadeOut(tL, scale=0.0), FadeOut(tR, scale=0.0),
            run_time=0.6,
        )
        # survivor re-centres and breathes: a·r = v²
        step3 = MathTex("a", r"\cdot", "r", "=", "v^2", font_size=54
                        ).move_to(ORIGIN).set_z_index(14)
        step3[0].set_color(COLOR_VEC_F)
        step3[2].set_color(COLOR_INDIGO)
        step3[4].set_color(COLOR_AMBER)
        self.play(
            ReplacementTransform(step2[0], step3[0]),   # a
            ReplacementTransform(step2[2], step3[1]),   # · (the surviving dot)
            ReplacementTransform(step2[3], step3[2]),   # r
            ReplacementTransform(step2[4], step3[3]),   # =
            ReplacementTransform(step2[5], step3[4]),   # v²
            run_time=0.9, rate_func=rate_functions.ease_in_out_sine,
        )
        self.wait(0.9)

        # ══════════════════════════════════════════════════════════
        #  ACT 5 · a = v²/r   (the destination)
        # ══════════════════════════════════════════════════════════
        final = MathTex("a", "=", r"\frac{v^2}{r}", font_size=64
                        ).move_to(ORIGIN).set_z_index(14)
        final[0].set_color(COLOR_VEC_F)
        final[2].set_color(COLOR_AMBER)         # the v²/r fraction, the quantity

        self.play(
            ReplacementTransform(step3[0], final[0]),                 # a
            ReplacementTransform(step3[3], final[1]),                 # =
            ReplacementTransform(VGroup(step3[4], step3[2]), final[2]),  # v², r → fraction
            FadeOut(step3[1], scale=0.0),                             # the lone ·
            run_time=1.4, rate_func=rate_functions.ease_in_out_cubic,
        )
        self.wait(0.6)

        self.play(
            FadeOut(VGroup(lineAD, A_label,
                           ab_fact, bc_fact, ad_fact)),
            run_time=1.0, rate_func=rate_functions.ease_in_out_sine,
        )
        self.wait(0.3)

        ripple = Circle(radius=0.4, color=COLOR_AMBER, stroke_width=3
                        ).move_to(final.get_center()).set_z_index(13)

        self.play(
            final.animate.scale(1.18),
            ripple.animate.scale(9).set_stroke(opacity=0.0),
            run_time=1.1, rate_func=rate_functions.ease_out_cubic,
        )
        self.play(final.animate.scale(1 / 1.18),
                  run_time=0.5, rate_func=rate_functions.ease_in_out_sine)

        self.wait(1.6)