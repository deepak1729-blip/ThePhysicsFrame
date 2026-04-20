from manim import *
import numpy as np

class ChannelLogo(Scene):
    def construct(self):
        self.camera.background_color = "#1C1C1E"

        # --- 1. The Squircle (Superellipse - Uniform Speed Fix) ---
        r = 2
        n = 4.5
        
        def squircle_curve(t):
            x = r * 1.04 * np.sign(np.cos(t)) * (np.abs(np.cos(t)) ** (2/n))
            y = r * np.sign(np.sin(t)) * (np.abs(np.sin(t)) ** (2/n))
            return np.array([x, y, 0])

        # 1. Generate the raw mathematical path (which has uneven speeds)
        t_values = np.linspace(0, TAU, 1000)
        raw_points = [squircle_curve(t) for t in t_values]
        temp_path = VMobject().set_points_as_corners(raw_points)
        
        # 2. Resample the path by perfectly even physical distances
        uniform_points = [temp_path.point_from_proportion(p) for p in np.linspace(0, 1, 500)]
        
        # 3. Create the final uniform box
        squircle_box = VMobject(color="#E5E5EA", stroke_width=10)
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
        num_segments = 200 # Increased for smoother tapering
        for i in range(num_segments):
            a1 = i / num_segments
            a2 = (i + 1) / num_segments
            p1 = base_arc.point_from_proportion(a1)
            p2 = base_arc.point_from_proportion(a2)
            
            # Pointy End Logic: Taper from 16 down to effectively 0
            # Using a non-linear taper (a1**2) makes the point look sharper
            current_width = 16 * (1 - a1**1.5)
            
            segment = Line(p1, p2, stroke_width=current_width)
            swoosh.add(segment)
        
        swoosh.set_color_by_gradient("#1C1C1E", "#E5E5EA", "#E5E5EA", "#E5E5EA")

        # --- 4. The Buffed Cutouts (The Secret Sauce) ---
        # We create a black version of the swoosh that is slightly THICKER 
        # than the white one. This creates the "buffed" gap in the box.
        buff_mask = VGroup()
        for i in range(num_segments):
            a1 = i / num_segments
            a2 = (i + 1) / num_segments
            p1 = base_arc.point_from_proportion(a1)
            p2 = base_arc.point_from_proportion(a2)
            
            # The mask is 8 units wider than the swoosh to create the gap
            mask_width = (16 * (1 - a1**1.5)) + 14
            
            mask_segment = Line(p1, p2, color="#1C1C1E", stroke_width=mask_width)
            buff_mask.add(mask_segment)

        # --- 5. The Realistic Flare (Rapid Fade & Shorter Spikes) ---
        flare_center = base_arc.point_from_proportion(0.82)
        
        # 1. Core and Concentric Halos
        # Central bright core (slightly smaller for a sharper look)
        core = Dot(flare_center, radius=0.1, color="#FFFFFF", fill_opacity=1)
        
        # Distinct inner halo ring (less dense)
        inner_halo = Circle(radius=0.12, color="#E5E5EA", fill_opacity=0.2, stroke_width=0).move_to(flare_center)
        
        # Soft outer bloom with a RAPID fade
        outer_glow = VGroup()
        for i in range(15):
            # Using **2 creates a steep curve, meaning it fades out very early on
            opacity = 0.1 * (1 - (i / 30))**2
            ring = Dot(
                flare_center, 
                radius=0.12 + (i * 0.015), # Spreads out from the inner halo
                color="#E5E5EA", 
                fill_opacity=opacity,
                stroke_width=0
            )
            outer_glow.add(ring)

        # 2. Tapered Starburst Rays
        def create_star_ray(direction, length, thickness):
            ray = VGroup()
            segs = 40
            for i in range(segs):
                p_start = flare_center + direction * (i / segs) * length
                p_end = flare_center + direction * ((i + 1) / segs) * length
                
                # Taper width linearly, but fade opacity on a curve for softer tips
                w = thickness * (1 - (i / segs))
                o = 0.8 * (1 - (i / segs))**1.5 
                
                seg = Line(p_start, p_end, stroke_width=w, stroke_opacity=o, color="#E5E5EA")
                ray.add(seg)
            return ray

        # Much shorter main rays (reduced from 4.5 down to 2.2)
        # main_ray_len = 0.6
        # main_ray_thick = 3.5
        # ray_up = create_star_ray(UP, main_ray_len, main_ray_thick)
        # ray_down = create_star_ray(DOWN, main_ray_len, main_ray_thick)
        # ray_left = create_star_ray(LEFT, main_ray_len, main_ray_thick)
        # ray_right = create_star_ray(RIGHT, main_ray_len, main_ray_thick)

        # Much shorter diagonal rays (reduced from 1.5 down to 0.8)
        # diag_ray_len = 0.4
        # diag_ray_thick = 2.0
        # diag_ul = create_star_ray(UP + LEFT, diag_ray_len, diag_ray_thick)
        # diag_ur = create_star_ray(UP + RIGHT, diag_ray_len, diag_ray_thick)
        # diag_dl = create_star_ray(DOWN + LEFT, diag_ray_len, diag_ray_thick)
        # diag_dr = create_star_ray(DOWN + RIGHT, diag_ray_len, diag_ray_thick)

        flare = VGroup(
            outer_glow, 
            inner_halo,
            # ray_up, ray_down, ray_left, ray_right,
            # diag_ul, diag_ur, diag_dl, diag_dr,
            core
        )
        # --- PREPARE LEFT-TO-RIGHT ANIMATION ---
        # By default, your math generated the arc from Right (a1=0) to Left (a1=1).
        # Reversing the sub-mobjects forces Manim to draw them from Left to Right!
        swoosh = VGroup(*reversed(swoosh))
        buff_mask = VGroup(*reversed(buff_mask))

        # --- 6. Group and Transform ---
        # Create a group of all the elements you want to move together
        logo_group = VGroup(squircle_box, buff_mask, swoosh, flare).scale(1.2)

        # Now add the group to the scene
        self.add(logo_group)
