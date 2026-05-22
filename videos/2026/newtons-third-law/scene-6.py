# scene-4.py — Newton's Third Law · closing scene
# Universal pattern: car (road) → rocket (gas) → look around your house
from manim import *
import numpy as np


# ─────────────────────────────────────────────
#  BRAND PALETTE  (consistent with the series)
# ─────────────────────────────────────────────
COLOR_BG        = "#1C1C1E"
COLOR_DARK_GRAY = "#3A3A3C"
COLOR_GROUND    = "#8E8E93"
COLOR_WHITE     = "#E5E5EA"
COLOR_GREY_BALL = "#D1D1D6"
COLOR_BLUE_BALL = "#007AFF"
COLOR_VEC_F     = "#FF3B30"
COLOR_VEC_V     = "#32ADE6"
COLOR_GREEN     = "#34C759"
COLOR_AMBER     = "#FFCC00"
COLOR_YELLOW    = "#FFCC00"
COLOR_PINK      = "#FF2D55"
COLOR_PURPLE    = "#AF52DE"
COLOR_ORANGE    = "#FF9500"
COLOR_BROWN     = "#A2845E"


# ═══════════════════════════════════════════════════════════════════
#  HELPERS  (consistent with the series)
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
            op = peak_op * 0.40 * (1 - (2 * t - 1) ** 2)
            segs.add(Line(p1, p2, stroke_opacity=op,
                          stroke_width=1, color=COLOR_WHITE))
        return segs

    for x in np.arange(-max_x, max_x + 0.1, spacing):
        peak = 0.35 * (1 - (abs(x) / max_x) ** 1.5)
        if peak > 0:
            grid.add(fading_line(UP * max_y + RIGHT * x,
                                 DOWN * max_y + RIGHT * x, peak))
    for y in np.arange(-max_y, max_y + 0.1, spacing):
        peak = 0.35 * (1 - (abs(y) / max_y) ** 1.5)
        if peak > 0:
            grid.add(fading_line(LEFT * max_x + UP * y,
                                 RIGHT * max_x + UP * y, peak))
    return grid


def pill_bg(text_mob, fill=COLOR_BG, fill_opacity=0.85,
            stroke_color=None, stroke_width=0, buff=0.10):
    """Sleek rounded pill behind a text mobject."""
    h = text_mob.height + buff * 2
    w = text_mob.width + buff * 3
    bg = RoundedRectangle(
        corner_radius=min(h * 0.5, 0.25),
        height=h, width=w,
        color=stroke_color if stroke_color else fill,
        stroke_width=stroke_width,
        fill_color=fill, fill_opacity=fill_opacity,
    ).move_to(text_mob.get_center())
    return bg


def make_ground(y, x_extent=7.0, hatch_density=0.32):
    """Ground line + hatching, matching scene-3a/3 style."""
    ground = Line(
        LEFT * x_extent + UP * y, RIGHT * x_extent + UP * y,
        color=COLOR_GROUND, stroke_width=3, stroke_opacity=0.9
    )
    hatching = VGroup()
    for x in np.arange(-x_extent + 0.3, x_extent, hatch_density):
        h = Line(
            np.array([x, y, 0]),
            np.array([x - 0.18, y - 0.25, 0]),
            color=COLOR_GROUND, stroke_width=1.5, stroke_opacity=0.5
        )
        hatching.add(h)
    return ground, hatching


def make_stars(n=70, x_range=(-12, 12), y_range=(-7, 7), seed=42):
    """Subtle starfield for the 'space' beat."""
    rng = np.random.default_rng(seed)
    stars = VGroup()
    for _ in range(n):
        x = rng.uniform(*x_range)
        y = rng.uniform(*y_range)
        r = rng.uniform(0.012, 0.030)
        op = rng.uniform(0.35, 0.95)
        s = Dot(point=np.array([x, y, 0]), radius=r,
                color=COLOR_WHITE).set_opacity(op)
        stars.add(s)
    return stars


# ═══════════════════════════════════════════════════════════════════
#  SCENE 4 · The Universal Pattern  (closing scene)
# ═══════════════════════════════════════════════════════════════════

class Scene6_Everywhere(MovingCameraScene):
    def construct(self):
        self.camera.background_color = COLOR_BG

        grid = build_grid()
        grid.set_z_index(-10)
        self.add(grid)

        # ══════════════════════════════════════════════════════════
        #  ACT 2 · THE CAR — engine spins tyres, tyres push road,
        #          road pushes car forward
        # ══════════════════════════════════════════════════════════
        chapter_car = Text(
            "EXAMPLE 1 · THE CAR",
            font="Segoe UI", font_size=22, weight=BOLD,
            color=COLOR_AMBER
        )
        chapter_car_line = Line(
            chapter_car.get_corner(DL) + DOWN * 0.08,
            chapter_car.get_corner(DR) + DOWN * 0.08,
            color=COLOR_AMBER, stroke_width=2.2, stroke_opacity=0.85
        )
        chapter_car_grp = VGroup(chapter_car, chapter_car_line)\
            .to_edge(UP, buff=0.45).set_z_index(10)

        self.play(
            FadeIn(chapter_car, shift=DOWN * 0.15),
            Create(chapter_car_line),
            run_time=0.8, rate_func=rate_functions.ease_out_cubic
        )

        ground_y = -2.2
        ground, hatching = make_ground(ground_y)
        ground.set_z_index(1)
        hatching.set_z_index(1)

        self.play(
            Create(ground),
            LaggedStartMap(Create, hatching, lag_ratio=0.01),
            run_time=0.9
        )

        # Car image — falls back to a stylized rect if asset missing
        try:
            car = ImageMobject("car.png")
            car.scale_to_fit_height(1.9)
        except Exception:
            car = RoundedRectangle(
                corner_radius=0.25, width=3.2, height=1.5,
                fill_color=COLOR_BLUE_BALL, fill_opacity=1.0,
                stroke_color=COLOR_WHITE, stroke_width=1
            )
        car.set_z_index(3)
        # Park the car slightly LEFT of center so we can pan right later.
        car_x = -0.6
        car.move_to(np.array([car_x, ground_y + car.height / 2 + 0.05, 0]))

        self.play(FadeIn(car, shift=RIGHT * 0.4, scale=0.97), run_time=0.7)
        self.wait(0.3)

        # ── Misconception: "we think the engine does it all" ───────
        engine_lbl = Text(
            "“Engine does everything.”",
            font="Segoe UI", font_size=22, slant=ITALIC,
            color=COLOR_GROUND
        ).move_to(UP * 2.4).set_z_index(9)
        engine_lbl_pill = pill_bg(engine_lbl).set_z_index(8)

        self.play(
            FadeIn(engine_lbl_pill, shift=DOWN * 0.1),
            FadeIn(engine_lbl, shift=DOWN * 0.1),
            run_time=0.55
        )
        self.wait(0.4)

        # X-out the misconception with a pink strike
        strike = Line(
            engine_lbl.get_corner(DL) + LEFT * 0.25,
            engine_lbl.get_corner(UR) + RIGHT * 0.25,
            color=COLOR_PINK, stroke_width=5
        ).set_z_index(11)
        self.play(Create(strike),
                  rate_func=rate_functions.ease_in_out_expo,
                  run_time=0.4)
        self.play(
            FadeOut(engine_lbl_pill),
            FadeOut(engine_lbl),
            FadeOut(strike),
            run_time=0.45
        )

        # ── The actual third-law pair at the tyre contact ─────────
        # Pick a contact point under the car's back wheel area.
        # Car asset width unknown — assume tyres sit near the bottom
        # corners of the bounding box; bias slightly inward.
        tyre_contact_x = car.get_left()[0] + car.width * 0.28 - 0.4
        tyre_contact = np.array([tyre_contact_x, ground_y + 0.04, 0])

        # Tyre pushes road BACKWARD (left)
        push_road = Arrow(
            tyre_contact,
            tyre_contact + LEFT * 1.55,
            color=COLOR_PURPLE, buff=0, stroke_width=7,
            max_tip_length_to_length_ratio=0.22
        ).set_z_index(6)
        push_road_lbl = MathTex(
            r"P_{\text{push}}", color=COLOR_PURPLE, font_size=34
        ).next_to(push_road.get_end(), UP, buff=0.18).set_z_index(8)
        push_road_pill = pill_bg(push_road_lbl).set_z_index(7)

        # Road-skid streaks — short purple dashes streaming leftward
        # along the ground from the contact, suggesting the road
        # being scraped/pushed backward by the tyre.
        skid_streaks = VGroup()
        for i in range(6):
            x0 = tyre_contact_x - 0.15 - i * 0.20
            y0 = ground_y - 0.05 - (i % 2) * 0.05
            streak = Line(
                np.array([x0, y0, 0]),
                np.array([x0 - 0.22, y0, 0]),
                color=COLOR_PURPLE,
                stroke_width=3.0 - i * 0.25,
                stroke_opacity=0.85 - i * 0.10
            )
            skid_streaks.add(streak)
        skid_streaks.set_z_index(5)

        self.play(
            GrowArrow(push_road),
            run_time=0.7, rate_func=rate_functions.ease_out_expo
        )
        self.play(
            FadeIn(push_road_pill, shift=UP * 0.08),
            FadeIn(push_road_lbl, shift=UP * 0.08),
            LaggedStart(
                *[Create(s) for s in skid_streaks],
                lag_ratio=0.08
            ),
            run_time=0.6
        )
        self.wait(0.7)

        # Road pushes car FORWARD (right) — the 3rd Law reaction
        push_car = Arrow(
            tyre_contact,
            tyre_contact + RIGHT * 1.55,
            color=COLOR_AMBER, buff=0, stroke_width=9,
            max_tip_length_to_length_ratio=0.22
        ).set_z_index(7)
        push_car_lbl = MathTex(
            r"P_{\text{road}}", color=COLOR_AMBER, font_size=40
        ).next_to(push_car.get_end(), UP, buff=0.18).set_z_index(9)
        push_car_pill = pill_bg(push_car_lbl).set_z_index(8)

        # 3rd Law badge — visual continuity with scene-3a
        badge_text = Text(
            "3rd Law Pair", font="Segoe UI",
            font_size=18, weight=BOLD, color=COLOR_AMBER
        )
        badge_bg = RoundedRectangle(
            corner_radius=0.18,
            height=badge_text.height + 0.28,
            width=badge_text.width + 0.55,
            color=COLOR_AMBER, stroke_width=1.5,
            fill_color=COLOR_BG, fill_opacity=0.92,
        )
        badge = VGroup(badge_bg, badge_text).move_to(
            tyre_contact + UP * 2.4 + RIGHT * 2.6
        ).set_z_index(10)

        self.play(
            GrowArrow(push_car),
            run_time=0.8, rate_func=rate_functions.ease_out_expo
        )
        self.play(
            FadeIn(push_car_pill, shift=DOWN * 0.1),
            FadeIn(push_car_lbl, shift=DOWN * 0.1),
            FadeIn(badge, scale=0.7),
            run_time=0.7, rate_func=rate_functions.ease_out_back
        )
        self.wait(0.6)

        # Visual verdict (no text): the car physically lurches FORWARD
        # the moment the reaction force lands. A short green streak
        # trails behind the rear tyre — direct evidence that the road's
        # push is what moves the car.
        forward_shift = RIGHT * 0.6
    

        car_and_arrow = Group(car, push_car, push_car_lbl, push_car_pill)
        # The push-road arrow + skid stay PUT — they live on the road,
        # not on the car. That contrast is the whole point.

        self.play(
            car_and_arrow.animate.shift(forward_shift),
            badge.animate.shift(forward_shift * 0.4),
            run_time=0.9, rate_func=rate_functions.ease_out_cubic
        )
        # Keep tyre_contact's logical position in sync for the next act
        tyre_contact = tyre_contact + forward_shift
        tyre_contact_x = tyre_contact[0]
        self.wait(0.8)

        # ── "Without grip, even a loud engine does nothing" ────────
        # Clean transition: drop the pair, keep car + road, then
        # show wheel spinning but car NOT moving.
        self.play(
            FadeOut(badge),
            FadeOut(push_road), FadeOut(push_road_lbl),
            FadeOut(push_road_pill),
            FadeOut(skid_streaks, shift=LEFT * 0.1),
            FadeOut(push_car), FadeOut(push_car_lbl), FadeOut(push_car_pill),
            run_time=0.6
        )

        # Spinning indicator at the tyre contact — curved motion arrows
        # circling the contact point, suggesting a wheel slipping in place.
        spin_arcs = VGroup()
        for i in range(3):
            arc = Arc(
                radius=0.28 + i * 0.04,
                start_angle=(PI * 0.85) + i * 0.05,
                angle=-PI * 1.5,
                color=COLOR_PINK, stroke_width=3,
                stroke_opacity=0.75 - i * 0.18
            )
            arc.move_arc_center_to(tyre_contact + UP * 0.25)
            spin_arcs.add(arc)
        spin_arcs.set_z_index(6)

        self.play(
            LaggedStart(*[Create(a) for a in spin_arcs], lag_ratio=0.08),
            run_time=0.6
        )

        # Engine-noise ripples — pink concentric arcs radiating outward
        # from the engine bay (front of the car). Visual stand-in for
        # "roar."  Drawn once, then re-emitted twice for a pulse effect.
        engine_pt = np.array([car.get_right()[0] - 0.25,
                              car.get_center()[1] + 0.05, 0])

        def emit_ripple():
            ripple = Circle(
                radius=0.05, color=COLOR_PINK, stroke_width=2.5,
                stroke_opacity=0.85, fill_opacity=0
            ).move_to(engine_pt).set_z_index(4)
            self.add(ripple)
            self.play(
                ripple.animate.scale(8).set_stroke(opacity=0, width=0.5),
                run_time=0.55, rate_func=rate_functions.ease_out_quad
            )
            self.remove(ripple)

        # Wheel spins furiously — fast back-and-forth — while car body
        # tries to lurch right but snaps back. Engine ripples pulse.
        spin_center = tyre_contact + UP * 0.25

        # Capture car's resting position before the failed-lurch
        car_rest_x = car.get_center()[0]
        rest_pos = car.get_center()

        # First spin + ripple + tiny failed lurch
        self.play(
            Rotate(spin_arcs, angle=-PI * 0.8, about_point=spin_center),
            car.animate.shift(RIGHT * 0.10),
            run_time=0.35, rate_func=rate_functions.ease_in_out_sine
        )
        emit_ripple()
        self.play(
            Rotate(spin_arcs, angle=PI * 0.4, about_point=spin_center),
            car.animate.move_to(rest_pos),
            run_time=0.30, rate_func=rate_functions.ease_in_out_sine
        )

        # Second pulse — more violent spin, same failed lurch
        self.play(
            Rotate(spin_arcs, angle=-PI * 1.0, about_point=spin_center),
            car.animate.shift(RIGHT * 0.08),
            run_time=0.30, rate_func=rate_functions.ease_in_out_sine
        )
        emit_ripple()
        self.play(
            Rotate(spin_arcs, angle=PI * 0.5, about_point=spin_center),
            car.animate.move_to(rest_pos),
            run_time=0.30, rate_func=rate_functions.ease_in_out_sine
        )

        # "Missing reaction" — the amber forward arrow tries to appear
        # but never materializes. A ghost-outlined arrow flickers in,
        # gets X'd out, and dies. No road push = no forward motion.
        ghost_arrow = Arrow(
            tyre_contact,
            tyre_contact + RIGHT * 1.55,
            color=COLOR_AMBER, buff=0, stroke_width=9,
            max_tip_length_to_length_ratio=0.22,
            stroke_opacity=0.18
        ).set_z_index(5)
        ghost_arrow.set_fill(opacity=0.18)
        cross = VGroup(
            Line(ghost_arrow.get_start() + UL * 0.18,
                 ghost_arrow.get_end() + DR * 0.18,
                 color=COLOR_PINK, stroke_width=4),
            Line(ghost_arrow.get_start() + DL * 0.18,
                 ghost_arrow.get_end() + UR * 0.18,
                 color=COLOR_PINK, stroke_width=4),
        ).set_z_index(7)

        self.play(FadeIn(ghost_arrow, shift=RIGHT * 0.1), run_time=0.5)
        self.play(Create(cross), run_time=0.45)

        # Final "still stuck" micro-vibration — fast small shakes,
        # the car visibly trying and failing.
        for _ in range(3):
            self.play(car.animate.shift(RIGHT * 0.04),
                      run_time=0.08,
                      rate_func=rate_functions.linear)
            self.play(car.animate.shift(LEFT * 0.08),
                      run_time=0.08,
                      rate_func=rate_functions.linear)
            self.play(car.animate.shift(RIGHT * 0.04),
                      run_time=0.08,
                      rate_func=rate_functions.linear)

        self.wait(0.9)

        # Dissolve the car scene cleanly
        car_block = Group(
            car, ground, hatching,
            ghost_arrow, cross, spin_arcs,
            chapter_car, chapter_car_line
        )
        self.play(FadeOut(car_block, shift=UP * 0.1), run_time=0.9)

        # ══════════════════════════════════════════════════════════
        #  ACT 3 · THE ROCKET — gas down, rocket up. Even in space.
        # ══════════════════════════════════════════════════════════

        # Transition into pitch-black space: hide grid, only stars visible.
        stars = make_stars(n=85).set_z_index(-9)
        self.play(
            FadeOut(grid),
            FadeIn(stars, rate_func=rate_functions.ease_in_out_sine),
            run_time=1.0,
        )

        chapter_rocket = Text(
            "EXAMPLE 2 · THE ROCKET",
            font="Segoe UI", font_size=22, weight=BOLD,
            color=COLOR_AMBER
        )
        chapter_rocket_line = Line(
            chapter_rocket.get_corner(DL) + DOWN * 0.08,
            chapter_rocket.get_corner(DR) + DOWN * 0.08,
            color=COLOR_AMBER, stroke_width=2.2, stroke_opacity=0.85
        )
        chapter_rocket_grp = VGroup(chapter_rocket, chapter_rocket_line)\
            .to_edge(UP, buff=0.45).set_z_index(10)

        self.play(
            FadeIn(chapter_rocket, shift=DOWN * 0.15),
            Create(chapter_rocket_line),
            run_time=0.8
        )

        # Rocket image — slightly LEFT so the equation can sit RIGHT.
        try:
            rocket = ImageMobject("rocket.png")
            rocket.scale_to_fit_height(3.6)
        except Exception:
            rocket = VGroup(
                Polygon(UP * 1.0, LEFT * 0.35 + DOWN * 1.4,
                        RIGHT * 0.35 + DOWN * 1.4,
                        fill_color=COLOR_WHITE, fill_opacity=1, stroke_width=0),
                Triangle(color=COLOR_VEC_F, fill_opacity=1, stroke_width=0)
                    .scale(0.35).next_to(ORIGIN, UP, buff=0.6),
            )
        rocket.set_z_index(5)
        rocket.move_to(LEFT * 2.6 + DOWN * 0.2)
        rocket_initial_center = rocket.get_center()

        self.play(FadeIn(rocket, shift=UP * 0.4, scale=0.95), run_time=0.7)
        self.wait(0.3)

        # ── Gas jets DOWN out of the rocket nozzle ────────────────
        # The nozzle is roughly at the rocket's bottom center.
        nozzle = np.array([rocket.get_center()[0],
                           rocket.get_bottom()[1] + 0.05, 0])

        # Action — rocket throws gas DOWN
        gas_arrow = Arrow(
            nozzle + UP * 0.05,
            nozzle + DOWN * 1.7,
            color=COLOR_VEC_F, buff=0, stroke_width=7,
            max_tip_length_to_length_ratio=0.20
        ).set_z_index(6)
        gas_lbl = MathTex(
            r"F_{\text{gas}}", color=COLOR_VEC_F, font_size=36
        ).next_to(gas_arrow, RIGHT, buff=0.15).set_z_index(8)
        gas_pill = pill_bg(gas_lbl).set_z_index(7)

        # Gas particles — small red/orange dots that erupt downward
        # from the nozzle and disperse outward. They CARRY the message
        # "the rocket is throwing real stuff downward" — no text needed.
        rng = np.random.default_rng(7)
        gas_particles = VGroup()
        particle_targets = []
        for i in range(26):
            r = rng.uniform(0.04, 0.09)
            jitter_x = rng.uniform(-0.18, 0.18)
            col = COLOR_VEC_F if rng.random() < 0.6 else COLOR_ORANGE
            p = Dot(
                point=nozzle + np.array([jitter_x, 0, 0]),
                radius=r, color=col
            ).set_opacity(0.95)
            gas_particles.add(p)
            # Precompute where each particle disperses to
            spread = rng.uniform(-0.55, 0.55)
            depth  = rng.uniform(0.9, 2.0)
            particle_targets.append((spread, depth))
        gas_particles.set_z_index(5)
        self.add(gas_particles)

        self.play(
            GrowArrow(gas_arrow),
            run_time=0.6, rate_func=rate_functions.ease_out_expo
        )
        self.play(
            FadeIn(gas_pill, shift=LEFT * 0.08),
            FadeIn(gas_lbl, shift=LEFT * 0.08),
            LaggedStart(
                *[p.animate.shift(np.array([sp, -dp, 0])).set_opacity(0)
                  for p, (sp, dp) in zip(gas_particles, particle_targets)],
                lag_ratio=0.025
            ),
            run_time=1.4, rate_func=rate_functions.ease_in_quad
        )
        self.remove(gas_particles)
        self.wait(0.4)

        # Reaction — gas pushes rocket UP
        thrust_arrow = Arrow(
            nozzle + UP * 0.1,
            nozzle + UP * 1.7,
            color=COLOR_AMBER, buff=0, stroke_width=9,
            max_tip_length_to_length_ratio=0.22
        ).set_z_index(7)
        # Place the thrust label to the LEFT of the rocket so it
        # doesn't collide with the rocket body.
        thrust_lbl = MathTex(
            r"F_{\text{thrust}}", color=COLOR_AMBER, font_size=40
        ).next_to(rocket, LEFT, buff=0.45).set_z_index(9)
        thrust_pill = pill_bg(thrust_lbl).set_z_index(8)

        # 3rd Law badge — same visual vocabulary
        rbadge_text = Text(
            "3rd Law Pair", font="Segoe UI",
            font_size=18, weight=BOLD, color=COLOR_AMBER
        )
        rbadge_bg = RoundedRectangle(
            corner_radius=0.18,
            height=rbadge_text.height + 0.28,
            width=rbadge_text.width + 0.55,
            color=COLOR_AMBER, stroke_width=1.5,
            fill_color=COLOR_BG, fill_opacity=0.92,
        )
        rbadge = VGroup(rbadge_bg, rbadge_text).move_to(
            RIGHT * 3.4 + UP * 1.4
        ).set_z_index(10)

        self.play(
            GrowArrow(thrust_arrow),
            run_time=0.7, rate_func=rate_functions.ease_out_expo
        )
        self.play(
            FadeIn(thrust_pill, shift=RIGHT * 0.1),
            FadeIn(thrust_lbl, shift=RIGHT * 0.1),
            FadeIn(rbadge, scale=0.7),
            run_time=0.7, rate_func=rate_functions.ease_out_back
        )
        self.wait(0.9)

        # ── The "no road needed / it carries its own road" punchline ─
        # No text. The rocket stays STATIONARY while continuously
        # emitting gas — the gas IS the road. Particles erupt from the
        # nozzle and fall away, looping until the act ends.

        # Continuous exhaust via an updater. Each particle tracks its
        # own lifetime; on death it respawns at the nozzle with new
        # random spread/fall targets. This runs until we detach the
        # updater at the end of the act.
        n_trail = 36
        particle_lifetime = 1.1  # seconds per particle
        trail = VGroup()
        # state[i] = [age, jitter_x, spread, depth, radius, color_choice]
        state = []
        for i in range(n_trail):
            age = rng.uniform(0, particle_lifetime)  # stagger initial ages
            jitter_x = rng.uniform(-0.18, 0.18)
            spread   = rng.uniform(-0.55, 0.55)
            depth    = rng.uniform(1.2, 2.4)
            r        = rng.uniform(0.04, 0.09)
            col      = COLOR_VEC_F if rng.random() < 0.6 else COLOR_ORANGE
            p = Dot(point=nozzle, radius=r, color=col).set_opacity(0)
            trail.add(p)
            state.append([age, jitter_x, spread, depth, r, col])
        trail.set_z_index(5)
        self.add(trail)

        def update_trail(mob, dt):
            for p, s in zip(mob, state):
                s[0] += dt
                if s[0] >= particle_lifetime:
                    # respawn
                    s[0] = 0.0
                    s[1] = rng.uniform(-0.18, 0.18)
                    s[2] = rng.uniform(-0.55, 0.55)
                    s[3] = rng.uniform(1.2, 2.4)
                    new_r = rng.uniform(0.04, 0.09)
                    new_col = COLOR_VEC_F if rng.random() < 0.6 else COLOR_ORANGE
                    p.set_color(new_col)
                    # scale radius by adjusting (Dot has no easy resize;
                    # use a uniform scale relative to current width)
                    cur_r = max(p.width / 2, 1e-4)
                    p.scale(new_r / cur_r)
                t = s[0] / particle_lifetime
                # position: from nozzle drifting down-and-out
                px = nozzle[0] + s[1] + s[2] * t
                py = nozzle[1] - s[3] * t
                p.move_to(np.array([px, py, 0]))
                # opacity: quick fade-in, slow fade-out
                if t < 0.08:
                    op = (t / 0.08) * 0.95
                else:
                    op = 0.95 * (1 - (t - 0.08) / (1 - 0.08))
                p.set_opacity(max(0.0, op))

        trail.add_updater(update_trail)

        # Let the continuous exhaust play for the duration of the act.
        # Rocket stays put — the void + the never-ending jet say it all.
        self.wait(3.0)

        trail.remove_updater(update_trail)
        self.remove(trail)

        self.wait(0.5)

        # Clear stage for the synthesis
        rocket_block = Group(
            rocket, gas_arrow, gas_lbl, gas_pill,
            thrust_arrow, thrust_lbl, thrust_pill,
            rbadge,
            chapter_rocket, chapter_rocket_line,
            stars
        )
        self.play(
            FadeOut(rocket_block, shift=UP * 0.2),
            FadeIn(grid),
            run_time=1.0, rate_func=rate_functions.ease_in_out_sine
        )

        # ══════════════════════════════════════════════════════════
        #  ACT 4 · THE SYNTHESIS — same funda everywhere
        #          (no title text; the convergence visual will speak)
        # ══════════════════════════════════════════════════════════

        # Four mini-cards — book/table, horse/ground, car/road, rocket/gas
        # Each is a small icon-style pair of arrows with a label below.
        def make_pair_card(title_str, a_label, b_label, accent=COLOR_AMBER,
                           vertical=False):
            """A small card with a stylized action/reaction pair and label."""
            card_w, card_h = 2.6, 2.05
            card_bg = RoundedRectangle(
                corner_radius=0.14, width=card_w, height=card_h,
                stroke_color=accent, stroke_width=1.6, stroke_opacity=0.55,
                fill_color=accent, fill_opacity=0.04
            )

            # Two opposing arrows centered in the card's upper area
            cx = card_bg.get_center()[0]
            cy = card_bg.get_center()[1] + 0.25
            if not vertical:
                a_arrow = Arrow(
                    np.array([cx + 0.05, cy, 0]),
                    np.array([cx - 0.85, cy, 0]),
                    color=COLOR_VEC_F, buff=0, stroke_width=5,
                    max_tip_length_to_length_ratio=0.22
                )
                b_arrow = Arrow(
                    np.array([cx - 0.05, cy - 0.30, 0]),
                    np.array([cx + 0.85, cy - 0.30, 0]),
                    color=accent, buff=0, stroke_width=5,
                    max_tip_length_to_length_ratio=0.22
                )
                a_lbl = Text(a_label, font="Segoe UI", font_size=14,
                             color=COLOR_VEC_F).next_to(a_arrow, UP, buff=0.06)
                b_lbl = Text(b_label, font="Segoe UI", font_size=14,
                             color=accent).next_to(b_arrow, DOWN, buff=0.06)
            else:
                a_arrow = Arrow(
                    np.array([cx - 0.35, cy + 0.05, 0]),
                    np.array([cx - 0.35, cy - 0.85, 0]),
                    color=COLOR_VEC_F, buff=0, stroke_width=5,
                    max_tip_length_to_length_ratio=0.22
                )
                b_arrow = Arrow(
                    np.array([cx + 0.35, cy - 0.05, 0]),
                    np.array([cx + 0.35, cy + 0.85, 0]),
                    color=accent, buff=0, stroke_width=5,
                    max_tip_length_to_length_ratio=0.22
                )
                a_lbl = Text(a_label, font="Segoe UI", font_size=14,
                             color=COLOR_VEC_F).next_to(a_arrow, LEFT, buff=0.10)
                b_lbl = Text(b_label, font="Segoe UI", font_size=14,
                             color=accent).next_to(b_arrow, RIGHT, buff=0.10)

            title_t = Text(title_str, font="Segoe UI", font_size=18,
                           weight=BOLD, color=COLOR_WHITE)
            title_t.move_to(card_bg.get_bottom() + UP * 0.28)

            card = VGroup(card_bg, a_arrow, b_arrow, a_lbl, b_lbl, title_t)
            return card

        card_book = make_pair_card("BOOK · TABLE",
                                   "book ↓", "table ↑",
                                   accent=COLOR_BLUE_BALL, vertical=True)
        card_horse = make_pair_card("HORSE · GROUND",
                                    "push ←", "ground →",
                                    accent=COLOR_AMBER)
        card_car = make_pair_card("CAR · ROAD",
                                  "tyre ←", "road →",
                                  accent=COLOR_GREEN)
        card_rocket = make_pair_card("ROCKET · GAS",
                                     "gas ↓", "thrust ↑",
                                     accent=COLOR_PURPLE, vertical=True)

        cards = VGroup(card_book, card_horse, card_car, card_rocket)\
            .arrange(RIGHT, buff=0.30)\
            .move_to(DOWN * 0.2).set_z_index(8)

        self.play(
            LaggedStart(
                *[FadeIn(c, shift=UP * 0.25, scale=0.96) for c in cards],
                lag_ratio=0.18
            ),
            run_time=1.6, rate_func=rate_functions.ease_out_cubic
        )
        self.wait(1.2)

        # Glow ripple across all cards — same funda
        for c in cards:
            self.play(
                Indicate(c[0], color=COLOR_AMBER, scale_factor=1.04),
                run_time=0.35
            )

        # The unifying line
        same_funda = Text(
            "Push something. It pushes back. Always.",
            font="Segoe UI", font_size=28, weight=BOLD,
            color=COLOR_WHITE,
            t2c={"pushes back": COLOR_AMBER, "Always": COLOR_GREEN}
        ).move_to(DOWN * 2.9).set_z_index(10)

        self.play(FadeIn(same_funda, shift=UP * 0.2), run_time=0.9)
        self.wait(1.6)