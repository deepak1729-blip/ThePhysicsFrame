from manim import *
import numpy as np
import math

# ─────────────────────────────────────────────────────────────────────────
#  OBSERVATORY PALETTE  (verbatim from the series design system)
# ─────────────────────────────────────────────────────────────────────────
VOID      = "#0A0C10"   # base background
PANEL     = "#11151C"   # lifted surfaces
STARLIGHT = "#E8E6DF"   # primary text / the ball-as-character
DUST      = "#9A958C"   # secondary · metadata · the dimmed state
AMBER     = "#D98A3D"   # primary accent · focus (amber follows the eye)
CYAN      = "#5B8FB0"   # secondary · sparing

# quantity pigments — each quantity keeps its colour across the whole series
C_MASS    = "#B89A86"   # MASS / the property of the object (its stubbornness)
C_FORCE   = "#E06450"   # FORCE — the push I APPLY
C_GRAV    = "#8B8FF2"   # GRAVITY / WEIGHT — the external down-pull
C_VEL     = "#57C08A"   # VELOCITY
C_GROUND  = "#7F8A99"   # ground / reference axis

SERIF = "Spectral"      # ideas; italic is the channel's speaking voice
MONO  = "Space Mono"    # labels & metadata only

config.background_color = VOID
RNG = np.random.default_rng(4)   # deterministic -> stable render cache


# ═══════════════════════════════════════════════════════════════════════════
#  CONSTRUCTION VOCABULARY  (reused verbatim from Scenes 1–3, then extended)
# ═══════════════════════════════════════════════════════════════════════════
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
    """Dense, dark sphere with three finger-holes. Reads HEAVY: near-Void fill,
    a Mass-pigment rim, a tight STARLIGHT specular. Exposes `.disc`, `.radius`."""
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
    # three finger-holes, clustered up-left like a real grip
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

def make_push_arrow(length=0.92, color=C_FORCE):
    """THE push arrow — built once, copied forever. Its exact size IS the
    experiment, so it is fixed-geometry (no Arrow auto-scaling). (Scene 3.)"""
    shaft = Line(ORIGIN, RIGHT * length, stroke_color=color, stroke_width=6.0)
    tip = Triangle().scale(0.085)
    tip.set_fill(color, opacity=1.0).set_stroke(width=0)
    tip.rotate(-90 * DEGREES)                     # point +x
    tip.move_to(shaft.get_end())
    g = VGroup(shaft, tip)
    g.tail = shaft.get_start
    g.head = shaft.get_end
    return g


# ─────────────────────────── new vocabulary for Scene 4 ───────────────────
def v_arrow_down(length, top_point, color=C_GRAV, width=6.0):
    """A fixed-geometry vertical arrow pointing DOWN from `top_point`.
    Anchored at the top so it can be retracted to zero (weight → 0 in space)."""
    length = max(1e-4, length)
    shaft = Line(top_point, top_point + DOWN * length,
                 stroke_color=color, stroke_width=width)
    tip = Triangle().scale(0.085)
    tip.set_fill(color, opacity=1.0).set_stroke(width=0)
    tip.rotate(180 * DEGREES)                      # apex down
    tip.move_to(shaft.get_end())
    g = VGroup(shaft, tip)
    g.top_point = np.array(top_point, dtype=float)
    g.acolor = color
    g.awidth = width
    return g


def set_v_arrow(arrow, length):
    """Rebuild a v_arrow_down to a new length, anchored at its stored top.
    Below a floor length the tip is dropped so it reads as 'gone', not a stub."""
    top = arrow.top_point
    length = max(0.0, length)
    if length < 0.07:
        shaft = Line(top, top + DOWN * 0.0001,
                     stroke_color=arrow.acolor, stroke_width=arrow.awidth)
        shaft.set_opacity(0.0)
        arrow.become(VGroup(shaft))
        return
    shaft = Line(top, top + DOWN * length,
                 stroke_color=arrow.acolor, stroke_width=arrow.awidth)
    tip = Triangle().scale(0.085)
    tip.set_fill(arrow.acolor, opacity=1.0).set_stroke(width=0)
    tip.rotate(180 * DEGREES)
    tip.move_to(shaft.get_end())
    arrow.become(VGroup(shaft, tip))


def right_angle_marker(vertex, size=0.20, color=DUST, width=1.6, opacity=0.8):
    """Small square corner sitting between the +x (MASS) and -y (WEIGHT) arms —
    the geometric thesis of the scene: two jobs, two directions, 90° apart."""
    a = vertex + RIGHT * size
    b = vertex + DOWN * size
    c = vertex + RIGHT * size + DOWN * size
    l1 = Line(a, c, stroke_color=color, stroke_width=width, stroke_opacity=opacity)
    l2 = Line(b, c, stroke_color=color, stroke_width=width, stroke_opacity=opacity)
    return VGroup(l1, l2)


def make_finger(color=STARLIGHT):
    """Minimal flick glyph — a forearm rod + soft knuckle (Scene 1/3 vocabulary)."""
    arm = RoundedRectangle(width=1.2, height=0.18, corner_radius=0.09,
                           stroke_width=0, fill_color=DUST, fill_opacity=0.9)
    knuckle = RoundedRectangle(width=0.24, height=0.42, corner_radius=0.11,
                               stroke_width=0, fill_color=color, fill_opacity=0.92)
    knuckle.next_to(arm, RIGHT, buff=-0.02)
    return VGroup(arm, knuckle)


def ghost_disc(center, radius, color=C_MASS, opacity=0.34):
    """One equal-time strobe stamp of the ball. A row of these encodes speed by
    SPACING — the Scenes 1–2 grammar, reused verbatim in the Act-4 crux."""
    d = Circle(radius=radius, stroke_color=color, stroke_width=2.0,
               stroke_opacity=opacity, fill_color=color, fill_opacity=0.05)
    d.move_to(center)
    return d


def starfield(n=120, x_range=(-7.4, 7.4), y_range=(-4.3, 4.3), seed=4):
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
class Scene4_MassVsWeight(MovingCameraScene):

    # ── director toggles (each is a one-line flip) ────────────────────────
    USE_ASTRONAUT_OVERLAY = True
    CRUX_SPLIT_SCREEN     = True
    USE_MYSTERY_TOKEN     = True
    SHOW_EQUATION_WHISPER = True

    # ── locked geometry ───────────────────────────────────────────────────
    GROUND_Y = -2.40
    BALL_R   = 0.62
    BALL_X   = -1.05                       # Acts 1–2 station (room to the right)
    BALL_Y   = GROUND_Y + BALL_R           # ball rests ON the ground line

    # ── honest physics constants (everything derives from these) ──────────
    M_BALL  = 6.00                         # kg — carried from Scene 3, never changes
    G_EARTH = 9.81                         # m/s²
    G_SPACE = 0.00                         # m/s²
    W_EARTH = M_BALL * G_EARTH             # ≈ 58.9 N  (the honest weight)
    PUSH_SPAN = 3.05                       # scene-units travelled under one push
    N_STROBE  = 6                          # equal-time strobe samples

    def construct(self):
        self.camera.frame.save_state()

        # Frame marks pinned to the camera frame via updater (Scene 1–3 pattern;
        # the constant-screen-size variant from Scene 3 — survives every zoom).
        self.frame_marks = VGroup(*[corner_L(o, opacity=0.0)
                                    for o in (UL, UR, DL, DR)])
        self._pin_frame_marks()

        self.act1_heavy_is_a_lie()
        self.act2_mass_is_how_hard()
        self.act3_take_it_to_space()
        self.act4_same_push_same_stubbornness()
        self.act5_weight_moved_mass_didnt()

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

    # convenience: keep the inner glow centred on its ball

    # ═══════════════════════════════════════════════════════════════ A1 ═══
    def act1_heavy_is_a_lie(self):
        """Re-summon the Scene-3 ball onto the ground. 'HEAVY' instinct attaches
        to the ball — then we PEEL it off and re-attach it to the gravity arrow.
        Heaviness was never the ball's; it's something being done TO it."""
        # the dashed reference line, now reading as Earth ground
        ground = DashedLine(LEFT * 6.6 + UP * self.GROUND_Y,
                            RIGHT * 6.6 + UP * self.GROUND_Y,
                            dash_length=0.18, dashed_ratio=0.55, color=C_GROUND,
                            stroke_width=2.0, stroke_opacity=0.0).set_z_index(-1)
        self.ground = ground

        # MAGIC-MOVE IN: the tagged bowling ball arrives from Scene 3's final
        # frame (slightly high & large, like its scaled Scene-3 exit) and settles.
        ball = make_bowling_ball(self.BALL_R).set_z_index(5)
        ball.move_to(RIGHT * self.BALL_X + UP * (self.BALL_Y + 0.9)).scale(1.12)
        self.ball = ball

        self.add(ground, self.frame_marks)
        self.frame_marks.set_opacity(0.45)
        # >>> POST: a soft low settle as the ball arrives and the ground draws in
        self.play(
            ball.animate.scale(1 / 1.12).move_to(RIGHT * self.BALL_X
                                                 + UP * self.BALL_Y),
            ground.animate.set_stroke(opacity=0.85),
            run_time=1.2, rate_func=rate_functions.ease_out_cubic,
        )
        self.wait(0.6)

        # 1) the instinct word, attached to the ball
        heavy = Text("HEAVY", font=SERIF, weight=BOLD, font_size=44,
                     color=STARLIGHT).next_to(ball, UP, buff=0.5).set_z_index(9)
        self.play(FadeIn(heavy, shift=DOWN * 0.12), run_time=0.7,
                  rate_func=rate_functions.ease_out_cubic)
        self.wait(0.5)

        # 2) where heaviness ACTUALLY lives: a down-arrow (gravity) grows out of
        #    the ball toward the ground, labelled WEIGHT. Anchored at the centre
        #    of mass so it reads down THROUGH the ball to the contact point — its
        #    cool pigment vs the warm internal glow is the external/internal tell.
        top = ball.get_center()
        wlen = self.BALL_R                              # centre → ground contact
        weight = v_arrow_down(0.0001, top, color=C_GRAV).set_z_index(7)
        self.weight_arrow = weight
        self.weight_len_earth = wlen
        self.add(weight)
        tlen = ValueTracker(0.0)
        weight.add_updater(lambda m: set_v_arrow(m, tlen.get_value()))
        self.play(tlen.animate.set_value(wlen), run_time=0.9,
                  rate_func=rate_functions.ease_out_cubic)
        weight.clear_updaters()
        set_v_arrow(weight, wlen)

        wlabel = Text("WEIGHT", font=MONO, font_size=18, color=C_GRAV)
        wlabel.next_to(weight, RIGHT, buff=0.22).set_z_index(9)
        self.play(FadeIn(wlabel, shift=RIGHT * 0.1), run_time=0.5)
        self.wait(0.7)

        # 3) THE PEEL. 'HEAVY' is not the ball's. Slide it down and re-attach it
        #    to the ARROW — heaviness is a property of gravity, not the object.
        #    >>> POST (light): a tiny 'de-tach' tick the instant it peels.
        heavy_target = Text("HEAVY", font=SERIF, slant=ITALIC, weight=NORMAL,
                            font_size=22, color=C_GRAV)
        heavy_target.next_to(wlabel, DOWN, buff=0.14).align_to(wlabel, LEFT)
        self.play(
            ReplacementTransform(heavy, heavy_target),
            run_time=1.1, rate_func=rate_functions.ease_in_out_cubic,
        )
        self.weight_group = VGroup(weight, wlabel, heavy_target)

        # 4) what's LEFT: a naked ball — just the shape and its inner glow.
        #    Pulse the glow once so the eye registers the internal thing that
        #    the external arrow never touched.
        self.wait(1.0)

    # ═══════════════════════════════════════════════════════════════ A2 ═══
    def act2_mass_is_how_hard(self):
        """Rotate the question 90°. A horizontal push shoves the ball; it barely
        budges. THAT resistance is MASS — and the inner glow finally gets named."""
        ball = self.ball

        # 1) introduce the HORIZONTAL axis: a faint guide through the ball centre
        haxis = DashedLine(ball.get_center() + LEFT * 4.4,
                           ball.get_center() + RIGHT * 4.6,
                           dash_length=0.12, dashed_ratio=0.5, color=DUST,
                           stroke_width=1.4, stroke_opacity=0.0).set_z_index(2)
        self.play(haxis.animate.set_stroke(opacity=0.35), run_time=0.7,
                  rate_func=rate_functions.ease_in_out_sine)

        # 2) the flick + recoil (Scene 3 grammar). A finger drives in from the
        #    left; the ball resists with a long, heavy ease-in and barely moves;
        #    the finger recoils. Sluggishness IS the point.
        finger = make_finger().set_z_index(8)
        finger.next_to(ball, LEFT, buff=0.02).shift(LEFT * 3.0)
        self.add(finger)
        self.play(finger.animate.shift(RIGHT * 3.0), run_time=0.7,
                  rate_func=rate_functions.ease_out_cubic)

        nudge = 0.30                                   # ball barely budges
        ball_grp = VGroup(ball)
        self.play(
            finger.animate.shift(RIGHT * nudge),
            ball_grp.animate.shift(RIGHT * nudge),
            self.weight_group.animate.shift(RIGHT * nudge),  # gravity rides along
            run_time=1.2, rate_func=rate_functions.ease_in_cubic,   # heavy start
        )
        # the arrow moved with the ball — re-anchor its stored top for later edits
        self.weight_arrow.top_point = ball.get_center()
        # >>> POST (light): a dull 'thud', not a snap — the push barely landed.
        self.play(finger.animate.shift(LEFT * 2.6), run_time=0.55,
                  rate_func=rate_functions.ease_in_out_cubic)
        self.remove(finger)

        # the horizontal resistance arrow + its name: MASS (mass pigment)
        push = make_push_arrow(length=0.95, color=C_FORCE).set_z_index(7)
        push.next_to(ball, LEFT, buff=0.14)
        self.play(GrowFromPoint(push, push.tail()), run_time=0.6,
                  rate_func=rate_functions.ease_out_cubic)
        self.push_arrow = push

        mass_word = Text("MASS", font=SERIF, weight=BOLD, font_size=40,
                         color=C_MASS).set_z_index(9)
        mass_word.next_to(ball, UP, buff=0.55)
        self.play(Write(mass_word), run_time=0.8)
        self.mass_word = mass_word
        self.wait(0.6)

        # 3) BOTH arrows coexist at a right angle — two jobs, two directions.
        ram = right_angle_marker(ball.get_center(), size=0.22, color=DUST,
                                 opacity=0.85).set_z_index(7)
        self.play(Create(ram), run_time=0.6)
        self.right_angle = ram
        self.wait(0.8)

        # 4) NAME THE GLOW. A thin connector runs from the inner core to the word
        #    MASS — inertia, finally given its name.
        connector = Line(mass_word.get_bottom() + DOWN * 0.04,
                         stroke_color=C_MASS, stroke_width=1.6,
                         stroke_opacity=0.0).set_z_index(6)
        self.add(connector)
        self.play(connector.animate.set_stroke(opacity=0.7), run_time=0.7,
                  rate_func=rate_functions.ease_in_out_sine)

        caption = Text("Mass = how hard to move or stop", font=SERIF,
                       slant=ITALIC, font_size=26, color=STARLIGHT)
        caption.to_edge(DOWN, buff=0.55).set_z_index(9)
        self.play(FadeIn(caption, shift=UP * 0.1), run_time=0.8)
        self.wait(1.3)

        # tidy the horizontal scaffolding; keep ball, glow, weight
        self.play(
            FadeOut(connector), FadeOut(caption), FadeOut(haxis),
            FadeOut(self.push_arrow), FadeOut(self.right_angle),
            FadeOut(self.mass_word),
            run_time=0.8,
        )
        self.wait(0.3)

    # ═══════════════════════════════════════════════════════════════ A3 ═══
    def act3_take_it_to_space(self):
        """Lift the ball off the ground into a starfield. Gravity leaves: the
        WEIGHT arrow shrinks to zero, a scale ticks to 0. The inner glow must
        NOT change. Optional: a live ISS microgravity inset."""
        ball = self.ball
        ball_grp = VGroup(ball)

        # park a small spring-scale readout where weight lives (W = m·g, honest)
        scale_panel = self._make_scale_panel(self.W_EARTH)
        scale_panel.next_to(self.weight_group, RIGHT, buff=0.5)
        scale_panel.align_to(self.weight_arrow, UP)
        self.play(FadeIn(scale_panel, shift=RIGHT * 0.1), run_time=0.6)
        self.scale_panel = scale_panel
        self.wait(0.5)

        # camera eases back; ball rises; the ground slides out from under it and
        # vanishes (no floor in space — reinforce the absence). Stars fade in.
        stars = starfield(n=130, seed=4).set_z_index(-2)
        stars.set_opacity(0.0)
        self.add(stars)

        float_center = UP * 0.35 + LEFT * 1.05
        # the exact translation the ball undergoes — apply the SAME vector to the
        # weight arrow and the scale so they ride along locked, no drift.
        rise = float_center - ball.get_center()
        self.play(
            self.camera.frame.animate.scale(1.12),
            ball_grp.animate.shift(rise),
            self.weight_group.animate.shift(rise),
            self.scale_panel.animate.shift(rise),
            self.ground.animate.shift(DOWN * 3.0).set_stroke(opacity=0.0),
            stars.animate.set_opacity(1.0),
            run_time=1.6, rate_func=rate_functions.ease_in_out_cubic,
        )
        self.remove(self.ground)

        # re-anchor the weight arrow's top to the ball CENTRE (as in Act 1), then
        # RETRACT it to zero as gravity leaves; the scale ticks to 0 in lockstep.
        self.weight_arrow.top_point = ball.get_center()
        set_v_arrow(self.weight_arrow, self.weight_len_earth)
        tlen = ValueTracker(self.weight_len_earth)
        wval = ValueTracker(self.W_EARTH)
        self.weight_arrow.add_updater(lambda m: set_v_arrow(m, tlen.get_value()))
        self._bind_scale(self.scale_panel, wval)

        # >>> POST: a descending tone as weight bleeds to nothing.
        self.play(
            tlen.animate.set_value(0.0),
            wval.animate.set_value(0.0),
            self.weight_group[1].animate.set_opacity(0.25),   # WEIGHT label dims
            self.weight_group[2].animate.set_opacity(0.25),   # HEAVY tag dims
            run_time=1.5, rate_func=rate_functions.ease_in_out_cubic,
        )
        self.weight_arrow.clear_updaters()
        self.scale_panel.num.clear_updaters()
        self.wait(0.4)

        # the glow did NOT change. Make the eye catch it: external thing gone,
        # internal thing identical. A single calm pulse, same size.

        # buoyant idle drift — slow, weightless
        self.play(ball_grp.animate.shift(UP * 0.12 + RIGHT * 0.06),
                  run_time=1.4, rate_func=rate_functions.ease_in_out_sine)
        self.play(ball_grp.animate.shift(DOWN * 0.10 + LEFT * 0.04),
                  run_time=1.4, rate_func=rate_functions.ease_in_out_sine)

        # OPTIONAL live-footage inset — the astronaut nudging a massive module.
        # safe_image degrades to a framed placeholder if the still isn't present.
        if self.USE_ASTRONAUT_OVERLAY:
            inset = safe_image("s4_astronaut_iss.png", target_width=3.4,
                               fallback_label="ISS · MICROGRAVITY")
            inset.to_corner(DR, buff=0.7).set_z_index(12)
            cap = Text("massive — yet it floats, and still shoves back",
                       font=MONO, font_size=12, color=DUST)
            cap.next_to(inset, UP, buff=0.14).align_to(inset, RIGHT)
            self.play(FadeIn(inset, shift=UP * 0.1), FadeIn(cap), run_time=0.7)
            self.wait(1.6)
            self.play(FadeOut(inset), FadeOut(cap), run_time=0.6)

        # set the trap (English on-screen): weight's gone — is it still stubborn?
        trap = Text("weight is gone — so is it still stubborn?", font=SERIF,
                    slant=ITALIC, font_size=26, color=STARLIGHT)
        trap.to_edge(UP, buff=0.7).set_z_index(10)
        self.play(Write(trap), run_time=1.0)
        self.wait(1.0)
        self.trap_line = trap

    # ═══════════════════════════════════════════════════════════════ A4 ═══
    def act4_same_push_same_stubbornness(self):
        """THE CRUX. Earth | Space, same ball, same glow. Identical push → the
        strobe spacing matches exactly. Then slide Space's trail onto Earth's so
        they OVERLAP — the only difference left is the vertical arrow. Hold."""
        ball = self.ball

        # clear Act-3 furniture; reset camera to a clean stable frame
        self.play(
            FadeOut(self.trap_line),
            FadeOut(self.scale_panel),
            FadeOut(self.weight_group),
            self.camera.frame.animate.restore(),
            run_time=0.9, rate_func=rate_functions.ease_in_out_cubic,
        )
        # fold the original ball/glow away — Act 4 builds a fresh matched pair

        self.play(FadeOut(VGroup(ball), scale=0.85), run_time=0.5)

        if not self.CRUX_SPLIT_SCREEN:
            return self._act4_ghost_overlay()

        # ── split-screen staging ───────────────────────────────────────────
        y = -0.55
        divider = DashedLine(UP * 3.4, DOWN * 3.4, dash_length=0.14,
                             dashed_ratio=0.5, color=DUST, stroke_width=1.2,
                             stroke_opacity=0.0)
        # EARTH side (left): a short ground tick + a long down weight arrow
        eground = DashedLine(LEFT * 6.3 + UP * (y - self.BALL_R - 0.25),
                             LEFT * 0.5 + UP * (y - self.BALL_R - 0.25),
                             dash_length=0.16, dashed_ratio=0.55, color=C_GROUND,
                             stroke_width=2.0, stroke_opacity=0.0).set_z_index(-1)
        # SPACE side (right): stars only
        sstars = starfield(n=70, x_range=(0.6, 7.2), y_range=(-3.6, 3.6),
                           seed=7).set_z_index(-2)
        sstars.set_opacity(0.0)

        x0_E, x0_S = -6.0, 0.95
        eball = make_bowling_ball(self.BALL_R).set_z_index(5)
        sball = make_bowling_ball(self.BALL_R).set_z_index(5)
        for b, x in ((eball, x0_E), (sball, x0_S)):
            b.move_to(RIGHT * x + UP * y)

        e_lab = Text("ON EARTH", font=MONO, font_size=15, color=C_GRAV)
        s_lab = Text("IN SPACE", font=MONO, font_size=15, color=CYAN)
        e_lab.move_to(LEFT * 3.4 + UP * 3.0)
        s_lab.move_to(RIGHT * 3.6 + UP * 3.0)

        self.add(eground, sstars, divider)
        self.play(
            divider.animate.set_stroke(opacity=0.3),
            eground.animate.set_stroke(opacity=0.8),
            sstars.animate.set_opacity(1.0),
            LaggedStart(FadeIn(e_lab, shift=DOWN * 0.1),
                        FadeIn(s_lab, shift=DOWN * 0.1), lag_ratio=0.2),
            run_time=1.0, rate_func=rate_functions.ease_in_out_sine,
        )
        self.play(
            LaggedStart(FadeIn(eball, scale=0.9),
                        FadeIn(sball, scale=0.9),
                        lag_ratio=0.08),
            run_time=0.9,
        )

        # Earth's weight arrow (long, down) anchored at ball CENTRE. Space has
        # NONE — that single missing arrow is the only difference in the frame.
        e_top = eball.get_center()
        e_weight = v_arrow_down(self.weight_len_earth + 0.35, e_top,
                                color=C_GRAV).set_z_index(7)
        self.play(GrowFromPoint(e_weight, e_top), run_time=0.6)
        self.wait(0.6)

        # IDENTICAL push impulse to both, same magnitude, same start time.
        e_push = make_push_arrow(0.95, C_FORCE).next_to(eball, LEFT, buff=0.14)
        s_push = make_push_arrow(0.95, C_FORCE).next_to(sball, LEFT, buff=0.14)
        e_push.set_z_index(7); s_push.set_z_index(7)
        self.play(GrowFromPoint(e_push, e_push.tail()),
                  GrowFromPoint(s_push, s_push.tail()),
                  run_time=0.5)
        impulse = Text("same push", font=MONO, font_size=15, color=C_FORCE)
        impulse.to_edge(UP, buff=0.7)
        self.play(FadeIn(impulse), run_time=0.4)
        self.wait(0.4)

        # ── the honest run: x = x0 + span·alpha², alpha = ease_in_quad(t/T).
        #    Equal-time strobe stamps → quadratic spacing → identical on both. ──
        span = self.PUSH_SPAN
        rt = 2.2
        # precompute equal-time stamp positions (quadratic spacing)
        e_ghosts, s_ghosts = VGroup(), VGroup()
        for k in range(1, self.N_STROBE + 1):
            frac = (k / self.N_STROBE) ** 2
            e_ghosts.add(ghost_disc(RIGHT * (x0_E + span * frac) + UP * y,
                                    self.BALL_R, C_MASS,
                                    opacity=0.16 + 0.30 * (k / self.N_STROBE)))
            s_ghosts.add(ghost_disc(RIGHT * (x0_S + span * frac) + UP * y,
                                    self.BALL_R, C_MASS,
                                    opacity=0.16 + 0.30 * (k / self.N_STROBE)))
        e_ghosts.set_z_index(3); s_ghosts.set_z_index(3)

        eball_grp = VGroup(eball)
        sball_grp = VGroup(sball)
        # push arrows AND Earth's gravity arrow ride along with their ball
        self.play(
            eball_grp.animate.shift(RIGHT * span),
            sball_grp.animate.shift(RIGHT * span),
            e_weight.animate.shift(RIGHT * span),
            e_push.animate.shift(RIGHT * span),
            s_push.animate.shift(RIGHT * span),
            LaggedStart(*[FadeIn(gg) for gg in e_ghosts],
                        lag_ratio=0.14),
            LaggedStart(*[FadeIn(gg) for gg in s_ghosts],
                        lag_ratio=0.14),
            run_time=rt, rate_func=rate_functions.ease_in_quad,   # honest ½at²
        )
        self.play(FadeOut(e_push), FadeOut(s_push), FadeOut(impulse),
                  run_time=0.4)
        self.wait(0.6)

        # ── THE OVERLAP: slide Space's trail + ball left so every stamp lands
        #    exactly on its Earth twin. Identical spacing → perfect superposition.
        offset = (x0_E - x0_S)
        same_speed = Text("same spacing  =  same speed", font=MONO, font_size=14,
                          color=DUST).to_edge(UP, buff=0.7)
        self.play(FadeIn(same_speed), run_time=0.4)
        self.play(
            sball_grp.animate.shift(RIGHT * offset),
            s_ghosts.animate.shift(RIGHT * offset),
            FadeOut(sstars), FadeOut(s_lab), FadeOut(divider),
            run_time=1.5, rate_func=rate_functions.ease_in_out_cubic,
        )
        # now both balls + both strobes coincide; the ONLY difference is e_weight
        self.wait(0.4)

        if self.SHOW_EQUATION_WHISPER:
            whisper = VGroup(
                Text("same F  →  same a", font=MONO, font_size=15, color=DUST),
                Text("W = m·g   differs only because g differs", font=MONO,
                     font_size=13, color=DUST),
            ).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
            whisper.to_corner(DL, buff=0.7).set_opacity(0.0)
            self.add(whisper)
            self.play(whisper.animate.set_opacity(0.7), run_time=0.6)

        # >>> POST (light): freeze on the overlapping trails, tiny English pop.
        same_mass = Text("same mass", font=SERIF, slant=ITALIC, font_size=30,
                         color=C_MASS).move_to(UP * 1.7).set_z_index(11)
        self.play(FadeIn(same_mass, shift=UP * 0.08), run_time=0.7)

        # ⚠️ THE HOLD — gravity deleted, ball exactly as hard to push. Breathe.
        self.wait(2.6)

        # stash references Act 5 needs, then clear the crux scaffolding
        self.crux_keep = VGroup(eball, e_weight)
        self._a4_clear = VGroup(e_ghosts, s_ghosts, sball, e_lab,
                                same_speed, same_mass, eground)
        if self.SHOW_EQUATION_WHISPER:
            self._a4_clear.add(whisper)

    def _act4_ghost_overlay(self):
        """Alternate Act-4 staging (CRUX_SPLIT_SCREEN = False): a single ball
        with its Earth-self summoned as a ghost beside it, pushed in lockstep.
        Denser but more on-grammar. Kept runnable as a drop-in."""
        y = -0.55
        x0 = -3.0
        span = self.PUSH_SPAN
        stars = starfield(n=110, seed=9).set_z_index(-2)
        self.add(stars)

        real = make_bowling_ball(self.BALL_R).set_z_index(5)
        real.move_to(RIGHT * x0 + UP * y)
        ghost = make_bowling_ball(self.BALL_R).set_z_index(4).set_opacity(0.4)
        ghost.move_to(real.get_center())
        e_top = ghost.get_center()
        e_weight = v_arrow_down(self.weight_len_earth + 0.35, e_top,
                                color=C_GRAV).set_z_index(3)

        self.play(LaggedStart(FadeIn(real), lag_ratio=0.1),
                  run_time=0.8)
        self.play(FadeIn(ghost), GrowFromPoint(e_weight, e_top),
                  run_time=0.6)

        ghosts = VGroup()
        for k in range(1, self.N_STROBE + 1):
            frac = (k / self.N_STROBE) ** 2
            ghosts.add(ghost_disc(RIGHT * (x0 + span * frac) + UP * y,
                                  self.BALL_R, C_MASS,
                                  opacity=0.16 + 0.30 * (k / self.N_STROBE)))
        ghosts.set_z_index(3)
        self.play(
            VGroup(real, ghost, e_weight).animate.shift(RIGHT * span),
            LaggedStart(*[FadeIn(gg) for gg in ghosts],
                        lag_ratio=0.14),
            run_time=2.2, rate_func=rate_functions.ease_in_quad,
        )
        same_mass = Text("same mass", font=SERIF, slant=ITALIC, font_size=30,
                         color=C_MASS).move_to(UP * 1.7)
        self.play(FadeIn(same_mass, shift=UP * 0.08), run_time=0.7)
        self.wait(2.6)
        self.crux_keep = VGroup(real, e_weight)
        self._a4_clear = VGroup(ghost, ghosts, same_mass, stars)

    # ═══════════════════════════════════════════════════════════════ A5 ═══
    def act5_weight_moved_mass_didnt(self):
        """Resolve to a two-row ledger: WEIGHT collapses Earth→0, MASS refuses to
        move. Then dim gravity to nothing, leave only the glow. Stash the seed."""
        # collapse the crux into a single tagged ball, centre-left
        ball = self.crux_keep[0]
        e_weight = self.crux_keep[1]
        self.play(FadeOut(self._a4_clear), run_time=0.7)

        ball_grp = VGroup(ball, e_weight)
        self.play(ball_grp.animate.move_to(LEFT * 3.6 + UP * 0.2),
                  run_time=1.0, rate_func=rate_functions.ease_in_out_cubic)
        # re-seat the weight arrow under the relocated ball (centre-anchored,
        # same length it had in the crux so there's no visible jump)
        e_weight.top_point = ball.get_center()
        set_v_arrow(e_weight, self.weight_len_earth + 0.35)

        # ── the ledger (English) ──────────────────────────────────────────
        head = Text("WEIGHT  vs  MASS", font=MONO, font_size=16, color=DUST)
        head.move_to(RIGHT * 2.2 + UP * 2.5)

        def row(name, name_col, earth_txt, space_txt, y):
            label = Text(name, font=SERIF, weight=BOLD, font_size=26,
                         color=name_col)
            label.move_to(RIGHT * 0.5 + UP * y)
            e_v = Text(earth_txt, font=MONO, font_size=22, color=STARLIGHT)
            s_v = Text(space_txt, font=MONO, font_size=22, color=STARLIGHT)
            e_v.move_to(RIGHT * 3.0 + UP * y)
            s_v.move_to(RIGHT * 5.3 + UP * y)
            return label, e_v, s_v

        col_e = Text("EARTH", font=MONO, font_size=12, color=DUST).move_to(RIGHT * 3.0 + UP * 1.55)
        col_s = Text("SPACE", font=MONO, font_size=12, color=DUST).move_to(RIGHT * 5.3 + UP * 1.55)

        w_lab, w_e, w_s = row("WEIGHT", C_GRAV, "58.9 N", "58.9 N", 0.7)
        m_lab, m_e, m_s = row("MASS", C_MASS, "6.00 kg", "6.00 kg", -0.6)

        self.play(
            LaggedStart(FadeIn(head), FadeIn(col_e), FadeIn(col_s),
                        FadeIn(w_lab), FadeIn(w_e), FadeIn(w_s),
                        FadeIn(m_lab), FadeIn(m_e), FadeIn(m_s),
                        lag_ratio=0.08),
            run_time=1.4,
        )
        self.wait(0.6)

        # WEIGHT collapses: Earth large → Space 0 (number shrinks away to 0.0 N)
        w_s_zero = Text("0.0 N", font=MONO, font_size=22, color=DUST)
        w_s_zero.move_to(w_s.get_center())
        # >>> POST: the same descending tone as the weight column drops out.
        self.play(
            ReplacementTransform(w_s, w_s_zero),
            w_e.animate.set_color(C_GRAV),       # Earth weight stays large & lit
            run_time=1.1, rate_func=rate_functions.ease_in_out_cubic,
        )
        self.wait(0.5)

        # MASS refuses to move: identical across both — a tiny resist-jitter as
        # if something tried to nudge it and failed. (Inertia, visibly.)
        self.play(
            m_s.animate.set_color(C_MASS), m_e.animate.set_color(C_MASS),
            run_time=0.5,
        )
        for dx in (0.07, -0.07, 0.04, -0.04, 0.0):
            self.play(m_s.animate.shift(RIGHT * dx), run_time=0.08,
                      rate_func=linear)
        self.play(Indicate(VGroup(m_e, m_s), scale_factor=1.08, color=C_MASS),
                  run_time=0.7)
        self.wait(0.9)

        # mass is not about gravity — dim the gravity arrow to nothing, leave
        # only the inner glow pulsing. Inertia is what survived the trip.
        line = Text("mass is not about gravity — it's about inertia",
                    font=SERIF, slant=ITALIC, font_size=26, color=STARLIGHT)
        line.to_edge(DOWN, buff=0.55)
        self.play(Write(line), run_time=1.0)
        self.play(
            FadeOut(e_weight),
            w_lab.animate.set_opacity(0.3), w_e.animate.set_opacity(0.3),
            w_s_zero.animate.set_opacity(0.3), head.animate.set_opacity(0.3),
            col_e.animate.set_opacity(0.3), col_s.animate.set_opacity(0.3),
            run_time=1.0, rate_func=rate_functions.ease_in_out_cubic,
        )
        self.wait(1.0)

        ledger = VGroup(head, col_e, col_s, w_lab, w_e, w_s_zero,
                        m_lab, m_e, m_s)

        # ── THE SEED ───────────────────────────────────────────────────────
        if self.USE_MYSTERY_TOKEN:
            # compress 'mass ≠ weight' into a small sealed, glowing token that
            # shrinks and docks to a corner, pinned to the frame — a promise.
            token = self._make_token()
            token.move_to(ball.get_center()).scale(0.01)
            self.add(token)
            self.play(
                FadeOut(line),
                FadeOut(ledger),
                token.animate.scale(100).move_to(ORIGIN),
                run_time=1.0, rate_func=rate_functions.ease_in_out_cubic,
            )
            self.wait(0.6)
            # >>> POST (light): a soft 'stash / bookmark' tick as it docks.
            target = self.camera.frame.get_corner(DR) + LEFT * 0.7 + UP * 0.55
            self.play(
                token.animate.scale(0.42).move_to(target),
                run_time=1.1, rate_func=rate_functions.ease_in_out_cubic,
            )
            # pin the docked token to the camera so it survives into Scene 5
            def pin_token(m):
                m.move_to(self.camera.frame.get_corner(DR)
                          + LEFT * 0.7 + UP * 0.55)
            token.add_updater(pin_token)
            self.mystery_token = token
            self.wait(1.2)
        else:
            # foreshadow purely in motion: the glow lingers alone
            self.play(FadeOut(line), FadeOut(ledger), run_time=0.9)
            self.play(VGroup(ball).animate.move_to(ORIGIN),
                      run_time=1.0, rate_func=rate_functions.ease_in_out_cubic)
            self.wait(1.4)

    # ── small builders ────────────────────────────────────────────────────
    def _make_scale_panel(self, value):
        """A compact spring-scale readout: 'WEIGHT' cap + a live Newton number."""
        w, h = 1.7, 0.92
        plate = RoundedRectangle(width=w, height=h, corner_radius=0.08,
                                 stroke_color=DUST, stroke_width=1.4,
                                 stroke_opacity=0.5, fill_color=PANEL,
                                 fill_opacity=0.65)
        cap = Text("WEIGHT", font=MONO, font_size=11, color=DUST)
        cap.next_to(plate.get_top(), DOWN, buff=0.1)
        num = Text(f"{value:.1f} N", font=MONO, font_size=22, color=C_GRAV)
        num.move_to(plate.get_center() + DOWN * 0.08)
        g = VGroup(plate, cap, num).set_z_index(8)
        g.num = num
        g.plate = plate
        return g

    def _bind_scale(self, panel, tracker):
        anchor = panel.plate.get_center() + DOWN * 0.08

        def upd(m):
            new = Text(f"{tracker.get_value():.1f} N", font=MONO,
                       font_size=22,
                       color=C_GRAV if tracker.get_value() > 0.05 else DUST)
            new.move_to(anchor)
            m.become(new)
        panel.num.add_updater(upd)

    def _make_token(self):
        """A small sealed, glowing seed — the planted callback. Generic on
        purpose (fits whichever later scene claims it). A rounded capsule with a
        faint mass-pigment core and a tiny seal mark."""
        body = RoundedRectangle(width=0.92, height=0.62, corner_radius=0.14,
                                stroke_color=C_MASS, stroke_width=1.8,
                                fill_color=PANEL, fill_opacity=0.9)
        core = Circle(radius=0.12, stroke_width=0, fill_color=C_MASS,
                      fill_opacity=0.9).move_to(body.get_center())
        halo = Circle(radius=0.2, stroke_width=0, fill_color=C_MASS,
                      fill_opacity=0.18).move_to(body.get_center())
        seal = Text("?", font=SERIF, slant=ITALIC, font_size=22, color=VOID)
        seal.move_to(core.get_center())
        cap = Text("FOR LATER", font=MONO, font_size=9, color=DUST)
        cap.next_to(body, DOWN, buff=0.1)
        g = VGroup(body, halo, core, seal, cap).set_z_index(13)
        return g