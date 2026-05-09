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
        # --- 7. ANIMATION SEQUENCE ---
        # ==========================================

        self.add(cloak)

        # --- Beat 0: Silence — let the viewer settle ---
        self.wait(0.25)

        # --- Beat 1: Squircle — arrives from large, decelerates smoothly to rest ---
        squircle_box.save_state()
        squircle_box.scale(5.5)
        squircle_box.set_opacity(0)

        self.play(
            squircle_box.animate.restore(),
            run_time=1.4
        )

        self.wait(0.25)

        # --- Beat 2: Swoosh draw — unhurried, like a confident pen stroke ---
        self.play(
            Create(buff_mask, lag_ratio=1),
            Create(swoosh, lag_ratio=1),
            rate_func=rate_functions.ease_out_expo
        )

        # --- Beat 3: Flare — quiet, clean appearance ---
        self.play(
            FadeIn(flare),
            run_time=0.5,
            rate_func=rate_functions.ease_out_sine
        )

        # --- Beat 4: The Grand Reveal — logo glides left, title emerges ---
        text.set_opacity(1)

        # --- Beat 5: Tagline — staggered fade-in with gentle upward drift ---
        for word in text2:
            word.save_state()
            word.shift(DOWN * 0.18)
            word.set_opacity(0)

        self.play(
            LaggedStart(
                text2[0].animate(rate_func=rate_functions.ease_out_expo).restore(),
                text2[1].animate(rate_func=rate_functions.ease_out_expo).restore(),
                text2[2].animate(rate_func=rate_functions.ease_out_expo).restore(),
                lag_ratio=0.5,
            ),logo_group.animate.move_to(final_logo_pos),
            cloak.animate.shift(final_logo_pos),
            text.animate.move_to(final_text_pos),
            run_time=2.0
        )

        # Hold the final frame briefly before the dissolve
        self.wait()

        # # --- Beat 6: Dissolve everything into minute particles ---
        # rng = np.random.default_rng(7)

        # particle_dots = []
        # rest_positions = []
        # velocities = []

        # for source in [squircle_box, swoosh, flare, text, text2]:
        #     for vm in source.family_members_with_points():
        #         if not isinstance(vm, VMobject) or vm.get_num_points() == 0:
        #             continue
        #         if vm.get_stroke_opacity() > 0.1 and vm.get_stroke_width() > 0.01:
        #             color = vm.get_stroke_color()
        #         elif vm.get_fill_opacity() > 0.05:
        #             color = vm.get_fill_color()
        #         else:
        #             continue

        #         try:
        #             length = vm.get_arc_length()
        #         except Exception:
        #             length = 0.05
        #         n = int(np.clip(length * 55, 6, 140))

        #         for _ in range(n):
        #             p = vm.point_from_proportion(rng.random())
        #             p = p + np.array([rng.normal(0, 0.008), rng.normal(0, 0.008), 0])
        #             dot = Dot(point=p, radius=0.01, color=color,
        #                       fill_opacity=0, stroke_width=0)
        #             particle_dots.append(dot)
        #             rest_positions.append(p.copy())
        #             angle = rng.uniform(0, TAU)
        #             speed = rng.uniform(0.25, 1.1)
        #             velocities.append(np.array([
        #                 np.cos(angle) * speed,
        #                 np.sin(angle) * speed + rng.uniform(0.05, 0.3),
        #                 0,
        #             ]))

        # particles = VGroup(*particle_dots)
        # rest_positions = np.array(rest_positions)
        # velocities = np.array(velocities)

        # t_tracker = ValueTracker(0)

        # def update_particles(group):
        #     t = t_tracker.get_value()
        #     fade = (t / 0.15) if t < 0.15 else max(0.0, 1 - (t - 0.15) / 0.85)
        #     drift = t ** 1.4
        #     for i, d in enumerate(group):
        #         d.move_to(rest_positions[i] + velocities[i] * drift)
        #         d.set_opacity(fade)

        # particles.add_updater(update_particles)
        # self.add(particles)

        self.play(
            FadeOut(
                VGroup(logo_group, text, text2),
            )
            # t_tracker.animate.set_value(1.0),
            # run_time=2.4,
            # rate_func=linear,
        )

        # particles.remove_updater(update_particles)
        self.wait()
