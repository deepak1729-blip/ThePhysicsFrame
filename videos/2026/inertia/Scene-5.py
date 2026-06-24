from manim import *
import numpy as np
import math

# ─────────────────────────────────────────────────────────────────────────
#  OBSERVATORY PALETTE  (verbatim from the series design system)
# ─────────────────────────────────────────────────────────────────────────
VOID      = "#0A0C10"   # base background
PANEL     = "#11151C"   # lifted surfaces
STARLIGHT = "#E8E6DF"   # primary text
DUST      = "#9A958C"   # secondary · metadata · the dimmed state
AMBER     = "#D98A3D"   # primary accent · focus (amber follows the eye)
CYAN      = "#5B8FB0"   # secondary · sparing

# quantity pigments — each quantity keeps its colour across the whole series
C_MASS    = "#B89A86"   # MASS / the property of the object
C_FORCE   = "#E06450"   # FORCE — the push I APPLY
C_GRAV    = "#8B8FF2"   # GRAVITY / WEIGHT
C_VEL     = "#57C08A"   # VELOCITY
C_GROUND  = "#7F8A99"   # ground / reference axis
C_TORQUE  = "#BB80D8"   # TORQUE — the turning effort (new this scene)
C_LEN     = "#5B8FB0"   # LENGTH / r — the radius (== CYAN; the Scene-6 seed)
C_ANGLE   = "#E08AAB"   # ANGLE θ

SERIF = "Spectral"      # ideas; italic is the channel's speaking voice
MONO  = "Space Mono"    # labels & metadata only

config.background_color = VOID
RNG = np.random.default_rng(5)   # deterministic -> stable render cache


# ═══════════════════════════════════════════════════════════════════════════
#  CONSTRUCTION VOCABULARY  (reused verbatim from Scenes 1–4, then extended)
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
    from Scenes 3–4. Exposes `.disc`, `.radius`. (Verbatim from Scene 4.)"""
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


def ghost_disc(center, radius, color=C_MASS, opacity=0.34):
    """One equal-time strobe stamp. A row of these encodes SPEED by spacing —
    the Scenes 1–2 grammar, here reused on the rotating weights. (From Scene 4.)"""
    d = Circle(radius=radius, stroke_color=color, stroke_width=2.0,
               stroke_opacity=opacity, fill_color=color, fill_opacity=0.05)
    d.move_to(center)
    return d


# ─────────────────────────── new vocabulary for Scene 5 ───────────────────
def make_mass_node(radius=0.24, color=C_MASS):
    """A small descendant of the bowling ball — same PANEL fill, same mass-pigment
    rim, same specular tell — so the rod weights read as the SAME heavy character
    from Scenes 3–4 without the finger-hole clutter at small scale. All four nodes
    are built identically: equal mass is shown by construction, not claimed."""
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
    """A clean uniform bar — the (massless) rod the weights ride on."""
    bar = RoundedRectangle(width=2 * half_len, height=thickness,
                           corner_radius=thickness / 2, stroke_width=0,
                           fill_color=color, fill_opacity=opacity)
    return bar


def make_pivot(radius=0.085, color=AMBER):
    """The clamp at a rod's centre — the axis it turns about."""
    outer = Circle(radius=radius, stroke_color=color, stroke_width=2.0,
                   fill_color=VOID, fill_opacity=1.0)
    inner = Dot(radius=radius * 0.42, color=color)
    return VGroup(outer, inner)


def curved_torque_arrow(center, radius, start_angle, sweep,
                        color=C_TORQUE, width=5.0):
    """A curved push — the turning effort. Built fixed-geometry so the SAME arrow
    can be copied onto both rods: identical size == 'same effort', unmistakably."""
    arc = Arc(radius=radius, start_angle=start_angle, angle=sweep,
              arc_center=center, stroke_color=color, stroke_width=width)
    end_angle = start_angle + sweep
    # tangent at the arc's end (direction of travel for a positive sweep)
    tdir = np.array([-math.sin(end_angle), math.cos(end_angle), 0.0]) * np.sign(sweep)
    tip = Triangle().scale(0.075)
    tip.set_fill(color, opacity=1.0).set_stroke(width=0)
    tip.rotate(math.atan2(tdir[1], tdir[0]) - 90 * DEGREES)   # Triangle apex = +y
    tip.move_to(arc.get_end())
    return VGroup(arc, tip)


def make_clock(radius=0.42):
    """A minimal clock face — summoned only to be DISMISSED. 'moment' misleads
    toward time; we show that reading, then strike it."""
    face = Circle(radius=radius, stroke_color=DUST, stroke_width=2.0,
                  fill_color=PANEL, fill_opacity=0.8)
    ticks = VGroup()
    for k in range(12):
        a = k * 30 * DEGREES + 90 * DEGREES
        p1 = radius * 0.86 * dir2(a)
        p2 = radius * 0.98 * dir2(a)
        ticks.add(Line(p1, p2, stroke_color=DUST, stroke_width=1.4,
                       stroke_opacity=0.7))
    hour = Line(ORIGIN, radius * 0.5 * dir2(60 * DEGREES),
                stroke_color=STARLIGHT, stroke_width=2.6)
    minute = Line(ORIGIN, radius * 0.8 * dir2(150 * DEGREES),
                  stroke_color=STARLIGHT, stroke_width=2.0)
    hub = Dot(radius=0.03, color=STARLIGHT)
    return VGroup(face, ticks, hour, minute, hub)


def make_lever(half_len=2.1):
    """A seesaw: a fulcrum and a balanced bar. The honest definition of 'moment' —
    push out at a distance and it turns; push near the pivot and it barely does."""
    fulcrum = Triangle().scale(0.34)
    fulcrum.set_fill(DUST, opacity=0.6).set_stroke(C_GROUND, width=1.6)
    bar = RoundedRectangle(width=2 * half_len, height=0.12, corner_radius=0.06,
                           stroke_width=0, fill_color=STARLIGHT, fill_opacity=0.9)
    bar.next_to(fulcrum.get_top(), UP, buff=-0.02)
    g = VGroup(fulcrum, bar)
    g.pivot = bar.get_center()
    g.bar = bar
    g.half_len = half_len
    return g


def make_wrench(length=2.0):
    """A wrench on a bolt — alternate 'leverage' glyph. Long handle, jaw at the
    bolt; push the far end and the bolt turns."""
    handle = RoundedRectangle(width=length, height=0.16, corner_radius=0.08,
                              stroke_width=0, fill_color=DUST, fill_opacity=0.92)
    jaw = VGroup(
        Arc(radius=0.2, start_angle=-120 * DEGREES, angle=240 * DEGREES,
            stroke_color=DUST, stroke_width=10),
    )
    jaw.next_to(handle, LEFT, buff=-0.04)
    g = VGroup(handle, jaw)
    g.handle = handle
    return g


def starfield(n=110, x_range=(-7.4, 7.4), y_range=(-4.3, 4.3), seed=5):
    """Deterministic starfield. Quiet — never competes with the amber focus."""
    rng = np.random.default_rng(seed)
    g = VGroup()
    for _ in range(n):
        x = rng.uniform(*x_range)
        y = rng.uniform(*y_range)
        r = rng.uniform(0.006, 0.022)
        op = rng.uniform(0.18, 0.7)
        col = CYAN if rng.random() < 0.12 else STARLIGHT
        s = Dot(point=np.array([x, y, 0]), radius=r,
                color=col, fill_opacity=op, stroke_width=0)
        g.add(s)
    return g


# ═══════════════════════════════════════════════════════════════════════════
class Scene5_WhereTheMassLives(MovingCameraScene):
    """SCENE 5 — the gear-shift from the straight-line world into rotation.
    Crux: two rods, same mass, different stubbornness — because of WHERE the mass
    sits. Plants the radius r that Scene 6 squares into mr²."""

    # ── director toggles (each is a one-line flip) ────────────────────────
    ACT1_MODE          = "bend"     # "bend" the line into a circle (2D, on-grammar)
    USE_BOWLING_WEIGHTS = False     # True -> full tagged finger-holed ball as weight
    USE_TWIST_OVERLAY  = True       # Act 3 live-action "twist a loaded rod" insert
    SHOW_MASS_TALLY    = True       # the unchanged count that proves equal mass
    MOMENT_DEF         = "lever"    # "lever" | "wrench" | "text"

    # ── locked geometry (class constants; the series convention) ──────────
    REF_Y     = 0.0                 # the inherited horizontal reference line
    CIRC_R    = 2.20                # radius the swept line rakes out in Act 1

    ROD_Y     = 1.65                # |y| of each rod's pivot (rods stacked)
    ROD_L     = 1.55                # rod half-length
    R_NEUTRAL = 0.85                # Act-2 starting weight radius (both rods)
    R_INNER   = 0.50                # Rod 1 after the slide (mass near centre)
    R_OUTER   = 1.38                # Rod 2 after the slide (mass at the ends)
    W_R       = 0.24                # weight-node radius
    N_STROBE  = 7                   # equal-time angular strobe samples

    # ── honest physics constants (everything derives from these) ──────────
    M_NODE  = 1.00                  # each weight, kg (4 identical -> equal totals)
    TH1     = math.radians(150.0)   # Rod 1 angle under one push, from rest
    # same torque, same time, from rest:  θ = ½(τ/I)t²  with I = 2·m·r²
    #   ⇒  θ ∝ 1/r²  ⇒  TH2 = TH1·(R_INNER/R_OUTER)²   (computed, not eyeballed)
    @property
    def TH2(self):
        return self.TH1 * (self.R_INNER / self.R_OUTER) ** 2

    def construct(self):
        self.camera.frame.save_state()
        # frame marks pinned to the camera (constant screen size under zoom) —
        # the Scene 1–4 pattern, carried in for continuity.
        self.frame_marks = VGroup(*[corner_L(o, opacity=0.0)
                                    for o in (UL, UR, DL, DR)])
        self._pin_frame_marks()

        self.act1_the_world_turns()
        self.act2_built_from_the_same_stuff()
        self.act3_the_spin_test()
        self.act4_same_mass_the_flip()
        self.act5_naming_it()

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
    def act1_the_world_turns(self):
        """Reuse the EXACT side-on reference line + travelling ball, then pin the
        midpoint and sweep the line around: the straight path becomes a radius,
        its tip rakes out a circle. 'Straight line' → 'Rotation', one smooth move."""
        self.add(self.frame_marks)
        self.frame_marks.set_opacity(0.45)

        # the inherited dashed horizontal reference (Scenes 1–4 live here)
        ref = DashedLine(LEFT * 6.6 + UP * self.REF_Y,
                         RIGHT * 6.6 + UP * self.REF_Y,
                         dash_length=0.18, dashed_ratio=0.55, color=C_GROUND,
                         stroke_width=2.0, stroke_opacity=0.0).set_z_index(-1)
        self.add(ref)

        word = Text("STRAIGHT LINE", font=MONO, font_size=20, color=DUST)
        word.to_edge(UP, buff=0.75).set_z_index(9)

        # the tagged ball travels left → right, exactly as for four scenes
        ball = make_bowling_ball(0.40).set_z_index(5)
        ball.move_to(LEFT * 5.0 + UP * self.REF_Y)
        self.add(ball)
        # >>> POST: a low continuous travel tone under the roll.
        self.play(ref.animate.set_stroke(opacity=0.85),
                  FadeIn(word, shift=DOWN * 0.1), run_time=0.7,
                  rate_func=rate_functions.ease_out_cubic)
        self.play(ball.animate.move_to(RIGHT * self.CIRC_R + UP * self.REF_Y),
                  run_time=1.6, rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.5)

        # the segment that will become the diameter, laid exactly on the ref line
        theta = ValueTracker(0.0)
        center = ORIGIN
        diameter = always_redraw(
            lambda: Line(center + self.CIRC_R * dir2(theta.get_value() + PI),
                         center + self.CIRC_R * dir2(theta.get_value()),
                         stroke_color=AMBER, stroke_width=3.0)
        )
        ghost = Line(center + self.CIRC_R * LEFT, center + self.CIRC_R * RIGHT,
                     stroke_color=STARLIGHT, stroke_width=2.0,
                     stroke_opacity=0.0).set_z_index(-1)
        pivot = make_pivot(0.075).move_to(center).set_z_index(6)
        rim = always_redraw(
            lambda: Dot(center + self.CIRC_R * dir2(theta.get_value()),
                        radius=0.045, color=AMBER).set_z_index(6)
        )
        traced = TracedPath(lambda: center + self.CIRC_R * dir2(theta.get_value()),
                            stroke_color=AMBER, stroke_width=2.6)
        traced.set_z_index(2)

        self.add(ghost, diameter, traced, rim, pivot)
        self.play(ghost.animate.set_stroke(opacity=0.22),
                  FadeIn(pivot, scale=0.6), run_time=0.6)

        # the ball rides the sweeping tip — same ball, now bent into a loop
        ball.add_updater(
            lambda m: m.move_to(center + self.CIRC_R * dir2(theta.get_value()))
        )
        # >>> POST: a soft whoosh keyed to the sweep — the dimensional shift.
        self.play(theta.animate.set_value(TAU), run_time=2.6,
                  rate_func=rate_functions.ease_in_out_cubic)
        ball.clear_updaters()

        rotation_word = Text("ROTATION", font=MONO, font_size=20, color=AMBER)
        rotation_word.move_to(word).set_z_index(9)
        self.play(ReplacementTransform(word, rotation_word),
                  ghost.animate.set_stroke(opacity=0.0),
                  run_time=1.0, rate_func=rate_functions.ease_in_out_cubic)

        # collapse the diameter to a single clean radius, the circle owns the frame
        self.remove(diameter, rim, traced)
        circle = Circle(radius=self.CIRC_R, stroke_color=AMBER, stroke_width=2.6)
        circle.move_to(center).set_z_index(2)
        radius_line = Line(center, center + self.CIRC_R * RIGHT,
                           stroke_color=AMBER, stroke_width=3.0).set_z_index(3)
        self.add(circle, radius_line)
        self.play(
            FadeOut(ball, scale=0.7),
            ref.animate.set_stroke(opacity=0.0),
            run_time=0.9, rate_func=rate_functions.ease_in_out_cubic,
        )
        self.remove(ref)
        self.wait(0.8)

        # hand the frame to Act 2 — fold the circle away into the new chapter
        self.play(FadeOut(VGroup(circle, radius_line, pivot, rotation_word),
                          scale=0.92),
                  run_time=0.9, rate_func=rate_functions.ease_in_out_cubic)
        self.wait(0.3)

    # ═══════════════════════════════════════════════════════════════ A2 ═══
    def act2_built_from_the_same_stuff(self):
        """Two identical rods. Four identical weights, all starting at the SAME
        neutral radius. Then slide Rod 1's pair INWARD and Rod 2's pair OUTWARD —
        the eye watches the very same furniture relocate. Equal mass, shown."""
        piv1 = UP * self.ROD_Y
        piv2 = DOWN * self.ROD_Y
        self.piv1, self.piv2 = piv1, piv2

        rod1 = make_rod(self.ROD_L).move_to(piv1).set_z_index(3)
        rod2 = make_rod(self.ROD_L).move_to(piv2).set_z_index(3)
        clamp1 = make_pivot().move_to(piv1).set_z_index(6)
        clamp2 = make_pivot().move_to(piv2).set_z_index(6)

        def weight():
            return (make_bowling_ball(self.W_R) if self.USE_BOWLING_WEIGHTS
                    else make_mass_node(self.W_R)).set_z_index(5)

        # all four start at the SAME neutral radius (±R_NEUTRAL) on each rod
        w1a, w1b = weight(), weight()
        w2a, w2b = weight(), weight()
        w1a.move_to(piv1 + RIGHT * self.R_NEUTRAL)
        w1b.move_to(piv1 + LEFT * self.R_NEUTRAL)
        w2a.move_to(piv2 + RIGHT * self.R_NEUTRAL)
        w2b.move_to(piv2 + LEFT * self.R_NEUTRAL)
        self.w1 = VGroup(w1a, w1b)
        self.w2 = VGroup(w2a, w2b)
        self.rod1_grp = VGroup(rod1, clamp1, w1a, w1b)
        self.rod2_grp = VGroup(rod2, clamp2, w2a, w2b)

        lbl1 = Text("ROD 1", font=MONO, font_size=16, color=DUST)
        lbl2 = Text("ROD 2", font=MONO, font_size=16, color=DUST)
        lbl1.next_to(VGroup(rod1), LEFT, buff=0.45).align_to(piv1, UP)
        lbl2.next_to(VGroup(rod2), LEFT, buff=0.45).align_to(piv2, UP)
        lbl1.shift(UP * 0.0); lbl2.shift(UP * 0.0)

        self.play(
            LaggedStart(
                Create(rod1), Create(rod2),
                FadeIn(clamp1, scale=0.6), FadeIn(clamp2, scale=0.6),
                FadeIn(lbl1), FadeIn(lbl2),
                lag_ratio=0.12),
            run_time=1.3, rate_func=rate_functions.ease_out_cubic,
        )
        self.play(
            LaggedStart(*[FadeIn(w, scale=0.85)
                          for w in (w1a, w1b, w2a, w2b)], lag_ratio=0.1),
            run_time=1.0,
        )
        self.rod_labels = VGroup(lbl1, lbl2)
        self.wait(0.6)

        # the unchanged tally: two equal pips per rod -> a total that never moves
        if self.SHOW_MASS_TALLY:
            tally = self._make_tally()
            tally.to_edge(LEFT, buff=0.8).scale(1.4).set_z_index(10)
            self.play(FadeIn(tally, shift=RIGHT * 0.1), run_time=0.7)
            self.tally = tally
            self.wait(0.4)

        guide = Text("same weights - only the position changes", font=SERIF,
                     slant=ITALIC, font_size=24, color=STARLIGHT)
        guide.to_edge(DOWN, buff=0.6).set_z_index(9)
        self.play(FadeIn(guide, shift=UP * 0.08), run_time=0.7)

        # THE SLIDE — simultaneous: Rod 1 inward, Rod 2 outward. Nothing added or
        # removed; the tally above does not so much as flicker.
        # >>> POST (light): a single soft 'set' click as the four nodes seat.
        self.play(
            w1a.animate.move_to(piv1 + RIGHT * self.R_INNER),
            w1b.animate.move_to(piv1 + LEFT * self.R_INNER),
            w2a.animate.move_to(piv2 + RIGHT * self.R_OUTER),
            w2b.animate.move_to(piv2 + LEFT * self.R_OUTER),
            run_time=1.7, rate_func=rate_functions.ease_in_out_cubic,
        )
        self.wait(0.8)
        self.play(FadeOut(guide), run_time=0.5)
        self.wait(0.3)

    # ═══════════════════════════════════════════════════════════════ A3 ═══
    def act3_the_spin_test(self):
        """Pose 'Which is harder to spin?' and HOLD — let the viewer commit. Then
        the SAME curved push on each. The reveal is the response: same torque,
        honestly different I = 2·m·r², so Rod 1 whips and Rod 2 grinds."""
        piv1, piv2 = self.piv1, self.piv2

        question = Text("Which is harder to spin?", font=SERIF, slant=ITALIC,
                        font_size=34, color=STARLIGHT).set_z_index(11)
        question.to_edge(UP, buff=0.7)
        self.play(Write(question), run_time=1.0)

        # ⚠️ THE COMMIT-BEFORE-THE-REVEAL HOLD — both rods dead still. Breathe.
        self.wait(2.6)

        # identical turning effort: the SAME curved arrow copied onto each pivot,
        # same radius, same sweep, same origin -> 'same effort' is unmistakable.
        push_r = 0.78
        push1 = curved_torque_arrow(piv1, push_r, -50 * DEGREES, 210 * DEGREES)
        push2 = curved_torque_arrow(piv2, push_r, -50 * DEGREES, 210 * DEGREES)
        push1.set_z_index(7); push2.set_z_index(7)
        effort = Text("same push", font=MONO, font_size=20, color=C_TORQUE)
        effort.next_to(question, DOWN, buff=0.1)
        self.play(
            LaggedStart(Create(push1), Create(push2), FadeIn(effort),
                        lag_ratio=0.12),
            run_time=1.0,
        )
        self.wait(0.6)

        # precompute equal-time strobe stamps for each rod's weights:
        #   θ_k = Θ·(k/N)²   (ease_in_quad == honest constant angular accel)
        def stamps(pivot, radius, total_angle, base_op=0.14):
            g = VGroup()
            for k in range(1, self.N_STROBE + 1):
                frac = (k / self.N_STROBE) ** 2
                ang = total_angle * frac
                op = base_op + 0.30 * (k / self.N_STROBE)
                for phi0 in (0.0, PI):
                    c = pivot + radius * dir2(phi0 + ang)
                    g.add(ghost_disc(c, self.W_R * 0.92, C_MASS, op))
            return g.set_z_index(2)

        g1 = stamps(piv1, self.R_INNER, self.TH1)
        g2 = stamps(piv2, self.R_OUTER, self.TH2)

        # Rod 1's fast weights also smear a faint swept WEDGE — the literal arc of
        # path covered — so 'dense blur' is honest motion, not decoration.
        blur1 = VGroup()
        for phi0 in (0.0, PI):
            sec = AnnularSector(inner_radius=self.R_INNER - self.W_R,
                                outer_radius=self.R_INNER + self.W_R,
                                angle=self.TH1, start_angle=phi0,
                                stroke_width=0, fill_color=C_MASS,
                                fill_opacity=0.10)
            sec.shift(piv1)
            blur1.add(sec)
        blur1.set_z_index(1)

        # >>> POST: identical 'shove' transient on both; the responses diverge.
        self.play(
            Rotate(self.rod1_grp, angle=self.TH1, about_point=piv1,
                   rate_func=rate_functions.ease_in_quad),
            Rotate(self.rod2_grp, angle=self.TH2, about_point=piv2,
                   rate_func=rate_functions.ease_in_quad),
            FadeIn(blur1),
            LaggedStart(*[FadeIn(s) for s in g1], lag_ratio=0.10),
            LaggedStart(*[FadeIn(s) for s in g2], lag_ratio=0.10),
            run_time=2.2,
        )
        self.play(FadeOut(push1), FadeOut(push2), FadeOut(effort), run_time=0.5)

        # tag the divergent responses (English, MONO — the metadata voice)
        fast = Text("whips up - eager", font=MONO, font_size=18, color=AMBER)
        slow = Text("grinds round - reluctant", font=MONO, font_size=18, color=DUST)
        fast.next_to(self.rod1_grp, RIGHT, buff=0.4).shift(UP * 0.1)
        slow.next_to(self.piv2 + RIGHT * self.R_OUTER, RIGHT, buff=0.4)
        self.play(LaggedStart(FadeIn(fast, shift=RIGHT * 0.08),
                              FadeIn(slow, shift=RIGHT * 0.08), lag_ratio=0.2),
                  run_time=0.9)
        self.wait(1.0)

        self.play(FadeOut(question), run_time=0.5)
        # keep the swept state + ghosts for the flip; stash what to clear
        self._a3_ghosts = VGroup(g1, g2, blur1)
        self._a3_tags = VGroup(fast, slow)
        self.wait(0.4)

    # ═══════════════════════════════════════════════════════════════ A4 ═══
    def act4_same_mass_the_flip(self):
        """The reversal the whole series runs on. mass = mass (dead equal); spin
        difficulty ≠ (not at all). Hold the contradiction. Then resolve it: the
        new variable is r — how far out the mass lives. Plant it for Scene 6."""
        # freeze the spins; clear strobes and tags but keep the rods where they are
        self.play(FadeOut(self._a3_ghosts), FadeOut(self._a3_tags),
                  run_time=0.7)

        # restore both rods to horizontal so the comparison reads clean
        self.play(
            Rotate(self.rod1_grp, angle=-self.TH1, about_point=self.piv1,
                   rate_func=rate_functions.ease_in_out_cubic),
            Rotate(self.rod2_grp, angle=-self.TH2, about_point=self.piv2,
                   rate_func=rate_functions.ease_in_out_cubic),
            run_time=1.0,
        )
        if self.SHOW_MASS_TALLY:
            self.play(FadeOut(self.tally), run_time=0.5)
        self.play(FadeOut(self.rod_labels), run_time=0.4)

        # lift both rods toward centre to free room for the =/≠ ledger on the right
        ledger_anchor = RIGHT * 3.5
        self.play(
            self.rod1_grp.animate.shift(LEFT * 2.6 + DOWN * 0.55),
            self.rod2_grp.animate.shift(LEFT * 2.6 + UP * 0.55),
            run_time=1.1, rate_func=rate_functions.ease_in_out_cubic,
        )
        new_piv1 = self.piv1 + LEFT * 2.6 + DOWN * 0.55
        new_piv2 = self.piv2 + LEFT * 2.6 + UP * 0.55
        self.piv1, self.piv2 = new_piv1, new_piv2

        # ── ROW 1: mass = mass (echoes Scene 3's =/≠ flip framing) ──────────
        def mass_chip(y):
            pips = VGroup(*[Dot(radius=0.07, color=C_MASS) for _ in range(2)])
            pips.arrange(RIGHT, buff=0.16)
            lab = Text("mass", font=SERIF, slant=ITALIC, font_size=22,
                       color=C_MASS)
            chip = VGroup(pips, lab).arrange(RIGHT, buff=0.18).scale(1.4)
            chip.move_to(ledger_anchor + UP * y)
            return chip

        m_top = mass_chip(1.1)
        m_bot = mass_chip(-1.1)
        eq = Text("=", font=SERIF, font_size=46, color=STARLIGHT)
        eq.move_to(ledger_anchor + RIGHT * 0.0)
        # place the two mass chips left/right of the '='
        m_top.next_to(eq, LEFT, buff=0.4)
        m_bot.next_to(eq, RIGHT, buff=0.4)
        eq_row = VGroup(m_top, eq, m_bot).move_to(ledger_anchor + UP * 1.25)

        self.play(
            LaggedStart(FadeIn(m_top, shift=RIGHT * 0.1),
                        FadeIn(m_bot, shift=LEFT * 0.1),
                        lag_ratio=0.15),
            run_time=0.9,
        )
        self.play(Write(eq), run_time=0.5)
        self.play(Indicate(eq, scale_factor=1.18, color=STARLIGHT), run_time=0.7)
        self.wait(0.6)

        # ── ROW 2: stubbornness ≠ stubbornness ──────────────────────────────
        spin_fast = self._mini_spin(self.R_INNER, self.TH1, "spins fast", AMBER).scale(1.4)
        spin_slow = self._mini_spin(self.R_OUTER * 0.62, self.TH2, "spins slow",
                                    DUST).scale(1.4)
        neq = Text("≠", font=SERIF, font_size=46, color=AMBER)
        neq.move_to(ledger_anchor + DOWN * 1.35)
        spin_fast.next_to(neq, LEFT, buff=0.45)
        spin_slow.next_to(neq, RIGHT, buff=0.45)

        self.play(
            LaggedStart(FadeIn(spin_fast, shift=RIGHT * 0.1),
                        FadeIn(spin_slow, shift=LEFT * 0.1), lag_ratio=0.15),
            run_time=0.9,
        )
        self.play(Write(neq), run_time=0.5)
        # >>> POST: the 'wait, what?' sting lands on the ≠.
        self.play(Indicate(neq, scale_factor=1.25, color=AMBER), run_time=0.8)

        contradiction = Text("same mass - different stubbornness", font=SERIF,
                             slant=ITALIC, font_size=24, color=STARLIGHT)
        contradiction.to_edge(DOWN, buff=0.55).set_z_index(9)
        self.play(FadeIn(contradiction, shift=UP * 0.08), run_time=0.8)

        # ⚠️ HOLD the contradiction — this is the 'wait, what?' beat.
        self.wait(1.8)

        # ── RESOLVE: draw the radius pivot→weight on each rod. Short stubby on
        #    Rod 1, long reaching on Rod 2. r (cyan) is the Scene-6 seed. ──────
        self.play(
            FadeOut(VGroup(eq_row, spin_fast, spin_slow, neq, contradiction)),
            run_time=0.8,
        )
        # recentre the two rods for the reveal
        self.play(
            self.rod1_grp.animate.move_to(self.piv1 + RIGHT * 2.6),
            self.rod2_grp.animate.move_to(self.piv2 + RIGHT * 2.6),
            run_time=1.0, rate_func=rate_functions.ease_in_out_cubic,
        )
        self.piv1 = self.piv1 + RIGHT * 2.6
        self.piv2 = self.piv2 + RIGHT * 2.6

        def radius_seg(pivot, radius, lab_txt, width):
            seg = Line(pivot, pivot + RIGHT * radius, stroke_color=C_LEN,
                       stroke_width=width).set_z_index(4)
            t = Text(lab_txt, font=SERIF, slant=ITALIC, font_size=22, color=C_LEN)
            t.next_to(seg, UP, buff=0.12)
            return seg, t

        r1_seg, r1_lab = radius_seg(self.piv1, self.R_INNER, "r", 4.0)
        r2_seg, r2_lab = radius_seg(self.piv2, self.R_OUTER, "r", 5.0)

        self.play(GrowFromPoint(r1_seg, self.piv1),
                  GrowFromPoint(r2_seg, self.piv2),
                  run_time=0.9, rate_func=rate_functions.ease_out_cubic)
        self.play(FadeIn(r1_lab), FadeIn(r2_lab), run_time=0.5)
        self.wait(0.4)

        # pulse the LONG radius — the new variable walks on stage
        self.play(
            r2_seg.animate.set_stroke(width=7.0),
            rate_func=there_and_back, run_time=0.9,
        )
        self.play(Indicate(r2_lab, scale_factor=1.25, color=C_LEN), run_time=0.7)

        click = Text("it's not how much mass - it's how far out it lives",
                     font=SERIF, slant=ITALIC, font_size=24, color=STARLIGHT)
        click.to_edge(DOWN, buff=0.55).set_z_index(9)
        self.play(FadeIn(click, shift=UP * 0.08), run_time=0.8)
        self.wait(1.4)

        # stash the long radius (the held final image / Scene-6 seed)
        self.r2_seg, self.r2_lab = r2_seg, r2_lab
        self._a4_clear = VGroup(r1_seg, r1_lab, click)
        self.wait(0.3)

    # ═══════════════════════════════════════════════════════════════ A5 ═══
    def act5_naming_it(self):
        """Crown the name 'Moment of Inertia' (the way Scene 3 crowned MASS).
        Rescue 'moment' from time: show the clock reading, strike it, replace it
        with leverage — a turning effect. End held on Rod 2's long radius."""
        # tidy to a clean frame; keep the two rods + the long radius
        self.play(FadeOut(self._a4_clear), run_time=0.7)
        self.play(
            self.rod1_grp.animate.set_opacity(0.15),
            self.rod2_grp.animate.set_opacity(0.15),
            self.r2_seg.animate.set_stroke(opacity=0.15),
            self.r2_lab.animate.set_opacity(0.15),
            run_time=0.8,
        )

        # THE CROWN — assemble the name; let it land (TransformMatchingShapes from
        # a small seed word, echoing Scene 3's inertia→MASS magic-move).
        seed = Text("stubbornness", font=SERIF, slant=ITALIC, font_size=30,
                    color=C_MASS).move_to(UP * 0.4)
        self.play(FadeIn(seed, shift=UP * 0.1), run_time=0.6)
        self.wait(0.5)
        title = Text("Moment of Inertia", font=SERIF, font_size=52,
                     color=STARLIGHT).move_to(UP * 0.4).set_z_index(11)
        self.play(ReplacementTransform(seed, title),
                  rate_func=rate_functions.ease_in_out_sine)
        rule = Line(LEFT * 1.6, RIGHT * 1.6, stroke_color=AMBER, stroke_width=1.4)
        rule.next_to(title, DOWN, buff=0.28)
        self.play(Create(rule), run_time=0.6)
        self.wait(1.0)

        # ── RESCUE 'moment' from TIME ────────────────────────────────────────
        self.play(VGroup(title, rule).animate.to_edge(UP, buff=0.7).scale(0.7),
                  run_time=0.9, rate_func=rate_functions.ease_in_out_cubic)

        moment = Text("moment", font=SERIF, slant=ITALIC, font_size=40,
                      color=STARLIGHT).move_to(LEFT * 2.4 + UP * 0.3)
        clock = make_clock(0.46).next_to(moment, RIGHT, buff=0.5)
        

        self.play(FadeIn(moment, shift=UP * 0.08),
                  FadeIn(clock, scale=0.8), run_time=0.7)
        # the clock actually ticks — sell the (wrong) time reading before we kill it
        self.play(Rotate(clock[3], angle=-90 * DEGREES,
                         about_point=clock[4].get_center()),
                  Rotate(clock[2], angle=-30 * DEGREES,
                         about_point=clock[4].get_center()),
                  rate_func=linear)
        self.wait(0.5)

        # STRIKE it — 'moment' has nothing to do with time.
        strike = Line(moment.get_left() + LEFT * 0.1,
                      moment.get_right() + RIGHT * 0.1,
                      stroke_color=C_FORCE, stroke_width=4.0).set_z_index(12)
        # >>> POST (light): a short dismissive 'no' tick on the strike.
        self.play(Create(strike), run_time=0.5)
        self.play(
            VGroup(moment, clock, strike).animate
                .set_opacity(0.0).shift(LEFT * 0.4),
            run_time=0.8, rate_func=rate_functions.ease_in_cubic,
        )
        self.remove(moment, clock, strike)

        # REPLACE with the real meaning — turning effect / leverage.
        real = Text("turning effect — leverage", font=SERIF, slant=ITALIC,
                    font_size=30, color=AMBER).move_to(UP * 1.4)
        self.play(FadeIn(real, shift=UP * 0.08), run_time=0.7)
        self._show_moment_definition()
        self.wait(0.8)
        self.play(FadeOut(real), run_time=0.5)

        # ── FORWARD HOOK — end held on Rod 2's long radius ───────────────────
        self.play(
            FadeOut(VGroup(title, rule)),
            self.rod1_grp.animate.set_opacity(0.0),
            run_time=0.7,
        )
        # bring Rod 2 + its long r back to full presence, centre it, hold
        self.play(
            self.rod2_grp.animate.set_opacity(1.0).move_to(ORIGIN),
            run_time=1.0, rate_func=rate_functions.ease_in_out_cubic,
        )
        # redraw r on the recentred rod (pivot now at ORIGIN)
        self.remove(self.r2_seg, self.r2_lab)
        r_final = Line(ORIGIN, RIGHT * self.R_OUTER, stroke_color=C_LEN,
                       stroke_width=5.0).set_z_index(4)
        r_lab = Text("r", font=SERIF, slant=ITALIC, font_size=26, color=C_LEN)
        r_lab.next_to(r_final, UP, buff=0.14)
        self.play(GrowFromPoint(r_final, ORIGIN), FadeIn(r_lab), run_time=0.8)
        self.play(r_final.animate.set_stroke(width=7.0),
                  rate_func=there_and_back, run_time=0.9)

        hook = Text("but by how much?", font=SERIF, slant=ITALIC, font_size=28,
                    color=STARLIGHT).to_edge(DOWN, buff=0.7).set_z_index(9)
        self.play(FadeIn(hook, shift=UP * 0.08), run_time=0.8)
        # ⚠️ FINAL HOLD on the long r — Scene 6 opens by squaring exactly this.
        self.wait(2.2)

    # ── Act-5 moment-definition variants (director toggle) ─────────────────
    def _show_moment_definition(self):
        if self.MOMENT_DEF == "text":
            return
        if self.MOMENT_DEF == "wrench":
            wrench = make_wrench(2.0).move_to(LEFT * 0.6 + DOWN * 0.4)
            bolt = make_pivot(0.12, AMBER).move_to(
                wrench.handle.get_left() + LEFT * 0.04)
            push = make_push_at(wrench.handle.get_right() + RIGHT * 0.1,
                                UP * 0.55, C_TORQUE)
            self.play(FadeIn(VGroup(wrench, bolt)), run_time=0.6)
            self.play(Create(push), run_time=0.4)
            self.play(Rotate(VGroup(wrench, push), angle=-35 * DEGREES,
                             about_point=bolt.get_center(),
                             rate_func=rate_functions.ease_in_out_cubic),
                      run_time=1.0)
            self.play(FadeOut(VGroup(wrench, bolt, push)), run_time=0.6)
            return

        # default: a seesaw lever — push far from the pivot and it turns
        lever = make_lever(2.1).move_to(DOWN * 0.5)
        fulcrum_pt = lever.bar.get_center()
        far = make_push_at(lever.bar.get_right() + UP * 0.12, DOWN * 0.6, C_TORQUE)
        near_lbl = Text("far force · large turn", font=MONO, font_size=18,
                        color=DUST).next_to(lever, DOWN, buff=0.3)
        self.play(FadeIn(lever), run_time=0.6)
        self.play(Create(far), FadeIn(near_lbl), run_time=0.5)
        # the bar swings under the off-centre push (force × distance)
        self.play(
            Rotate(VGroup(lever.bar, far), angle=-22 * DEGREES,
                   about_point=fulcrum_pt,
                   rate_func=rate_functions.ease_in_out_cubic),
            run_time=1.1,
        )
        self.wait(0.6)
        self.play(FadeOut(VGroup(lever, far, near_lbl)), run_time=0.6)

    # ── small builders ─────────────────────────────────────────────────────
    def _make_tally(self):
        """Two equal pips per rod feeding an unchanged total. Proof-by-count that
        the slide never adds or removes mass."""
        def row(name):
            pips = VGroup(*[Dot(radius=0.06, color=C_MASS) for _ in range(2)])
            pips.arrange(RIGHT, buff=0.14)
            lab = Text(name, font=MONO, font_size=11, color=DUST)
            return VGroup(lab, pips).arrange(RIGHT, buff=0.22)

        r1 = row("ROD 1")
        r2 = row("ROD 2")
        body = VGroup(r1, r2).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        total = Text("TOTAL  4 MASSES", font=MONO, font_size=11, color=STARLIGHT)
        total.next_to(body, DOWN, buff=0.22, aligned_edge=LEFT)
        rule = Line(body.get_left(), body.get_left() + RIGHT * 2.6,
                    stroke_color=DUST, stroke_width=1.0, stroke_opacity=0.5)
        rule.next_to(body, DOWN, buff=0.08, aligned_edge=LEFT)
        plate = SurroundingRectangle(VGroup(body, rule, total), buff=0.22,
                                     color=DUST, stroke_width=1.0)
        plate.set_fill(PANEL, opacity=0.55).set_stroke(opacity=0.4)
        return VGroup(plate, body, rule, total)

    def _mini_spin(self, radius, angle, caption, color):
        """A tiny rod-glyph showing how far its weights sweep under one push —
        a big arc vs a small arc, side by side, for the ≠ row."""
        scale = 0.7
        r = radius * scale
        bar = Line(LEFT * r, RIGHT * r, stroke_color=DUST, stroke_width=3.0)
        nodes = VGroup(Dot(radius=0.06, color=C_MASS).move_to(RIGHT * r),
                       Dot(radius=0.06, color=C_MASS).move_to(LEFT * r))
        arc = Arc(radius=r, start_angle=0, angle=angle, stroke_color=color,
                  stroke_width=3.0)
        glyph = VGroup(arc, bar, nodes)
        cap = Text(caption, font=MONO, font_size=11, color=color)
        cap.next_to(glyph, DOWN, buff=0.2)
        return VGroup(glyph, cap)


def make_push_at(point, vec, color=C_TORQUE, width=5.0):
    """A short straight force arrow from `point` along `vec` — used by the Act-5
    lever / wrench definitions."""
    end = np.array(point) + np.array(vec)
    shaft = Line(point, end, stroke_color=color, stroke_width=width)
    tip = Triangle().scale(0.07).set_fill(color, opacity=1.0).set_stroke(width=0)
    d = np.array(vec, dtype=float)
    tip.rotate(math.atan2(d[1], d[0]) - 90 * DEGREES)
    tip.move_to(end)
    return VGroup(shaft, tip)