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

class Scene2_TheNaiveAnswer(Scene):
    def construct(self):
        COLOR_BG = "#1C1C1E"
        COLOR_GROUND = "#8E8E93"
        COLOR_GREY_BALL = "#E5E5EA"
        COLOR_BLUE_BALL = "#007AFF"
        COLOR_VEC_G = "#FF3B30"     # Apple Red for gravity
        COLOR_VEC_V_X = "#32ADE6"   # Apple Cyan for initial velocity

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

        self.add(grid)

        # ==========================================
        # 1. SETUP & CONSTANTS
        # ==========================================
        self.camera.background_color = "#1C1C1E"
        ground = Line(start=LEFT*7, end=RIGHT*7, color="#3A3A3C", stroke_width=2)
        ground.to_edge(DOWN, buff=1)

        start_pos = np.array([-5.0, 2.5, 0.0])

        horizontal_distance = 10.0 

        self.play(FadeIn(ground, shift=UP*0.5), run_time=1.5, rate_func=smooth)
        self.wait(1)

        dummy_ball = Circle(radius=0.3).move_to(start_pos)

        drop_distance = dummy_ball.get_y() - ground.get_y() - dummy_ball.radius

        def drop_physics(mob, alpha):
            y = start_pos[1] - (drop_distance * (alpha ** 2))
            mob.move_to(np.array([start_pos[0], y, 0]))

        def throw_physics(mob, alpha):
            x = start_pos[0] + (horizontal_distance * alpha)
            y = start_pos[1] - (drop_distance * (alpha ** 2))
            mob.move_to(np.array([x, y, 0]))

        # Master clock
        t_tracker = ValueTracker(0)
        
        # ==========================================
        # 2 & 3. GREY BALL APPEAR & FALL (Trailing Dashes)
        # ==========================================
        ball1 = make_ball(COLOR_GREY_BALL, radius=0.30)
        ball1.set_z_index(2).move_to(start_pos)
        self.play(FadeIn(ball1, scale=0.5), run_time=1)
        self.wait(0.5)

        # Create the full dashed line, hide all dashes initially
        full_drop_path = DashedLine(
            start_pos, start_pos + DOWN * drop_distance, 
            dashed_ratio=0.5, color="#E5E5EA"
        ).set_z_index(0)

        for dash in full_drop_path.submobjects:
            dash.set_opacity(0)
        self.add(full_drop_path)

        # Updater: Only reveal dashes that are safely behind the ball
        def update_drop_trail(m):
            t = t_tracker.get_value()
            lag_y = 0.8 * (1 - t) # Lag shrinks to 0 as ball hits ground (catches up)
            ball_y = ball1.get_y()
            for dash in m.submobjects:
                # If dash is above the ball + gap, reveal it
                if dash.get_center()[1] >= ball_y + lag_y:
                    dash.set_opacity(1)

        ball1.add_updater(lambda m: drop_physics(m, t_tracker.get_value()))
        full_drop_path.add_updater(update_drop_trail)

        self.play(t_tracker.animate.set_value(1), run_time=2, rate_func=linear)
        
        ball1.clear_updaters()
        full_drop_path.clear_updaters()
        # Force any remaining dashes to appear at t=1
        for dash in full_drop_path.submobjects: dash.set_opacity(1)

        ripple = Circle(radius=0.3, color=COLOR_GREY_BALL, stroke_width=4)
        ripple.move_to(ball1.get_center())
        self.play(
            ripple.animate.scale(2.5).set_opacity(0),
            run_time=0.6,
            rate_func=rate_functions.ease_out_quad
        )
        self.wait()


        # ==========================================
        # 4 & 5. BLUE BALL APPEAR & THROW (Trailing Dashes)
        # ==========================================
        
        ball2 = make_ball(COLOR_BLUE_BALL, radius=0.30)
        # FIXED: Set z_index to be above the trail, and move to start_pos before fading in
        ball2.set_z_index(2).move_to(start_pos) 
        self.play(FadeIn(ball2, scale=0.5), run_time=1)
        self.wait(0.5)

        t_tracker.set_value(0) # Reset clock

        base_path_throw = ParametricFunction(
            lambda t: np.array([
                start_pos[0] + (horizontal_distance * t),
                start_pos[1] - (drop_distance * (t ** 2)),
                0
            ]),
            t_range=[0, 1]
        )
        
        full_throw_path = DashedVMobject(
            base_path_throw, num_dashes=35
        ).set_color("#FF3B30").set_stroke(width=4).set_z_index(0)

        for dash in full_throw_path.submobjects:
            dash.set_opacity(0)
        self.add(full_throw_path)

        def update_throw_trail(m):
            t = t_tracker.get_value()
            lag_x = 1.2 * (1 - t) # Gap shrinks to 0 at impact
            ball_x = ball2.get_x()
            for dash in m.submobjects:
                # If dash is left of the ball - gap, reveal it
                if dash.get_center()[0] <= ball_x - lag_x:
                    dash.set_opacity(1)

        ball2.add_updater(lambda m: throw_physics(m, t_tracker.get_value()))
        full_throw_path.add_updater(update_throw_trail)

        self.play(t_tracker.animate.set_value(1), run_time=2, rate_func=linear)
        
        ball2.clear_updaters()
        full_throw_path.clear_updaters()
        for dash in full_throw_path.submobjects: dash.set_opacity(1)

        ripple = Circle(radius=0.3, color=COLOR_GREY_BALL, stroke_width=4)
        ripple.move_to(ball2.get_center())
        self.play(
            ripple.animate.scale(2.5).set_opacity(0),
            run_time=0.6,
            rate_func=rate_functions.ease_out_quad
        )
        self.wait()
        # ==========================================
        # 6. PERFECT FLATTENING (Solid Swap Technique)
        # ==========================================
        # Create solid versions of the math paths for a clean unbending animation
        solid_drop = Line(start_pos, start_pos + DOWN * drop_distance, color="#E5E5EA", stroke_width=4)
        solid_throw = base_path_throw.copy().set_color("#FF3B30").set_stroke(width=4)

        # Swap dashed for solid seamlessly
        self.play(
            FadeIn(solid_drop), FadeIn(solid_throw),
            FadeOut(full_drop_path), FadeOut(full_throw_path),
            run_time=0.3
        )

        len_drop = solid_drop.get_length()
        len_throw = solid_throw.get_arc_length()

        # The target flat lines
        flat_drop = Line(ORIGIN, RIGHT * len_drop, color="#E5E5EA", stroke_width=4)
        flat_throw = Line(ORIGIN, RIGHT * len_throw, color="#FF3B30", stroke_width=4)

        bars_group = VGroup(flat_drop, flat_throw).arrange(DOWN, buff=0.8, aligned_edge=LEFT)
        bars_group.move_to(RIGHT * 0.5 + UP * 0.5)

        # Smooth Unbending Transformation
        self.play(
            Transform(solid_drop, flat_drop),
            Transform(solid_throw, flat_throw),
            run_time=1.5,
            rate_func=rate_functions.ease_in_out_cubic
        )
        
        diff_line = DashedLine(
            solid_drop.get_right(), 
            np.array([solid_drop.get_right()[0], solid_throw.get_right()[1], 0]), 
            color="#8E8E93"
        )
        self.play(Create(diff_line))
        self.wait(2)

        # ==========================================
        # 7. RESET FOR SIMULTANEOUS DROP
        # ==========================================
        self.play(FadeOut(solid_drop), FadeOut(solid_throw), FadeOut(diff_line))
        
        self.play(
            ball1.animate.move_to(start_pos),
            ball2.animate.move_to(start_pos),
            run_time=1.5,
            rate_func=smooth
        )
        self.wait(2)

        # ==========================================
        # 8. SLOW MOTION DROP (With Synced Timer)
        # ==========================================
        t_tracker.set_value(0)

        # The true physical time of the fall
        total_fall_time = 2.00 
        
        # 1. Create the label (our static anchor)
        timer_label = Text("Time:", font="monospace", font_size=36, color="#E5E5EA")
        
        # 2. DUMMY GROUP TRICK: Set the layout position perfectly in the UR corner
        dummy_number = Text("0.00", font="monospace", font_size=36)
        dummy_unit = Text("s", font="monospace", font_size=36)
        VGroup(timer_label, dummy_number, dummy_unit).arrange(RIGHT, buff=0.15).to_corner(UR, buff=1.0)
        
        # 3. Create the dynamically updating number (Using the anchor)
        timer_number = always_redraw(lambda: Text(
            f"{t_tracker.get_value() * total_fall_time:.2f}",
            font="monospace",
            font_size=36,
            color="#FFFFFF"
        ).next_to(timer_label, RIGHT, buff=0.15, aligned_edge=DOWN))
        
        # 4. Create the dynamically updating unit
        timer_unit = Text("s", font="monospace", font_size=36, color="#E5E5EA")
        timer_unit.add_updater(lambda u: u.next_to(timer_number, RIGHT, buff=0.1, aligned_edge=DOWN))
        
        # Add the visible parts to the scene
        timer_group = VGroup(timer_label, timer_number, timer_unit)
        self.play(FadeIn(timer_group), run_time=0.5)

        ball1.add_updater(lambda m: drop_physics(m, t_tracker.get_value()))
        ball2.add_updater(lambda m: throw_physics(m, t_tracker.get_value()))

        # Normal speed: 0 to 0.90 (which maps to 0.00 to 1.80 seconds on the timer)
        self.play(t_tracker.animate.set_value(0.90), run_time=1.8, rate_func=linear)
        
        # Slow motion: 0.90 to 1.0 (which maps to 1.80 to 2.00 seconds on the timer)
        self.play(t_tracker.animate.set_value(1.0), run_time=2.0, rate_func=linear)

        # Freeze the updaters instantly on impact
        ball1.clear_updaters()
        ball2.clear_updaters()
        timer_number.clear_updaters()
        timer_unit.clear_updaters()

        # The Impact Ripples
        ripple1 = Circle(radius=0.3, color="#E5E5EA", stroke_width=4).move_to(ball1.get_center())
        ripple2 = Circle(radius=0.3, color="#007AFF", stroke_width=4).move_to(ball2.get_center())
        self.play(
            ripple1.animate.scale(2.5).set_opacity(0),
            ripple2.animate.scale(2.5).set_opacity(0),
            run_time=0.6,
            rate_func=rate_functions.ease_out_quad
        )

        self.wait()

        # ==========================================
        # 9. APPLE-STYLE TEXT ("Exactly the same")
        # ==========================================
        full_text = Text(
            "Exactly the same", 
            font="Segoe UI", 
            font_size=64, 
            weight=BOLD,
            t2c={"same": "#34C759"}  # Automatically colors just the word "same" green
        )
        full_text.move_to(UP * 1.5)

        word1 = full_text[0:7]
        word2 = full_text[7:10]
        word3 = full_text[10:14]

        self.play(
            AnimationGroup(
                FadeIn(word1, shift=UP * 0.2),
                FadeIn(word2, shift=UP * 0.2),
                FadeIn(word3, shift=UP * 0.2),
                lag_ratio=0.4 
            ),
            run_time=3, # Adjusted to 3 seconds so the sequence flows a bit faster
            rate_func=rate_functions.ease_out_cubic
        )

        # Wait exactly 1 second before the next text appears
        self.wait(1)

        # ==========================================
        # 10. SURPRISED -> UNDERSTAND TEXT MORPH
        # ==========================================
        text_surprised = Text("surprised by this?", font="Segoe UI", font_size=40, color="#8E8E93")
        text_understand = Text("truly understand?", font="Segoe UI", font_size=40, color="#8E8E93")
        
        # Center is the default position, so no .move_to() is needed!
        

        self.play(
                FadeIn(text_surprised, shift=UP * 0.2),            
            run_time=3, # Adjusted to 3 seconds so the sequence flows a bit faster
            rate_func=rate_functions.ease_out_cubic
        )
        
        # Give the viewer a moment to read the first question
        self.wait(1.5)
        
        # 2. Transform the text seamlessly
        self.play(
            TransformMatchingShapes(text_surprised, text_understand), 
            run_time=2, 
            rate_func=rate_functions.ease_in_out_cubic
        )

        # Final pause and fade to black
        self.wait(2)
        
        objects_to_fade = [m for m in self.mobjects if m is not grid]
        self.play(FadeOut(Group(*objects_to_fade)), run_time=1.5)
        
        self.wait()