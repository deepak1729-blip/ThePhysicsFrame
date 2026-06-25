from manim import *
import numpy as np
import math

# ─────────────────────────────────────────────────────────────────────────
#  OBSERVATORY PALETTE  (verbatim from the series design system)
# ─────────────────────────────────────────────────────────────────────────
VOID      = "#0A0C10"   # base background
PANEL     = "#11151C"   # lifted surfaces
STARLIGHT = "#E8E6DF"   # primary text
DUST      = "#9A958C"   # secondary · metadata · the dimmed (ghost) state
AMBER     = "#D98A3D"   # primary accent · focus (amber follows the eye)
CYAN      = "#5B8FB0"   # secondary · sparing

# quantity pigments — each quantity keeps its colour across the whole series
C_MASS    = "#B89A86"   # MASS / the "laziness number" (Scenes 3–4 character)
C_FORCE   = "#E06450"   # FORCE — the push I APPLY
C_VEL     = "#57C08A"   # VELOCITY  v
C_ENERGY  = "#E4CF5E"   # ENERGY / the COST of motion
C_LEN     = "#5B8FB0"   # LENGTH / r — the radius (== CYAN; the Scene-5 seed)
C_ANGLE   = "#E08AAB"   # ANGLE θ — the swept wedge
C_GROUND  = "#7F8A99"   # ground / reference axis

SERIF = "Spectral"      # ideas; italic is the channel's speaking voice & equations
MONO  = "Space Mono"    # labels & metadata only

config.background_color = VOID
RNG = np.random.default_rng(6)   # deterministic -> stable render cache


# ═══════════════════════════════════════════════════════════════════════════
#  CONSTRUCTION VOCABULARY  (reused verbatim from Scenes 1–5, then extended)
# ═══════════════════════════════════════════════════════════════════════════
def dir2(angle):
    """Unit vector at `angle` (radians) in the XY plane."""
    return np.array([math.cos(angle), math.sin(angle), 0.0])


def corner_L(orientation, size=0.20, color=AMBER, width=1.4, opacity=0.7):
    """Registration corner — the Observatory mark that frames the animation."""
    sx = -1 if orientation[0] > 0 else 1
    sy = -1 if orientation[1] > 0 else 1
    h = Line(ORIGIN, RIGHT * size * sx, stroke_color=color,
             stroke_width=width, stroke_opacity=opacity)
    v = Line(ORIGIN, UP * size * sy, stroke_color=color,
             stroke_width=width, stroke_opacity=opacity)
    g = VGroup(h, v)
    g.anchor = orientation
    return g


def safe_image(name, target_width, fallback_label):
    """Load an image by name; if it isn't present yet, return a framed
    placeholder slot so the script always runs as-is. (From Scene 1.)"""
    try:
        img = ImageMobject(name)
        img.set(width=target_width)
        return img
    except Exception:
        h = target_width * 0.72
        slot = VGroup()
        plate = Rectangle(width=target_width, height=h,
                          fill_color=PANEL, fill_opacity=1.0,
                          stroke_color=DUST, stroke_width=1.2,
                          stroke_opacity=0.4)
        lbl = Text(fallback_label, font=MONO, font_size=13, color=DUST)
        lbl.move_to(plate.get_center())
        slot.add(plate, lbl)
        for o in (UL, UR, DL, DR):
            c = corner_L(o, size=0.14, color=AMBER, opacity=0.55)
            c.move_to(plate.get_corner(o), aligned_edge=o)
            slot.add(c)
        return slot


def make_bowling_ball(radius=0.62):
    """Dense, dark sphere with three finger-holes — the tagged heavy character
    from Scenes 3–4. The face of 'm'. Exposes `.disc`, `.radius`. (From Scene 4.)"""
    g = VGroup()
    body = Circle(radius=radius)
    body.set_fill(PANEL, opacity=1.0)
    body.set_sheen(-0.55, DR)
    body.set_stroke(color=C_MASS, width=2.6, opacity=0.95)
    g.add(body)
    inner = Circle(radius=radius * 0.97)
    inner.set_fill(opacity=0)
    inner.set_stroke(color=STARLIGHT, width=1.0, opacity=0.10)
    g.add(inner)
    holes = VGroup()
    for off in (np.array([-0.18, 0.30, 0]),
                np.array([0.10, 0.34, 0]),
                np.array([-0.04, 0.10, 0])):
        hole = Circle(radius=radius * 0.11)
        hole.set_fill(VOID, opacity=1.0)
        hole.set_stroke(color=C_MASS, width=1.2, opacity=0.5)
        hole.move_to(body.get_center() + off * radius / 0.62)
        holes.add(hole)
    g.add(holes)
    spec = Ellipse(width=radius * 0.46, height=radius * 0.28)
    spec.set_fill(STARLIGHT, opacity=0.45)
    spec.set_stroke(width=0)
    spec.move_to(body.get_center() + np.array([-radius * 0.34, -radius * 0.30, 0]))
    spec.rotate(-22 * DEGREES)
    g.add(spec)
    g.disc = body
    g.radius = radius
    return g


def make_mass_node(radius=0.22, color=C_MASS):
    """Small descendant of the bowling ball — same PANEL fill, mass-pigment rim,
    same specular tell — so the orbiting weights read as the SAME heavy
    character without the finger-hole clutter at small scale. (From Scene 5.)"""
    g = VGroup()
    body = Circle(radius=radius)
    body.set_fill(PANEL, opacity=1.0)
    body.set_sheen(-0.5, DR)
    body.set_stroke(color=color, width=2.4, opacity=0.95)
    g.add(body)
    spec = Ellipse(width=radius * 0.5, height=radius * 0.3)
    spec.set_fill(STARLIGHT, opacity=0.42)
    spec.set_stroke(width=0)
    spec.move_to(body.get_center() + np.array([-radius * 0.32, -radius * 0.30, 0]))
    spec.rotate(-22 * DEGREES)
    g.add(spec)
    g.radius = radius
    return g


def make_rod(half_len, thickness=0.085, color=DUST, opacity=0.85):
    """A clean uniform bar — the (massless) spoke the weights ride on."""
    return RoundedRectangle(width=2 * half_len, height=thickness,
                            corner_radius=thickness / 2, stroke_width=0,
                            fill_color=color, fill_opacity=opacity)


def make_pivot(radius=0.085, color=AMBER):
    """The clamp at the rod's centre — the axis it turns about. (From Scene 5.)"""
    outer = Circle(radius=radius, stroke_color=color, stroke_width=2.0,
                   fill_color=VOID, fill_opacity=1.0)
    inner = Dot(radius=radius * 0.42, color=color)
    return VGroup(outer, inner)


def make_crosshair(size=0.22, color=AMBER):
    """The LOCKED centre of Scene 6 — a small fixed crosshair pivot that
    everything orbits. (Retired at the top of Scene 7.)"""
    ring = Circle(radius=size * 0.5, stroke_color=color, stroke_width=2.0,
                  fill_color=VOID, fill_opacity=1.0)
    h = Line(LEFT * size, RIGHT * size, stroke_color=color, stroke_width=1.6)
    v = Line(DOWN * size, UP * size, stroke_color=color, stroke_width=1.6)
    dot = Dot(radius=size * 0.16, color=color)
    return VGroup(h, v, ring, dot)


def ghost_disc(center, radius, color=C_MASS, opacity=0.34):
    """One equal-time strobe stamp. A row of these encodes SPEED by spacing —
    the Scenes 1–2 grammar. (From Scene 4.)"""
    d = Circle(radius=radius, stroke_color=color, stroke_width=2.0,
               stroke_opacity=opacity, fill_color=color, fill_opacity=0.05)
    d.move_to(center)
    return d


# ─────────────────────────── new vocabulary for Scene 6 ───────────────────
def serif(s, color=STARLIGHT, size=46, italic=True):
    """The channel's idea/equation voice: Spectral, italic by default."""
    return Text(s, font=SERIF, slant=ITALIC if italic else NORMAL,
                font_size=size, color=color)


def squared(base, color=STARLIGHT, size=46):
    """Build `base²` from parts (no MathTex in this series). Exposes `.base`
    and `.exp` so the exponent can be animated in on its own — used when r
    literally 'squares itself' in Act 5."""
    b = serif(base, color, size)
    e = Text("2", font=SERIF, slant=ITALIC, font_size=int(size * 0.58), color=color)
    e.move_to(b.get_corner(UR) + RIGHT * e.width * 0.55 + UP * b.height * 0.30)
    g = VGroup(b, e)
    g.base = b
    g.exp = e
    return g


def velocity_arrow(start, vec, color=C_VEL, width=6.0):
    """A clean velocity vector — shaft + apex tip. Length is meaningful:
    it doubles honestly when v doubles."""
    end = np.array(start) + np.array(vec)
    shaft = Line(start, end, stroke_color=color, stroke_width=width)
    tip = Triangle().scale(0.085).set_fill(color, opacity=1.0).set_stroke(width=0)
    d = np.array(vec, dtype=float)
    tip.rotate(math.atan2(d[1], d[0]) - 90 * DEGREES)   # Triangle apex = +y
    tip.move_to(end)
    return VGroup(shaft, tip)


def cost_meter(height, width=0.62, color=C_ENERGY, max_units=4):
    """A vertical fill-meter whose filled height IS the cost. `height` is in the
    same units as `max_units`, so 1 vs 4 is a literal 4× column. Returns the
    group with `.fill` exposed for the fill animation."""
    unit_h = 0.62
    frame_h = max_units * unit_h
    track = Rectangle(width=width, height=frame_h, stroke_color=DUST,
                      stroke_width=1.4, stroke_opacity=0.5,
                      fill_color=PANEL, fill_opacity=0.5)
    fill = Rectangle(width=width, height=max(height, 1e-3) * unit_h,
                     stroke_width=0, fill_color=color, fill_opacity=0.92)
    fill.move_to(track.get_bottom() + UP * (max(height, 1e-3) * unit_h) / 2)
    # faint unit gridlines so the eye can COUNT the height, not just feel it
    grid = VGroup()
    for k in range(1, max_units):
        y = track.get_bottom()[1] + k * unit_h
        grid.add(Line(LEFT * width / 2 + UP * y, RIGHT * width / 2 + UP * y,
                      stroke_color=DUST, stroke_width=0.8, stroke_opacity=0.35))
    g = VGroup(track, grid, fill)
    g.fill = fill
    g.track = track
    g.unit_h = unit_h
    return g


# ═══════════════════════════════════════════════════════════════════════════
class Scene6_WhyTheSquare(MovingCameraScene):
    """SCENE 6 — the proof scene. We BUILD I = m r² instead of naming it.
    One argument with a twist: distance buys speed once (linear), speed buys
    cost squared — and the two stack into r². Everything orbits one locked
    pivot; the crux is Act 5, where 'double' visibly becomes 'quadruple'."""

    # ── director toggles (each is a one-line flip) ────────────────────────
    ACT3_MODE          = "both"     # "strobe" | "unroll" | "both"  (far = fast)
    USE_HAMMER_OVERLAY = False      # Act-3 slow-mo hammer-throw insert (cuttable)
    ACT4_TILES         = True       # True -> v² grows + tiles into a 2×2 grid
    CRUX_HOLD          = "meters"   # "meters" (1 vs 4 columns) | "relay" chain
    USE_FOCUS_PULL     = True       # Act-1 camera push-in onto the surviving mass

    # ── locked geometry (class constants) ─────────────────────────────────
    R_OUTER  = 2.00                 # the outer mass — distance r (then 2r)
    R_INNER  = 1.00                 # the inner mass — exactly half (the 'r' base)
    W_R      = 0.21                 # mass-node radius
    N_STROBE = 7                    # equal-TIME strobe samples (Scene-1 constant)
    SPIN_T   = 3.2                  # seconds per full turn (sets the shared clock)

    # ── honest physics (everything visible derives from these) ────────────
    #   constant angular velocity ω over the scene's spins -> linear rate_func
    #   is the PHYSICALLY honest easing here (constant ω is the exception the
    #   style guide carves out). speed v = ω·r, so the outer mass moves at
    #   exactly twice the inner's: v_outer / v_inner = R_OUTER / R_INNER = 2.
    OMEGA = TAU / SPIN_T

    def construct(self):
        self.camera.frame.save_state()
        # frame marks pinned to the camera (constant screen size under zoom)
        self.frame_marks = VGroup(*[corner_L(o, opacity=0.0)
                                    for o in (UL, UR, DL, DR)])
        self._pin_frame_marks()
        self.add(self.frame_marks)
        self.frame_marks.set_opacity(0.42)

        self.pivot_pt = ORIGIN
        self.act1_one_mass_one_spoke()
        self.act2_two_circles_one_spin()
        self.act3_farther_means_faster()
        self.act4_cost_is_a_square()
        self.act5_double_becomes_quadruple()
        self.act6_assemble_the_formula()

    # ── frame-mark plumbing (constant screen size under zoom) ──────────────
    def _pin_frame_marks(self):
        inset = 0.34

        def updater(grp):
            f = self.camera.frame
            scl = f.get_width() / config.frame_width
            for c in grp:
                o = c.anchor
                c.set(width=0.40 * scl, height=0.40 * scl)
                c.move_to(f.get_corner(o) - o * inset * scl, aligned_edge=o)
        self.frame_marks.add_updater(updater)

    # ═══════════════════════════════════════════════════════════════ A1 ═══
    def act1_one_mass_one_spoke(self):
        """Open on Scene 5's spinning two-weight rod, then STRIP it down: dim the
        world to a ghost, keep one outer mass, snap the rod into a single dashed
        arm = the radius r. Lock the crosshair pivot everything will orbit."""
        c = self.pivot_pt
        crosshair = make_crosshair(0.22).move_to(c).set_z_index(8)

        # the inherited two-weight rod, spinning (the Scene-5 closing image)
        rod = make_rod(self.R_OUTER).move_to(c).set_z_index(3)
        m_out = make_mass_node(self.W_R).move_to(c + RIGHT * self.R_OUTER).set_z_index(5)
        m_in_twin = make_mass_node(self.W_R).move_to(c + LEFT * self.R_OUTER).set_z_index(5)
        rod_grp = VGroup(rod, m_out, m_in_twin)

        self.play(
            LaggedStart(Create(rod), FadeIn(crosshair, scale=0.6),
                        FadeIn(m_out, scale=0.85), FadeIn(m_in_twin, scale=0.85),
                        lag_ratio=0.12),
            run_time=1.2, rate_func=rate_functions.ease_out_cubic,
        )
        # a steady half-turn — constant ω, so linear is the honest easing
        self.play(Rotate(rod_grp, angle=PI, about_point=c), run_time=1.7,
                  rate_func=linear)
        self.wait(0.4)

        intro = serif("Forget the whole rod — just watch one piece.",
                      STARLIGHT, 28).to_edge(UP, buff=0.7).set_z_index(9)
        self.play(FadeIn(intro, shift=DOWN * 0.08), run_time=0.7)

        # >>> POST (light): a soft focus-pull whoosh as the world dims to ghost.
        # strip to one honest object: the twin + rod body fall to faint outline
        surviving = m_out
        self.play(
            m_in_twin.animate.set_opacity(0.10),
            rod.animate.set_opacity(0.12),
            run_time=1.0, rate_func=rate_functions.ease_in_out_cubic,
        )

        # focus-pull: a brief camera push-in onto the surviving mass, then settle
        if self.USE_FOCUS_PULL:
            self.play(self.camera.frame.animate.scale(0.62).move_to(surviving),
                      run_time=1.0, rate_func=rate_functions.ease_in_out_sine)
            self.play(surviving.animate.set_stroke(width=3.2),
                      rate_func=there_and_back, run_time=0.7)
            self.play(Restore(self.camera.frame), run_time=1.0,
                      rate_func=rate_functions.ease_in_out_sine)

        # the dashed line that became a radius in Scene 5 snaps to a single arm
        radius = DashedLine(c, surviving.get_center(), dash_length=0.16,
                            dashed_ratio=0.6, stroke_color=C_LEN,
                            stroke_width=3.0).set_z_index(4)
        r_lab = serif("r", C_LEN, 30)
        r_lab.next_to(radius, UP, buff=0.16)
        self.play(ReplacementTransform(rod.copy().set_opacity(1), radius),
                  run_time=0.9, rate_func=rate_functions.ease_in_out_cubic)
        self.play(FadeIn(r_lab, shift=UP * 0.06), run_time=0.5)
        self.remove(rod, m_in_twin)   # the ghosts have done their job

        self.play(FadeOut(intro), run_time=0.5)
        self.wait(0.7)

        # hand the clean tableau forward
        self.crosshair = crosshair
        self.radius = radius
        self.r_lab = r_lab
        self.m_out = surviving

    # ═══════════════════════════════════════════════════════════════ A2 ═══
    def act2_two_circles_one_spin(self):
        """Add a second mass at HALF the radius on the same spoke. Spin one turn;
        trace both paths into concentric circles. Prove same-spin = same-time =
        same-angle with a shared swept wedge + a rigid spoke that can't drift."""
        c = self.pivot_pt
        theta = ValueTracker(0.0)
        self.theta = theta

        # promote the single arm to a full rigid spoke through the pivot, and
        # add the inner mass at exactly half the distance
        m_in = make_mass_node(self.W_R).set_z_index(5)
        self.m_in = m_in

        def out_pos():
            return c + self.R_OUTER * dir2(theta.get_value())

        def in_pos():
            return c + self.R_INNER * dir2(theta.get_value())

        self.m_out.add_updater(lambda x: x.move_to(out_pos()))
        m_in.add_updater(lambda x: x.move_to(in_pos()))

        # the spoke: a faint rigid line tip-to-tip through the centre (rigidity)
        spoke = always_redraw(lambda: Line(
            c - self.R_OUTER * dir2(theta.get_value()),
            c + self.R_OUTER * dir2(theta.get_value()),
            stroke_color=DUST, stroke_width=2.4, stroke_opacity=0.55).set_z_index(3))

        # the live dashed radius rides along too (keeps the 'r' arm present)
        live_r = always_redraw(lambda: DashedLine(
            c, out_pos(), dash_length=0.16, dashed_ratio=0.6,
            stroke_color=C_LEN, stroke_width=3.0).set_z_index(4))

        self.play(FadeOut(self.radius), FadeOut(self.r_lab), run_time=0.4)
        self.add(spoke, live_r)
        self.play(FadeIn(m_in, scale=0.85), run_time=0.6)
        half_lbl = serif("half as far", C_LEN, 22).next_to(m_in, DOWN, buff=0.22)
        self.play(FadeIn(half_lbl, shift=UP * 0.06), run_time=0.5)
        self.wait(0.5)
        self.play(FadeOut(half_lbl), run_time=0.4)

        # the same swept wedge BOTH masses ride — identical angle, identical time
        wedge = always_redraw(lambda: AnnularSector(
            inner_radius=0.0, outer_radius=self.R_OUTER,
            angle=theta.get_value(), start_angle=0.0,
            stroke_width=0, fill_color=C_ANGLE, fill_opacity=0.12).shift(c))
        wedge.set_z_index(1)

        # accumulate both circular paths as they're swept
        trail_out = TracedPath(out_pos, stroke_color=AMBER, stroke_width=2.6).set_z_index(2)
        trail_in = TracedPath(in_pos, stroke_color=C_LEN, stroke_width=2.4).set_z_index(2)
        self.add(wedge, trail_out, trail_in)

        # one honest full turn at constant ω
        self.play(theta.animate.set_value(TAU), run_time=self.SPIN_T,
                  rate_func=linear)
        self.wait(0.3)

        # freeze the finished frame: two concentric circles, one big one small
        circ_out = Circle(radius=self.R_OUTER, stroke_color=AMBER,
                          stroke_width=2.6).move_to(c).set_z_index(2)
        circ_in = Circle(radius=self.R_INNER, stroke_color=C_LEN,
                         stroke_width=2.4).move_to(c).set_z_index(2)
        self.remove(trail_out, trail_in)
        self.add(circ_out, circ_in)
        self.play(FadeOut(wedge), run_time=0.5)

        same = serif("same spin · same time", DUST, 22).to_edge(UP, buff=0.7)
        self.play(FadeIn(same, shift=DOWN * 0.06), run_time=0.6)
        self.wait(1.0)

        self.circ_out, self.circ_in, self.spoke = circ_out, circ_in, spoke
        self.live_r = live_r
        self.same_lbl = same

    # ═══════════════════════════════════════════════════════════════ A3 ═══
    def act3_farther_means_faster(self):
        """The payoff of the oldest grammar. Strobe both masses with equal-time
        ghosts: outer spaced far, inner bunched tight — spacing IS speed. Then
        unroll the arcs into straight tracks and race them. Land on: r → 2r
        doubles the velocity arrow. distance ×2 → speed ×2 (linear)."""
        c = self.pivot_pt
        theta = self.theta
        self.play(FadeOut(self.same_lbl), run_time=0.4)

        # ── (a) STROBE: equal-time stamps along each circle ────────────────
        if self.ACT3_MODE in ("strobe", "both"):
            def stamps(radius, color):
                g = VGroup()
                for k in range(self.N_STROBE + 1):
                    ang = TAU * (k / self.N_STROBE)
                    op = 0.16 + 0.34 * (k / self.N_STROBE)
                    g.add(ghost_disc(c + radius * dir2(ang), self.W_R * 0.9,
                                     color, op))
                return g.set_z_index(2)

            g_out = stamps(self.R_OUTER, C_MASS)
            g_in = stamps(self.R_INNER, C_MASS)
            # reset the spoke to θ=0 so the live masses sit at the first stamp
            theta.set_value(0.0)
            # drop stamps in TIME order while the spoke sweeps once more
            self.play(
                theta.animate.set_value(TAU),
                LaggedStart(*[FadeIn(s) for s in g_out], lag_ratio=0.11),
                LaggedStart(*[FadeIn(s) for s in g_in], lag_ratio=0.11),
                run_time=self.SPIN_T, rate_func=linear,
            )
            read = serif("spacing is speed", AMBER, 24).to_edge(UP, buff=0.7)
            self.play(FadeIn(read, shift=DOWN * 0.06), run_time=0.6)
            self.wait(1.1)
            self.play(FadeOut(read), FadeOut(g_out), FadeOut(g_in), run_time=0.6)

        # ── (b) UNROLL: peel each arc into a straight track and race ────────
        if self.ACT3_MODE in ("unroll", "both"):
            # clear the orbital furniture, keep the locked pivot
            self.m_out.clear_updaters(); self.m_in.clear_updaters()
            self.play(
                FadeOut(VGroup(self.circ_out, self.circ_in, self.spoke,
                               self.live_r, self.m_out, self.m_in)),
                run_time=0.7,
            )
            # display lengths preserve the honest 2:1 ratio (arc-length ∝ r)
            L_out, L_in = 5.4, 2.7
            y_out, y_in = 1.1, -0.9
            track_out = Line(LEFT * L_out / 2 + UP * y_out,
                             RIGHT * L_out / 2 + UP * y_out,
                             stroke_color=DUST, stroke_width=2.2,
                             stroke_opacity=0.6)
            track_in = Line(LEFT * L_in / 2 + UP * y_in,
                            RIGHT * L_in / 2 + UP * y_in,
                            stroke_color=DUST, stroke_width=2.2,
                            stroke_opacity=0.6)
            # the arcs visibly straighten into the tracks
            arc_out = Arc(radius=self.R_OUTER, start_angle=PI / 2, angle=TAU,
                          arc_center=c, stroke_color=AMBER, stroke_width=2.6)
            arc_in = Arc(radius=self.R_INNER, start_angle=PI / 2, angle=TAU,
                         arc_center=c, stroke_color=C_LEN, stroke_width=2.6)
            self.add(arc_out, arc_in)
            self.play(
                ReplacementTransform(arc_out, track_out),
                ReplacementTransform(arc_in, track_in),
                run_time=1.1, rate_func=rate_functions.ease_in_out_cubic,
            )
            lab_far = serif("far mass", AMBER, 20).next_to(track_out, LEFT, buff=0.3)
            lab_near = serif("near mass", C_LEN, 20).next_to(track_in, LEFT, buff=0.3)
            self.play(FadeIn(lab_far), FadeIn(lab_near), run_time=0.5)

            # race: both start together, finish together — top sprints
            dot_out = make_mass_node(self.W_R * 0.9).move_to(track_out.get_left())
            dot_in = make_mass_node(self.W_R * 0.9).move_to(track_in.get_left())
            self.add(dot_out, dot_in)
            self.play(
                dot_out.animate.move_to(track_out.get_right()),
                dot_in.animate.move_to(track_in.get_right()),
                run_time=2.0, rate_func=linear,   # constant speed = honest
            )
            self.wait(0.8)
            self.play(FadeOut(VGroup(track_out, track_in, dot_out, dot_in,
                                     lab_far, lab_near)), run_time=0.6)

        # ── (c) CLEAN: r → 2r doubles the velocity arrow (linear) ──────────
        c = self.pivot_pt
        self.add(self.crosshair)
        base_r = Line(c, c + RIGHT * self.R_INNER, stroke_color=C_LEN,
                      stroke_width=3.0).set_z_index(3)
        mass = make_mass_node(self.W_R).move_to(c + RIGHT * self.R_INNER).set_z_index(5)
        r_tag = serif("r", C_LEN, 26).next_to(base_r, DOWN, buff=0.14)
        v_arr = velocity_arrow(mass.get_center(),
                               UP * 0.9, C_VEL).set_z_index(6)
        v_tag = serif("v", C_VEL, 24).next_to(v_arr, RIGHT, buff=0.1)
        self.play(GrowFromPoint(base_r, c), FadeIn(mass, scale=0.85),
                  FadeIn(r_tag), run_time=0.8)
        self.play(GrowFromPoint(v_arr, mass.get_center()), FadeIn(v_tag),
                  run_time=0.6)
        self.wait(0.6)

        # slide the mass out to 2r; the velocity arrow doubles in length honestly
        long_r = Line(c, c + RIGHT * self.R_OUTER, stroke_color=C_LEN,
                      stroke_width=3.0).set_z_index(3)
        mass2_pt = c + RIGHT * self.R_OUTER
        v_arr2 = velocity_arrow(mass2_pt, UP * 1.8, C_VEL).set_z_index(6)
        r2_tag = serif("2r", C_LEN, 26).next_to(long_r, DOWN, buff=0.14)
        v2_tag = serif("2v", C_VEL, 24).next_to(v_arr2, RIGHT, buff=0.1)
        self.play(
            ReplacementTransform(base_r, long_r),
            mass.animate.move_to(mass2_pt),
            ReplacementTransform(v_arr, v_arr2),
            ReplacementTransform(r_tag, r2_tag),
            ReplacementTransform(v_tag, v2_tag),
            run_time=1.4, rate_func=rate_functions.ease_in_out_cubic,
        )
        self.wait(0.5)

        link = serif("distance ×2  →  speed ×2", STARLIGHT, 28).to_edge(
            DOWN, buff=0.7).set_z_index(9)
        linear_tag = Text("LINEAR", font=MONO, font_size=16, color=DUST)
        linear_tag.next_to(link, UP, buff=0.18)
        self.play(FadeIn(link, shift=UP * 0.06), FadeIn(linear_tag), run_time=0.7)

        self.wait(1.0)
        self.play(FadeOut(VGroup(long_r, mass, v_arr2, r2_tag, v2_tag,
                                 link, linear_tag)), run_time=0.7)
        # keep the crosshair locked for the rest of the scene

    # ═══════════════════════════════════════════════════════════════ A4 ═══
    def act4_cost_is_a_square(self):
        """The second ingredient, as a literal area. A v-length bar grows
        sideways into a v×v square — that square IS the cost. Double the side to
        2v and it fills as a 2×2 grid: four tiles. speed ×2 → cost ×4."""
        recall = serif("the cost of motion grows with speed²", STARLIGHT, 28)
        recall.to_edge(UP, buff=0.7).set_z_index(9)
        self.play(FadeIn(recall, shift=DOWN * 0.06), run_time=0.7)

        u = 1.3   # one 'v' in screen units
        base_corner = LEFT * 1.0 + DOWN * 1.2

        # the velocity bar of length v
        bar = Line(base_corner, base_corner + RIGHT * u, stroke_color=C_VEL,
                   stroke_width=7.0).set_z_index(5)
        v_lab = serif("v", C_VEL, 26).next_to(bar, DOWN, buff=0.14)
        self.play(GrowFromPoint(bar, base_corner), FadeIn(v_lab), run_time=0.7)
        self.wait(0.4)

        # grow it sideways into a v×v square — area v²
        sq1 = Square(side_length=u, stroke_color=C_ENERGY, stroke_width=2.4,
                     fill_color=C_ENERGY, fill_opacity=0.18)
        sq1.move_to(base_corner + RIGHT * u / 2 + UP * u / 2).set_z_index(4)
        self.play(GrowFromEdge(sq1, DOWN), run_time=0.9,
                  rate_func=rate_functions.ease_out_cubic)
        v2_lab = squared("v", C_ENERGY, 30).move_to(sq1.get_center())
        self.play(FadeIn(v2_lab, scale=0.85), run_time=0.6)
        cost1 = Text("= 1 unit of cost", font=MONO, font_size=16, color=DUST)
        cost1.next_to(sq1, RIGHT, buff=0.4)
        self.play(FadeIn(cost1, shift=RIGHT * 0.06), run_time=0.5)
        self.wait(0.8)

        # double the side to 2v -> the cost fills as a 2×2 grid of the original
        self.play(FadeOut(VGroup(bar, v_lab, cost1)), run_time=0.4)
        self.play(v2_lab.animate.set_opacity(0.0), run_time=0.3)
        self.remove(v2_lab)

        if self.ACT4_TILES:
            big_origin = sq1.get_corner(DL)
            tiles = VGroup()
            for (ix, iy) in [(0, 0), (1, 0), (0, 1), (1, 1)]:
                t = Square(side_length=u, stroke_color=C_ENERGY, stroke_width=2.0,
                           fill_color=C_ENERGY, fill_opacity=0.18)
                t.move_to(big_origin + RIGHT * (ix + 0.5) * u + UP * (iy + 0.5) * u)
                tiles.add(t)
            # the first tile IS the original square; snap the other three in
            self.remove(sq1)
            self.add(tiles[0])
            # >>> POST: a small tactile 'snap' on each of the next three tiles.
            self.play(
                LaggedStart(*[FadeIn(t, scale=0.6) for t in tiles[1:]],
                            lag_ratio=0.18),
                run_time=1.3, rate_func=rate_functions.ease_out_cubic,
            )
            big_sq = tiles
            # the doubled side labels
            side_b = serif("2v", C_VEL, 24).next_to(big_sq, DOWN, buff=0.16)
            self.play(FadeIn(side_b), run_time=0.4)
            four = squared("2v", C_ENERGY, 30).move_to(big_sq.get_center())
            four_eq = Text("= 4 units of cost", font=MONO, font_size=16,
                           color=AMBER).next_to(big_sq, RIGHT, buff=0.4)
            self.play(FadeIn(four, scale=0.85), run_time=0.5)
            self.play(FadeIn(four_eq, shift=RIGHT * 0.06), run_time=0.5)
        else:
            big_sq = Square(side_length=2 * u, stroke_color=C_ENERGY,
                            stroke_width=2.4, fill_color=C_ENERGY,
                            fill_opacity=0.18)
            big_sq.move_to(sq1.get_corner(DL) + RIGHT * u + UP * u)
            self.play(ReplacementTransform(sq1, big_sq), run_time=0.9)
            four = squared("2v", C_ENERGY, 30).move_to(big_sq.get_center())
            side_b = serif("2v", C_VEL, 24).next_to(big_sq, DOWN, buff=0.16)
            four_eq = Text("= 4 units of cost", font=MONO, font_size=16,
                           color=AMBER).next_to(big_sq, RIGHT, buff=0.4)
            self.play(FadeIn(four), FadeIn(side_b), FadeIn(four_eq), run_time=0.7)

        self.wait(0.6)
        prop = serif("cost ∝ speed²", AMBER, 30).to_edge(DOWN, buff=0.75)
        self.play(FadeIn(prop, shift=UP * 0.06), run_time=0.7)
        self.wait(1.4)

        self.play(FadeOut(VGroup(recall, big_sq, four, side_b, four_eq, prop)),
                  run_time=0.8)

    # ═══════════════════════════════════════════════════════════════ A5 ═══
    def act5_double_becomes_quadruple(self):
        """CRUX. Chain Act 3 and Act 4: a '×2' token slides in from distance,
        passes through the v² square, and EMERGES as '×4'. Then hold the side-by-
        side cost meters — 1 unit vs 4 units — and let r square itself."""
        # ── the multiplier relay: ×2 enters, ×4 leaves ────────────────────
        d_tok = serif("×2", C_LEN, 40).move_to(LEFT * 4.6)
        d_lab = Text("DISTANCE", font=MONO, font_size=14, color=DUST).next_to(
            d_tok, UP, buff=0.2)
        square = Square(side_length=1.5, stroke_color=C_ENERGY, stroke_width=2.4,
                        fill_color=C_ENERGY, fill_opacity=0.18).move_to(ORIGIN)
        sq_lab = squared("v", C_ENERGY, 28).move_to(square.get_center())
        out_tok = serif("×4", AMBER, 48).move_to(RIGHT * 4.6)
        out_lab = Text("COST", font=MONO, font_size=14, color=AMBER).next_to(
            out_tok, UP, buff=0.2)

        self.play(FadeIn(d_tok, shift=RIGHT * 0.1), FadeIn(d_lab), run_time=0.6)
        self.play(GrowFromEdge(square, DOWN), FadeIn(sq_lab), run_time=0.7)
        self.wait(0.4)

        speed_tok = serif("×2", C_VEL, 40)
        speed_lab = Text("SPEED", font=MONO, font_size=14, color=C_VEL)
        # ×2 (distance) travels to the square, becoming ×2 (speed) on the way
        self.play(d_tok.animate.move_to(LEFT * 1.9),
                  FadeOut(d_lab), run_time=0.8,
                  rate_func=rate_functions.ease_in_out_cubic)
        speed_tok.move_to(LEFT * 1.9)
        speed_lab.next_to(speed_tok, UP, buff=0.2)
        self.play(ReplacementTransform(d_tok, speed_tok), FadeIn(speed_lab),
                  run_time=0.5)
        self.wait(0.3)

        # the token passes THROUGH the square and emerges quadrupled
        self.play(speed_tok.animate.move_to(square.get_center()).scale(0.7),
                  FadeOut(speed_lab), run_time=0.7,
                  rate_func=rate_functions.ease_in_cubic)
        self.play(Indicate(square, scale_factor=1.18, color=AMBER), run_time=0.6)
        self.play(ReplacementTransform(speed_tok, out_tok), FadeIn(out_lab),
                  run_time=0.8, rate_func=rate_functions.ease_out_cubic)
        # >>> POST: a single low resonant cue as ×2 emerges as ×4.
        self.play(Indicate(out_tok, scale_factor=1.22, color=AMBER), run_time=0.7)

        if self.CRUX_HOLD == "relay":
            self.wait(2.6)   # hold the relay as the crux frame

        self.play(FadeOut(VGroup(square, sq_lab, out_tok, out_lab)), run_time=0.7)

        # ── the crux tableau: two masses, two cost meters (1 vs 4) ─────────
        cL = LEFT * 3.4 + DOWN * 0.3
        cR = RIGHT * 1.0 + DOWN * 0.3

        def mass_on_radius(center, radius, tag):
            cross = make_crosshair(0.16).move_to(center).set_z_index(8)
            seg = DashedLine(center, center + RIGHT * radius, dash_length=0.14,
                             dashed_ratio=0.6, stroke_color=C_LEN,
                             stroke_width=2.6).set_z_index(3)
            node = make_mass_node(self.W_R).move_to(
                center + RIGHT * radius).set_z_index(5)
            lab = serif(tag, C_LEN, 22).next_to(seg, DOWN, buff=0.12)
            return VGroup(cross, seg, node, lab)

        left_rig = mass_on_radius(cL, 1.0, "r")
        right_rig = mass_on_radius(cR, 2.0, "2r")
        meterL = cost_meter(1).next_to(left_rig, UP, buff=0.5)
        meterR = cost_meter(4).next_to(right_rig, UP, buff=0.5)
        # align meter bottoms to a common baseline
        base_y = min(meterL.track.get_bottom()[1], meterR.track.get_bottom()[1])
        meterL.shift(UP * (base_y - meterL.track.get_bottom()[1]))
        meterR.shift(UP * (base_y - meterR.track.get_bottom()[1]))

        self.play(FadeIn(left_rig, shift=RIGHT * 0.06),
                  FadeIn(right_rig, shift=LEFT * 0.06), run_time=0.8)

        # fill the meters: left to 1, right OVERSHOOTS to 4 then settles
        fillL = meterL.fill.copy()
        fillR_final = meterR.fill.copy()
        meterL.fill.stretch_to_fit_height(1e-3).align_to(meterL.track, DOWN)
        meterR.fill.stretch_to_fit_height(1e-3).align_to(meterR.track, DOWN)
        self.add(meterL, meterR)
        self.play(
            meterL.fill.animate.become(fillL),
            run_time=0.7, rate_func=rate_functions.ease_out_cubic,
        )
        cmL = Text("1×", font=MONO, font_size=20, color=DUST).next_to(meterL, UP, buff=0.18)
        self.play(FadeIn(cmL), run_time=0.4)
        self.wait(0.4)
        # >>> POST: low resonant cue as the right meter overshoots to 4×.
        over = fillR_final.copy().stretch_to_fit_height(
            fillR_final.height * 1.08).align_to(meterR.track, DOWN)
        self.play(meterR.fill.animate.become(over), run_time=0.7,
                  rate_func=rate_functions.ease_out_cubic)
        self.play(meterR.fill.animate.become(fillR_final), run_time=0.3,
                  rate_func=rate_functions.ease_in_out_sine)
        cmR = Text("4×", font=MONO, font_size=24, color=AMBER).next_to(meterR, UP, buff=0.18)
        self.play(FadeIn(cmR, scale=1.1), run_time=0.4)

        verdict = serif("same mass · twice the distance · four times as hard",
                        STARLIGHT, 26).to_edge(DOWN, buff=0.6).set_z_index(9)
        self.play(FadeIn(verdict, shift=UP * 0.06), run_time=0.8)

        # slight push-in on the side-by-side — and HOLD (the crux beat)
        if self.CRUX_HOLD == "meters":
            self.play(self.camera.frame.animate.scale(0.9).move_to(
                VGroup(meterL, meterR).get_center() + DOWN * 0.2),
                run_time=1.0, rate_func=rate_functions.ease_in_out_sine)
            self.wait(2.6)
            self.play(Restore(self.camera.frame), run_time=1.0,
                      rate_func=rate_functions.ease_in_out_sine)

        # ── seal it: r squares ITSELF into an r×r area ─────────────────────
        self.play(
            FadeOut(VGroup(left_rig, meterL, meterR, cmL, cmR, verdict)),
            run_time=0.8,
        )
        # reuse the right rig's radius, recentre, extrude the perpendicular copy
        self.play(right_rig.animate.move_to(ORIGIN + DOWN * 0.4), run_time=0.8,
                  rate_func=rate_functions.ease_in_out_cubic)
        # build a clean r-arm at the recentred pivot
        piv = right_rig[0].get_center()
        seg = DashedLine(piv, piv + RIGHT * self.R_OUTER, dash_length=0.14,
                         dashed_ratio=0.6, stroke_color=C_LEN,
                         stroke_width=3.0).set_z_index(4)
        self.remove(right_rig)
        self.add(make_crosshair(0.16).move_to(piv).set_z_index(8), seg)
        r_side = serif("r", C_LEN, 26).next_to(seg, DOWN, buff=0.14)
        self.play(FadeIn(r_side), run_time=0.4)

        # extrude an identical perpendicular copy upward -> a literal r×r square
        rr_square = Square(side_length=self.R_OUTER, stroke_color=C_LEN,
                           stroke_width=2.6, fill_color=C_LEN, fill_opacity=0.14)
        rr_square.move_to(piv + RIGHT * self.R_OUTER / 2 + UP * self.R_OUTER / 2)
        up_edge = DashedLine(piv, piv + UP * self.R_OUTER, dash_length=0.14,
                             dashed_ratio=0.6, stroke_color=C_LEN,
                             stroke_width=3.0)
        self.play(GrowFromPoint(up_edge, piv), run_time=0.6)
        self.play(GrowFromEdge(rr_square, DL), run_time=0.9,
                  rate_func=rate_functions.ease_out_cubic)
        rr_lab = squared("r", C_LEN, 36).move_to(rr_square.get_center())
        self.play(FadeIn(rr_lab.base), run_time=0.3)
        self.play(Write(rr_lab.exp), run_time=0.4)   # the exponent appears: r → r²
        self.wait(0.4)

        seal = serif("distance doesn't count once — it counts squared",
                     STARLIGHT, 26).to_edge(DOWN, buff=0.6).set_z_index(9)
        self.play(FadeIn(seal, shift=UP * 0.06), run_time=0.8)
        self.wait(1.6)

        # hand the r² square forward to Act 6
        self.rr_square = rr_square
        self.rr_lab = rr_lab
        self._a5_clear = VGroup(seg, up_edge, r_side, seal)

    # ═══════════════════════════════════════════════════════════════ A6 ═══
    def act6_assemble_the_formula(self):
        """Assemble I = m r² from parts the viewer already owns. Bring back m
        (the bowling-ball laziness number), dock it onto the r² square, and let
        each symbol pulse toward the act that earned it. End held, clean."""
        self.play(FadeOut(self._a5_clear), run_time=0.6)

        # shrink the r² square up into formula scale and park it on the right
        target = RIGHT * 1.7 + UP * 0.2
        r2_sym = self.rr_lab
        self.play(
            FadeOut(self.rr_square),
            r2_sym.animate.scale(1.0).move_to(target).set_color(C_LEN),
            run_time=0.9, rate_func=rate_functions.ease_in_out_cubic,
        )

        # bring back m — recognisably the same heavy character (bowling ball)
        ball = make_bowling_ball(0.42).move_to(LEFT * 4.0 + UP * 0.2).set_z_index(5)
        self.play(FadeIn(ball, shift=RIGHT * 0.1, scale=0.85), run_time=0.7)
        self.wait(0.4)
        m_sym = serif("m", C_MASS, 56).move_to(LEFT * 0.6 + UP * 0.2)
        # the ball condenses into its symbol m
        self.play(ReplacementTransform(ball, m_sym), run_time=0.9,
                  rate_func=rate_functions.ease_in_out_sine)

        # the equation assembles left to right, each symbol carrying its meaning
        I_sym = serif("I", STARLIGHT, 60).move_to(LEFT * 3.0 + UP * 0.2)
        eq = serif("=", STARLIGHT, 56, italic=False).move_to(LEFT * 1.9 + UP * 0.2)
        times = serif("·", STARLIGHT, 56, italic=False).move_to(RIGHT * 0.55 + UP * 0.2)

        self.play(FadeIn(I_sym, shift=RIGHT * 0.06), run_time=0.5)
        self.play(FadeIn(eq), run_time=0.4)
        self.play(m_sym.animate.move_to(LEFT * 0.2 + UP * 0.2), run_time=0.5)
        self.play(FadeIn(times), run_time=0.3)
        self.play(r2_sym.animate.move_to(RIGHT * 1.5 + UP * 0.2), run_time=0.5)

        formula = VGroup(I_sym, eq, m_sym, times, r2_sym)
        rule = Line(formula.get_left() + DOWN * 0.9, formula.get_right() + DOWN * 0.9,
                    stroke_color=AMBER, stroke_width=1.4)
        rule.set_length(formula.width * 0.5).next_to(formula, DOWN, buff=0.55)
        self.play(Create(rule), run_time=0.6)
        self.wait(0.6)

        # annotate each term with the act that earned it (mono, the quiet voice)
        a_I = Text("rotational stubbornness", font=MONO, font_size=13, color=DUST)
        a_m = Text("how lazy it is", font=MONO, font_size=13, color=C_MASS)
        a_r = Text("how far — counted squared", font=MONO, font_size=13, color=C_LEN)
        a_I.next_to(I_sym, UP, buff=0.55)
        a_m.next_to(m_sym, DOWN, buff=0.9)
        a_r.next_to(r2_sym, UP, buff=0.55)

        # m pulses toward its origin (mass character); r² toward the doubling square
        self.play(FadeIn(a_m, shift=UP * 0.05),
                  Indicate(m_sym, scale_factor=1.15, color=C_MASS), run_time=0.7)
        self.play(FadeIn(a_r, shift=DOWN * 0.05),
                  Indicate(r2_sym, scale_factor=1.15, color=C_LEN), run_time=0.7)
        self.play(FadeIn(a_I, shift=DOWN * 0.05),
                  Indicate(I_sym, scale_factor=1.12, color=STARLIGHT), run_time=0.7)
        self.wait(1.0)

        # settle on the clean isolated formula, held center-frame
        self.play(FadeOut(VGroup(a_I, a_m, a_r)), run_time=0.6)
        held = VGroup(formula, rule)
        self.play(held.animate.move_to(ORIGIN).scale(1.06), run_time=1.0,
                  rate_func=rate_functions.ease_in_out_cubic)
        self.wait(2.4)