from manim import *
import numpy as np

class Channelintro(Scene):
    def construct(self):

        self.camera.background_color = "#1C1C1E"

        # --- 1. The Squircle (Superellipse - Uniform Speed Fix) ---
        r = 2
        n = 4.5
        
        def squircle_curve(t):
            x = r * 1.04 * np.sign(np.cos(t)) * (np.abs(np.cos(t)) ** (2/n))
            y = r * np.sign(np.sin(t)) * (np.abs(np.sin(t)) ** (2/n))
            return np.array([x, y, 0])

        t_values = np.linspace(0, TAU, 1000)
        raw_points = [squircle_curve(t) for t in t_values]
        temp_path = VMobject().set_points_as_corners(raw_points)
        
        uniform_points = [temp_path.point_from_proportion(p) for p in np.linspace(0, 1, 500)]
        
        # ADDED FILL: This makes the center of the squircle opaque to hide the text!
        squircle_box = VMobject(
            color="#E5E5EA", 
            stroke_width=10, 
            fill_color="#1C1C1E", 
            fill_opacity=1
        )
        squircle_box.set_points_as_corners(uniform_points)

        # --- 2. The Swoosh Path ---
        start_point = np.array([2.8, 1.6, 0])
        end_point =   np.array([-2.15, -2, 0])
        
        base_arc = ArcBetweenPoints(
            start=start_point,
            end=end_point,
            angle=PI/3,
        )

        # --- 3. The Pointy Swoosh ---
        swoosh = VGroup()
        num_segments = 200 
        for i in range(num_segments):
            a1 = i / num_segments
            a2 = (i + 1) / num_segments
            p1 = base_arc.point_from_proportion(a1)
            p2 = base_arc.point_from_proportion(a2)
            
            current_width = 16 * (1 - a1**1.5)
            segment = Line(p1, p2, stroke_width=current_width)
            swoosh.add(segment)
        
        swoosh.set_color_by_gradient("#1C1C1E", "#E5E5EA", "#E5E5EA", "#E5E5EA")

        # --- 4. The Buffed Cutouts ---
        buff_mask = VGroup()
        for i in range(num_segments):
            a1 = i / num_segments
            a2 = (i + 1) / num_segments
            p1 = base_arc.point_from_proportion(a1)
            p2 = base_arc.point_from_proportion(a2)
            
            mask_width = (16 * (1 - a1**1.5)) + 14
            mask_segment = Line(p1, p2, color="#1C1C1E", stroke_width=mask_width)
            buff_mask.add(mask_segment)

        # --- 5. The Realistic Flare ---
        flare_center = base_arc.point_from_proportion(0.82)
        
        core = Dot(flare_center, radius=0.1, color="#FFFFFF", fill_opacity=1)
        inner_halo = Circle(radius=0.12, color="#E5E5EA", fill_opacity=0.2, stroke_width=0).move_to(flare_center)
        
        outer_glow = VGroup()
        for i in range(15):
            opacity = 0.1 * (1 - (i / 30))**2
            ring = Dot(
                flare_center, 
                radius=0.12 + (i * 0.015),
                color="#E5E5EA", 
                fill_opacity=opacity,
                stroke_width=0
            )
            outer_glow.add(ring)

        flare = VGroup(outer_glow, inner_halo, core)

        # --- PREPARE LEFT-TO-RIGHT ANIMATION ---
        swoosh = VGroup(*reversed(swoosh))
        buff_mask = VGroup(*reversed(buff_mask))

        # --- 6. Group, Scale, and Layout ---
        SCALE_FACTOR = 0.42
        
        logo_group = VGroup(squircle_box, buff_mask, swoosh, flare).scale(SCALE_FACTOR)
        
        for mob in logo_group.family_members_with_points():
            if isinstance(mob, VMobject):
                mob.set_stroke(width=mob.get_stroke_width() * SCALE_FACTOR)

        text = VGroup(*[
            Text(w, font="SF Pro", font_size=54, color="#E5E5EA") 
            for w in ["The", "Physics", "Frame"]
        ]).arrange(RIGHT, buff=0.2, aligned_edge=UP)

        text2 = VGroup(*[
            Text(w, font="SF Pro", font_size=20, color="#8E8E93") 
            for w in ["Understand", "Visualize", "Solve"]
        ]).arrange(RIGHT, buff=0.6).move_to([0, -3.5, 0])

        # Find the final layout positions
        text.next_to(logo_group, RIGHT, buff=0.4444)
        text.match_y(squircle_box) 
        
        # Center the final composition to capture exact coordinates
        layout_group = VGroup(logo_group, text)
        layout_group.move_to(ORIGIN)
        
        final_logo_pos = logo_group.get_center()
        final_text_pos = text.get_center()

        # --- THE SECRET CLOAK ---
        # A background-colored rectangle that moves with the logo to hide the long tail of the text
        cloak = Rectangle(width=30, height=15, fill_color="#1C1C1E", fill_opacity=1, stroke_width=0)
        
        # Reset to starting positions
        logo_group.move_to(ORIGIN)
        cloak.next_to(logo_group.get_center(), LEFT, buff=0)
        
        text.move_to(ORIGIN)
        text.match_y(squircle_box)
        text.align_to(squircle_box, RIGHT) # Align text so it's behind the squircle
        text.shift(LEFT * 0.5) # Tuck it safely inside
        
        # Layering depth: Text in back, then cloak, then logo in front
        text.set_z_index(-1)
        cloak.set_z_index(0)
        logo_group.set_z_index(1)
        
        # Keep text invisible during the initial drop-in
        text.set_opacity(0) 

        # ==========================================
        # --- CUSTOM RATE FUNCTIONS ---
        # ==========================================
        
        # Apple-style spring: fast attack, gentle overshoot, smooth settle
        def apple_spring(t):
            # Critically damped spring with slight overshoot
            if t >= 1:
                return 1
            return 1 - np.exp(-6 * t) * np.cos(2.5 * t)

        # Dramatic deceleration — fast snap then ultra-slow glide to rest
        def cinematic_decel(t):
            return 1 - (1 - t) ** 5

        # Smooth anticipation: tiny pull-back before launching forward
        def anticipate_overshoot(t):
            c1 = 1.70158
            c3 = c1 + 1
            return 1 + c3 * ((t - 1) ** 3) + c1 * ((t - 1) ** 2)
        
        # Gentle breathe pulse for the flare (sine-based, peaks at center)
        def breathe_pulse(t):
            return 0.5 * (1 - np.cos(2 * PI * t))

        # ==========================================
        # --- 7. ANIMATION SEQUENCE ---
        # ==========================================
        
        self.add(cloak)

        # --- Beat 0: A moment of darkness (builds anticipation) ---
        self.wait(0.4)

        # --- Beat 1: The Squircle Arrival ---
        # Start from scaled up AND slightly rotated for a more dramatic entrance
        squircle_box.save_state()
        squircle_box.scale(12)
        squircle_box.set_opacity(0) 
        
        # Two-phase arrival: fast slam-in, then a subtle settle scale
        self.play(
            squircle_box.animate.restore(), 
            run_time=1.2, 
            rate_func=apple_spring
        )
        
        # Micro-settle: the squircle "breathes" into place (barely perceptible overshoot)
        self.play(
            squircle_box.animate.scale(1.015),
            run_time=0.2,
            rate_func=rate_functions.ease_out_sine
        )
        self.play(
            squircle_box.animate.scale(1 / 1.015),
            run_time=0.25,
            rate_func=rate_functions.ease_in_out_sine
        )

        # --- Tiny beat before the swoosh (Apple loves these pauses) ---
        self.wait(0.15)

        # --- Beat 2: The Swoosh & Cutout ---
        # Slower, more deliberate draw with exponential deceleration
        # The swoosh should feel like it's being "written" with a confident hand
        self.play(
            Create(buff_mask, lag_ratio=1),
            Create(swoosh, lag_ratio=1),
            run_time=1.3,
            rate_func=cinematic_decel
        )

        # --- Beat 3: The Flare Pop ---
        # Two-stage flare: fast scale-in with overshoot, then a lingering glow pulse
        
        # Stage A: The pop — snappy with a spring overshoot
        self.play(
            FadeIn(flare, scale=0.15), 
            run_time=0.45,
            rate_func=anticipate_overshoot
        )
        
        # Stage B: A single mesmerising "breathe" — the flare gently pulses once
        # This is the moment that makes people go "ooh"
        self.play(
            flare.animate.scale(1.25),
            rate_func=rate_functions.ease_out_sine,
            run_time=0.35
        )
        self.play(
            flare.animate.scale(1 / 1.25),
            rate_func=rate_functions.ease_in_out_sine,
            run_time=0.45
        )

        # --- Breath before the reveal ---
        self.wait(0.25)

        # Make text fully opaque right before it slides (safely hidden)
        text.set_opacity(1)

        # --- Beat 4: The Grand Reveal ---
        # Logo slides left, text emerges from behind — the hero moment
        # Using a custom ease that starts slow (anticipation), accelerates, then
        # decelerates gracefully into position
        self.play(
            logo_group.animate.move_to(final_logo_pos),
            cloak.animate.shift(final_logo_pos),
            text.animate.move_to(final_text_pos),
            run_time=1.8,
            rate_func=rate_functions.ease_out_expo
        )

        # --- Beat 4b: Text settle — each word gets a staggered micro-scale pulse ---
        # Like each word "lands" with weight, left to right
        self.play(
            LaggedStart(
                Succession(
                    text[0].animate(run_time=0.12, rate_func=rate_functions.ease_out_sine).scale(1.03),
                    text[0].animate(run_time=0.18, rate_func=rate_functions.ease_in_out_sine).scale(1/1.03),
                ),
                Succession(
                    text[1].animate(run_time=0.12, rate_func=rate_functions.ease_out_sine).scale(1.03),
                    text[1].animate(run_time=0.18, rate_func=rate_functions.ease_in_out_sine).scale(1/1.03),
                ),
                Succession(
                    text[2].animate(run_time=0.12, rate_func=rate_functions.ease_out_sine).scale(1.03),
                    text[2].animate(run_time=0.18, rate_func=rate_functions.ease_in_out_sine).scale(1/1.03),
                ),
                lag_ratio=0.15,
            ),
            run_time=0.8
        )

        # --- Breath before tagline ---
        self.wait(0.35)

        # --- Beat 5: The Bottom Text ---
        # Each word fades in from below with a staggered, decelerating slide
        # Longer lag_ratio for a more deliberate, considered rhythm
        
        # Prepare: start each word slightly scaled down for a subtle "grow into place" feel
        for word in text2:
            word.save_state()
            word.shift(DOWN * 0.3)
            word.set_opacity(0)
            word.scale(0.92)

        self.play(
            LaggedStart(
                text2[0].animate(rate_func=rate_functions.ease_out_expo).restore(),
                text2[1].animate(rate_func=rate_functions.ease_out_expo).restore(),
                text2[2].animate(rate_func=rate_functions.ease_out_expo).restore(),
                lag_ratio=0.35,
            ),
            run_time=2.2,
        )
        
        # Hold the final frame
        self.wait(1.5)
