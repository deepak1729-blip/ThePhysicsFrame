from manim import *
import numpy as np

class Channelbanner(Scene):
    def construct(self):
        self.camera.background_color = "#1C1C1E"

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
                op = peak_opacity * (1 - (2*t - 1)**2)
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
            current_width = 16 * (1 - a1**1.5)
            
            segment = Line(p1, p2, stroke_width=current_width)
            swoosh.add(segment)
        
        swoosh.set_color_by_gradient("#E5E5EA", "#E5E5EA", "#E5E5EA", "#E5E5EA")

        # --- 4. The Buffed Cutouts (The Secret Sauce) ---
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
        
        # Central bright core
        core = Dot(flare_center, radius=0.1, color="#FFFFFF", fill_opacity=1)
        # Distinct inner halo ring
        inner_halo = Circle(radius=0.12, color="#E5E5EA", fill_opacity=0.2, stroke_width=0).move_to(flare_center)
        
        # Soft outer bloom with a RAPID fade
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


        # ==================================================
        # --- NEW BANNER LAYOUT (Grouping, Scaling, Text) ---
        # ==================================================

        # 1. Group, Scale, and Move the Logo
        logo_group = VGroup(squircle_box, buff_mask, swoosh, flare)
        logo_group.scale(0.75) # Scale down by 3/4
        logo_group.move_to(np.array([-4.0, 0, 0])) # Move to the left

        # 2. Extend the Arc (Perfect Tangency & Continuous Color)
        
        # A. Get the exact right-most tip of the transformed logo
        tip_segment = swoosh[-1]
        p1 = tip_segment.get_start()
        p2 = tip_segment.get_end()
        
        # B. Calculate the exact outward pointing tangent vector
        if p1[0] > p2[0]:
            P0 = p1
            tangent = p1 - p2
        else:
            P0 = p2
            tangent = p2 - p1
            
        tangent = tangent / np.linalg.norm(tangent) # Normalize the vector
        
        # C. Define the Bezier curve control points
        P3 = np.array([5.8, -1.4, 0]) # The final pointed destination
        dist = np.linalg.norm(P3 - P0)
        
        # P1 forces the curve to shoot out exactly along the tangent
        P1 = P0 + tangent * (dist * 0.45) 
        # P2 curves it gently downward for the landing
        P2 = P3 + np.array([-1.0, 1.5, 0]) 
        
        extension_base = CubicBezier(P0, P1, P2, P3)

        # D. Build the tapered extension line
        extension_swoosh = VGroup()
        num_ext_segments = 200
        
        # --- THE FIX: Dynamically read the exact scaled thickness ---
        # This guarantees a 100% flawless width match at the junction.
        try:
            starting_width = tip_segment.get_stroke_width()
            # If Manim returns an array of widths, grab the first one
            if isinstance(starting_width, (np.ndarray, list)):
                starting_width = starting_width[0]
        except AttributeError:
            starting_width = tip_segment.stroke_width
            
        for i in range(num_ext_segments):
            a1 = i / num_ext_segments
            a2 = (i + 1) / num_ext_segments
            pt1 = extension_base.point_from_proportion(a1)
            pt2 = extension_base.point_from_proportion(a2)
            
            # Taper from the exact matching junction width down to 0
            current_width = starting_width * (1 - a1**1.5)
            
            segment = Line(pt1, pt2, stroke_width=current_width)
            extension_swoosh.add(segment)

        # E. Seamless Gradient: Start with the light gray of the tip, fade to dark
        extension_swoosh.set_color_by_gradient("#E5E5EA", "#E5E5EA", "#E5E5EA")

        # 3. Add the Text
        title = Text("The Physics Frame", font_size=32, color="#E5E5EA", font="SF Pro Text")
        subtitle = Text("understand,  visualize,  solve", font_size=18, color="#E5E5EA", font="SF Pro Text")
        
        # Adding aligned_edge=LEFT perfectly left-justifies the subtitle under the title
        subtitle.next_to(title, DOWN, buff=0.2, aligned_edge=LEFT)
        
        text_group = VGroup(title, subtitle)
        text_group.move_to(np.array([4.0, 0, 0]))

        # 4. The Bulletproof Text Cutout
        # An exact rectangle sized slightly larger than the text to act as an eraser
        text_cutout = Rectangle(
            width=text_group.width + 0.6,
            height=text_group.height + 0.4,
            color="#1C1C1E", # Matches background perfectly
            fill_opacity=1,
            stroke_width=0
        ).move_to(text_group)


        # --- FINAL RENDER ---
        self.add(logo_group, extension_swoosh, text_cutout, text_group,grid)
