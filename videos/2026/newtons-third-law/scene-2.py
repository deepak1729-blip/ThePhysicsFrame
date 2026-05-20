# scene-2.py — Newton's Third Law · book on table
from manim import *
import numpy as np


# ─────────────────────────────────────────────
#  BRAND PALETTE  (consistent with the series)
# ─────────────────────────────────────────────
COLOR_BG        = "#1C1C1E"
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

def make_book(width=2.0, height=0.46, color=COLOR_BLUE_BALL, depth=0.55):
    """A hardcover book lying flat, viewed in 3/4 perspective.

    The bounding-box bottom is the resting surface (front-edge bottom),
    so positioning by `book.move_to(... table_top_y + book.height/2 ...)`
    still seats the book flush on the table. The top cover, right-side
    page block, and spine recede up-and-right using the same perspective
    tilt as the table so the pair reads as one composed scene.

    Semantic anchors used by the scene:
        book.cover  →  the top cover (the prominent face)
        book.body   →  front edge + top cover + right side (for highlights)
    """
    cover_color  = color
    cover_shadow = "#003F8A"
    pages_color  = "#F2EDDF"
    pages_shadow = "#C9C0AA"
    hl_color     = "#9CC4FF"

    tilt_x = depth * 0.55
    tilt_y = depth * 0.42

    # Front edge: cover-wrap + page block + cover-wrap, stacked vertically.
    wrap_h  = height * 0.18
    pages_h = height - 2 * wrap_h

    front_top_wrap = Rectangle(
        width=width, height=wrap_h,
        fill_color=cover_color, fill_opacity=1.0,
        stroke_color=COLOR_WHITE, stroke_width=0.8, stroke_opacity=0.25
    )
    front_pages = Rectangle(
        width=width, height=pages_h,
        fill_color=pages_color, fill_opacity=1.0, stroke_width=0
    )
    front_pages.set_sheen(-0.20, DR)
    front_bot_wrap = Rectangle(
        width=width, height=wrap_h,
        fill_color=cover_color, fill_opacity=1.0,
        stroke_color=COLOR_WHITE, stroke_width=0.8, stroke_opacity=0.25
    )
    front_face = VGroup(front_bot_wrap, front_pages, front_top_wrap)\
        .arrange(UP, buff=0)

    # Subtle page-edge lines across the visible page band.
    pages_lines = VGroup()
    for fy in (0.30, 0.55, 0.78):
        py = front_pages.get_bottom()[1] + pages_h * fy
        pages_lines.add(Line(
            np.array([front_pages.get_left()[0]  + 0.025, py, 0]),
            np.array([front_pages.get_right()[0] - 0.025, py, 0]),
            stroke_color=pages_shadow, stroke_width=0.5, stroke_opacity=0.40
        ))

    # Top cover — parallelogram receding back-and-up from the front edge.
    fl = front_top_wrap.get_corner(UL)
    fr = front_top_wrap.get_corner(UR)
    bl = fl + np.array([tilt_x, tilt_y, 0])
    br = fr + np.array([tilt_x, tilt_y, 0])
    top_cover = Polygon(
        fl, fr, br, bl,
        fill_color=cover_color, fill_opacity=1.0,
        stroke_color=COLOR_WHITE, stroke_width=1.2, stroke_opacity=0.30
    )
    top_cover.set_sheen(0.30, UL)

    # Binding line — thin darker stripe near the left edge of the cover.
    spine_inset = width * 0.06
    sp_top = fl + (fr - fl) * (spine_inset / width)
    sp_bot = bl + (br - bl) * (spine_inset / width)
    spine_line = Line(
        sp_top, sp_bot,
        stroke_color=cover_shadow, stroke_width=1.4, stroke_opacity=0.75
    )

    # Right-side face — page block thickness shown in 3/4 view. The
    # right edge of a flat-lying book shows page edges (not wrapped
    # cover), so the side face takes the pages color, shaded slightly.
    side_face = Polygon(
        fr,
        front_face.get_corner(DR),
        front_face.get_corner(DR) + np.array([tilt_x, tilt_y, 0]),
        br,
        fill_color=pages_color, fill_opacity=1.0,
        stroke_color=COLOR_WHITE, stroke_width=0.6, stroke_opacity=0.18
    )
    side_face.set_sheen(-0.30, DR)

    # Faint page-stack lines on the right side, parallel to the front edge.
    side_lines = VGroup()
    fr_b = front_face.get_corner(DR)
    fr_t = fr
    for t in (0.30, 0.55, 0.78):
        # Lines run along the perspective direction (parallel to depth).
        a = fr_b + (fr_t - fr_b) * t
        b = a + np.array([tilt_x, tilt_y, 0])
        side_lines.add(Line(
            a + (b - a) * 0.05,
            a + (b - a) * 0.95,
            stroke_color=pages_shadow, stroke_width=0.5, stroke_opacity=0.55
        ))

    # Specular highlight on the upper-left of the top cover.
    spec_pos = fl * 0.36 + fr * 0.18 + bl * 0.32 + br * 0.14
    spec = Ellipse(
        width=width * 0.32, height=tilt_y * 0.42,
        fill_color=hl_color, fill_opacity=0.55, stroke_width=0
    )
    spec.move_to(spec_pos)
    spec.rotate(np.arctan2(tilt_y, tilt_x) * 0.6)

    g = VGroup(
        front_face, pages_lines,
        top_cover, spine_line, spec,
        side_face, side_lines,
    )
    g.cover = top_cover
    g.body  = VGroup(front_face, top_cover, side_face)
    return g


def make_table(width=6.5, top_thickness=0.30, leg_height=1.55, depth=0.85):
    """A 3/4 perspective table.

    Built around a flat front face (the 'deck') whose top edge is the
    resting surface. The top surface recedes back-and-up as a tilted
    parallelogram, with a visible right-side thickness, four tapered
    legs (front pair sharp, back pair shaded), grain lines, a rim
    highlight, and a soft layered floor shadow.

    Semantic anchors used by the scene:
        table.deck      →  front-face Rectangle; its top edge is where
                           objects rest (use for resting-y queries)
        table.top_slab  →  visible top deck (top + side + grain + rim)
                           for highlight rectangles
    """
    top_color   = "#7C747A"
    front_color = "#5E575C"
    side_color  = "#3A3438"
    grain_color = "#A89EA4"
    leg_color   = "#4E464C"
    leg_shadow  = "#2A242A"
    hl_color    = "#B0A8AE"

    tilt_x = depth * 0.55
    tilt_y = depth * 0.42

    # Deck — front face of the top slab. Its top edge is the resting line.
    deck = Rectangle(
        width=width, height=top_thickness,
        fill_color=front_color, fill_opacity=1.0,
        stroke_color=COLOR_WHITE, stroke_width=1.0, stroke_opacity=0.20
    )
    deck.set_sheen(-0.25, DR)

    fl = deck.get_corner(UL)
    fr = deck.get_corner(UR)
    bl = fl + np.array([tilt_x, tilt_y, 0])
    br = fr + np.array([tilt_x, tilt_y, 0])

    # Top surface — parallelogram receding back-and-up.
    top_surface = Polygon(
        fl, fr, br, bl,
        fill_color=top_color, fill_opacity=1.0,
        stroke_color=COLOR_WHITE, stroke_width=1.0, stroke_opacity=0.22
    )
    top_surface.set_sheen(0.25, UL)

    # Subtle wood-grain lines across the top surface.
    grain = VGroup()
    for t in (0.22, 0.42, 0.62, 0.82):
        p_left  = fl + (bl - fl) * t
        p_right = fr + (br - fr) * t
        grain.add(Line(
            p_left  + (p_right - p_left) * 0.06,
            p_left  + (p_right - p_left) * 0.94,
            stroke_color=grain_color, stroke_width=0.8,
            stroke_opacity=0.30
        ))

    # Right side face — perspective thickness on the right edge.
    side_face = Polygon(
        fr,
        deck.get_corner(DR),
        deck.get_corner(DR) + np.array([tilt_x, tilt_y, 0]),
        br,
        fill_color=side_color, fill_opacity=1.0,
        stroke_color=COLOR_WHITE, stroke_width=1.0, stroke_opacity=0.18
    )

    # Bright rim along the front-top edge — catches the light.
    rim = Line(
        fl + RIGHT * (width * 0.015),
        fr + LEFT  * (width * 0.015),
        stroke_color=hl_color, stroke_width=1.6, stroke_opacity=0.55
    )

    # Legs: front pair (sharp), back pair (offset by perspective, shaded).
    leg_w     = width * 0.048
    leg_inset = width * 0.085
    front_y   = deck.get_bottom()[1]

    def build_leg(top_x_center, top_y, in_back=False):
        col_f = leg_shadow if in_back else leg_color
        col_s = leg_shadow
        taper = 0.018
        tl_ = np.array([top_x_center - leg_w / 2, top_y, 0])
        tr_ = np.array([top_x_center + leg_w / 2, top_y, 0])
        bl_ = tl_ + DOWN * leg_height + RIGHT * taper
        br_ = tr_ + DOWN * leg_height + LEFT  * taper
        panel = Polygon(
            tl_, tr_, br_, bl_,
            fill_color=col_f, fill_opacity=1.0,
            stroke_color=COLOR_WHITE, stroke_width=0.7, stroke_opacity=0.14
        )
        sh_w = leg_w * 0.30
        shadow_strip = Polygon(
            tr_ + LEFT * sh_w, tr_, br_, br_ + LEFT * sh_w,
            fill_color=col_s, fill_opacity=0.55, stroke_width=0
        )
        pieces = [panel, shadow_strip]
        if not in_back:
            hl_w = leg_w * 0.16
            hl_strip = Polygon(
                tl_, tl_ + RIGHT * hl_w,
                bl_ + RIGHT * hl_w, bl_,
                fill_color=hl_color, fill_opacity=0.22, stroke_width=0
            )
            pieces.append(hl_strip)
        return VGroup(*pieces)

    fl_x = deck.get_left()[0]  + leg_inset
    fr_x = deck.get_right()[0] - leg_inset

    front_left_leg  = build_leg(fl_x, front_y)
    front_right_leg = build_leg(fr_x, front_y)
    back_left_leg   = build_leg(fl_x + tilt_x, front_y + tilt_y, in_back=True)
    back_right_leg  = build_leg(fr_x + tilt_x, front_y + tilt_y, in_back=True)

    # Soft floor shadow — layered ellipses for a gentle falloff.
    shadow = VGroup()
    shadow_cx = deck.get_center()[0] + tilt_x * 0.45
    shadow_y  = front_y - leg_height + 0.02
    for i, op in enumerate([0.46, 0.30, 0.16]):
        s = Ellipse(
            width=width * (0.85 + i * 0.10),
            height=top_thickness * (0.55 + i * 0.20),
            fill_color=BLACK, fill_opacity=op, stroke_width=0
        )
        s.move_to(np.array([shadow_cx, shadow_y, 0]))
        shadow.add(s)

    # Assemble back-to-front for natural occlusion.
    g = VGroup(
        shadow,
        back_left_leg, back_right_leg,
        top_surface, grain,
        side_face,
        deck,
        rim,
        front_left_leg, front_right_leg,
    )
    g.deck     = deck
    g.top_slab = VGroup(top_surface, grain, side_face, deck, rim)
    return g


# ═══════════════════════════════════════════════════════════════════
#  SCENE 2 · Newton's Third Law — book on table
# ═══════════════════════════════════════════════════════════════════

class Scene2_BookOnTable(Scene):
    def construct(self):
        self.camera.background_color = COLOR_BG
        grid = build_grid()
        grid.set_z_index(-10)
        self.add(grid)

        # ══════════════════════════════════════════════════════════
        #  ACT 1 · The Setup — look at your table
        # ══════════════════════════════════════════════════════════
        eyebrow = Text("LOOK AT YOUR TABLE", font="Segoe UI",
                       font_size=20, weight=BOLD, color=COLOR_GROUND)
        eb_l = Line(LEFT * 0.55, ORIGIN, color=COLOR_GROUND,
                    stroke_width=1, stroke_opacity=0.7)
        eb_r = Line(ORIGIN, RIGHT * 0.55, color=COLOR_GROUND,
                    stroke_width=1, stroke_opacity=0.7)
        eb_l.next_to(eyebrow, LEFT, buff=0.25)
        eb_r.next_to(eyebrow, RIGHT, buff=0.25)
        eyebrow_grp = VGroup(eb_l, eyebrow, eb_r).move_to(UP * 3.3)

        self.play(
            LaggedStart(
                Create(eb_l),
                FadeIn(eyebrow, shift=DOWN * 0.1),
                Create(eb_r),
                lag_ratio=0.3
            )
        )

        # Table + book
        table = make_table()
        table.move_to(DOWN * 1.5)
        table_top_y = table.deck.get_top()[1]

        book = make_book(color=COLOR_BLUE_BALL)
        book.move_to(np.array([0.0, table_top_y + book.height / 2, 0.0]))
        book.set_z_index(1)

        self.play(
            FadeIn(table, shift=UP * 0.25),
            rate_func=rate_functions.ease_out_cubic
        )

        # Book settles softly onto the table from slightly above
        self.play(
            FadeIn(book, shift=DOWN * 0.55),
            run_time=1.0,
            rate_func=rate_functions.ease_in_out_sine
        )
        self.wait(0.5)

        # ══════════════════════════════════════════════════════════
        #  ACT 2 · Gravity → "Book on Table" pressure
        # ══════════════════════════════════════════════════════════

        g_start = book.get_center()
        g_end = g_start + DOWN * 1.1
        gravity_arrow = Arrow(
            g_start, g_end, color=COLOR_VEC_F,
            buff=0, stroke_width=5,
            max_tip_length_to_length_ratio=0.20
        ).set_z_index(2)
        gravity_label = Text("Gravity", font="Segoe UI",
                             font_size=22, color=COLOR_VEC_F)
        gravity_label.next_to(gravity_arrow, RIGHT, buff=0.18)

        self.play(
            GrowArrow(gravity_arrow),
            FadeIn(gravity_label, shift=LEFT * 0.15),
            run_time=0.9,
            rate_func=rate_functions.ease_out_cubic
        )
        self.wait(1.0)

        # Gravity morphs into the contact-force arrow at the interface,
        # offset LEFT so the third-law pair can sit beside it cleanly.
        contact_y = book.get_bottom()[1]
        b_arrow_x = -0.45
        b_start = np.array([b_arrow_x, contact_y, 0.0])
        b_end = b_start + DOWN * 0.85
        book_on_table = Arrow(
            b_start, b_end, color=COLOR_VEC_F,
            buff=0, stroke_width=5,
            max_tip_length_to_length_ratio=0.22
        ).set_z_index(2)

        self.play(
            ReplacementTransform(gravity_arrow, book_on_table),
            FadeOut(gravity_label, shift=DOWN * 0.2),
            rate_func=rate_functions.ease_in_out_sine
        )
        self.wait()

        # ══════════════════════════════════════════════════════════
        #  ACT 3 · Newton's Third Law — table pushes back
        # ══════════════════════════════════════════════════════════

        t_arrow_x = +0.45
        t_start = np.array([t_arrow_x, contact_y, 0.0])
        t_end = t_start + UP * 0.85
        table_on_book = Arrow(
            t_start, t_end, color=COLOR_VEC_F,
            buff=0, stroke_width=5,
            max_tip_length_to_length_ratio=0.22
        ).set_z_index(2)

        self.play(
            GrowArrow(table_on_book),
            rate_func=rate_functions.ease_out_cubic
        )
        self.wait(0.7)

        # EQUAL. OPPOSITE.
        eq_lbl = Text("EQUAL.", font="Segoe UI",
                      font_size=28, weight=BOLD, color=COLOR_GREEN)
        op_lbl = Text("OPPOSITE.", font="Segoe UI",
                      font_size=28, weight=BOLD, color=COLOR_GREEN)
        eo_grp = VGroup(eq_lbl, op_lbl).arrange(RIGHT, buff=0.55)
        eo_grp.move_to(UP * 1.95)

        self.play(
            LaggedStart(
                FadeIn(eq_lbl, shift=UP * 0.15),
                FadeIn(op_lbl, shift=UP * 0.15),
                lag_ratio=0.4
            ),
            run_time=1.0
        )
        self.wait()

        # ══════════════════════════════════════════════════════════
        #  ACT 4 · "But here's what we miss"
        # ══════════════════════════════════════════════════════════

        # Dim only the arrows + labels (preserves book/table fine opacities)
        arrows_lbls = VGroup(book_on_table, table_on_book)

        self.play(FadeOut(eo_grp, shift=UP * 0.15), run_time=0.45)

        self.wait()

        # ══════════════════════════════════════════════════════════
        #  ACT 5 · Two different bodies. Two different targets.
        # ══════════════════════════════════════════════════════════

        table_hl = SurroundingRectangle(
            table.top_slab, color=COLOR_AMBER, corner_radius=0.05,
            buff=0.06, stroke_width=2.4, stroke_opacity=0.85
        )
        book_hl = SurroundingRectangle(
            book.body, color=COLOR_BLUE_BALL, corner_radius=0.07,
            buff=0.06, stroke_width=2.4, stroke_opacity=0.85
        )

        # "Book's force lands on TABLE"
        self.play(
            Create(table_hl),
            run_time=0.9
        )
        self.wait(0.4)
        # "Table's force lands on BOOK"
        self.play(
            Create(book_hl)
        )
        self.wait(0.5)

        two_bodies = Text("Two different bodies.",
                          font="Segoe UI", font_size=28, weight=BOLD,
                          color=COLOR_WHITE,
                          t2c={"different": COLOR_PINK})
        two_targets = Text("Two different targets.",
                           font="Segoe UI", font_size=28, weight=BOLD,
                           color=COLOR_WHITE,
                           t2c={"different": COLOR_PINK})
        tb_grp = VGroup(two_bodies, two_targets).arrange(DOWN, buff=0.22)
        tb_grp.move_to(UP * 2.2)

        self.play(
            LaggedStart(
                FadeIn(two_bodies, shift=UP * 0.15),
                FadeIn(two_targets, shift=UP * 0.15),
                lag_ratio=0.4
            ),
            run_time=1.2
        )
        self.wait(1.5)

        # Clear stage for the cancellation contrast — plain FadeOut so
        # the book/table mobjects retain their positions for Act 7.
        unified_scene = VGroup(book, table, book_on_table, table_on_book, table_hl, book_hl)
        self.play(
            FadeOut(unified_scene),
            FadeOut(tb_grp, shift=UP * 0.15),
            FadeOut(eyebrow_grp, shift=UP * 0.15),
            run_time=0.6
        )

        # ══════════════════════════════════════════════════════════
        #  ACT 6 · The cancellation rule — both forces on SAME body
        # ══════════════════════════════════════════════════════════

        cancel_rule = Text(
            "Forces cancel only when they act on the same body.",
            font="Segoe UI", font_size=24,
            color=COLOR_GROUND, slant=ITALIC,
            t2c={"same body": COLOR_GREEN}
        )
        cancel_rule.to_edge(UP, buff=1.1)

        cancel_box = Square(
            side_length=1.35,
            fill_color=COLOR_GREEN, fill_opacity=0.85,
            stroke_color=COLOR_WHITE, stroke_width=1.4,
            stroke_opacity=0.28
        )
        cancel_box.set_sheen(-0.3, DR)
        cancel_box.move_to(ORIGIN + DOWN * 0.1)
        cancel_box_lbl = Text("BOX", font="Segoe UI", font_size=22,
                              weight=BOLD, color=COLOR_BG)
        cancel_box_lbl.move_to(cancel_box.get_center())

        left_push = Arrow(
            cancel_box.get_left() + LEFT * 1.35,
            cancel_box.get_left() + LEFT * 0.06,
            color=COLOR_VEC_F, buff=0, stroke_width=5,
            max_tip_length_to_length_ratio=0.22
        )
        right_push = Arrow(
            cancel_box.get_right() + RIGHT * 1.35,
            cancel_box.get_right() + RIGHT * 0.06,
            color=COLOR_VEC_F, buff=0, stroke_width=5,
            max_tip_length_to_length_ratio=0.22
        )

        net_zero = MathTex(r"\vec{F}_{\text{net}} = 0",
                           font_size=42, color=COLOR_GREEN)
        net_zero.next_to(cancel_box, DOWN, buff=0.65)

        self.play(
            FadeIn(cancel_rule, shift=DOWN * 0.15),
            FadeIn(cancel_box, scale=0.92),
            FadeIn(cancel_box_lbl, shift=UP * 0.05),
            run_time=0.7
        )
        self.play(
            GrowArrow(left_push), GrowArrow(right_push),
            run_time=0.7
        )
        self.play(FadeIn(net_zero, shift=UP * 0.15), run_time=0.55)
        self.wait(1.1)

        contrast_grp = VGroup(cancel_box, cancel_box_lbl,
                              left_push, right_push,
                              net_zero, cancel_rule)
        self.play(FadeOut(contrast_grp, shift=UP * 0.1), run_time=0.55)

        # ══════════════════════════════════════════════════════════
        #  ACT 7 · THE SPLIT — Book's world vs Table's world
        # ══════════════════════════════════════════════════════════

        # Bring the unified scene back to launch the split
        self.play(
            FadeIn(VGroup(book, table, book_on_table, table_on_book,
                          ), shift=UP * 0.2),
            run_time=0.6
        )
        self.wait(0.3)

        panel_w, panel_h = 5.7, 5.0
        panel_left = RoundedRectangle(
            corner_radius=0.14, width=panel_w, height=panel_h,
            stroke_color=COLOR_BLUE_BALL, stroke_width=1.8,
            stroke_opacity=0.55,
            fill_color=COLOR_BLUE_BALL, fill_opacity=0.04
        ).move_to(LEFT * 3.4 + DOWN * 0.4).set_z_index(-5)
        panel_right = RoundedRectangle(
            corner_radius=0.14, width=panel_w, height=panel_h,
            stroke_color=COLOR_AMBER, stroke_width=1.8,
            stroke_opacity=0.55,
            fill_color=COLOR_AMBER, fill_opacity=0.04
        ).move_to(RIGHT * 3.4 + DOWN * 0.4).set_z_index(-5)

        title_left = Text("BOOK'S WORLD", font="Segoe UI",
                          font_size=20, weight=BOLD, color=COLOR_BLUE_BALL)
        title_left.move_to(panel_left.get_top() + DOWN * 0.32)
        title_right = Text("TABLE'S WORLD", font="Segoe UI",
                           font_size=20, weight=BOLD, color=COLOR_AMBER)
        title_right.move_to(panel_right.get_top() + DOWN * 0.32)

        # What travels with each body:
        #   book gets the force ACTING ON it (table_on_book)
        #   table gets the force ACTING ON it (book_on_table)
        book_pack  = VGroup(book,  table_on_book)
        table_pack = VGroup(table, book_on_table)

        book_dest  = panel_left.get_center()  + UP * 0.4
        table_dest = panel_right.get_center() + UP * 0.1

        book_shift  = book_dest  - book.get_center()
        table_shift = table_dest - table.get_center()

        self.play(
            FadeIn(panel_left), FadeIn(panel_right),
            FadeIn(title_left, shift=DOWN * 0.1),
            FadeIn(title_right, shift=DOWN * 0.1),
            run_time=0.8
        )

        # The dramatic split: each body is dragged into its own world,
        # taking only its own force with it. The two forces literally
        # cannot share a frame any more — the central reveal.
        self.play(
            book_pack.animate.shift(book_shift).scale(0.75),
            table_pack.animate.shift(table_shift).scale(0.75),
            run_time=1.5,
            rate_func=rate_functions.ease_in_out_sine
        )
        self.wait(0.7)

        verdict = Text("They live in different worlds.",
                       font="Segoe UI", font_size=26, weight=BOLD,
                       color=COLOR_WHITE,
                       t2c={"different worlds": COLOR_PINK})
        verdict.move_to(DOWN * 3.3)
        self.play(FadeIn(verdict, shift=UP * 0.15), run_time=0.7)
        self.wait(1.4)

        # ══════════════════════════════════════════════════════════
        #  ACT 8 · THE BIG TAKEAWAY
        # ══════════════════════════════════════════════════════════

        all_split = VGroup(panel_left, panel_right,
                           title_left, title_right,
                           book_pack, table_pack)
        self.play(
            FadeOut(all_split, shift=DOWN * 0.1),
            FadeOut(verdict, shift=UP * 0.1),
            run_time=0.8
        )

        takeaway = Text("Action and reaction never act on the same body.",
                        font="Segoe UI", font_size=34, weight=BOLD,
                        color=COLOR_WHITE,
                        t2c={"never": COLOR_PINK,
                             "same body": COLOR_AMBER})
        takeaway.move_to(UP * 0.3)
        self.play(Write(takeaway), run_time=2.4,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(1.6)

        # ══════════════════════════════════════════════════════════
        #  ACT 9 · THE HIDDEN DEFINITION
        # ══════════════════════════════════════════════════════════

        self.play(
            takeaway.animate.scale(0.55).to_edge(UP, buff=0.55).set_opacity(0.55),
            run_time=0.8,
            rate_func=rate_functions.ease_in_out_sine
        )


        defn_main = Text(
            "For every action, there is an equal and opposite reaction.",
            font="Segoe UI", font_size=26, color=COLOR_WHITE,
            t2c={"equal": COLOR_GREEN, "opposite": COLOR_GREEN}
        )
        defn_main.move_to(UP * 0.3)

        self.play(Write(defn_main), run_time=2.2,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.9)

        missing = Text("…on a different body.", font="Segoe UI",
                       font_size=30, weight=BOLD, slant=ITALIC,
                       color=COLOR_PINK)
        missing.next_to(defn_main, DOWN, buff=0.55)

        missing_box = SurroundingRectangle(
            missing, color=COLOR_PINK, corner_radius=0.1,
            buff=0.20, stroke_width=2, stroke_opacity=0.0
        )

        self.play(
            FadeIn(missing, shift=UP * 0.2),
            run_time=0.9,
            rate_func=rate_functions.ease_out_cubic
        )
        self.play(
            missing_box.animate.set_stroke(opacity=0.85),
            run_time=0.7
        )
        self.wait(2.2)

        defn_all = VGroup(defn_main, missing,
                          missing_box, takeaway)
        self.play(FadeOut(defn_all, shift=UP * 0.1), run_time=0.7)

        # ══════════════════════════════════════════════════════════
        #  ACT 10 · THE HORSE PARADOX — half-solved meter
        # ════════════════════════════════════════════════════

        title = Text("THE HORSE-CART PARADOX",
                     font="Segoe UI", font_size=36, weight=BOLD,
                     color=COLOR_WHITE)
        title.move_to(UP * 1.7)

        self.play(
            LaggedStart(
                *[FadeIn(ch, shift=UP * 0.18) for ch in title],
                lag_ratio=0.035
            ),
            run_time=1.2,
            rate_func=rate_functions.ease_out_cubic
        )
        self.wait(0.4)

        # Empty progress track with ticks at 0 / 50 / 100
        bar_w, bar_h = 7.2, 0.50
        track = RoundedRectangle(
            corner_radius=bar_h * 0.5,
            width=bar_w, height=bar_h,
            fill_color=COLOR_GROUND, fill_opacity=0.18,
            stroke_color=COLOR_GROUND, stroke_width=1.2,
            stroke_opacity=0.55
        )
        track.move_to(DOWN * 0.1)

        track_left  = track.get_left()
        track_right = track.get_right()
        track_mid   = track.get_center()

        tick_mid = Line(
            track_mid + UP * (bar_h * 0.7),
            track_mid + DOWN * (bar_h * 0.7),
            color=COLOR_GROUND, stroke_width=1.5, stroke_opacity=0.85
        )
        mid_pct = Text("50%", font="Segoe UI", font_size=16,
                       weight=BOLD, color=COLOR_GROUND)
        mid_pct.next_to(tick_mid, UP, buff=0.20)

        tick_end = Line(
            track_right + UP * (bar_h * 0.7),
            track_right + DOWN * (bar_h * 0.7),
            color=COLOR_GROUND, stroke_width=1.5, stroke_opacity=0.85
        )
        end_pct = Text("100%", font="Segoe UI", font_size=16,
                       weight=BOLD, color=COLOR_GROUND)
        end_pct.next_to(tick_end, UP, buff=0.20)

        self.play(
            FadeIn(track, shift=UP * 0.1),
            FadeIn(tick_mid), FadeIn(tick_end),
            FadeIn(mid_pct), FadeIn(end_pct),
            run_time=0.7
        )

        # Animated fill — anchored at the LEFT edge of the track,
        # widens from 0 to exactly half the bar's width and stops dead.
        progress = ValueTracker(0.0)

        def make_fill():
            w = max(0.001, bar_w * progress.get_value())
            f = RoundedRectangle(
                corner_radius=bar_h * 0.4,
                width=w, height=bar_h * 0.84,
                fill_color=COLOR_GREEN, fill_opacity=0.95,
                stroke_width=0
            )
            f.move_to(track_left + RIGHT * (w / 2))
            return f

        fill = always_redraw(make_fill)
        self.add(fill)

        # smooth ease so the hard stop at 50% feels deliberate
        self.play(progress.animate.set_value(0.5),
                  run_time=1.7,
                  rate_func=rate_functions.ease_in_out_sine)

        # Freeze: swap the dynamic fill for a static copy
        fill.clear_updaters()
        static_fill = make_fill()
        self.remove(fill)
        self.add(static_fill)

        # The final stamp
        half = Text("HALF SOLVED.", font="Segoe UI",
                    font_size=34, weight=BOLD, color=COLOR_GREEN)
        half.move_to(DOWN * 2.7)
        self.play(
            LaggedStart(
                *[FadeIn(ch, shift=UP * 0.22) for ch in half],
                lag_ratio=0.045
            ),
            run_time=1.0,
            rate_func=rate_functions.ease_out_cubic
        )
        self.wait()