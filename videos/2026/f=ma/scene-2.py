from manim import *
import numpy as np

# ─────────────────────────────────────────────
#  BRAND PALETTE
# ─────────────────────────────────────────────
COLOR_BG        = "#1C1C1E"
COLOR_GROUND    = "#8E8E93"
COLOR_GREY_BALL = "#E5E5EA"
COLOR_BLUE_BALL = "#007AFF"
COLOR_VEC_G     = "#FF3B30"
COLOR_VEC_V_X   = "#32ADE6"
COLOR_GREEN     = "#34C759"
COLOR_AMBER     = "#FFCC00"
COLOR_PINK      = "#FF2D55"
COLOR_PURPLE    = "#BF5AF2"
COLOR_ORANGE    = "#FF9500"
COLOR_WHITE     = "#E5E5EA"


# ═══════════════════════════════════════════════════════════════════
#  HELPERS
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
            op = peak_op * 0.25 * (1 - (2 * t - 1) ** 2)
            segs.add(Line(p1, p2, stroke_opacity=op,
                          stroke_width=1, color=COLOR_WHITE))
        return segs

    for x in np.arange(-max_x, max_x + 0.1, spacing):
        peak = 0.2 * (1 - (abs(x) / max_x) ** 1.5)
        if peak > 0:
            grid.add(fading_line(UP * max_y + RIGHT * x,
                                 DOWN * max_y + RIGHT * x, peak))
    for y in np.arange(-max_y, max_y + 0.1, spacing):
        peak = 0.2 * (1 - (abs(y) / max_y) ** 1.5)
        if peak > 0:
            grid.add(fading_line(LEFT * max_x + UP * y,
                                 RIGHT * max_x + UP * y, peak))
    return grid


def text_bg(text_mob, fill_color=COLOR_BG, fill_opacity=0.85,
            pad_x=0.25, pad_y=0.20, stroke=False,
            stroke_color=COLOR_WHITE, stroke_opacity=0.3):
    bg = RoundedRectangle(
        corner_radius=0.1,
        width=text_mob.width + pad_x * 2,
        height=text_mob.height + pad_y * 2,
        fill_color=fill_color, fill_opacity=fill_opacity,
        stroke_width=1 if stroke else 0,
        stroke_color=stroke_color,
        stroke_opacity=stroke_opacity if stroke else 0
    ).move_to(text_mob.get_center()).set_z_index(text_mob.get_z_index() - 1)
    return VGroup(bg, text_mob)


def make_cycle(scale=1.0):
    img = ImageMobject("bicycle.png") 
    img.scale(scale)
    return img


def make_truck(scale=1.0):
    img = ImageMobject("truck.png")
    img.scale(scale)
    return img

def make_person(color=COLOR_WHITE, scale=1.0):
    """Simple stick-figure 'YOU'."""
    g = VGroup()
    s = scale

    head = Circle(radius=0.16 * s, color=color, stroke_width=2.5,
                  fill_color=color, fill_opacity=0.45)
    head.move_to(UP * 0.7 * s)

    body = Line(UP * 0.54 * s, DOWN * 0.3 * s,
                color=color, stroke_width=4)
    arm_l = Line(UP * 0.32 * s, LEFT * 0.28 * s,
                 color=color, stroke_width=3.5)
    arm_r = Line(UP * 0.32 * s, RIGHT * 0.28 * s,
                 color=color, stroke_width=3.5)
    leg_l = Line(DOWN * 0.3 * s, DOWN * 0.75 * s + LEFT * 0.20 * s,
                 color=color, stroke_width=3.5)
    leg_r = Line(DOWN * 0.3 * s, DOWN * 0.75 * s + RIGHT * 0.20 * s,
                 color=color, stroke_width=3.5)

    g.add(head, body, arm_l, arm_r, leg_l, leg_r)
    return g


def place_on_ground(mob, x_position, ground_y):
    """Position a mobject so its bottom sits on the ground at given x."""
    mob.shift(np.array([
        x_position - mob.get_x(),
        ground_y - mob.get_bottom()[1],
        0
    ]))
    return mob


# ═══════════════════════════════════════════════════════════════════
#  SCENE 2 · The Mass Matters — discovering F ∝ m
# ═══════════════════════════════════════════════════════════════════

class Scene2_MassMatters(Scene):
    def construct(self):
        self.camera.background_color = COLOR_BG
        grid = build_grid()
        grid.set_z_index(-10)
        self.add(grid)

        # ══════════════════════════════════════════════════════════
        #  ACT 1 · INTRO — "Imagine this..."
        # ══════════════════════════════════════════════════════════

        eyebrow = Text(
            "A THOUGHT EXPERIMENT",
            font="Segoe UI", font_size=18,
            weight=BOLD, color=COLOR_GROUND
        )
        eyebrow_l = Line(LEFT * 0.5, ORIGIN,
                         color=COLOR_GROUND, stroke_width=1, stroke_opacity=0.6)
        eyebrow_r = Line(ORIGIN, RIGHT * 0.5,
                         color=COLOR_GROUND, stroke_width=1, stroke_opacity=0.6)
        eyebrow_l.next_to(eyebrow, LEFT, buff=0.25)
        eyebrow_r.next_to(eyebrow, RIGHT, buff=0.25)
        eyebrow_group = VGroup(eyebrow_l, eyebrow, eyebrow_r).move_to(UP * 0.5)

        intro_text = Text(
            "Imagine this...",
            font="Segoe UI", font_size=44,
            color=COLOR_WHITE, weight=BOLD
        ).move_to(DOWN * 0.3)

        self.play(
            FadeIn(eyebrow, shift=UP * 0.15),
            Create(eyebrow_l), Create(eyebrow_r)
        )
        self.play(
            FadeIn(intro_text, shift=UP * 0.2),
            run_time=1.0,
            rate_func=rate_functions.ease_out_cubic
        )
        self.wait()

        self.play(
            FadeOut(eyebrow_group, shift=UP * 0.2),
            FadeOut(intro_text, shift=UP * 0.2),
            run_time=0.5
        )

        # ══════════════════════════════════════════════════════════
        #  ACT 2 · THE CYCLE COLLIDES
        # ══════════════════════════════════════════════════════════

        GROUND_Y = -2.5
        ground = Line(LEFT * 7, RIGHT * 7,
                      color=COLOR_GROUND, stroke_width=2)
        ground.move_to([0, GROUND_Y, 0])

        PERSON_X = 3.8
        person = make_person(color=COLOR_WHITE, scale=1.0).set_z_index(3)
        place_on_ground(person, PERSON_X, GROUND_Y)

        person_label = Text("YOU", font="Segoe UI", font_size=15,
                            color=COLOR_GROUND, weight=BOLD)
        person_label.next_to(person, UP, buff=0.25)

        self.play(
            Create(ground),
            FadeIn(person, scale=0.92),
            FadeIn(person_label, shift=DOWN * 0.1),
            run_time=1.0,
            rate_func=rate_functions.ease_out_cubic
        )
        self.wait(0.4)

        # Cycle enters from left
        CYCLE_START_X = -5.5
        cycle = make_cycle(scale=0.5).set_z_index(2)
        place_on_ground(cycle, CYCLE_START_X, GROUND_Y)

        cycle_speed = MathTex(
            r"v = 10 \text{ km/h}",
            font_size=28, color=COLOR_BLUE_BALL
        )
        cycle_speed.next_to(cycle, UP, buff=0.5)

        cycle_arrow = Arrow(
            cycle.get_right() + RIGHT * 0.15,
            cycle.get_right() + RIGHT * 0.85,
            color=COLOR_BLUE_BALL, stroke_width=4, buff=0,
            max_tip_length_to_length_ratio=0.25
        )

        self.play(
            FadeIn(cycle, shift=RIGHT * 0.3),
            FadeIn(cycle_speed, shift=DOWN * 0.15),
            GrowArrow(cycle_arrow),
            run_time=0.8
        )
        self.wait(0.6)

        # Cycle approaches person
        cycle_group = Group(cycle, cycle_speed, cycle_arrow)
        impact_x_cycle = PERSON_X - 0.85
        travel_dist_c = impact_x_cycle - CYCLE_START_X

        self.play(
            cycle_group.animate.shift(RIGHT * travel_dist_c),
            run_time=1.6,
            rate_func=linear
        )

        # Mild impact — small ripple, person rocks back
        ripple_c = Circle(radius=0.32, color=COLOR_BLUE_BALL,
                          stroke_width=3).move_to(person.get_center())

        self.play(
            ripple_c.animate.scale(2.2).set_opacity(0),
            person.animate.shift(RIGHT * 0.25).rotate(
                -8 * DEGREES, about_point=person.get_bottom()),
            cycle_arrow.animate.set_opacity(0),
            run_time=0.4,
            rate_func=rate_functions.ease_out_quad
        )
        self.play(
            person.animate.shift(LEFT * 0.25).rotate(
                8 * DEGREES, about_point=person.get_bottom() + LEFT * 0.25),
            run_time=0.4,
            rate_func=rate_functions.ease_in_out_sine
        )

        mild_text = Text("Mild bump.",
                         font="Segoe UI", font_size=24,
                         color=COLOR_GROUND, slant=ITALIC)
        mild_text.move_to(UP * 2.6)
        self.play(FadeIn(mild_text, shift=UP * 0.15), run_time=0.5)
        self.wait(1.0)

        # Reset
        self.play(
            FadeOut(cycle, shift=LEFT * 0.4),
            FadeOut(cycle_speed),
            FadeOut(mild_text, shift=UP * 0.2),
            run_time=0.5
        )

        # ══════════════════════════════════════════════════════════
        #  ACT 3 · THE TRUCK COLLIDES (same speed!)
        # ══════════════════════════════════════════════════════════

        TRUCK_START_X = -5.5
        truck = make_truck(scale=2.5).set_z_index(2)
        place_on_ground(truck, TRUCK_START_X, GROUND_Y)

        truck_speed = MathTex(
            r"v = 10 \text{ km/h}",
            font_size=28, color=COLOR_VEC_G
        )
        truck_speed.next_to(truck, UP, buff=0.5)

        truck_arrow = Arrow(
            truck.get_right() + RIGHT * 0.15,
            truck.get_right() + RIGHT * 0.95,
            color=COLOR_VEC_G, stroke_width=5, buff=0,
            max_tip_length_to_length_ratio=0.22
        )

        self.play(
            FadeIn(truck, shift=RIGHT * 0.3),
            FadeIn(truck_speed, shift=DOWN * 0.15),
            GrowArrow(truck_arrow),
            run_time=0.9
        )

        # Emphasize SAME speed
        same_emp = Text(
            "Same speed!",
            font="Segoe UI", font_size=22,
            color=COLOR_AMBER, weight=BOLD
        )
        same_emp.next_to(truck_speed, UP, buff=0.2)

        self.play(
            FadeIn(same_emp, shift=DOWN * 0.1),
            Indicate(truck_speed, scale_factor=1.18, color=COLOR_AMBER),
            run_time=0.9
        )
        self.wait(0.6)
        self.play(FadeOut(same_emp), run_time=0.3)

        # Truck approaches at SAME speed (same time = same speed)
        truck_group = Group(truck, truck_speed, truck_arrow)
        impact_x_truck = PERSON_X - 1.5  # truck is bigger
        travel_dist_t = impact_x_truck - TRUCK_START_X-3.0

        # Same effective speed: scale run_time by distance ratio
        self.play(
            truck_group.animate.shift(RIGHT * travel_dist_t),
            run_time=1.6 * (travel_dist_t / travel_dist_c),
            rate_func=linear
        )

        # MAJOR impact — multiple ripples + person knocked far back
        ripple_t1 = Circle(radius=0.4, color=COLOR_VEC_G,
                           stroke_width=4).move_to(person.get_center())
        ripple_t2 = Circle(radius=0.4, color=COLOR_PINK,
                           stroke_width=3, stroke_opacity=0.7
                           ).move_to(person.get_center())
        ripple_t3 = Circle(radius=0.4, color=COLOR_AMBER,
                           stroke_width=2, stroke_opacity=0.5
                           ).move_to(person.get_center())

        # Flash on impact
        flash = Rectangle(
            width=14, height=8, fill_color=COLOR_WHITE,
            fill_opacity=0.0, stroke_width=0
        ).set_z_index(20)

        self.play(
            flash.animate.set_fill(opacity=0.18),
            run_time=0.08
        )
        self.play(
            flash.animate.set_fill(opacity=0),
            person.animate.shift(RIGHT * 2.8 + UP * 0.4).rotate(
                -35 * DEGREES, about_point=person.get_center()),
            person_label.animate.set_opacity(0),
            ripple_t1.animate.scale(4.0).set_opacity(0),
            ripple_t2.animate.scale(5.5).set_opacity(0),
            ripple_t3.animate.scale(7.0).set_opacity(0),
            truck_arrow.animate.set_opacity(0),
            run_time=0.65,
            rate_func=rate_functions.ease_out_expo
        )
        self.remove(flash)

        # Person settles
        self.play(
            person.animate.shift(DOWN * 0.4),
            run_time=0.4,
            rate_func=rate_functions.ease_in_quad
        )

        danger_text = Text("DANGEROUS!",
                           font="Segoe UI", font_size=34,
                           color=COLOR_PINK, weight=BOLD)
        danger_text.move_to(UP * 2.6)
        self.play(
            FadeIn(danger_text, shift=DOWN * 0.15, scale=0.85),
            run_time=0.6,
            rate_func=rate_functions.ease_out_back
        )
        self.wait(1.4)

        # Clean up scene
        self.play(
            FadeOut(truck), FadeOut(truck_speed),
            FadeOut(person), FadeOut(person_label),
            FadeOut(danger_text),
            FadeOut(ground),
            run_time=0.7
        )

        # ══════════════════════════════════════════════════════════
        #  ACT 4 · THE COMPARISON CHART
        # ══════════════════════════════════════════════════════════

        cmp_cycle = make_cycle(scale=0.45)
        cmp_cycle.move_to(LEFT * 3.6 + UP * 1.4)

        cmp_truck = make_truck(scale=1.1)
        cmp_truck.move_to(RIGHT * 3.0 + UP * 1.4)

        # Stat rows for each side
        def stat_row(symbol, value, color, font_size=26):
            row = MathTex(symbol, "=", value, font_size=font_size,
                          color=color)
            return row

        # Cycle stats
        c_v = stat_row("v", r"10 \text{ km/h}", COLOR_BLUE_BALL)
        c_a = stat_row("a", r"\text{same}", COLOR_BLUE_BALL)
        c_F = stat_row("F", r"\text{small}", COLOR_BLUE_BALL)

        cycle_stats = VGroup(c_v, c_a, c_F).arrange(
            DOWN, buff=0.3, aligned_edge=LEFT
        )
        cycle_stats.next_to(cmp_cycle, DOWN, buff=0.5)

        # Truck stats
        t_v = stat_row("v", r"10 \text{ km/h}", COLOR_VEC_G)
        t_a = stat_row("a", r"\text{same}", COLOR_VEC_G)
        t_F = stat_row("F", r"\text{HUGE}", COLOR_VEC_G)
        t_F[2].set_color(COLOR_PINK)

        truck_stats = VGroup(t_v, t_a, t_F).arrange(
            DOWN, buff=0.3, aligned_edge=LEFT
        )
        truck_stats.next_to(cmp_truck, DOWN, buff=0.5)

        # Bring in the comparison
        self.play(
            FadeIn(cmp_cycle, shift=RIGHT * 0.3),
            FadeIn(cmp_truck, shift=LEFT * 0.3),
            run_time=0.8
        )

        # Reveal stats one row at a time on both sides
        self.play(
            FadeIn(c_v, shift=UP * 0.15),
            FadeIn(t_v, shift=UP * 0.15),
            run_time=0.6
        )
        # Mark "Same speed" with check
        check_v = Text("✓ Same", font="Segoe UI", font_size=20,
                       color=COLOR_GREEN, weight=BOLD)
        check_v.move_to(UP * 1.4 + ORIGIN * 0)
        check_v.set_y((c_v.get_y() + t_v.get_y()) / 2)
        check_v.set_x(0)
        self.play(
            FadeIn(check_v, scale=0.85),
            Indicate(c_v, color=COLOR_AMBER, scale_factor=1.10),
            Indicate(t_v, color=COLOR_AMBER, scale_factor=1.10),
            run_time=0.8
        )
        self.wait(0.4)

        self.play(
            FadeIn(c_a, shift=UP * 0.15),
            FadeIn(t_a, shift=UP * 0.15),
            run_time=0.6
        )
        check_a = Text("✓ Same", font="Segoe UI", font_size=20,
                       color=COLOR_GREEN, weight=BOLD)
        check_a.set_y(c_a.get_y())
        check_a.set_x(0)
        self.play(
            FadeIn(check_a, scale=0.85),
            Indicate(c_a, color=COLOR_AMBER, scale_factor=1.10),
            Indicate(t_a, color=COLOR_AMBER, scale_factor=1.10),
            run_time=0.8
        )
        self.wait(0.4)

        self.play(
            FadeIn(c_F, shift=UP * 0.15),
            FadeIn(t_F, shift=UP * 0.15),
            run_time=0.6
        )
        cross_F = Text("✗ Different", font="Segoe UI", font_size=20,
                       color=COLOR_PINK, weight=BOLD)
        cross_F.set_y(c_F.get_y())
        cross_F.set_x(0)
        self.play(
            FadeIn(cross_F, scale=0.85),
            Indicate(c_F, color=COLOR_PINK, scale_factor=1.10),
            Indicate(t_F, color=COLOR_PINK, scale_factor=1.15),
            run_time=0.9
        )
        self.wait(1.2)

        # ══════════════════════════════════════════════════════════
        #  ACT 5 · THE QUESTION — "Kyun?"
        # ══════════════════════════════════════════════════════════

        why_text = Text("Why?",
                        font="Segoe UI", font_size=72,
                        color=COLOR_WHITE, weight=BOLD)
        why_text.to_edge(UP, buff=0.5)

        self.play(
            FadeIn(why_text, scale=0.85),
            run_time=0.7,
            rate_func=rate_functions.ease_out_back
        )
        self.wait(1.0)

        # Hint that something else must matter
        hint_text = Text(
            "Something else must matter...",
            font="Segoe UI", font_size=22,
            color=COLOR_GROUND, slant=ITALIC
        )
        hint_text.to_edge(DOWN, buff=0.6)
        self.play(FadeIn(hint_text, shift=UP * 0.15), run_time=0.7)
        self.wait(1.5)

        # ══════════════════════════════════════════════════════════
        #  ACT 6 · THE REVEAL — MASS
        # ══════════════════════════════════════════════════════════

        # Clear out comparison clutter, keep visuals
        self.play(
            FadeOut(c_v), FadeOut(c_a), FadeOut(c_F),
            FadeOut(t_v), FadeOut(t_a), FadeOut(t_F),
            FadeOut(check_v), FadeOut(check_a), FadeOut(cross_F),
            FadeOut(why_text), FadeOut(hint_text),
            run_time=0.6
        )

        # Bring vehicles closer for mass comparison
        self.play(
            cmp_cycle.animate.move_to(LEFT * 3.0 + UP * 0.4),
            cmp_truck.animate.move_to(RIGHT * 3.0 + UP * 0.4),
            run_time=0.7
        )

        # Mass labels under each
        cycle_mass = MathTex(r"m \approx \text{small}",
                             font_size=30, color=COLOR_BLUE_BALL)
        cycle_mass.next_to(cmp_cycle, DOWN, buff=0.55)

        truck_mass = MathTex(r"m \approx \text{HUGE}",
                             font_size=34, color=COLOR_VEC_G)
        truck_mass[0][2:].set_color(COLOR_PINK)
        truck_mass.next_to(cmp_truck, DOWN, buff=0.55)

        self.play(
            FadeIn(cycle_mass, shift=UP * 0.15),
            FadeIn(truck_mass, shift=UP * 0.15),
            run_time=0.8
        )
        self.wait(0.6)

        # Big "MASS" reveal at the top
        mass_reveal = Text(
            "MASS",
            font="Segoe UI", font_size=88,
            color=COLOR_AMBER, weight=BOLD
        ).to_edge(UP, buff=0.5)

        # A subtle accent pulse behind it
        mass_glow = Text(
            "MASS",
            font="Segoe UI", font_size=88,
            color=COLOR_AMBER, weight=BOLD
        ).to_edge(UP, buff=0.5).set_opacity(0)

        self.play(
            FadeIn(mass_reveal, scale=0.85),
            run_time=0.9,
            rate_func=rate_functions.ease_out_back
        )

        # Tiny pulse for emphasis
        self.play(
            Indicate(mass_reveal, color=COLOR_AMBER, scale_factor=1.08),
            run_time=0.6
        )
        self.wait(1.2)

        # ══════════════════════════════════════════════════════════
        #  ACT 7 · MORE MASS → MORE FORCE
        # ══════════════════════════════════════════════════════════

        # Push vehicles + mass labels off, keep MASS as title
        self.play(
            FadeOut(cmp_cycle, shift=LEFT * 0.3),
            FadeOut(cmp_truck, shift=RIGHT * 0.3),
            FadeOut(cycle_mass), FadeOut(truck_mass),
            run_time=0.6
        )

        # Demote MASS to corner like a chapter marker
        self.play(
            mass_reveal.animate.scale(0.42).to_corner(UL, buff=0.6).set_opacity(0.55),
            run_time=0.8,
            rate_func=rate_functions.ease_in_out_sine
        )

        # The relationship in plain words
        more_mass = Text("More mass",
                         font="Segoe UI", font_size=42,
                         color=COLOR_AMBER, weight=BOLD)
        arrow_mid = MathTex(r"\rightarrow",
                            font_size=56, color=COLOR_WHITE)
        more_force = Text("More force",
                          font="Segoe UI", font_size=42,
                          color=COLOR_VEC_G, weight=BOLD)

        relation = VGroup(more_mass, arrow_mid, more_force).arrange(
            RIGHT, buff=0.5
        ).move_to(UP * 0.7)

        self.play(
            LaggedStart(
                FadeIn(more_mass, shift=UP * 0.2),
                FadeIn(arrow_mid, scale=0.7),
                FadeIn(more_force, shift=UP * 0.2),
                lag_ratio=0.4
            ),
            run_time=1.5,
            rate_func=rate_functions.ease_out_cubic
        )
        self.wait(1.0)

        # "Makes sense" beat
        makes_sense = Text(
            "Makes sense.",
            font="Segoe UI", font_size=24,
            color=COLOR_GROUND, slant=ITALIC
        )
        makes_sense.next_to(relation, DOWN, buff=0.5)
        self.play(FadeIn(makes_sense, shift=UP * 0.15), run_time=0.6)
        self.wait()

        # The proportionality equation — our running equation so far
        running_label = Text(
            "Our equation so far:",
            font="Segoe UI", font_size=20,
            color=COLOR_GROUND
        ).move_to(DOWN * 0.6)

        prop_eq = MathTex("F", r"\propto", "m",
                          font_size=110, color=COLOR_WHITE)
        prop_eq[0].set_color(COLOR_VEC_G)
        prop_eq[2].set_color(COLOR_AMBER)
        prop_eq.move_to(DOWN * 1.9)

        self.play(TransformMatchingShapes(makes_sense, running_label))

        f_src = more_force[4]
        m_src = more_mass[4]
        self.play(
            TransformFromCopy(f_src, prop_eq[0]),
            TransformFromCopy(arrow_mid, prop_eq[1]),
            TransformFromCopy(m_src, prop_eq[2]),
            run_time=1.5,
            rate_func=rate_functions.ease_in_out_sine
        )
        self.wait()

        # A soft halo box around the equation to mark it as a milestone
        eq_box = RoundedRectangle(
            corner_radius=0.18,
            width=prop_eq.width + 1.2,
            height=prop_eq.height + 0.7,
            stroke_color=COLOR_AMBER, stroke_width=2,
            stroke_opacity=0.45,
            fill_opacity=0
        ).move_to(prop_eq.get_center())
        self.play(Create(eq_box), run_time=0.7)

        self.wait(2.5)

        # ══════════════════════════════════════════════════════════
        #  FINAL FADE
        # ══════════════════════════════════════════════════════════
        objects_to_fade = [m for m in self.mobjects if m is not grid]
        self.play(FadeOut(Group(*objects_to_fade)))
        self.wait(0.4)