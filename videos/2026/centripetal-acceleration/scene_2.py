from manim import *
import numpy as np

# ─────────────────────────────────────────────
#  BRAND PALETTE  (consistent with the series)
# ─────────────────────────────────────────────
COLOR_BG        = "#0E1117"  
COLOR_GROUND    = "#8E8E93"
COLOR_GREY_BALL = "#E5E5EA"
COLOR_BLUE_BALL = "#007AFF"
COLOR_VEC_F     = "#FF3B30"
COLOR_VEC_V     = "#32ADE6"
COLOR_GREEN     = "#34C759"
COLOR_AMBER     = "#FFCC00"
COLOR_PINK      = "#FF2D55"
COLOR_PURPLE    = "#AF52DE"
COLOR_ORANGE    = "#FF9500"
COLOR_WHITE     = "#E5E5EA"
COLOR_CYAN      = "#32ADE6"


HAND_CENTER   = ORIGIN
ORBIT_RADIUS  = 2.3
MIN_VEC_LEN   = 0.02


# ═══════════════════════════════════════════════════════════════════
#  HELPERS  (consistent with the rest of the series)
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

def make_ball(color, radius=0.28):
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

def make_liquid_glass_card(width, height):
    """Creates a glassmorphism card with an iridescent rim and glossy sheen."""
    card = VGroup()

    # 1. The Base Plate: Semi-transparent to let the background peak through
    base = RoundedRectangle(
        corner_radius=0.3,
        width=width,
        height=height,
        fill_color=COLOR_GREY_BALL,
        fill_opacity=0.12, 
        stroke_width=0
    )

    # 2. The Specular Highlight: A soft wash of white that fades out, faking surface reflection
    highlight = RoundedRectangle(
        corner_radius=0.3,
        width=width,
        height=height,
        fill_color=COLOR_WHITE,
        fill_opacity=0.08,
        stroke_width=0
    )
    # Sheen directs the gradient fade. -0.5 pulls it to the top left.
    highlight.set_sheen(-0.5, UL) 

    # 3. The Iridescent Rim: Simulates chromatic refraction on the glass edge
    rim = RoundedRectangle(
        corner_radius=0.3,
        width=width,
        height=height,
        stroke_width=2.5,
        fill_opacity=0
    )
    # Using your Apple palette to create that colorful edge
    rim.set_color([COLOR_PURPLE, COLOR_CYAN, COLOR_GREEN, COLOR_PINK])
    rim.set_stroke(opacity=0.85)

    card.add(base, highlight, rim)
    return card

def make_center_point(scale=1.0):
    """The grip/anchor at the orbit center: a dot with an addressable
    strain-shimmer ring we can pulse without touching the dot.
    NOTE: this is the single anchor helper for the whole scene — Acts 4
    and 5 route through here too (no separate make_hand_anchor)."""
    g = VGroup()
    dot = Dot(point=ORIGIN, radius=0.05 * scale, color=COLOR_GREY_BALL)
    dot.set_fill(COLOR_GREY_BALL, opacity=1.0)
    shimmer = Circle(radius=0.18 * scale,
                     stroke_color=COLOR_VEC_F, stroke_width=3,
                     stroke_opacity=0.0, fill_opacity=0)
    g.add(shimmer, dot)
    g.shimmer = shimmer
    return g


def make_stone(radius=0.26):
    """Generates a static, non-random irregular stone to preserve caching."""
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

    spec_data = [
        (0.3 * radius, 1.2, 0.08 * radius),
        (0.5 * radius, 3.5, 0.06 * radius),
        (0.25 * radius, 5.0, 0.09 * radius)
    ]
    for r, a, sr in spec_data:
        spec = Dot(point=np.array([r * np.cos(a), r * np.sin(a), 0]),
                   radius=sr, color="#3A3A3C")
        spec.set_fill("#3A3A3C", opacity=0.75)
        g.add(spec)

    return g


def safe_put(arrow, start, end):
    if np.linalg.norm(end - start) < MIN_VEC_LEN:
        end = start + (end - start) / max(np.linalg.norm(end - start), 1e-6) * MIN_VEC_LEN
    arrow.put_start_and_end_on(start, end)


def orbit_point(center, radius, angle):
    return center + radius * np.array([np.cos(angle), np.sin(angle), 0])


# ═══════════════════════════════════════════════════════════════════
#  SCENE 2 · The String, the Stone, and the Pull Toward Center
# ═══════════════════════════════════════════════════════════════════

class Scene2_PullTowardCenter(MovingCameraScene):
    def construct(self):
        self.camera.background_color = COLOR_BG
        grid = build_grid()
        grid.set_z_index(-10)
        self.add(grid)
        self.camera.frame.save_state()

        # ══════════════════════════════════════════════════════════
        #  ACT 0 · BRINGING THE BOY IN FIRST
        # ══════════════════════════════════════════════════════════
        boy = ImageMobject("cartoon.png")
        boy.height = 3.0
        _px_scale = 3.0 / 850.0

        boy.move_to(np.array([
            -(315 - 280) * _px_scale,
            -(425 - 66) * _px_scale,
            0
        ]))
        boy.set_z_index(-3)

        hand = make_center_point().move_to(HAND_CENTER).set_z_index(4)

        self.play(FadeIn(boy, shift=UP * 0.15), FadeIn(hand, scale=0.6), run_time=0.8)
        self.wait(0.2)

        # ══════════════════════════════════════════════════════════
        #  ACT 1 · THE INVITATION — the stone in your hand
        # ══════════════════════════════════════════════════════════

        stone = make_ball(COLOR_GREY_BALL, radius=0.06).move_to(HAND_CENTER)
        stone.set_z_index(5)
        self.play(FadeIn(stone, scale=0.4), run_time=0.7)

        self.wait(0.4)

        string = Line(HAND_CENTER, orbit_point(HAND_CENTER, ORBIT_RADIUS, PI / 2),
                      color=COLOR_GREY_BALL, stroke_width=2.5, stroke_opacity=0.9)
        string.set_z_index(2)

        stone_target = orbit_point(HAND_CENTER, ORBIT_RADIUS, PI / 2)
        self.play(
            Create(string),
            stone.animate.move_to(stone_target),
            run_time=1.0,
            rate_func=rate_functions.ease_out_cubic
        )

        big_stone = make_stone(radius=0.26).move_to(stone_target)
        big_stone.set_z_index(5)
        self.play(ReplacementTransform(stone, big_stone),
                  run_time=0.6, rate_func=rate_functions.ease_out_back)
        stone = big_stone

        self.wait(0.5)

        theta = ValueTracker(PI / 2)

        def stone_pos():
            return orbit_point(HAND_CENTER, ORBIT_RADIUS, theta.get_value())

        stone.add_updater(lambda m: m.move_to(stone_pos()))
        string.add_updater(lambda m: m.put_start_and_end_on(HAND_CENTER, stone_pos()))

        TRAIL_LIFETIME = 0.6
        trail = TracedPath(
            stone.get_center,
            stroke_color=COLOR_GREY_BALL,
            stroke_width=4,
            stroke_opacity=0.55,
            dissipating_time=TRAIL_LIFETIME
        ).set_z_index(1)

        self.add(trail)

        STEADY_OMEGA = TAU * 2.0 / 2.4
        RAMP_TIME    = 1.6
        STEADY_TIME  = 2.4

        ramp_angle_gain = STEADY_OMEGA * RAMP_TIME / 2.0
        steady_angle_gain = STEADY_OMEGA * STEADY_TIME

        def smooth_ramp(t):
            return t * t

        start_theta = theta.get_value()

        self.play(
            theta.animate.set_value(start_theta + ramp_angle_gain),
            run_time=RAMP_TIME,
            rate_func=smooth_ramp
        )

        mid_theta = theta.get_value()
        self.play(
            theta.animate.set_value(mid_theta + steady_angle_gain),
            run_time=STEADY_TIME,
            rate_func=linear
        )

        # ══════════════════════════════════════════════════════════
        #  ACT 2 · WHAT DOES YOUR HAND FEEL? — tension made visible
        # ══════════════════════════════════════════════════════════
  
        cur = theta.get_value()
        target = (np.ceil((cur - PI / 2) / TAU)) * TAU + PI / 2
        self.play(theta.animate.set_value(target),
                  run_time=0.9, rate_func=rate_functions.ease_out_cubic)

        FREEZE_ANGLE = PI / 2

        stone.clear_updaters()
        string.clear_updaters()
        self.wait(TRAIL_LIFETIME)
        self.remove(trail)

        stone.move_to(orbit_point(HAND_CENTER, ORBIT_RADIUS, FREEZE_ANGLE))
        string.put_start_and_end_on(HAND_CENTER, stone.get_center())

        self.wait(0.4)

        out_arrow = Arrow(
            HAND_CENTER,
            HAND_CENTER + UP * 1.0,
            color=COLOR_VEC_F, buff=0, stroke_width=5,
            max_tip_length_to_length_ratio=0.28
        ).set_z_index(6)
        out_lbl = Text("pulls outward", font="Segoe UI", font_size=20,
                       color=COLOR_VEC_F, weight=BOLD)
        out_lbl.next_to(out_arrow, RIGHT, buff=0.18)


        in_arrow = Arrow(
            stone.get_center(),
            stone.get_center() + DOWN * 1.0,
            color=COLOR_VEC_F, buff=0, stroke_width=5,
            max_tip_length_to_length_ratio=0.28
        ).set_z_index(6)
        in_lbl = Text("you hold it in", font="Segoe UI", font_size=20,
                      color=COLOR_VEC_F, weight=BOLD)
        in_lbl.next_to(in_arrow, RIGHT, buff=0.18)

        self.play(GrowArrow(out_arrow), FadeIn(out_lbl, shift=RIGHT * 0.1),
                  run_time=0.6)
        self.play(GrowArrow(in_arrow), FadeIn(in_lbl, shift=RIGHT * 0.1),
                  run_time=0.6)

        self.play(
            out_arrow.animate.scale(1.12),
            in_arrow.animate.scale(1.12),
            hand.shimmer.animate.set_stroke(opacity=0.7),
            run_time=0.4, rate_func=rate_functions.ease_out_sine
        )
        self.play(
            out_arrow.animate.scale(1 / 1.12),
            in_arrow.animate.scale(1 / 1.12),
            hand.shimmer.animate.set_stroke(opacity=0.0),
            run_time=0.4, rate_func=rate_functions.ease_in_out_sine
        )
        self.wait(0.5)

        question = Text("but why you have to pull?", font="Segoe UI",
                        font_size=34, color=COLOR_WHITE, weight=BOLD)
        question.to_edge(UP, buff=1.4).set_z_index(6)

        self.play(
            FadeOut(out_arrow), FadeOut(out_lbl),
            FadeOut(in_lbl),
            string.animate.set_stroke(opacity=0.25),
            stone.animate.set_opacity(0.55),
            FadeIn(question, shift=DOWN * 0.15),
            run_time=0.8
        )

        for _ in range(2):
            self.play(in_arrow.animate.scale(1.15),
                      run_time=0.5, rate_func=rate_functions.ease_out_sine)
            self.play(in_arrow.animate.scale(1 / 1.15),
                      run_time=0.5, rate_func=rate_functions.ease_in_sine)
        self.wait(0.6)

        self.play(
            FadeOut(question, shift=UP * 0.15),
            FadeOut(in_arrow), FadeOut(string),
            FadeOut(stone),
            FadeOut(boy, shift=DOWN * 0.2),
            FadeOut(hand),
            run_time=0.6
        )

        # ══════════════════════════════════════════════════════════
        #  ACT 3 · NEWTON ANSWERS — the stone wants to fly straight
        # ══════════════════════════════════════════════════════════

        stone = make_stone(radius=0.26).set_z_index(5)
        top = orbit_point(HAND_CENTER, ORBIT_RADIUS, FREEZE_ANGLE)   # 12 o'clock
        stone.move_to(top)
        string = Line(HAND_CENTER, top,
                      color=COLOR_GREY_BALL, stroke_width=2.5,
                      stroke_opacity=0.9).set_z_index(2)
        orbit_ref = Circle(radius=ORBIT_RADIUS, color=COLOR_GREY_BALL,
                           stroke_width=1.5, stroke_opacity=0.18).move_to(HAND_CENTER)
        orbit_ref.set_z_index(0)

        self.play(
            FadeIn(orbit_ref),
            FadeIn(stone, scale=0.7),
            Create(string),
            run_time=0.7
        )
        self.wait(0.3)

        tangent_dir = np.array([-np.sin(FREEZE_ANGLE), np.cos(FREEZE_ANGLE), 0])
        intended = Arrow(
            top, top + tangent_dir * 2.4,
            color=COLOR_VEC_V, buff=0, stroke_width=5,
            max_tip_length_to_length_ratio=0.18
        ).set_z_index(4)
        intended_lbl = Text("wants to fly straight", font="Segoe UI",
                            font_size=22, color=COLOR_VEC_V, weight=BOLD)
        intended_lbl.next_to(intended, UP, buff=0.18)

        self.play(
            string.animate.set_stroke(opacity=0.18),
            GrowArrow(intended),
            FadeIn(intended_lbl, shift=LEFT * 0.1),
            run_time=0.8, rate_func=rate_functions.ease_out_cubic
        )
        self.wait(0.6)

        self.play(
            string.animate.set_stroke(opacity=0.9),
            FadeOut(intended, shift=tangent_dir * 0.2),
            FadeOut(intended_lbl, shift=tangent_dir * 0.2),
            run_time=0.5, rate_func=rate_functions.ease_in_back
        )
        self.wait(0.3)

        self.play(FadeOut(stone), FadeOut(string), run_time=0.4)

        snapshot_angles = [PI / 2, PI, -PI / 2, 0]   # 12, 3, 6, 9 o'clock
        inward_arrows = VGroup()
        snapshot_extras = VGroup()   # dots + ghost tangents, tracked for cleanup
        for ang in snapshot_angles:
            p = orbit_point(HAND_CENTER, ORBIT_RADIUS, ang)
            # tangent (cyan, faint) — perpendicular to radius, CCW direction
            tan_dir = np.array([-np.sin(ang), np.cos(ang), 0])
            ghost_tan = Arrow(
                p, p + tan_dir * 1.3,
                color=COLOR_VEC_V, buff=0, stroke_width=3,
                max_tip_length_to_length_ratio=0.2,
                stroke_opacity=0.45
            ).set_z_index(3)
            ghost_tan.set_fill(opacity=0.45)
            # inward (red, bright) — radius direction, toward center
            in_dir = (HAND_CENTER - p) / np.linalg.norm(HAND_CENTER - p)
            inw = Arrow(
                p, p + in_dir * 0.9,
                color=COLOR_VEC_F, buff=0, stroke_width=5,
                max_tip_length_to_length_ratio=0.28
            ).set_z_index(4)
            inward_arrows.add(inw)
            dot = Dot(p, radius=0.06, color=COLOR_GREY_BALL).set_z_index(5)
            self.play(
                FadeIn(dot, scale=0.5),
                GrowArrow(ghost_tan),
                GrowArrow(inw),
                run_time=0.45
            )
            self.add(dot, ghost_tan)
            snapshot_extras.add(dot, ghost_tan)
        self.wait(0.6)

        label = VGroup(
            Text("centripetal", font="Segoe UI", font_size=40,
                 weight=BOLD, color=COLOR_VEC_F),
            Text("acceleration", font="Segoe UI", font_size=28,
                 weight=BOLD, color=COLOR_AMBER),
        ).arrange(DOWN, buff=0.12).move_to(HAND_CENTER)
        label.set_z_index(8)
        label_bg = RoundedRectangle(
            corner_radius=0.12,
            width=label.width + 0.5, height=label.height + 0.35,
            fill_color=COLOR_BG, fill_opacity=0.9, stroke_width=0
        ).move_to(HAND_CENTER).set_z_index(7)

        self.play(
            LaggedStart(
                *[arr.animate.scale(0.3, about_point=HAND_CENTER).set_opacity(0)
                  for arr in inward_arrows],
                lag_ratio=0.08
            ),
            FadeIn(label_bg),
            FadeIn(label, scale=0.85),
            run_time=1.2, rate_func=rate_functions.ease_in_out_sine
        )
        self.wait(0.8)

        diagram_now = Group(orbit_ref, snapshot_extras, inward_arrows,
                            label_bg, label)
        self.play(
            diagram_now.animate.shift(LEFT * 2.6),
            self.camera.frame.animate.move_to(RIGHT * 1.2),
            run_time=1.0, rate_func=rate_functions.ease_in_out_sine
        )

        # ── LIQUID GLASS CARD REVEAL ──
        glass_card = make_liquid_glass_card(width=4.5, height=2.8)
        glass_card.move_to(RIGHT * 3.4 + UP * 0.3)
        glass_card.set_z_index(7) # Ensure it sits above the background grid
        
        self.play(FadeIn(glass_card, shift=UP * 0.1), run_time=0.8, rate_func=rate_functions.ease_out_cubic)

        # ── TEXT ON TOP OF THE GLASS ──
        root1 = VGroup(
            Text("Centrum", font="Segoe UI", font_size=30, slant=ITALIC,
                 weight=BOLD, color=COLOR_AMBER),
            Text("center", font="Segoe UI", font_size=22, color=COLOR_GROUND),
        ).arrange(RIGHT, buff=0.35)
        
        root2 = VGroup(
            Text("Petere", font="Segoe UI", font_size=30, slant=ITALIC,
                 weight=BOLD, color=COLOR_AMBER),
            Text("to seek", font="Segoe UI", font_size=22, color=COLOR_GROUND),
        ).arrange(RIGHT, buff=0.35)
        
        roots = VGroup(root1, root2).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        # Center the text precisely on the glass card
        roots.move_to(glass_card.get_center())
        roots.set_z_index(8)

        self.play(FadeIn(root1, shift=RIGHT * 0.2), run_time=0.6)
        self.play(FadeIn(root2, shift=RIGHT * 0.2), run_time=0.6)
        self.wait(0.5)

        reassembled = Text("centri·petal", font="Segoe UI", font_size=36,
                           weight=BOLD, color=COLOR_WHITE,
                           t2c={"centri": COLOR_AMBER, "petal": COLOR_AMBER})
        
        gloss = Text("= seeks the center", font="Segoe UI", font_size=22,
                     color=COLOR_GROUND, slant=ITALIC)
        
        reassembled_group = VGroup(reassembled, gloss).arrange(DOWN, buff=0.35)
        reassembled_group.move_to(glass_card.get_center())
        reassembled_group.set_z_index(8)

        self.play(
            ReplacementTransform(VGroup(root1, root2), reassembled),
            run_time=0.9, rate_func=rate_functions.ease_in_out_sine
        )
        self.play(FadeIn(gloss, shift=UP * 0.1), run_time=0.5)
        self.wait(1.0)

        self.play(
            FadeOut(reassembled_group, shift=RIGHT * 0.3),
            FadeOut(glass_card, shift=RIGHT * 0.3), # Fade the card out with the text
            diagram_now.animate.shift(RIGHT * 2.6),
            self.camera.frame.animate.move_to(ORIGIN),
            run_time=1.0, rate_func=rate_functions.ease_in_out_sine
        )
        self.wait(0.4)

        clear_3 = Group(*[m for m in self.mobjects
                          if m is not grid])
        self.play(FadeOut(clear_3), run_time=0.7)

        # ══════════════════════════════════════════════════════════
        #  ACT 4 · TWO EXPERIMENTS — spin faster / lengthen the string
        #  Split-screen. The inward RED arrow is the through-line variable.
        # ══════════════════════════════════════════════════════════
        divider = DashedLine(UP * 3.4, DOWN * 3.4, color=COLOR_GROUND,
                             stroke_width=1.5, stroke_opacity=0.35,
                             dash_length=0.18)
        self.play(Create(divider), run_time=0.6)

        # ---- LEFT PANEL: Experiment 1 — spin faster, same length ----
        L_center = LEFT * 3.5 + DOWN * 0.3
        exp1_title = Text("Spin faster", font="Segoe UI", font_size=24,
                          weight=BOLD, color=COLOR_VEC_V).move_to(LEFT * 3.5 + UP * 2.6)
        R1 = 1.45
        hand1 = make_center_point(scale=0.8).move_to(L_center).set_z_index(4)
        orbit1 = Circle(radius=R1, color=COLOR_GREY_BALL, stroke_width=1.5,
                        stroke_opacity=0.18).move_to(L_center)
        stone1 = make_stone(radius=0.20).set_z_index(5)
        th1 = ValueTracker(0.0)

        def s1_pos():
            return orbit_point(L_center, R1, th1.get_value())
        stone1.move_to(s1_pos())
        str1 = Line(L_center, s1_pos(), color=COLOR_GREY_BALL,
                    stroke_width=2, stroke_opacity=0.8).set_z_index(2)

        self.play(
            FadeIn(exp1_title, shift=DOWN * 0.1),
            FadeIn(orbit1), FadeIn(hand1, scale=0.6),
            FadeIn(stone1, scale=0.7), Create(str1),
            run_time=0.7
        )

        stone1.add_updater(lambda m: m.move_to(s1_pos()))
        str1.add_updater(lambda m: m.put_start_and_end_on(L_center, s1_pos()))

        # Inward arrow grows as speed rises. Its length is driven by a
        # tracker that we ramp alongside angular speed.
        in1_len = ValueTracker(0.45)

        def make_in1():
            p = s1_pos()
            d = (L_center - p) / np.linalg.norm(L_center - p)
            return Arrow(p, p + d * in1_len.get_value(),
                         color=COLOR_VEC_F, buff=0,
                         stroke_width=3 + in1_len.get_value() * 4,
                         max_tip_length_to_length_ratio=0.3).set_z_index(6)
        in1 = always_redraw(make_in1)
        self.add(in1)

        # Pull meter (left).
        meter1_track = RoundedRectangle(corner_radius=0.175, width=0.35,
                                        height=2.0, stroke_color=COLOR_GROUND,
                                        stroke_width=1.5, fill_opacity=0)
        meter1_track.move_to(LEFT * 6.0 + DOWN * 0.3)
        meter1_fill_v = ValueTracker(0.2)

        def make_meter1():
            h = max(0.001, 2.0 * meter1_fill_v.get_value())
            f = RoundedRectangle(corner_radius=0.135, width=0.27, height=h,
                                 fill_color=COLOR_VEC_F, fill_opacity=0.9,
                                 stroke_width=0)
            f.move_to(meter1_track.get_bottom() + UP * (h / 2))
            return f
        meter1_fill = always_redraw(make_meter1)
        meter1_lbl = Text("pull", font="Segoe UI", font_size=16,
                          color=COLOR_GROUND).next_to(meter1_track, DOWN, buff=0.15)
        self.add(meter1_track, meter1_fill, meter1_lbl)

        # Slow spin first.
        self.play(th1.animate.set_value(TAU * 1.0), run_time=1.4, rate_func=linear)
        # Crank speed: faster rotation + arrow grows + meter fills + shimmer.
        # ── POST CUE: rising pitch tone as the arrow grows. ──
        self.play(
            th1.animate.set_value(TAU * 1.0 + TAU * 4.4),
            in1_len.animate.set_value(1.05),
            meter1_fill_v.animate.set_value(0.85),
            hand1.shimmer.animate.set_stroke(opacity=0.6),
            run_time=3.6, rate_func=rate_functions.ease_in_sine
        )
        stone1.clear_updaters()
        str1.clear_updaters()
        self.wait(0.4)

        # ---- RIGHT PANEL: Experiment 2 — longer string, same speed ----
        R_center = RIGHT * 3.3 + DOWN * 0.3
        exp2_title = Text("Longer string", font="Segoe UI", font_size=24,
                          weight=BOLD, color=COLOR_PINK).move_to(RIGHT * 3.3 + UP * 2.6)
        R2_small = 1.0
        R2_big = 2.0
        R2 = ValueTracker(R2_small)
        hand2 = make_center_point(scale=0.8).move_to(R_center).set_z_index(4)
        # faint old (tight) circle stays for contrast; bright new (wide) circle.
        orbit2_old = Circle(radius=R2_small, color=COLOR_PINK, stroke_width=1.5,
                            stroke_opacity=0.25).move_to(R_center)
        stone2 = make_stone(radius=0.26).set_z_index(5)
        th2 = ValueTracker(0.0)

        def s2_pos():
            return orbit_point(R_center, R2.get_value(), th2.get_value())
        stone2.move_to(s2_pos())
        str2 = Line(R_center, s2_pos(), color=COLOR_GREY_BALL,
                    stroke_width=2, stroke_opacity=0.8).set_z_index(2)
        orbit2_new = always_redraw(lambda: Circle(
            radius=R2.get_value(), color=COLOR_GREY_BALL, stroke_width=1.5,
            stroke_opacity=0.30).move_to(R_center))

        self.play(
            FadeIn(exp2_title, shift=DOWN * 0.1),
            FadeIn(orbit2_old),
            FadeIn(hand2, scale=0.6),
            FadeIn(stone2, scale=0.7), Create(str2),
            run_time=0.7
        )
        self.add(orbit2_new)

        stone2.add_updater(lambda m: m.move_to(s2_pos()))
        str2.add_updater(lambda m: m.put_start_and_end_on(R_center, s2_pos()))

        # inward arrow SHRINKS as the curve gentles. Same red arrow.
        in2_len = ValueTracker(0.95)

        def make_in2():
            p = s2_pos()
            d = (R_center - p) / np.linalg.norm(R_center - p)
            return Arrow(p, p + d * in2_len.get_value(),
                         color=COLOR_VEC_F, buff=0,
                         stroke_width=3 + in2_len.get_value() * 4,
                         max_tip_length_to_length_ratio=0.3).set_z_index(6)
        in2 = always_redraw(make_in2)
        self.add(in2)

        # Pull meter (right) starts high.
        meter2_track = RoundedRectangle(corner_radius=0.175, width=0.35,
                                        height=2.0, stroke_color=COLOR_GROUND,
                                        stroke_width=1.5, fill_opacity=0)
        meter2_track.move_to(RIGHT * 6.0 + DOWN * 0.3)
        meter2_fill_v = ValueTracker(0.8)

        def make_meter2():
            h = max(0.001, 2.0 * meter2_fill_v.get_value())
            f = RoundedRectangle(corner_radius=0.135, width=0.27, height=h,
                                 fill_color=COLOR_VEC_F, fill_opacity=0.9,
                                 stroke_width=0)
            f.move_to(meter2_track.get_bottom() + UP * (h / 2))
            return f
        meter2_fill = always_redraw(make_meter2)
        meter2_lbl = Text("pull", font="Segoe UI", font_size=16,
                          color=COLOR_GROUND).next_to(meter2_track, DOWN, buff=0.15)
        self.add(meter2_track, meter2_fill, meter2_lbl)

        # Same speed throughout (linear). Lengthen the string: radius grows,
        # arc gentles, inward arrow shrinks, meter drops.
        # ── POST CUE: falling tone as the arrow shrinks. ──
        self.play(th2.animate.set_value(TAU * 0.8), run_time=1.2, rate_func=linear)
        self.play(
            th2.animate.set_value(TAU * 0.8 + TAU * 3.2),
            R2.animate.set_value(R2_big),
            in2_len.animate.set_value(0.40),
            meter2_fill_v.animate.set_value(0.30),
            run_time=4.0, rate_func=linear
        )
        stone2.clear_updaters()
        str2.clear_updaters()
        self.wait(0.6)

        # Sweep Act 4 out. Detach the always_redraw mobjects' updaters first
        # so they don't keep redrawing while/after they fade.
        in1.clear_updaters()
        in2.clear_updaters()
        orbit2_new.clear_updaters()
        meter1_fill.clear_updaters()
        meter2_fill.clear_updaters()

        clear_4 = Group(*[m for m in self.mobjects
                          if m is not grid])
        self.play(FadeOut(clear_4), run_time=0.8)

        # ══════════════════════════════════════════════════════════
        #  ACT 5 · THE CLIFFHANGER — enter Huygens
        # ══════════════════════════════════════════════════════════
        # A calm steady spin settles, pushed into the background; the name
        # rises with restraint; a faint "a = ?" lingers by the stone.
        calm_stone = make_stone(radius=0.26).set_z_index(3)
        calm_orbit = Circle(radius=1.7, color=COLOR_GREY_BALL, stroke_width=1.5,
                            stroke_opacity=0.18).move_to(ORIGIN)
        calm_hand = make_center_point(scale=0.8).move_to(ORIGIN).set_z_index(2)
        th5 = ValueTracker(0.0)

        def s5_pos():
            return orbit_point(ORIGIN, 1.7, th5.get_value())
        calm_stone.move_to(s5_pos())
        calm_str = Line(ORIGIN, s5_pos(), color=COLOR_GREY_BALL,
                        stroke_width=2, stroke_opacity=0.7).set_z_index(1)

        self.play(
            FadeIn(calm_orbit), FadeIn(calm_hand, scale=0.6),
            FadeIn(calm_stone, scale=0.7), Create(calm_str),
            run_time=0.7
        )
        calm_stone.add_updater(lambda m: m.move_to(s5_pos()))
        calm_str.add_updater(lambda m: m.put_start_and_end_on(ORIGIN, s5_pos()))
        calm_blur = TracedPath(calm_stone.get_center, stroke_color=COLOR_GREY_BALL,
                               stroke_width=3, stroke_opacity=0.4,
                               dissipating_time=0.5).set_z_index(1)
        self.add(calm_blur)

        # gentle continuous spin while we dim into the background
        self.play(th5.animate.set_value(TAU * 1.2), run_time=2.4, rate_func=linear)

        calm_stone.clear_updaters()
        calm_str.clear_updaters()
        self.remove(calm_blur)

        calm_group = VGroup(calm_orbit, calm_hand, calm_stone, calm_str)
        self.play(
            calm_group.animate.set_opacity(0.3),
            run_time=0.8, rate_func=rate_functions.ease_in_out_sine
        )

        # faint "a = ?" lingering near the stone's last position
        a_q = MathTex("a = ?", font_size=40, color=COLOR_AMBER).set_opacity(0.7)
        a_q.next_to(calm_stone, UR, buff=0.2)
        self.play(FadeIn(a_q, shift=UP * 0.1), run_time=0.6)
        self.wait(0.4)

        # ══════════════════════════════════════════════════════════
        #  CLOSING CHALLENGE — step away from the screen (series rule)
        # ══════════════════════════════════════════════════════════
        self.play(
            FadeOut(calm_group), FadeOut(a_q),
            run_time=0.8
        )
        self.wait(0.5)