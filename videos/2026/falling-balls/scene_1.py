from manim import *
import numpy as np

# We define the Apple-inspired colors for consistency
COLOR_BG = "#1C1C1E"
COLOR_GROUND = "#8E8E93"
COLOR_GREY_BALL = "#E5E5EA"
COLOR_BLUE_BALL = "#007AFF"
COLOR_VEC_G = "#FF3B30"     # Apple Red for gravity
COLOR_VEC_V_X = "#32ADE6"   # Apple Cyan for initial velocity

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

class Scene1_Act1_Drop(Scene):
    
    def construct(self):

        self.camera.background_color = COLOR_BG
        # ==================================================
        # --- 0. THE FADING BACKGROUND GRID ---
        # ==================================================
        grid = VGroup()
        max_x = 12
        max_y = 8
        grid_spacing = 0.5
        
        # Helper function to create a line that fades out at its ends
        def get_fading_line(start, end, peak_opacity):
            line_segments = VGroup()
            segs = 30
            vec = end - start
            for i in range(segs):
                p1 = start + vec * (i / segs)
                p2 = start + vec * ((i + 1) / segs)
                # Parabolic fade along the line length
                t = (i + 0.5) / segs
                op = peak_opacity *0.25* (1 - (2*t - 1)**2)
                line_segments.add(Line(p1, p2, stroke_opacity=op, stroke_width=1, color="#E5E5EA"))
            return line_segments
            
        # Vertical grid lines (fade based on X distance from center)
        for x in np.arange(-max_x, max_x + 0.1, grid_spacing):
            peak = 0.2 * (1 - (abs(x)/max_x)**1.5) # The 0.2 controls maximum grid opacity
            if peak > 0:
                grid.add(get_fading_line(UP*max_y + RIGHT*x, DOWN*max_y + RIGHT*x, peak))
                
        # Horizontal grid lines (fade based on Y distance from center)
        for y in np.arange(-max_y, max_y + 0.1, grid_spacing):
            peak = 0.2 * (1 - (abs(y)/max_y)**1.5)
            if peak > 0:
                grid.add(get_fading_line(LEFT*max_x + UP*y, RIGHT*max_x + UP*y, peak))

        self.play(
            LaggedStart(
                *[Create(line) for line in grid],
                lag_ratio=0.02
            ),
            run_time=3
        )

        ground = Line(start=LEFT*7, end=RIGHT*7, color=COLOR_GROUND, stroke_width=2)
        ground.to_edge(DOWN, buff=1)

        ball = make_ball(COLOR_GREY_BALL, radius=0.30)
        
        # Ensure the ball is drawn on top of the vectors
        ball.set_z_index(1) 
        
        start_pos = np.array([-5.0, 2.5, 0.0])
        ball.move_to(start_pos)

        # Fade in sequence
        self.play(FadeIn(ground, shift=UP*0.5), run_time=1.5, rate_func=smooth)
        self.wait()
        self.play(FadeIn(ball, scale=0.5), run_time=1.5)
        self.wait(2) 

        # --- NEW: Gravity Vector for Drop ---
        grav_vec_drop = Arrow(
            start=ball.get_center(),
            end=ball.get_center() + DOWN * 1.5,
            color=COLOR_VEC_G,
            buff=0,
            stroke_width=6
        ).set_z_index(0) # Ensure vector is drawn behind the ball
        
        grav_lbl_drop = MathTex("g", color=COLOR_VEC_G).next_to(grav_vec_drop, RIGHT, buff=0.2).set_z_index(0)

        # Introduce the vector static (allows VO explanation before movement)
        self.play(GrowArrow(grav_vec_drop), Write(grav_lbl_drop), run_time=1)
        self.wait(2) 

        drop_distance = ball.get_y() - ground.get_y()- 0.30

        # TRUE PHYSICS: Alpha acts as pure time. Squaring it mimics perfect gravity.
        def drop_physics(mob, alpha):
            y = start_pos[1] - (drop_distance * (alpha ** 2))
            mob.move_to(np.array([start_pos[0], y, 0]))

        # The Drop (Vector fades out concurrently as ball falls in front of it)
        self.play(
            UpdateFromAlphaFunc(ball, drop_physics),
            FadeOut(VGroup(grav_vec_drop, grav_lbl_drop), run_time=0.7), # Fades out during the first half of the drop
            run_time=2,
            rate_func=linear 
        )

        # The Impact Ripple
        ripple = Circle(radius=0.3, color=COLOR_GREY_BALL, stroke_width=4)
        ripple.move_to(ball.get_center())
        self.play(
            ripple.animate.scale(2.5).set_opacity(0),
            run_time=0.6,
            rate_func=rate_functions.ease_out_quad
        )
        self.wait()


        # Clear the first ball
        self.play(FadeOut(ball))

        # Create the Second Ball
        ball2 = make_ball(COLOR_BLUE_BALL, radius=0.30)
        ball2.move_to(start_pos)
        ball2.set_z_index(1) 

        # Fade in
        self.play(FadeIn(ball2, scale=0.5), run_time=1.5)
        self.wait(1.5)


        # --- NEW: Vectors for the Throw (g and vx) ---
        grav_vec_throw = Arrow(
            start=ball2.get_center(), end=ball2.get_center() + DOWN * 1.5,
            color=COLOR_VEC_G, buff=0, stroke_width=6
        ).set_z_index(0) 
        grav_lbl_throw = MathTex("g", color=COLOR_VEC_G).next_to(grav_vec_throw, RIGHT, buff=0.1)

        vx_vec = Arrow(
            start=ball2.get_center(), end=ball2.get_center() + RIGHT * 1.5,
            color=COLOR_VEC_V_X, buff=0, stroke_width=6
        ).set_z_index(0) 
        vx_lbl = MathTex("v_x", color=COLOR_VEC_V_X).next_to(vx_vec, DOWN, buff=0.1)

        # Introduce both vectors while stationary
        self.play(
            GrowArrow(vx_vec), Write(vx_lbl),
            GrowArrow(grav_vec_throw), Write(grav_lbl_throw),
            run_time=1.5
        )
        self.wait(2.5) 

        horizontal_distance = 10.0 

        # TRUE PHYSICS + Dynamic Vector Updates
        def throw_physics(mob, alpha):
            x = start_pos[0] + (horizontal_distance * alpha)
            y = start_pos[1] - (drop_distance * (alpha ** 2))
            current_pos = np.array([x, y, 0])
            mob.move_to(current_pos)

            # Move and update the labels/arrows attached to ball2
            # grav_vec_throw.put_start_and_end_on(current_pos, current_pos + DOWN * 1.5)
            # vx_vec.put_start_and_end_on(current_pos, current_pos + RIGHT * 2.0)
            # grav_lbl_throw.next_to(grav_vec_throw, RIGHT, buff=0.1)
            # vx_lbl.next_to(vx_vec, DOWN, buff=0.1)


        # The Throw 
        self.play(
            UpdateFromAlphaFunc(ball2, throw_physics),
            FadeOut(VGroup(grav_vec_throw, vx_vec, grav_lbl_throw, vx_lbl), run_time=0.1, rate_func=linear),
            run_time=2, 
            rate_func=linear 
        )

        # The Impact Ripple
        ripple2 = Circle(radius=0.3, color=COLOR_BLUE_BALL, stroke_width=4)
        ripple2.move_to(ball2.get_center())
        self.play(
            ripple2.animate.scale(2.5).set_opacity(0),
            run_time=0.6,
            rate_func=rate_functions.ease_out_quad
        )
        self.wait()

        self.play(FadeOut(ball2, ground))

        # Text Reveal
        word1 = Text("Which", font="Segoe UI", font_size=64, weight=BOLD, color="#FFFFFF")
        word2 = Text("lands", font="Segoe UI", font_size=64, weight=BOLD, color="#FFFFFF")
        word3 = Text("first?", font="Segoe UI", font_size=64, weight=BOLD, color="#FFFFFF")
        
        question_group = VGroup(word1, word2, word3).arrange(RIGHT, buff=0.3)
        question_group.move_to(ORIGIN)

        self.play(
            AnimationGroup(
                FadeIn(word1, shift=UP * 0.2),
                FadeIn(word2, shift=UP * 0.2),
                FadeIn(word3, shift=UP * 0.2),
                lag_ratio=0.4 
            ),
            run_time=3.5,
            rate_func=rate_functions.ease_out_cubic 
        )

        self.wait(3)

        self.play(FadeOut(question_group), run_time=0.5)
        self.wait(0.5)
