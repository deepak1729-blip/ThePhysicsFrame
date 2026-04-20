from manim import *
import numpy as np

def make_ball(color: str, radius: float = 0.30) -> VGroup:
    """
    Returns a VGroup that looks like a lit 3-D sphere:
      • solid body with set_sheen() gradient (bright top-left → dark bottom-right)
      • thin rim-highlight stroke
      • white specular ellipse (upper-left)

    The VGroup's reference point is the centre of the sphere, so you can
    call  ball.move_to(pos)  and  ball.get_center()  exactly like a Circle.
    """
    g = VGroup()

    # Glow aura — four concentric halos, outermost first (drawn first = behind)

    # Main sphere body
    sphere = Circle(radius=radius)
    sphere.set_fill(color, opacity=1.0)
    sphere.set_sheen(-0.45, DR)          # darkens bottom-right, brightens top-left
    sphere.set_stroke(color=WHITE, width=1.5, opacity=0.22)
    g.add(sphere)

    # Rim light (coloured stroke, gives the "lit edge" feel)
    rim = Circle(radius=radius)
    rim.set_fill(opacity=0)
    rim.set_stroke(color=color, width=3, opacity=0.50)
    g.add(rim)

    # Specular highlight — small white ellipse offset to upper-left
    spec = Ellipse(width=radius * 0.52, height=radius * 0.34)
    spec.set_fill(WHITE, opacity=0.62)
    spec.set_stroke(width=0)
    spec.move_to(
        np.array([-radius * 0.28,  radius * 0.30, 0])   # offset from origin
    )
    spec.rotate(-20 * DEGREES)
    g.add(spec)

    return g

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
COLOR_WHITE     = "#E5E5EA" 

MIN_VEC_LEN = 0.02

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
                          stroke_width=1, color="#E5E5EA"))
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

def safe_put(arrow, start, end):
    if np.linalg.norm(end - start) < MIN_VEC_LEN:
        end = start + np.array([0.0, -MIN_VEC_LEN, 0.0])
    arrow.put_start_and_end_on(start, end)

def text_bg(text_mob, fill_color=COLOR_BG, fill_opacity=0.80,
            pad_x=0.22, pad_y=0.18, stroke=False,
            stroke_color=COLOR_WHITE, stroke_opacity=0.3):
    """Solid dark background rect behind text for readability."""
    bg = Rectangle(
        width=text_mob.width + pad_x * 2,
        height=text_mob.height + pad_y * 2,
        fill_color=fill_color, fill_opacity=fill_opacity,
        stroke_width=1 if stroke else 0,
        stroke_color=stroke_color,
        stroke_opacity=stroke_opacity if stroke else 0,
    ).move_to(text_mob.get_center()).set_z_index(text_mob.get_z_index() - 1)
    return VGroup(bg, text_mob)

def make_dashed_connector(get_start, get_end, color):
    """always_redraw DashedLine connector that never crashes on zero length."""
    def draw():
        s = get_start()
        e = get_end()
        if np.linalg.norm(e - s) < MIN_VEC_LEN:
            e = s + np.array([0.0, -MIN_VEC_LEN * 2, 0.0])
        # Set z_index to 0 to remain behind the balls
        return DashedLine(
            s, e, color=color,
            stroke_width=1.8, dash_length=0.14,
            dashed_ratio=0.5, stroke_opacity=0.65
        ).set_z_index(0)
    return always_redraw(draw)

# ═══════════════════════════════════════════════════════════════════
#  SCENE
# ═══════════════════════════════════════════════════════════════════
class Scene3_TheFrameShift(Scene):

    def construct(self):
        self.camera.background_color = COLOR_BG
        grid = build_grid()
        self.add(grid)

        # ──────────────────────────────────────────────────────────
        # ACT 1 · "Reality Splits"
        # ──────────────────────────────────────────────────────────
        words     = ["Reality", "Splits"] 
        word_mobs = [
            Text(w, font="Segoe UI", font_size=72,
                 weight=BOLD, color=COLOR_WHITE).set_z_index(6)
            for w in words
        ]
        title_group = VGroup(*word_mobs).arrange(RIGHT, buff=0.25).move_to(ORIGIN)

        title_bg = Rectangle(
            width=title_group.width + 0.5,
            height=title_group.height + 0.35,
            fill_color=COLOR_BG, fill_opacity=0.78, stroke_width=0
        ).move_to(title_group).set_z_index(5)
        self.add(title_bg)

        self.play(
            AnimationGroup(
                FadeIn(word_mobs[0], shift=UP * 0.2),
                FadeIn(word_mobs[1], shift=UP * 0.2),
                lag_ratio=0.4,
            ),
            run_time=1.5
        )
        self.wait()

        self.play(
            title_group.animate.scale(0.52).move_to(UP * 3.25).set_opacity(0.50),
            title_bg.animate.scale(0.52).move_to(UP * 3.25).set_opacity(0.50),
            run_time=1.0,
        )
        self.wait()

        divider = DashedLine(
            UP * 4.2, DOWN * 4.2,
            color=COLOR_GROUND, stroke_width=2,
            dash_length=0.22, dashed_ratio=0.45
        ).set_z_index(0) 
        self.play(Create(divider), run_time=1.4)
        self.wait()

        lbl_vert = Text("Vertical World", font="Segoe UI",
                        font_size=28, weight=BOLD, color=COLOR_VEC_G)
        lbl_vert.move_to(LEFT * 3.5 + UP * 2.25)

        lbl_horiz = Text("Horizontal World", font="Segoe UI",
                         font_size=28, weight=BOLD, color=COLOR_VEC_V_X)
        lbl_horiz.move_to(RIGHT * 3.5 + UP * 2.25)

        self.play(
            FadeIn(lbl_vert,  shift=RIGHT * 0.3),
            FadeIn(lbl_horiz, shift=LEFT  * 0.3),
            run_time=1
        )

        sep_l = Line(LEFT * 6.5 + UP * 2, LEFT * 0.25 + UP * 2,
                     color=COLOR_VEC_G, stroke_width=1, stroke_opacity=0.35)
        sep_r = Line(RIGHT * 0.25 + UP * 2, RIGHT * 6.5 + UP * 2,
                     color=COLOR_VEC_V_X, stroke_width=1, stroke_opacity=0.35)
        self.play(Create(sep_l), Create(sep_r), run_time=0.6)
        self.wait(0.5)

        # ──────────────────────────────────────────────────────────
        # ACT 2 · VERTICAL WORLD
        # ──────────────────────────────────────────────────────────
        q_vert = Text("How far did it fall?",
                      font="Segoe UI", font_size=20,
                      color=COLOR_VEC_G, slant=ITALIC)
        q_vert.move_to(LEFT * 3.5 + UP * 1.75)
        self.play(FadeIn(q_vert, shift=UP * 0.15))
        self.wait()

        BALL_V_START = np.array([-3.5, 1.0, 0.0])
        # Set ball_v z_index to 3 so it is in front of the arrow
        ball_v = make_ball(COLOR_GREY_BALL, radius=0.30).move_to(BALL_V_START).set_z_index(3)
        self.play(FadeIn(ball_v, scale=0.4), run_time=0.5)
        self.wait(0.5)

        # Set arrow z_index to 1 so it is behind the ball
        g_arrow_v = Arrow(
            ball_v.get_center(),
            ball_v.get_center() + DOWN * 1.0,
            color=COLOR_VEC_G, buff=0, stroke_width=5
        ).set_z_index(1)

        G_LBL_OFFSET = np.array([-0.50, -0.50, 0.0])
        g_lbl_v = MathTex(r"g", color=COLOR_VEC_G,
                          font_size=34).set_z_index(4)
        g_lbl_v.move_to(ball_v.get_center() + np.array([0.35, -0.5, 0.0]))

        self.play(GrowArrow(g_arrow_v), Write(g_lbl_v), run_time=0.9)
        self.wait(0.8)

        # --- PHYSICS ENGINE ALIGNMENT ---
        GRAVITY = 2.75  # Derived from 5.5 units / 2 sec
        t_final = 1.6   # Time required to fall exactly 3.5 units at this gravity
        
        N_DOTS     = 9
        dot_t_vals = np.linspace(0.15, 1.45, N_DOTS)
        
        trail_dots_v = VGroup()
        for tv in dot_t_vals:
            y_pos = BALL_V_START[1] - 0.5 * GRAVITY * (tv ** 2)
            d = Dot(
                point=np.array([BALL_V_START[0], y_pos, 0.0]),
                radius=0.055, color=COLOR_GREY_BALL, fill_opacity=0.0
            ).set_z_index(1)
            trail_dots_v.add(d)
        self.add(trail_dots_v)

        t_v = ValueTracker(0)

        def update_v(m):
            t   = t_v.get_value()
            y   = BALL_V_START[1] - 0.5 * GRAVITY * (t ** 2)
            pos = np.array([BALL_V_START[0], y, 0.0])
            m.move_to(pos)
            safe_put(g_arrow_v, pos, pos + DOWN * 1.0)
            g_lbl_v.move_to(pos + np.array([0.35, -0.5, 0.0]))
            for tv, dot in zip(dot_t_vals, trail_dots_v):
                if t >= tv:
                    dot.set_fill(opacity=0.50)

        ball_v.add_updater(update_v)
        
        self.play(t_v.animate.set_value(t_final),
                  run_time=t_final, rate_func=linear) 
        ball_v.clear_updaters()
        self.wait(0.7)

        axes_v_note = Text("Only ↑↓ matters here",
                           font="Segoe UI", font_size=16,
                           color=COLOR_GROUND).set_z_index(6)
        axes_v_note.move_to(LEFT * 3.5 + DOWN * 3.3)
        axes_v_group = text_bg(axes_v_note)
        self.play(FadeIn(axes_v_group), run_time=0.6)
        self.wait(0.8)

        # ──────────────────────────────────────────────────────────
        # ACT 3 · HORIZONTAL WORLD
        # ──────────────────────────────────────────────────────────
        q_horiz = Text("How far did it move sideways?",
                       font="Segoe UI", font_size=20,
                       color=COLOR_VEC_V_X, slant=ITALIC).set_z_index(6)
        q_horiz.move_to(RIGHT * 3.5 + UP * 1.75)
        self.play(FadeIn(q_horiz, shift=UP * 0.15), run_time=0.7)
        self.wait()

        BALL_H_START = np.array([0.8, 1.0, 0.0])
        # Set ball_h z_index to 3
        ball_h = make_ball(COLOR_BLUE_BALL, radius=0.30).move_to(BALL_H_START).set_z_index(3)
        self.play(FadeIn(ball_h, scale=0.4), run_time=0.5)
        self.wait(0.5)

        # Set arrow z_index to 1
        vx_arrow = Arrow(
            ball_h.get_center(),
            ball_h.get_center() + RIGHT * 1.4,
            color=COLOR_VEC_V_X, buff=0, stroke_width=5
        ).set_z_index(1)
        vx_lbl = MathTex(r"v_x", color=COLOR_VEC_V_X,
                         font_size=32).set_z_index(4)
        vx_lbl.next_to(vx_arrow, UP, buff=0.05)

        self.play(GrowArrow(vx_arrow), Write(vx_lbl))
        self.wait()

        # Set phantom arrow z_index to 1
        phantom_g = Arrow(
            ball_h.get_center(),
            ball_h.get_center() + DOWN * 1.0,
            color=COLOR_VEC_G, buff=0, stroke_width=4,
            stroke_opacity=0.6
        ).set_z_index(1)
        phantom_lbl = MathTex(r"g", color=COLOR_VEC_G,
                          font_size=34)
        phantom_lbl.next_to(phantom_g, RIGHT, buff=0.05)

        self.play(GrowArrow(phantom_g),
                  FadeIn(phantom_lbl, shift=RIGHT * 0.1))

        self.wait(0.5)
        self.play(
            phantom_g.animate.shift(DOWN * 0.4).set_opacity(0),
            phantom_lbl.animate.shift(DOWN * 0.4).set_opacity(0)
        )
        self.remove(phantom_g, phantom_lbl)

        no_g_text = Text("Gravity does NOT exist here.",
                         font="Segoe UI", font_size=22,
                         weight=BOLD, color=COLOR_VEC_G).set_z_index(7)
        no_g_text.move_to(RIGHT * 3.5 + DOWN * 0.25)
        no_g_bg = RoundedRectangle(
            width=no_g_text.width + 0.30,
            height=no_g_text.height + 0.25,
            corner_radius=0.25,
            fill_color=COLOR_BG, fill_opacity=0.80,
            stroke_color=COLOR_VEC_G, stroke_width=1.2,
            stroke_opacity=0.45
        ).move_to(no_g_text.get_center()).set_z_index(6)
        self.play(FadeIn(VGroup(no_g_bg, no_g_text), scale=0.88),
                  run_time=0.8)
        self.wait(1.5)

        # --- PHYSICS ENGINE ALIGNMENT (Horizontal) ---
        t_final = 1.6  
        slide_dist = 4.6
        H_VEL = slide_dist / t_final  
        
        N_DOTS_H = 9
        dot_t_vals_h = np.linspace(0.15, 1.45, N_DOTS_H) 
        
        trail_dots_h = VGroup()
        for tv in dot_t_vals_h:
            x_pos = BALL_H_START[0] + H_VEL * tv
            d = Dot(
                point=np.array([x_pos, BALL_H_START[1], 0.0]),
                radius=0.055, color=COLOR_BLUE_BALL, fill_opacity=0.0
            ).set_z_index(1)
            trail_dots_h.add(d)
        self.add(trail_dots_h)

        t_h = ValueTracker(0)

        def update_h(m):
            t = t_h.get_value()
            x = BALL_H_START[0] + H_VEL * t
            m.move_to([x, BALL_H_START[1], 0])
            safe_put(vx_arrow, m.get_center(), m.get_center() + RIGHT * 1.4)
            vx_lbl.next_to(vx_arrow, UP, buff=0.08)
            for tv, dot in zip(dot_t_vals_h, trail_dots_h):
                if t >= tv:
                    dot.set_fill(opacity=0.50)

        ball_h.add_updater(update_h)
        
        self.play(t_h.animate.set_value(t_final),
                  run_time=t_final, rate_func=linear)
        ball_h.clear_updaters()
        self.wait()

        axes_h_note = Text("Only ←→ matters here",
                           font="Segoe UI", font_size=16,
                           color=COLOR_GROUND).set_z_index(6)
        axes_h_note.move_to(RIGHT * 3.5 + DOWN * 3.3)
        axes_h_group = text_bg(axes_h_note)
        self.play(FadeIn(axes_h_group))
        self.wait()

        # ──────────────────────────────────────────────────────────
        # ACT 4 · INDEPENDENCE OF MOTION
        # ──────────────────────────────────────────────────────────
        
        # Added ball_v and ball_h to the cleanup group so they transform too
        cleanup_group = VGroup(
            lbl_vert, lbl_horiz, sep_l, sep_r, divider,
            title_group, title_bg,
            q_vert, q_horiz,
            g_arrow_v, g_lbl_v,
            vx_arrow, vx_lbl,
            no_g_bg, no_g_text,
            axes_v_group, axes_h_group,
            trail_dots_v, trail_dots_h,
            ball_v, ball_h 
        )
        ground = Line(start=LEFT*7, end=RIGHT*7, color="#3A3A3C", stroke_width=2)
        ground.to_edge(DOWN, buff=1)

        # 1. Prepare the final title text FIRST
        iom_words = Text("Independence of Motion", font="Segoe UI", font_size=46,
                         weight=BOLD, color=COLOR_GREEN).to_edge(UP, buff=0.25)

        # 2. Morph everything (including balls) into the title
        self.play(
            ReplacementTransform(cleanup_group, iom_words),
            run_time=2
        )
        self.wait()
        
        ORIGIN_PT = np.array([-5.0, 2.5, 0.0])
        
        # 3. Recreate the balls transparently at the text's location 
        # so they can smoothly move to their starting positions.
        ball_v = make_ball(COLOR_GREY_BALL, radius=0.30).move_to(iom_words.get_center()).set_opacity(0).set_z_index(3)
        ball_h = make_ball(COLOR_BLUE_BALL, radius=0.30).move_to(iom_words.get_center()).set_opacity(0).set_z_index(3)
        self.add(ball_v, ball_h)

        self.play(
            ball_v.animate.move_to(ORIGIN_PT).set_opacity(0.35),
            ball_h.animate.move_to(ORIGIN_PT).set_opacity(0.35),
            FadeIn(ground, shift=UP*0.5),
            run_time=1.5
        )

        ball_real = make_ball(COLOR_BLUE_BALL, radius=0.30).move_to(ORIGIN_PT).set_z_index(4)
        self.play(
            FadeIn(ball_real, scale=0.5),
            ball_v.animate.set_opacity(0.25),
            ball_h.animate.set_opacity(0.25)
        )
        self.wait(0.5)

        proj_v_line = make_dashed_connector(
            lambda: ball_v.get_center(),
            lambda: ball_real.get_center(),
            COLOR_VEC_G
        )
        proj_h_line = make_dashed_connector(
            lambda: ball_h.get_center(),
            lambda: ball_real.get_center(),
            COLOR_AMBER
        )
        self.add(proj_v_line, proj_h_line)

        self.wait(0.5)

        # ─── Physics & Timer Setup ────────────────────────────────
        t_master = ValueTracker(0)
        
        total_fall_time = 2.00 
        
        vertical_drop_distance = 5.5 - 0.28
        H_VEL   = 10.0 / total_fall_time                
        V_ACC   = (vertical_drop_distance * 2) / (total_fall_time ** 2)    
        
        timer_label = Text("Time:", font="monospace", font_size=28, color=LIGHT_GRAY)
        dummy_number = Text("0.00", font="monospace", font_size=28)
        dummy_unit = Text("s", font="monospace", font_size=28)
        VGroup(timer_label, dummy_number, dummy_unit).arrange(RIGHT, buff=0.15).to_edge(DOWN, buff=0.5)
        
        timer_number = always_redraw(lambda: Text(
            f"{t_master.get_value() * total_fall_time:.2f}",
            font="monospace",
            font_size=28,
            color=LIGHT_GRAY
        ).next_to(timer_label, RIGHT, buff=0.15, aligned_edge=DOWN))
        
        timer_unit = Text("s", font="monospace", font_size=28, color=LIGHT_GRAY)
        timer_unit.add_updater(lambda u: u.next_to(timer_number, RIGHT, buff=0.1, aligned_edge=DOWN))
        
        timer_group = VGroup(timer_label, timer_number, timer_unit)
        self.play(FadeIn(timer_group), run_time=0.5)

        # 5. Fix: Assign individual updaters directly to the balls
        def update_real(mob):
            t = t_master.get_value() * total_fall_time
            x = ORIGIN_PT[0] + H_VEL * t
            y = ORIGIN_PT[1] - 0.5 * V_ACC * (t ** 2)
            mob.move_to([x, y, 0])

        def update_h_ball(mob):
            t = t_master.get_value() * total_fall_time
            x = ORIGIN_PT[0] + H_VEL * t
            mob.move_to([x, ORIGIN_PT[1], 0])

        def update_v_ball(mob):
            t = t_master.get_value() * total_fall_time
            y = ORIGIN_PT[1] - 0.5 * V_ACC * (t ** 2)
            mob.move_to([ORIGIN_PT[0], y, 0])

        ball_real.add_updater(update_real)
        ball_h.add_updater(update_h_ball)
        ball_v.add_updater(update_v_ball)

        # ─── Animation Execution ──────────────────────────────────
        self.play(t_master.animate.set_value(1.0), run_time=total_fall_time, rate_func=linear)

        # Freeze the updaters instantly on impact
        ball_real.clear_updaters()
        ball_h.clear_updaters()
        ball_v.clear_updaters()
        timer_number.clear_updaters()
        timer_unit.clear_updaters()

        # The Impact Ripples
        ripple_v = Circle(radius=0.3, color=COLOR_GROUND, stroke_width=4).move_to(ball_v.get_center())
        ripple_real = Circle(radius=0.3, color=COLOR_BLUE_BALL, stroke_width=4).move_to(ball_real.get_center())
        
        self.play(
            ripple_v.animate.scale(2.5).set_opacity(0),
            ripple_real.animate.scale(2.5).set_opacity(0),
            run_time=0.6,
            rate_func=rate_functions.ease_out_quad
        )

        self.wait()

        # ──────────────────────────────────────────────────────────
        # ACT 5 · BLIND TO EACH OTHER
        # ──────────────────────────────────────────────────────────

        blind_text = Text(
            "Same space. Same object. Completely blind to each other.",
            font="Segoe UI", font_size=19, color=COLOR_AMBER
        ).set_z_index(7)
        blind_text.move_to(DOWN * 1.25)
        blind_bg = Rectangle(
            width=blind_text.width + 0.40,
            height=blind_text.height + 0.26,
            fill_color=COLOR_BG, fill_opacity=0.82, stroke_width=0
        ).move_to(blind_text.get_center()).set_z_index(6)
        self.play(FadeIn(blind_bg),
                  Write(blind_text),
                  run_time = 2)
        self.wait(1.5)

        objects_to_fade = [m for m in self.mobjects if m not in [grid, ground, iom_words]]
        
        self.play(FadeOut(Group(*objects_to_fade)), run_time=1.5)
        self.wait(0.5)