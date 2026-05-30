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
COLOR_VEC_F     = "#FF3B30"   # red  — force
COLOR_VEC_V     = "#32ADE6"   # cyan — velocity / θ
COLOR_GREEN     = "#34C759"   # right angles
COLOR_AMBER     = "#FFCC00"   # measured quantities
COLOR_PINK      = "#FF2D55"
COLOR_PURPLE    = "#AF52DE"   # φ
COLOR_ORANGE    = "#FF9500"
COLOR_WHITE     = "#E5E5EA"
COLOR_CYAN      = "#32ADE6"


# ═══════════════════════════════════════════════════════════════════
#  HELPERS  (carried over from the rest of the series)
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


# ── geometry helpers specific to this scene ────────────────────────
def angle_arc(vertex, p1, p2, radius=0.45, color=COLOR_WHITE, stroke_width=4):
    """Interior-angle arc at `vertex`, swept the short way from p1 to p2."""
    a1 = math.atan2((p1 - vertex)[1], (p1 - vertex)[0])
    a2 = math.atan2((p2 - vertex)[1], (p2 - vertex)[0])
    diff = (a2 - a1 + PI) % TAU - PI          # signed smallest sweep
    return Arc(radius=radius, start_angle=a1, angle=diff, arc_center=vertex,
               color=color, stroke_width=stroke_width)


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
#  SCENE 4 · The Hidden Triangle — Huygens' geometry → AC² = BC·AD
#  Carries straight on from Scene 3's closing frame.
# ═══════════════════════════════════════════════════════════════════
class Scene4_HiddenTriangle(MovingCameraScene):
    def construct(self):
        self.camera.background_color = COLOR_BG
        grid = build_grid()
        grid.set_z_index(-10)
        self.add(grid)
        self.camera.frame.save_state()

        # ── shared geometry (identical to Scene 3) ────────────────
        O = np.array([0.0, 0.0, 0.0])
        R = 2.5
        A = O + R * UP                                  # (0, 2.5)
        D_TANGENT = R * math.tan(37 * DEGREES)
        B = A + LEFT * D_TANGENT                          # (-1.884, 2.5)
        C_radial = O + R * (B - O) / np.linalg.norm(B - O)   # Scene 3's C
        C_clean = np.array([B[0], math.sqrt(R ** 2 - B[0] ** 2), 0.0])  # below B
        D = O - R * UP                                   # (0, -2.5)

        c_ang = ValueTracker(math.atan2(C_radial[1], C_radial[0]))   # C lives here

        def C_pos():
            return orbit_point(O, R, c_ang.get_value())

        # ══════════════════════════════════════════════════════════
        #  RE-ESTABLISH SCENE 3's CLOSING FRAME  (a hard cut, no entrance)
        # ══════════════════════════════════════════════════════════
        orbit = Circle(radius=R, color=COLOR_GREY_BALL, stroke_width=1.5,
                       stroke_opacity=0.18).move_to(O)
        hand = make_center_point(scale=0.8).move_to(O).set_z_index(2)
        string = Line(O, C_radial, color=COLOR_GREY_BALL, stroke_width=2.6
                      ).set_z_index(1)
        swept_arc = Arc(radius=R, start_angle=PI / 2, angle=math.radians(37),
                        arc_center=O, color=COLOR_WHITE,
                        stroke_width=2.2, stroke_opacity=0.55).set_z_index(2)
        bc_line = Line(B, C_radial, color=COLOR_AMBER, stroke_width=4
                       ).set_z_index(8)

        A_label = MathTex("A", font_size=40, color=COLOR_WHITE
                          ).next_to(A, UP, buff=0.22).set_z_index(9)
        b_lbl = MathTex("B", font_size=40, color=COLOR_WHITE
                        ).next_to(B, UP, buff=0.22).set_z_index(9)
        C_label = MathTex("C", font_size=40, color=COLOR_WHITE
                          ).next_to(C_radial, LEFT, buff=0.20).set_z_index(9)

        ghost_stone = make_stone(radius=0.2).move_to(B).set_z_index(6)
        real_stone = make_stone(radius=0.2).move_to(C_radial).set_z_index(6)

        # docked facts, rebuilt exactly as Scene 3 parked them
        eq_ab = MathTex("AB", "=", "v", r"\cdot", "t", font_size=40)
        eq_ab[0].set_color(COLOR_VEC_V); eq_ab[2].set_color(COLOR_VEC_V)
        eq_ab[4].set_color(COLOR_WHITE)
        ab_fact = VGroup(pill_bg(eq_ab), eq_ab).scale(0.78).to_corner(UL, buff=0.55)
        ab_fact.set_z_index(9)

        eq_bc = MathTex("BC", "=", r"\frac{1}{2}", "a", "t^2", font_size=42)
        eq_bc[0].set_color(COLOR_AMBER)
        bc_fact = VGroup(pill_bg(eq_bc), eq_bc).scale(0.78)
        bc_fact.next_to(ab_fact, DOWN, buff=0.22, aligned_edge=LEFT)
        bc_fact.set_z_index(9)

        self.add(orbit, hand, string, swept_arc, bc_line, A_label, b_lbl,
                 C_label, ghost_stone, real_stone, ab_fact, bc_fact)
        self.wait(0.6)

        # ══════════════════════════════════════════════════════════
        #  ACT 1 · HUYGENS PICKS UP THE PENCIL  (motion → geometry)
        # ══════════════════════════════════════════════════════════
        # Settle the dynamic stuff, ink the page: stones recede, the swept
        # arc fades, the orbit brightens from a sleepy guide into a drawing.
        self.play(
            ghost_stone.animate.set_opacity(0.18),
            real_stone.animate.set_opacity(0.18),
            FadeOut(swept_arc),
            orbit.animate.set_stroke(opacity=0.40),
            run_time=1.0, rate_func=rate_functions.ease_in_out_sine,
        )
        self.wait(0.4)

        # Hero: birth the diameter. It grows from A, straight through O, to D.
        diameter = Line(A, D, color=COLOR_GREY_BALL, stroke_width=2.6
                        ).set_z_index(1)
        self.play(Create(diameter), run_time=1.1,
                  rate_func=rate_functions.ease_in_out_cubic)

        D_label = MathTex("D", font_size=40, color=COLOR_WHITE
                          ).next_to(D, DOWN, buff=0.22).set_z_index(9)
        self.play(FadeIn(D_label, scale=1.9),
                  run_time=0.55, rate_func=rate_functions.ease_out_back)

        # AD = 2R — a measured quantity, so amber. Parked low, clear of the
        # triangle zone up top.
        ad_tag = MathTex("AD", "=", "2R", font_size=30)
        ad_tag[0].set_color(COLOR_AMBER); ad_tag[2].set_color(COLOR_AMBER)
        ad_tag.shift(RIGHT*1.7).set_z_index(9)
        ad_pill = pill_bg(ad_tag, fill_opacity=0.7).set_z_index(8)
        self.play(FadeIn(VGroup(ad_pill, ad_tag), shift=UP * 0.1), run_time=0.5)
        self.wait(0.8)

        # ══════════════════════════════════════════════════════════
        #  ACT 2 · THALES' PROMISE  (general law → our figure → tighten)
        # ══════════════════════════════════════════════════════════
        # A separate little stage on the right: any vertex on a semicircle
        # whose base is a diameter sees a right angle — and it never changes.
        demo_c = np.array([4.3, 0.4, 0.0])
        center = Dot(demo_c, color=COLOR_WHITE, radius=0.06).set_z_index(6)
        demo_r = 1.15
        demo_circ = Circle(radius=demo_r, color=COLOR_GROUND, stroke_width=2,
                           stroke_opacity=0.5).move_to(demo_c).set_z_index(5)
        demo_L = demo_c + LEFT * demo_r
        demo_R = demo_c + RIGHT * demo_r
        demo_diam = Line(demo_L, demo_R, color=COLOR_GROUND, stroke_width=2,
                         stroke_opacity=0.6).set_z_index(5)
        demo_a = ValueTracker(105 * DEGREES)

        def demo_v():
            return demo_c + demo_r * np.array(
                [math.cos(demo_a.get_value()), math.sin(demo_a.get_value()), 0])

        demo_ch1 = always_redraw(lambda: Line(
            demo_v(), demo_L, color=COLOR_GREY_BALL, stroke_width=2.2).set_z_index(6))
        demo_ch2 = always_redraw(lambda: Line(
            demo_v(), demo_R, color=COLOR_GREY_BALL, stroke_width=2.2).set_z_index(6))
        demo_sq = always_redraw(lambda: right_angle_marker(
            demo_v(), demo_L, demo_R, size=0.22, color=COLOR_GREEN,
            stroke_width=3.5).set_z_index(7))
        demo_dot = always_redraw(lambda: Dot(demo_v(), radius=0.05,
                                             color=COLOR_GREY_BALL).set_z_index(7))
        demo_trace = TracedPath(demo_v, stroke_color=COLOR_VEC_V,
                                stroke_width=2, stroke_opacity=0.45).set_z_index(4)

        self.play(FadeIn(demo_circ), Create(demo_diam), Create(center), run_time=0.6)
        self.add(demo_trace)
        self.play(FadeIn(demo_dot, scale=0.5), Create(demo_ch1), Create(demo_ch2),
                  run_time=0.5)
        self.play(GrowFromCenter(demo_sq), run_time=0.4)

        thales_lbl = Text("Thales' theorem", font="Segoe UI", font_size=20,
                          color=COLOR_GROUND).move_to(demo_c + DOWN * 1.7)
        self.play(FadeIn(thales_lbl, shift=UP * 0.08), run_time=0.5)

        # The "wait, it never changes?" pass — slow, one way then the other.
        self.play(demo_a.animate.set_value(155 * DEGREES), run_time=1.6,
                  rate_func=rate_functions.ease_in_out_sine)
        self.play(demo_a.animate.set_value(25 * DEGREES), run_time=2.2,
                  rate_func=rate_functions.ease_in_out_sine)
        self.play(demo_a.animate.set_value(90 * DEGREES), run_time=1.3,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.4)

        # Carry the law onto our figure: the SAME green square flies from the
        # demo vertex and seats at C (∠ACD). Thales holds for any C on the
        # circle, so this is honest even before we tighten the time-slice.
        demo_sq.clear_updaters()
        demo_ch1.clear_updaters(); demo_ch2.clear_updaters()
        demo_dot.clear_updaters(); demo_trace.clear_updaters()

        sq_C = right_angle_marker(C_radial, A, D, size=0.26, color=COLOR_GREEN,
                                  stroke_width=4).set_z_index(9)
        ac_line = Line(A, C_radial, color=COLOR_WHITE, stroke_width=2.4,
                       stroke_opacity=0.9).set_z_index(3)
        cd_line = Line(C_radial, D, color=COLOR_WHITE, stroke_width=2.4,
                       stroke_opacity=0.9).set_z_index(3)

        self.play(
            FadeOut(VGroup(demo_circ, demo_diam, demo_ch1, demo_ch2,
                           demo_dot, demo_trace, thales_lbl, center)),
            ReplacementTransform(demo_sq, sq_C),
            run_time=1.0, rate_func=rate_functions.ease_in_out_sine,
        )
        self.play(Create(ac_line), Create(cd_line), run_time=0.7)
        self.play(Indicate(sq_C, color=COLOR_GREEN, scale_factor=1.18),
                  run_time=0.7)
        self.wait(0.6)

        # ── Tighten to the limit (the honest fix for the corner at B) ──
        # Slide C along the circle to sit directly below B. As it arrives,
        # ∠ABC snaps from 53° to a clean 90°. The string, the amber drop,
        # AC, CD, the C-label and the parked stone all ride C.
        string.add_updater(lambda m: m.put_start_and_end_on(O, C_pos()))
        bc_line.add_updater(lambda m: m.put_start_and_end_on(B, C_pos()))
        ac_line.add_updater(lambda m: m.put_start_and_end_on(A, C_pos()))
        cd_line.add_updater(lambda m: m.put_start_and_end_on(C_pos(), D))
        C_label.add_updater(lambda m: m.next_to(C_pos(), LEFT, buff=0.20))
        real_stone.add_updater(lambda m: m.move_to(C_pos()))
        sq_C.add_updater(lambda m: m.become(
            right_angle_marker(C_pos(), A, D, size=0.26, color=COLOR_GREEN,
                               stroke_width=4).set_z_index(9)))

        b_angle = always_redraw(lambda: angle_arc(
            B, A, C_pos(), radius=0.25, color=COLOR_WHITE, stroke_width=3
        ).set_z_index(8))
        self.play(Create(b_angle))

        self.play(c_ang.animate.set_value(math.atan2(C_clean[1], C_clean[0])),
                  run_time=2.0, rate_func=rate_functions.ease_in_out_cubic)

        for m in (string, bc_line, ac_line, cd_line, C_label, real_stone, sq_C):
            m.clear_updaters()
        b_angle.clear_updaters()

        # the corner at B locks: swap the arc for a green square, with a click
        sq_B = right_angle_marker(B, A, C_clean, size=0.26, color=COLOR_GREEN,
                                  stroke_width=4).set_z_index(9)
        self.play(
            ReplacementTransform(b_angle, sq_B),
            Flash(B, color=COLOR_GREEN, line_length=0.16, num_lines=10,
                  flash_radius=0.3, line_stroke_width=2.2),
            run_time=0.6, rate_func=rate_functions.ease_out_back,
        )
        self.wait(0.8)

        # everyone now uses the clean C
        C = C_clean

        # ══════════════════════════════════════════════════════════
        #  ACT 3 · TWO TRIANGLES HIDING IN ONE FIGURE
        # ══════════════════════════════════════════════════════════
        small_fill = Polygon(A, B, C, stroke_width=0,
                             fill_color=COLOR_CYAN, fill_opacity=0.14).set_z_index(0)
        big_fill = Polygon(A, C, D, stroke_width=0,
                           fill_color=COLOR_PURPLE, fill_opacity=0.14).set_z_index(0)

        small_edges = VGroup(
            Line(A, B, color=COLOR_CYAN, stroke_width=4),
            Line(B, C, color=COLOR_CYAN, stroke_width=4),
            Line(C, A, color=COLOR_CYAN, stroke_width=4),
        ).set_z_index(4)
        big_edges = VGroup(
            Line(A, C, color=COLOR_PURPLE, stroke_width=4),
            Line(C, D, color=COLOR_PURPLE, stroke_width=4),
            Line(D, A, color=COLOR_PURPLE, stroke_width=4),
        ).set_z_index(4)

        # dim the field so the shapes can step forward
        field = VGroup(orbit, hand, string, bc_line, ac_line, cd_line, diameter)
        self.play(field.animate.set_stroke(opacity=0.18),
                  ghost_stone.animate.set_opacity(0.1),
                  real_stone.animate.set_opacity(0.1),
                  FadeOut(VGroup(ad_pill, ad_tag)),
                  run_time=0.7)

        # small triangle steps up: fill blooms, edges glow, vertices ping
        self.play(FadeIn(small_fill), Create(small_edges), run_time=0.7)
        self.play(
            LaggedStart(*[Flash(p, color=COLOR_CYAN, line_length=0.12,
                                flash_radius=0.22, num_lines=10,
                                line_stroke_width=2) for p in (A, B, C)],
                        lag_ratio=0.35)
        )
        self.play(small_fill.animate.set_fill(opacity=0.18).scale(1.03),
                  run_time=0.4, rate_func=there_and_back)
        self.wait(0.5)

        # hand off to the big triangle
        self.play(
            small_fill.animate.set_fill(opacity=0.05),
            small_edges.animate.set_stroke(opacity=0.3),
            FadeIn(big_fill), Create(big_edges)
        )
        self.play(
            LaggedStart(*[Flash(p, color=COLOR_PURPLE, line_length=0.12,
                                flash_radius=0.22, num_lines=10,
                                line_stroke_width=2) for p in (A, C, D)],
                        lag_ratio=0.35),
            big_fill.animate.set_fill(opacity=0.18).scale(1.03),
            run_time=1.1, rate_func=there_and_back,
        )
        self.wait(0.5)

        # both up — and the shared edge AC blazes white: the seam they lean on
        shared_AC = Line(A, C, color=COLOR_WHITE, stroke_width=6).set_z_index(5)
        self.play(
            small_fill.animate.set_fill(opacity=0.14),
            small_edges.animate.set_stroke(opacity=1.0),
            run_time=0.6
        )
        
        self.wait(0.8)

        # ══════════════════════════════════════════════════════════
        #  ACT 4 · SAME SHAPE, DIFFERENT SIZE  (AAA → the magic move)
        # ══════════════════════════════════════════════════════════

        # Clear the preview flashes to rebuild the logic step-by-step
        self.play(
            big_fill.animate.set_fill(opacity=0.03),
            big_edges.animate.set_stroke(opacity=0.2),
            small_fill.animate.set_fill(opacity=0.25),
            small_edges.animate.set_stroke(opacity=1.0),
            run_time=0.7
        )

        # ── 1. Zoom into Triangle ABC ──
        # Shift camera slightly right so equations have breathing room
        self.play(
            self.camera.frame.animate.move_to(small_fill.get_center() + RIGHT * 0.8).set(width=5.5),
            run_time=1.2, rate_func=rate_functions.ease_in_out_cubic
        )

        # Label ∠BAC = θ
        theta_arc = angle_arc(A, B, C, radius=0.45, color=RED, stroke_width=4).set_z_index(8)
        theta_tex = MathTex(r"\theta", font_size=20, color=RED)
        theta_tex.move_to(angle_arc(A, B, C, radius=0.65).point_from_proportion(0.5))
        
        self.play(Create(theta_arc), FadeIn(theta_tex, shift=LEFT * 0.1), run_time=0.6)
        self.wait(0.3)

        # Deduce ∠BCA
        self.play(Indicate(sq_B, color=COLOR_GREEN, scale_factor=1.2), run_time=0.5)
        
        self.wait(0.4)

        phi_arc = angle_arc(C, B, A, radius=0.35, color=COLOR_PURPLE, stroke_width=4).set_z_index(8)
        phi_tex = MathTex(r"90^\circ - \theta", font_size=20, color=COLOR_PURPLE)
        phi_tex.move_to(angle_arc(C, B, A, radius=0.70).point_from_proportion(0.5))

        self.play(Create(phi_arc), FadeIn(phi_tex, shift=UP * 0.1), run_time=0.6)
        self.wait(0.5)

        # ── 2. Zoom back out to full geometry ──
        self.play(
            self.camera.frame.animate.restore(),
            small_fill.animate.set_fill(opacity=0.08),
            small_edges.animate.set_stroke(opacity=0.4),
            big_fill.animate.set_fill(opacity=0.25),
            big_edges.animate.set_stroke(opacity=1.0),
            run_time=1.2, rate_func=rate_functions.ease_in_out_cubic
        )

        # Show ∠BAD = 90° (Radius meets tangent)
        sq_A = right_angle_marker(A, B, D, size=0.35, color=COLOR_GREEN, stroke_width=4).set_z_index(9)
        self.play(GrowFromCenter(sq_A), run_time=0.5)
        self.play(Flash(A, color=COLOR_GREEN, flash_radius=0.4, num_lines=8, line_stroke_width=2), run_time=0.5)
        self.wait(0.3)

        cad_arc = angle_arc(A, C, D, radius=0.45, color=COLOR_PURPLE, stroke_width=4).set_z_index(8)
        cad_tex = MathTex(r"90^\circ - \theta", font_size=32, color=COLOR_PURPLE)
        cad_tex.move_to(angle_arc(A, C, D, radius=1.0).point_from_proportion(0.5))

        self.wait(0.3)
        self.play(ReplacementTransform(sq_A,cad_arc), FadeIn(cad_tex, shift=UP * 0.1))
        self.wait(0.5)

        # Deduce ∠CDA
        self.play(Indicate(sq_C, color=COLOR_GREEN, scale_factor=1.2), run_time=0.5)

        self.wait(0.4)

        cda_arc = angle_arc(D, A, C, radius=0.5, color=RED, stroke_width=4).set_z_index(8)
        cda_tex = MathTex(r"\theta", font_size=36, color=RED)
        cda_tex.move_to(angle_arc(D, A, C, radius=0.75).point_from_proportion(0.5))

        self.play(Create(cda_arc), FadeIn(cda_tex, shift=DOWN * 0.1), run_time=0.6)
        self.wait(0.5)

        # ── 3. The Grand Conclusion (AAA) ──
        self.play(
            small_fill.animate.set_fill(opacity=0.18),
            small_edges.animate.set_stroke(opacity=1.0),
            run_time=0.6
        )

        # Highlight corresponding angle pairs visually
        self.play(
            LaggedStart(
                Indicate(theta_tex, color=COLOR_CYAN, scale_factor=1.6),
                Indicate(cda_tex, color=COLOR_CYAN, scale_factor=1.6),
                lag_ratio=0.2
            ),
            run_time=1.0
        )
        self.play(
            LaggedStart(
                Indicate(phi_tex, color=COLOR_PURPLE, scale_factor=1.6),
                Indicate(cad_tex, color=COLOR_PURPLE, scale_factor=1.6),
                lag_ratio=0.2
            ),
            run_time=1.0
        )

        self.wait(1.5)

        self.play(FadeOut(theta_tex), FadeOut(phi_tex), FadeOut(cad_tex), FadeOut(cda_tex))

        # ── THE MAGIC MOVE ──
        # ABC ~ DCA is a *mirror* similarity (scale 2.416, rotate -65.5°, flip),
        # so we realize it as a 3D card-flip-grow that lands exactly on ACD.
        # A→D, B→C, C→A. The flip lifts into z mid-move (the pirouette) and
        # returns flat at the end.
        S = [A, B, C]
        F = [D, C, A]
        Q = (A + B + C) / 3.0
        absA = float(np.linalg.norm(D - A) / np.linalg.norm(C - A))   # 2.4161
        # ψ = arg of the mirror map's complex multiplier (computed once)
        a_cx = complex(A[0], A[1]); b_cx = complex(B[0], B[1])
        c_cx = complex(C[0], C[1]); d_cx = complex(D[0], D[1])
        alpha = (d_cx - c_cx) / (a_cx.conjugate() - b_cx.conjugate())
        psi = math.atan2(alpha.imag, alpha.real)

        def _pre_end(s):
            rel = s - Q
            w = np.array([Q[0] + rel[0], Q[1] - rel[1], 0.0])     # full flip
            wx, wy = w[0] - Q[0], w[1] - Q[1]
            rx = absA * (wx * math.cos(psi) - wy * math.sin(psi))
            ry = absA * (wx * math.sin(psi) + wy * math.cos(psi))
            return np.array([Q[0] + rx, Q[1] + ry, 0.0])

        Tfix = F[0] - _pre_end(S[0])

        def morph_pt(t, s):
            rel = s - Q
            w = Q + np.array([rel[0], rel[1] * math.cos(PI * t),
                              rel[1] * math.sin(PI * t)])
            wx, wy = w[0] - Q[0], w[1] - Q[1]
            sc = 1 + (absA - 1) * t
            g = psi * t
            rx = sc * (wx * math.cos(g) - wy * math.sin(g))
            ry = sc * (wx * math.sin(g) + wy * math.cos(g))
            return np.array([Q[0] + rx, Q[1] + ry, w[2] * sc]) + t * Tfix

        morph = Polygon(A, B, C, stroke_color=COLOR_WHITE, stroke_width=4,
                        fill_color=COLOR_CYAN, fill_opacity=0.45).set_z_index(11)

        def morph_update(m, alpha_t):
            pts = [morph_pt(alpha_t, s) for s in S]
            m.set_points_as_corners([pts[0], pts[1], pts[2], pts[0]])

        self.play(UpdateFromAlphaFunc(morph, morph_update),
                  run_time=2.4, rate_func=rate_functions.ease_in_out_sine)

        # land: white flash along the coincident outline
        outline = Polygon(D, C, A, stroke_color=COLOR_WHITE, stroke_width=5,
                          fill_opacity=0).set_z_index(12)
        self.play(ShowPassingFlash(outline, time_width=0.8), run_time=0.8)
        self.wait(0.6)

        # ghost the overlay back off; restore framing for ACT 5
        self.play(
            FadeOut(morph),
            Restore(self.camera.frame),
            run_time=1.2, rate_func=rate_functions.ease_in_out_cubic,
        )
        self.wait(0.4)

        # ══════════════════════════════════════════════════════════
        #  ACT 5 · THE GOLDEN RATIO OF SIDES → cross-multiply
        # ══════════════════════════════════════════════════════════
        # First fraction BC/AC (the sides opposite θ).
        # First fraction BC/AC — the sides opposite θ (cyan).
        bc_glow = Line(B, C, color=COLOR_AMBER, stroke_width=6).set_z_index(10)
        ac_glow = Line(A, C, color=COLOR_AMBER, stroke_width=6).set_z_index(10)
        theta_arc_glow = angle_arc(A, B, C, radius=0.45, color=COLOR_AMBER, stroke_width=5).set_z_index(10)
        cda_arc_glow = angle_arc(D, A, C, radius=0.5, color=COLOR_AMBER, stroke_width=5).set_z_index(10)
        self.play(Create(bc_glow), Create(ac_glow),Create(theta_arc_glow), Create(cda_arc_glow),
                  ShowPassingFlash(Line(A, D, color=COLOR_CYAN, stroke_width=3),
                                   time_width=0.5),
                  run_time=0.9)

        def build_fraction(num_str, den_str, col, fs=50):
            num = MathTex(num_str, font_size=fs, color=col)
            den = MathTex(den_str, font_size=fs, color=col)
            w = max(num.width, den.width) + 0.20
            bar = Line(LEFT * w / 2, RIGHT * w / 2, stroke_width=3,
                       color=COLOR_WHITE)
            num.next_to(bar, UP, buff=0.12)
            den.next_to(bar, DOWN, buff=0.12)
            g = VGroup(num, bar, den)
            g.num, g.den, g.bar = num, bar, den
            return g

        frac1 = build_fraction("BC", "AC", COLOR_CYAN).move_to([2.7, 2.35, 0])
        frac1.set_z_index(11)
        f1_bg = pill_bg(frac1, fill_opacity=0.6).set_z_index(10)
        self.play(
            FadeIn(f1_bg),
            TransformFromCopy(bc_glow, frac1.num),
            TransformFromCopy(ac_glow, frac1.den),
            Create(frac1.bar),
            run_time=1.2, rate_func=rate_functions.ease_in_out_sine,
        )
        self.wait(0.4)

        # Second fraction AC/AD — the two hypotenuses (green).
        self.play(Indicate(sq_B, color=COLOR_GREEN, scale_factor=1.2),
                  Indicate(sq_C, color=COLOR_GREEN, scale_factor=1.2),
                  run_time=0.6)
        ac_glow2 = Line(A, C, color=COLOR_GREEN, stroke_width=6).set_z_index(10)
        ad_glow = Line(A, D, color=COLOR_GREEN, stroke_width=6).set_z_index(10)
        self.play(Create(ac_glow2), Create(ad_glow), run_time=0.8)

        eq_sign = MathTex("=", font_size=54).next_to(frac1, RIGHT, buff=0.45)
        eq_sign.set_z_index(11)
        frac2 = build_fraction("AC", "AD", COLOR_GREEN).next_to(eq_sign, RIGHT,
                                                                buff=0.45)
        frac2.set_z_index(11)
        prop_bg = pill_bg(VGroup(frac1.copy(), eq_sign, frac2),
                          fill_opacity=0.6).set_z_index(10)
        self.play(
            ReplacementTransform(f1_bg, prop_bg),
            FadeIn(eq_sign),
            TransformFromCopy(ac_glow2, frac2.num),
            TransformFromCopy(ad_glow, frac2.den),
            Create(frac2.bar),
            run_time=1.2, rate_func=rate_functions.ease_in_out_sine,
        )
        self.wait(0.4)
        
        self.play(FadeOut(VGroup(bc_glow, ac_glow, ac_glow2, ad_glow)),
                  run_time=0.4)
        self.wait(0.3)

        # cross-multiply, Apple-style: BC·AD (diag1) and AC·AC (diag2)
        proportion = VGroup(frac1, eq_sign, frac2)
        self.wait(0.4)

        crossed = MathTex("AC", r"\cdot", "AC", "=", "BC", r"\cdot", "AD",
                          font_size=50).move_to(proportion).set_z_index(11)
        crossed.set_color_by_tex("AC", COLOR_WHITE)
        crossed[4].set_color(COLOR_AMBER)       # BC
        crossed[6].set_color(COLOR_GREEN)        # AD
        crossed_bg = pill_bg(crossed, fill_opacity=0.6).set_z_index(10)
        self.play(
            ReplacementTransform(prop_bg, crossed_bg),
            ReplacementTransform(proportion, crossed),
            run_time=1.2, rate_func=rate_functions.ease_in_out_sine,
        )
        self.wait(0.5)

        # AC·AC collapses into AC² (the ² pops last with a tiny overshoot)
        golden = MathTex("AC^2", "=", "BC", r"\cdot", "AD", font_size=52
                         ).move_to(crossed).set_z_index(11)
        golden_bg = pill_bg(golden, fill_opacity=0.6).set_z_index(10)
        self.play(
            ReplacementTransform(crossed_bg, golden_bg),
            ReplacementTransform(crossed[0], golden[0][0:2]),   # first AC → base
            FadeOut(crossed[1], scale=0.3),                     # the middle dot
            ReplacementTransform(crossed[2], golden[0][2]),     # second AC → ²
            ReplacementTransform(crossed[3], golden[1]),
            ReplacementTransform(crossed[4], golden[2]),
            ReplacementTransform(crossed[5], golden[3]),
            ReplacementTransform(crossed[6], golden[4]),
            run_time=1.0, rate_func=rate_functions.ease_in_out_sine,
        )
        self.wait(0.6)

        # ── HERO TREATMENT: the liquid-glass card from Scene 3 ──
        dark_card = Rectangle(width=24, height=14, fill_color=COLOR_BG,
                              fill_opacity=0.55, stroke_width=0).set_z_index(12)
        glass_card = make_liquid_glass_card(width=5.0, height=2.6).set_z_index(13)
        glass_card.move_to(ORIGIN)
        golden_hero = golden.copy().scale(1.15).move_to(ORIGIN).set_z_index(14)

        self.play(
            FadeIn(dark_card),
            FadeIn(glass_card, scale=0.85, rate_func=rate_functions.ease_out_back),
            ReplacementTransform(VGroup(golden_bg, golden), golden_hero),
            run_time=1.0,
        )
        self.wait()