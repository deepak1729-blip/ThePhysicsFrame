"""
THE PHYSICS FRAME — SCENE 3 · THE SIZE OF LAZINESS
==================================================
Series: INERTIA (2026).  Continues directly from Scene 2's last frame:
the STARLIGHT "lazy" ball sitting dead-still with the word *Lazy* above it.

SCENE JOB
  Turn the WORD "lazy" into a NUMBER you can measure — mass.
  Spine (one unbroken magic-move chain, Keynote-style):
    Lazy → lazy → iners → inertia → (the doubt) → two silhouettes →
    bowling ball + balloon → the shared push arrow → two laziness gauges →
    the word MASS sitting on the heavier object.

PHYSICS HONESTY (series principle)
  The whole asymmetry is derived, not eased. One impulse J is applied to both
  objects. The launch speed of each is the honest  v = J / m.  With
  M_BALLOON << M_BALL, the balloon's v is ~600x the ball's, so over the same
  flick it sails off-frame while the ball moves a single pixel. The laziness
  gauges fill in proportion to m itself, and the Act-7 mass readouts are those
  same masses. Tiny cause, enormous effect — straight out of  Δv = J/m.

ACT-5 "OW" OVERLAY
  USE_OW_OVERLAY layers your live-action finger-recoil still on top of the
  always-present Manim pain-star (so the beat lands either way). Drop
  `s3_finger_recoil.png` beside this file; if it's missing, safe_image() shows
  a framed placeholder and the script still runs as-is.

HANDOFF TO SCENE 4
  The final frame leaves the bowling ball tagged with its intrinsic mass,
  bottom-centre, ready to be lifted into the astronaut scene via magic-move.
  No mention of weight / gravity / heaviness here — that's Scene 4's twist.

TUNING KNOBS (eyeball after first render): FLOOR_Y, the object positions,
J / M_BALLOON / M_BALL, gauge HEIGHTS, and the Act-6 HOLD duration.
"""

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
C_FORCE   = "#E06450"   # FORCE — the push I APPLY  (kept visually distinct)
C_VEL     = "#57C08A"   # VELOCITY — the huge effect of a tiny push
C_GROUND  = "#7F8A99"   # ground / reference axis

SERIF = "Spectral"      # ideas; italic is the channel's speaking voice
MONO  = "Space Mono"    # labels & metadata only

config.background_color = VOID
RNG = np.random.default_rng(3)   # deterministic -> stable render cache


# ═══════════════════════════════════════════════════════════════════════════
#  CONSTRUCTION VOCABULARY  (reused verbatim from Scenes 1–2, then extended)
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


def make_ball(color, radius=0.17):
    """Top-down ball: base disc + sheen + specular (series shading vocabulary).
    Carried over from Scene 2 so the Scene-2 'lazy' character matches exactly."""
    g = VGroup()
    sphere = Circle(radius=radius)
    sphere.set_fill(color, opacity=1.0)
    sphere.set_sheen(-0.40, DR)
    sphere.set_stroke(color=STARLIGHT, width=1.4, opacity=0.18)
    g.add(sphere)
    rim = Circle(radius=radius)
    rim.set_fill(opacity=0)
    rim.set_stroke(color=color, width=2.6, opacity=0.45)
    g.add(rim)
    spec = Ellipse(width=radius * 0.50, height=radius * 0.32)
    spec.set_fill(STARLIGHT, opacity=0.62)
    spec.set_stroke(width=0)
    spec.move_to(np.array([-radius * 0.28, radius * 0.30, 0]))
    spec.rotate(-20 * DEGREES)
    g.add(spec)
    g.disc = sphere
    g.radius = radius
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


# ─────────────────────────── new vocabulary for Scene 3 ───────────────────
def make_silhouette(h=1.30, color=DUST):
    """A featureless 'blank' standing form — a seed that becomes a real object
    in Act 3. Capsule body so it reads as a thing, not yet a known thing."""
    w = h * 0.62
    body = RoundedRectangle(width=w, height=h, corner_radius=w / 2,
                            stroke_color=color, stroke_width=2.0,
                            fill_color=color, fill_opacity=0.16)
    return VGroup(body)


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


def make_balloon(height=1.16):
    """An airy teardrop balloon: thin STARLIGHT shell, knot, little string.
    Reads as NOTHING — light, hollow, a faint Cyan sheen. Exposes `.shell`."""
    g = VGroup()
    w = height * 0.74
    shell = Ellipse(width=w, height=height)
    shell.set_fill(STARLIGHT, opacity=0.10)
    shell.set_stroke(color=STARLIGHT, width=2.0, opacity=0.85)
    g.add(shell)
    sheen = Ellipse(width=w * 0.34, height=height * 0.42)
    sheen.set_fill(CYAN, opacity=0.16)
    sheen.set_stroke(width=0)
    sheen.move_to(shell.get_center() + np.array([-w * 0.18, height * 0.18, 0]))
    g.add(sheen)
    # knot (small triangle) at the bottom
    knot = Triangle().scale(0.08)
    knot.set_fill(STARLIGHT, opacity=0.85).set_stroke(width=0)
    knot.next_to(shell, DOWN, buff=-0.02)
    g.add(knot)
    # a short curling string
    string = VMobject(stroke_color=STARLIGHT, stroke_width=1.6,
                      stroke_opacity=0.55)
    string.set_points_smoothly([
        knot.get_bottom(),
        knot.get_bottom() + np.array([0.10, -0.18, 0]),
        knot.get_bottom() + np.array([-0.08, -0.34, 0]),
        knot.get_bottom() + np.array([0.06, -0.50, 0]),
    ])
    g.add(string)
    g.shell = shell
    g.height = height
    return g


def make_push_arrow(length=0.92, color=C_FORCE):
    """THE push arrow — built once, copied forever. Its exact size IS the
    experiment, so it is a fixed-geometry object (no Arrow auto-scaling)."""
    shaft = Line(ORIGIN, RIGHT * length, stroke_color=color, stroke_width=6.0)
    tip = Triangle().scale(0.085)
    tip.set_fill(color, opacity=1.0).set_stroke(width=0)
    tip.rotate(-90 * DEGREES)                     # point +x
    tip.move_to(shaft.get_end())
    g = VGroup(shaft, tip)
    g.tail = shaft.get_start
    g.head = shaft.get_end
    return g


def make_gauge(height=2.4, color=C_MASS, label="LAZINESS"):
    """A vertical 'laziness gauge': an empty track + a fill that a ValueTracker
    drives from the bottom up. The fill carries the MASS pigment so it reads as
    a *property of the object*, never to be confused with the FORCE-red push."""
    w = 0.46
    track = RoundedRectangle(width=w, height=height, corner_radius=0.08,
                             stroke_color=DUST, stroke_width=1.6,
                             stroke_opacity=0.55, fill_opacity=0.0)
    fill = RoundedRectangle(width=w - 0.08, height=0.02, corner_radius=0.05,
                            stroke_width=0, fill_color=color, fill_opacity=0.92)
    fill.move_to(track.get_bottom(), aligned_edge=DOWN)
    cap = Text(label, font=MONO, font_size=12, color=DUST)
    cap.next_to(track, DOWN, buff=0.16)
    g = VGroup(track, fill, cap)
    g.track = track
    g.fill = fill
    g.cap = cap
    g._h = height
    g._w = w
    g._fill_color = color
    return g


def set_gauge(gauge, frac):
    """Drive a gauge's fill to `frac` of full (0..1), anchored at its base.

    The fill is *rebuilt* (via .become) each call rather than stretched. A
    RoundedRectangle stretched repeatedly from a near-zero height — where the
    corner radius dwarfs the height — keeps a correct bounding box but mangles
    its corner control points, so it renders far shorter than it measures. A
    fresh rect with the radius clamped to the current height sidesteps that
    entirely and always fills the track honestly."""
    frac = max(0.0008, min(1.0, frac))
    h = gauge._h * frac
    w = gauge._w - 0.08
    r = min(0.05, h * 0.45)          # radius can never exceed ~half the height
    fresh = RoundedRectangle(width=w, height=h, corner_radius=r,
                             stroke_width=0, fill_color=gauge._fill_color,
                             fill_opacity=0.92)
    fresh.move_to(gauge.track.get_bottom(), aligned_edge=DOWN)
    gauge.fill.become(fresh)


def pain_star(color=C_FORCE, scale=0.5):
    """A small comic impact burst for the 'ow' — short radial spikes."""
    g = VGroup()
    for i in range(8):
        ang = i * 45 * DEGREES
        r0 = 0.10 if i % 2 == 0 else 0.05
        r1 = 0.26 if i % 2 == 0 else 0.15
        d = np.array([math.cos(ang), math.sin(ang), 0])
        g.add(Line(d * r0, d * r1, stroke_color=color, stroke_width=3.4))
    return g.scale(scale)


# ═══════════════════════════════════════════════════════════════════════════
class Scene3_TheSizeOfLaziness(MovingCameraScene):

    # ── render switches ───────────────────────────────────────────────────
    USE_OW_OVERLAY = True            # director's pick: live finger-recoil still

    # ── locked geometry ───────────────────────────────────────────────────
    FLOOR_Y   = -2.55
    BALL_X    = -3.15                # bowling-ball station (left)
    BALLOON_X =  3.15                # balloon station (right)
    BALL_R    = 0.62
    BALLOON_H = 1.16

    # ── honest physics constants (everything derives from these) ──────────
    J         = 0.060               # one impulse, identical for both objects
    M_BALLOON = 0.010               # kg — almost nothing
    M_BALL    = 6.00                # kg — stubborn
    #   v = J / m   →   balloon flies, ball barely twitches.

    def construct(self):
        self.camera.frame.save_state()

        # Frame marks pinned to the camera (survive the Act-1 push-in).
        self.frame_marks = VGroup(*[corner_L(o, opacity=0.0)
                                    for o in (UL, UR, DL, DR)])
        self._pin_frame_marks()

        # derived honest launch speeds (scene-units/s); only the RATIO matters
        self.v_balloon = self.J / self.M_BALLOON
        self.v_ball    = self.J / self.M_BALL

        self.act1_the_word()
        self.act2_but_equally_lazy()
        self.act3_two_things()
        self.act4_flick_the_balloon()
        self.act5_flick_the_ball()
        self.act6_same_push_different_reaction()
        self.act7_we_call_it_mass()

    # ── frame-mark plumbing (verbatim pattern from Scenes 1–2) ─────────────
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
    def act1_the_word(self):
        """Carry Scene 2's mood; the 'lazy' ball lingers, then the WORD is born:
        Lazy → lazy → iners → inertia (shared stem 'iner' stays put)."""
        # 1) Open EXACTLY on Scene 2's last frame: the still STARLIGHT ball,
        #    sitting on the SOLID cruise floor (the ground line + faint ticks
        #    Scene 2 ends on), with 'Lazy' in Spectral italic above it.
        ground = Line(LEFT * 14 + UP * self.FLOOR_Y, RIGHT * 14 + UP * self.FLOOR_Y,
                      color=C_GROUND, stroke_width=2.0, stroke_opacity=0.85)
        ticks = VGroup(*[
            Line(UP * 0.06, DOWN * 0.06, color=C_GROUND, stroke_width=1.2,
                 stroke_opacity=0.30).move_to(RIGHT * (k * 0.5) + UP * self.FLOOR_Y)
            for k in range(-13, 14)])
        ground_grp = VGroup(ground, ticks).set_z_index(-1)
        ball = make_ball(STARLIGHT, radius=0.17)
        ball.move_to(UP * 0.05).set_z_index(8)
        lazy = Text("Lazy", font=SERIF, slant=ITALIC, font_size=58,
                    color=STARLIGHT).next_to(ball, UP, buff=0.55).set_z_index(9)
        self.add(ground_grp, ball, lazy, self.frame_marks)
        self.frame_marks.set_opacity(0.45)
        self.wait(0.6)
        # cross-fade the Scene-2 solid ground into Scene 3's own dashed floor
        floor = DashedLine(LEFT * 6.6 + UP * self.FLOOR_Y,
                           RIGHT * 6.6 + UP * self.FLOOR_Y,
                           dash_length=0.18, dashed_ratio=0.55, color=C_GROUND,
                           stroke_width=2.0, stroke_opacity=0.0)
        self.add(floor)
        self.play(floor.animate.set_stroke(opacity=0.85),
                  ground_grp.animate.set_opacity(0.0),
                  run_time=0.8, rate_func=rate_functions.ease_in_out_sine)
        self.remove(ground_grp)

        # a tiny idle 'z z z' rises and evaporates — the sleeping-laziness joke
        zzz = VGroup(*[Text("z", font=SERIF, slant=ITALIC,
                            font_size=20 + 6 * i, color=DUST)
                       for i in range(3)])
        for i, z in enumerate(zzz):
            z.move_to(ball.get_center()
                      + np.array([0.34 + i * 0.20, 0.30 + i * 0.22, 0]))
        self.play(LaggedStart(*[FadeIn(z, shift=UP * 0.12) for z in zzz],
                              lag_ratio=0.35), run_time=1.0)
        self.play(LaggedStart(*[FadeOut(z, shift=UP * 0.25) for z in zzz],
                              lag_ratio=0.3), run_time=0.8)
        self.wait(0.3)

        # 2) The word takes over from the character. 'Lazy' shrinks UP into the
        #    gloss-satellite 'lazy'; the ball quietly bows out, its job done.
        gloss_lazy = Text("lazy", font=SERIF, slant=ITALIC, font_size=26,
                          color=DUST)
        gloss_lazy.move_to(UP * 1.95 + RIGHT * 1.7)
        self.play(
            ReplacementTransform(lazy, gloss_lazy),
            FadeOut(ball, shift=DOWN * 0.3, scale=0.7),
            FadeOut(floor, run_time=0.9),
            run_time=1.1, rate_func=rate_functions.ease_in_out_cubic,
        )

        # 3) Carve the Latin root at centre. Write-on, letter by letter.
        iners = Text("iners", font=SERIF, font_size=72, color=STARLIGHT)
        iners.move_to(ORIGIN)
        self.play(Write(iners), run_time=1.4)

        # two more gloss-satellites fade in to orbit and define the root
        gloss_idle = Text("idle", font=SERIF, slant=ITALIC, font_size=26,
                          color=DUST).move_to(UP * 1.55 + LEFT * 2.6)
        gloss_slug = Text("sluggish", font=SERIF, slant=ITALIC, font_size=26,
                          color=DUST).move_to(DOWN * 1.55 + LEFT * 1.9)
        self.play(LaggedStart(FadeIn(gloss_idle, shift=DOWN * 0.1),
                              FadeIn(gloss_slug, shift=UP * 0.1),
                              lag_ratio=0.25), run_time=1.0)
        # slow push-in: stillness as the aesthetic
        self.play(self.camera.frame.animate.scale(0.92),
                  run_time=1.6, rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.5)

        # the satellites have done their work — let them evaporate, root alone
        self.play(LaggedStart(*[FadeOut(g, scale=0.8)
                                for g in (gloss_idle, gloss_lazy, gloss_slug)],
                              lag_ratio=0.2), run_time=0.9)
        self.wait(0.4)

        # 4) THE SIGNATURE MOVE: iners → inertia. Shared stem 'iner' physically
        #    stays; only '-tia' grows out of it. The physics word is BORN from
        #    the Latin, not swapped for it.
        inertia = Text("inertia", font=SERIF, font_size=72, color=STARLIGHT)
        inertia.move_to(ORIGIN)
        self.play(TransformMatchingShapes(iners, inertia),
                  run_time=1.3, rate_func=rate_functions.ease_in_out_sine)
        self.inertia_word = inertia          # <-- reused in Act 7 (→ MASS)
        self.wait(0.6)

        # 5) Resolve one clean definition line beneath it.
        self.definition = Text(
            "INERTIA — the reluctance to change its state of motion.",
            font=SERIF, slant=ITALIC, font_size=26, color=DUST,
            t2c={"INERTIA": AMBER})
        self.definition.next_to(inertia, DOWN, buff=0.55)
        self.play(FadeIn(self.definition, shift=UP * 0.08), run_time=0.9)
        self.wait(1.2)

    # ═══════════════════════════════════════════════════════════════ A2 ═══
    def act2_but_equally_lazy(self):
        """Record-scratch doubt beat: are ALL things equally lazy? Test the
        hidden assumption, then collapse to two blank silhouettes."""
        # restore the easy framing as the record scratches
        self.play(self.camera.frame.animate.restore(),
                  run_time=0.5, rate_func=rate_functions.ease_out_cubic)

        # park the word/definition up top; we go investigate
        self.play(
            self.inertia_word.animate.scale(0.5).to_edge(UP, buff=0.5)
                .set_opacity(0.6),
            FadeOut(self.definition, shift=UP * 0.1),
            run_time=0.9, rate_func=rate_functions.ease_in_out_cubic,
        )

        # stamp the IDENTICAL 'inertia' tag onto a mismatched spread of objects
        feather = self._mini_feather().move_to(LEFT * 3.6 + DOWN * 0.2)
        block   = self._mini_block().move_to(DOWN * 0.2)
        cup     = self._mini_cup().move_to(RIGHT * 3.6 + DOWN * 0.2)
        spread = VGroup(feather, block, cup)
        self.play(LaggedStart(*[FadeIn(o, shift=UP * 0.12) for o in spread],
                              lag_ratio=0.18), run_time=1.0)

        tags = VGroup()
        for o in spread:
            t = Text("inertia", font=MONO, font_size=15, color=DUST)
            t.next_to(o, UP, buff=0.28)
            tags.add(t)
        self.play(LaggedStart(*[FadeIn(t, scale=0.85) for t in tags],
                              lag_ratio=0.18), run_time=0.9)
        self.wait(0.6)

        # a swelling question between them: have we actually CHECKED?
        q = Text("= ?", font=SERIF, font_size=58, color=AMBER, weight=BOLD)
        q.move_to(UP * 1.05)
        self.play(GrowFromCenter(q), run_time=0.6)
        self.play(q.animate.scale(1.18), rate_func=there_and_back, run_time=0.7)
        self.wait(0.7)

        # collapse the spread + tags DIRECTLY into the two real objects on the
        # floor (no intermediate rounded-rectangle silhouette step).
        self.ball = make_bowling_ball(radius=self.BALL_R)
        self.ball.move_to(RIGHT * self.BALL_X
                          + UP * (self.FLOOR_Y + self.BALL_R)).set_z_index(6)
        self.balloon = make_balloon(height=self.BALLOON_H)
        self.balloon.move_to(RIGHT * self.BALLOON_X
                             + UP * (self.FLOOR_Y + self.BALLOON_H / 2 + 0.04))
        self.balloon.set_z_index(6)
        self.play(
            ReplacementTransform(VGroup(feather, block), self.ball),
            ReplacementTransform(cup.copy(), self.balloon),
            FadeOut(cup), FadeOut(tags), FadeOut(q),
            run_time=1.1, rate_func=rate_functions.ease_in_out_cubic,
        )
        self.wait(0.6)

    def _mini_feather(self):
        spine = Line(DOWN * 0.32, UP * 0.32, stroke_color=STARLIGHT,
                     stroke_width=2.0, stroke_opacity=0.8)
        g = VGroup(spine)
        for s in (-1, 1):
            for k in range(5):
                t = k / 4
                base = interpolate(DOWN * 0.26, UP * 0.30, t)
                barb = Line(base, base + np.array([s * 0.16 * (1 - 0.4 * t),
                                                   0.10, 0]),
                            stroke_color=STARLIGHT, stroke_width=1.4,
                            stroke_opacity=0.6)
                g.add(barb)
        return g

    def _mini_block(self):
        return RoundedRectangle(width=0.62, height=0.5, corner_radius=0.05,
                                stroke_color=C_MASS, stroke_width=2.0,
                                fill_color=C_MASS, fill_opacity=0.22)

    def _mini_cup(self):
        body = Polygon(np.array([-0.22, 0.28, 0]), np.array([0.22, 0.28, 0]),
                       np.array([0.16, -0.28, 0]), np.array([-0.16, -0.28, 0]),
                       stroke_color=STARLIGHT, stroke_width=2.0,
                       fill_color=STARLIGHT, fill_opacity=0.08)
        handle = Arc(radius=0.16, start_angle=-PI / 2, angle=PI,
                     stroke_color=STARLIGHT, stroke_width=2.0,
                     stroke_opacity=0.8).next_to(body, RIGHT, buff=-0.03)
        return VGroup(body, handle)

    # ═══════════════════════════════════════════════════════════════ A3 ═══
    def act3_two_things(self):
        """Floor draws in beneath the two real objects (already placed in Act 2).
        Body language sells the asymmetry before anyone touches anything."""
        self.floor = DashedLine(LEFT * 6.6 + UP * self.FLOOR_Y,
                                RIGHT * 6.6 + UP * self.FLOOR_Y,
                                dash_length=0.18, dashed_ratio=0.55,
                                color=C_GROUND, stroke_width=2.0,
                                stroke_opacity=0.85)
        self.play(Create(self.floor), run_time=1.0,
                  rate_func=rate_functions.ease_in_out_sine)

        # a quiet name tag under each (mono, metadata only)
        tag_ball = Text("bowling ball", font=MONO, font_size=14, color=DUST)
        tag_ball.next_to(self.ball, DOWN, buff=0.30)
        tag_balloon = Text("balloon", font=MONO, font_size=14, color=DUST)
        tag_balloon.next_to(self.floor, UP, buff=0.10)
        tag_balloon.set_x(self.BALLOON_X)
        self.play(LaggedStart(FadeIn(tag_ball, shift=UP * 0.06),
                              FadeIn(tag_balloon, shift=UP * 0.06),
                              lag_ratio=0.2), run_time=0.7)
        self.wait(0.5)

        # IDLE BODY LANGUAGE: the balloon bobs on invisible air; the ball is dead.
        bob = ValueTracker(0.0)
        base_y = self.balloon.get_center()[1]
        self.balloon.add_updater(
            lambda m: m.set_y(base_y + 0.07 * math.sin(bob.get_value())))
        self.add(bob)                     # keep the tracker alive in-scene
        self._bob_tracker = bob
        self.play(bob.animate.set_value(2 * TAU), run_time=2.6,
                  rate_func=linear)
        self.wait(0.4)
        # freeze both bob + tags so the next act is clean
        self.balloon.clear_updaters()
        self.balloon.set_y(base_y)
        self.play(FadeOut(tag_ball), FadeOut(tag_balloon), run_time=0.5)

    # ═══════════════════════════════════════════════════════════════ A4 ═══
    def act4_flick_the_balloon(self):
        """A modest flick → an enormous, floaty flight. Tiny cause, huge effect.
        Build THE push arrow here; it will be copied (never remade) later."""
        contact = self.balloon.get_left() + RIGHT * 0.02

        # a stylized flick streak snapping in from the right edge
        streak = ArcBetweenPoints(self.balloon.get_right() + RIGHT * 2.6
                                  + UP * 0.4,
                                  self.balloon.get_left() + LEFT * 0.05,
                                  angle=-0.8, stroke_color=STARLIGHT,
                                  stroke_width=3.0)
        streak = DashedVMobject(streak, num_dashes=14)
        streak.set_stroke(opacity=0.0)
        self.add(streak)
        self.play(streak.animate.set_stroke(opacity=0.55), run_time=0.25)

        # THE push arrow — built once, at the contact point, pointing into the
        # balloon. Deliberately small & sharply defined: its size is the test.
        self.push_arrow = make_push_arrow(length=0.92, color=C_FORCE)
        self.push_arrow.next_to(contact, LEFT, buff=0.04)
        self.push_arrow.set_z_index(9)
        self.play(GrowFromEdge(self.push_arrow, LEFT), run_time=0.4)
        self.play(FadeOut(streak), run_time=0.2)
        self.wait(0.2)

        # honest launch speed for the balloon: v = J / m  (large)
        start = self.balloon.get_center()
        # a long, fast, slightly floaty arc across the frame, soft bounce on exit
        apex = start + np.array([3.6, 1.7, 0])
        far  = np.array([6.9, self.FLOOR_Y + 0.8, 0])           # off-frame right
        path = VMobject()
        path.set_points_smoothly([start, apex, far])
        trail = DashedVMobject(path.copy(), num_dashes=30)
        trail.set_stroke(color=DUST, width=2.4, opacity=0.0)

        # a BIG velocity arrow grows out of the tiny push — tiny in, enormous out
        vel = Arrow(start, start + RIGHT * 2.7, buff=0, color=C_VEL,
                    stroke_width=7, max_tip_length_to_length_ratio=0.12)
        vel_lbl = Text("v", font=SERIF, slant=ITALIC, font_size=26, color=C_VEL)
        vel_lbl.next_to(vel.get_end(), UP, buff=0.12)
        self.play(GrowArrow(vel), FadeIn(vel_lbl, shift=UP * 0.06),
                  run_time=0.4)

        # the flight: balloon rides the honest arc; push arrow recoils to nothing
        self.add(trail)
        self.play(
            MoveAlongPath(self.balloon, path,
                          rate_func=rate_functions.ease_out_sine),
            trail.animate.set_stroke(opacity=0.7),
            self.push_arrow.animate.set_opacity(0.0).shift(LEFT * 0.12),
            FadeOut(vel), FadeOut(vel_lbl),
            run_time=1.1,
        )
        # the giant displacement, undeniable; the balloon parks just off-frame
        big = Text("flew across the room", font=MONO, font_size=15, color=DUST)
        big.move_to(UP * 1.7 + RIGHT * 1.0)
        self.play(FadeIn(big, shift=UP * 0.08), run_time=0.5)
        self.wait(0.7)
        self.play(FadeOut(big), FadeOut(trail), run_time=0.5)
        # restore the (now invisible) push arrow object for reuse, off-screen
        self.push_arrow.set_opacity(1.0).next_to(contact, LEFT, buff=0.04)
        self.push_arrow.set_opacity(0.0)

    # ═══════════════════════════════════════════════════════════════ A5 ═══
    def act5_flick_the_ball(self):
        """The SAME push arrow, copied onto the bowling ball. Same input — and
        the ball doesn't move. The arrow crumples; the finger recoils. 'Ow.'"""
        # bring the balloon back to its station so both objects share the frame
        rest = RIGHT * self.BALLOON_X + UP * (self.FLOOR_Y + self.BALLOON_H / 2
                                              + 0.04)
        # NOTE: don't call set_opacity(1.0) here — that flattens the balloon's
        # thin translucent shell into a solid white blob. Its styling from
        # make_balloon() is intact after the flight, so just glide it back.
        self.play(self.balloon.animate.move_to(rest), run_time=0.6,
                  rate_func=rate_functions.ease_in_out_cubic)

        contact_ball = self.ball.get_left() + RIGHT * 0.02

        # LITERALLY the same arrow: copy the Act-4 object, place it on the ball.
        arrow_on_ball = self.push_arrow.copy().set_opacity(1.0)
        arrow_on_ball.next_to(contact_ball, LEFT, buff=0.04).set_z_index(9)

        # briefly show the two arrows side by side so the viewer SEES they match
        arrow_ref = self.push_arrow.copy().set_opacity(1.0)
        arrow_ref.move_to(UP * 1.4 + LEFT * 1.0).set_z_index(9)
        arrow_ref2 = self.push_arrow.copy().set_opacity(1.0)
        arrow_ref2.next_to(arrow_ref, DOWN, buff=0.28, aligned_edge=LEFT)
        same = Text("same push", font=MONO, font_size=14, color=C_FORCE)
        same.next_to(VGroup(arrow_ref, arrow_ref2), LEFT, buff=0.3)
        self.play(LaggedStart(FadeIn(arrow_ref, shift=RIGHT * 0.1),
                              FadeIn(arrow_ref2, shift=RIGHT * 0.1),
                              lag_ratio=0.25), run_time=0.7)
        self.play(FadeIn(same, shift=RIGHT * 0.06), run_time=0.4)
        self.wait(0.6)
        # one of them flies down onto the ball — that's the input we'll apply
        self.play(
            ReplacementTransform(arrow_ref2, arrow_on_ball),
            FadeOut(arrow_ref), FadeOut(same),
            run_time=0.8, rate_func=rate_functions.ease_in_out_cubic,
        )
        self.wait(0.3)

        # the flick lands. honest result: v = J/m is ~tiny → a single-pixel jitter.
        jitter = 0.04
        self.play(self.ball.animate.shift(RIGHT * jitter), run_time=0.06)
        self.play(self.ball.animate.shift(LEFT * jitter), run_time=0.06)

        # the push arrow CRUMPLES / bounces back off the dense surface
        self.play(
            arrow_on_ball.animate.stretch(0.45, 0).shift(LEFT * 0.22)
                .set_color(DUST),
            run_time=0.35, rate_func=rate_functions.ease_out_back,
        )

        # the finger recoils with a comic pain-star burst — the 'ow'
        star = pain_star(color=C_FORCE, scale=0.8)
        star.move_to(contact_ball + LEFT * 0.05).set_z_index(11)
        ow = Text("ow.", font=SERIF, slant=ITALIC, font_size=30, color=C_FORCE)
        ow.next_to(star, UL, buff=0.05).set_z_index(11)
        self.play(GrowFromCenter(star), FadeIn(ow, shift=UP * 0.1),
                  run_time=0.35)
        self.play(star.animate.scale(1.25).set_opacity(0.0),
                  run_time=0.4)

        self.wait(0.8)

        self.play(FadeOut(ow), FadeOut(arrow_on_ball), run_time=0.5)
        self.wait(0.4)

    # ═══════════════════════════════════════════════════════════════ A6 ═══
    def act6_same_push_different_reaction(self):
        """THE CRUX. Same push on each; wildly mismatched outcome; two gauges
        that disagree violently. Then FREEZE for 2.5s. This frame is the scene."""
        # 1) Bring both objects onto a shared baseline, side by side.
        base_y = -0.55
        ball_target = LEFT * 3.4 + UP * (base_y + 0.0)
        balloon_target = RIGHT * 3.4 + UP * (base_y + 0.05)
        # shrink the ball slightly so both read at a comparable scale
        self.play(
            self.ball.animate.scale(0.72).move_to(ball_target),
            self.balloon.animate.scale(0.82).move_to(balloon_target),
            FadeOut(self.floor),
            self.inertia_word.animate.set_opacity(0.0),   # park the word away
            run_time=1.0, rate_func=rate_functions.ease_in_out_cubic,
        )

        # 2) Re-show the IDENTICAL input arrow on each (same object, copied once
        #    more — sameness is sacred). Sits above each object.
        arr_ball = self.push_arrow.copy().set_opacity(1.0).set_color(C_FORCE)
        arr_ball[1].set_fill(C_FORCE, opacity=1.0)
        arr_ball.next_to(self.ball, UP, buff=0.22)
        arr_balloon = self.push_arrow.copy().set_opacity(1.0).set_color(C_FORCE)
        arr_balloon[1].set_fill(C_FORCE, opacity=1.0)
        arr_balloon.next_to(self.balloon, UP, buff=0.22)
        push_lbl = Text("same push", font=MONO, font_size=13, color=C_FORCE)
        push_lbl.next_to(VGroup(arr_ball, arr_balloon), UP, buff=0.2)
        push_lbl.set_x(0)
        self.play(LaggedStart(FadeIn(arr_ball, shift=DOWN * 0.06),
                              FadeIn(arr_balloon, shift=DOWN * 0.06),
                              lag_ratio=0.2), run_time=0.7)
        self.play(FadeIn(push_lbl, shift=DOWN * 0.05), run_time=0.4)
        self.wait(0.4)

        # 3) The OUTCOME as a measurable bar (geometry teaches it).
        out_y = base_y - 1.05
        ball_out = Line(self.ball.get_center()[0] * RIGHT + UP * out_y,
                        self.ball.get_center()[0] * RIGHT + UP * out_y
                        + RIGHT * 0.34,
                        stroke_color=DUST, stroke_width=7, stroke_opacity=0.85)
        balloon_out = Line(self.balloon.get_center()[0] * RIGHT + UP * out_y,
                           RIGHT * 7.2 + UP * out_y,             # off-frame
                           stroke_color=CYAN, stroke_width=7, stroke_opacity=0.85)
        out_lbl_b = Text("moved a hair", font=MONO, font_size=12, color=DUST)
        out_lbl_b.next_to(ball_out, DOWN, buff=0.16, aligned_edge=LEFT)
        out_lbl_v = Text("flew off-frame", font=MONO, font_size=12, color=CYAN)
        out_lbl_v.move_to(UP * out_y + RIGHT * 4.4 + DOWN * 0.32)
        self.play(Create(ball_out), Create(balloon_out),
                  run_time=0.9, rate_func=rate_functions.ease_out_cubic)
        self.play(FadeIn(out_lbl_b), FadeIn(out_lbl_v), run_time=0.4)
        self.wait(0.5)

        # 4) Give LAZINESS a SIZE. A gauge on each, filled by a ValueTracker, in
        #    the MASS pigment (a property of the object — heavier than the push).
        g_ball = make_gauge(height=2.5, color=C_MASS, label="LAZINESS")
        g_ball.next_to(self.ball, LEFT, buff=0.7)
        g_ball.align_to(self.ball, DOWN)
        g_balloon = make_gauge(height=2.5, color=C_MASS, label="LAZINESS")
        g_balloon.next_to(self.balloon, RIGHT, buff=0.7)
        g_balloon.align_to(self.balloon, DOWN)
        set_gauge(g_ball, 0.0008)
        set_gauge(g_balloon, 0.0008)
        self.play(LaggedStart(Create(g_ball.track), Create(g_balloon.track),
                              lag_ratio=0.2), run_time=0.7)
        self.add(g_ball.fill, g_balloon.fill, g_ball.cap, g_balloon.cap)

        # honest fill fractions: balloon a sliver, ball dominating the frame
        frac_ball = self.M_BALL / self.M_BALL                  # = 1.0 (full)
        frac_balloon = self.M_BALLOON / self.M_BALL            # ~0.0017 (sliver)
        t_ball = ValueTracker(0.0008)
        t_balloon = ValueTracker(0.0008)
        g_ball.fill.add_updater(lambda m: set_gauge(g_ball, t_ball.get_value()))
        g_balloon.fill.add_updater(
            lambda m: set_gauge(g_balloon, t_balloon.get_value()))
        self.play(
            t_ball.animate.set_value(frac_ball),
            t_balloon.animate.set_value(max(frac_balloon, 0.012)),
            run_time=1.4, rate_func=rate_functions.ease_in_out_cubic,
        )
        g_ball.fill.clear_updaters()
        g_balloon.fill.clear_updaters()

        # 5) one minimal text pop is allowed
        crux = Text("same push  →  different result", font=SERIF, slant=ITALIC,
                    font_size=30, color=STARLIGHT,
                    t2c={"same push": C_FORCE, "different result": C_MASS})
        crux.to_edge(UP, buff=0.7)
        self.play(Write(crux), run_time=1.0)

        # ⚠️ THE HOLD — two objects, identical input arrows, two gauges that
        #    disagree violently. Freeze. Let it breathe. (low sustained tone)
        self.wait(2.6)

        # carry forward what Act 7 needs
        self.gauge_ball = g_ball
        self.gauge_balloon = g_balloon
        self._a6_cleanup = VGroup(arr_ball, arr_balloon, push_lbl, ball_out,
                                  balloon_out, out_lbl_b, out_lbl_v, crux)

    # ═══════════════════════════════════════════════════════════════ A7 ═══
    def act7_we_call_it_mass(self):
        """Name it. The gauge becomes a NUMBER; the word 'inertia' descends and
        magic-moves into MASS, seated on the heavier object. Intrinsic, owned."""
        # clear the Act-6 scaffolding but KEEP the two gauges + objects
        self.play(FadeOut(self._a6_cleanup), run_time=0.7)
        self.wait(0.2)

        # 1) a climbing readout rises out of each gauge: big on the ball, tiny
        #    on the balloon. Space Mono (the series' number voice), not LaTeX —
        #    keeps the typography on-brand and the script dependency-free.
        #    (kg = mass, NOT weight — Scene 4's twist stays armed.)
        anchor_ball = self.gauge_ball.get_top() + UP * 0.35
        anchor_balloon = self.gauge_balloon.get_top() + UP * 0.35
        tb = ValueTracker(0.0)
        tv = ValueTracker(0.0)

        def _readout(tracker, anchor, fs):
            txt = Text("0.00", font=MONO, font_size=fs, color=C_MASS)
            txt.move_to(anchor, aligned_edge=DOWN)

            def upd(m):
                new = Text(f"{tracker.get_value():.2f}", font=MONO,
                           font_size=fs, color=C_MASS)
                new.move_to(anchor, aligned_edge=DOWN)
                m.become(new)
            txt.add_updater(upd)
            return txt

        num_ball = _readout(tb, anchor_ball, 34)
        num_balloon = _readout(tv, anchor_balloon, 30)
        unit_ball = Text("kg", font=MONO, font_size=18, color=DUST)
        unit_ball.next_to(num_ball, RIGHT, buff=0.12).align_to(num_ball, DOWN)
        unit_balloon = Text("kg", font=MONO, font_size=16, color=DUST)
        unit_balloon.next_to(num_balloon, RIGHT, buff=0.1).align_to(num_balloon,
                                                                    DOWN)

        self.add(num_ball, unit_ball, num_balloon, unit_balloon)
        self.play(
            tb.animate.set_value(self.M_BALL),
            tv.animate.set_value(self.M_BALLOON),
            run_time=1.3, rate_func=rate_functions.ease_out_cubic,
        )
        num_ball.clear_updaters()
        num_balloon.clear_updaters()
        self.wait(0.6)

        # 2) THE NAMING MAGIC-MOVE. The 'inertia' word from Act 1 descends and
        #    transforms into MASS, settling onto the heavy object's readout.
        self.inertia_word.set_opacity(1.0).scale(1.0)
        self.inertia_word.move_to(UP * 2.6)
        self.play(self.inertia_word.animate.set_opacity(0.85),
                  run_time=0.5)
        mass_word = Text("MASS", font=SERIF, font_size=46, color=C_MASS,
                         weight=BOLD)
        mass_word.move_to(self.gauge_ball.get_top() + UP * 1.1)
        self.play(
            TransformMatchingShapes(self.inertia_word, mass_word),
            run_time=1.3, rate_func=rate_functions.ease_in_out_sine,
        )
        self.wait(0.8)

        # 3) Resolve to a clean two-object frame. The number reads as living
        #    INSIDE each object — intrinsic, belonging to it. Collapse gauges
        #    into the objects so the value sits ON the thing.
        m_ball = VGroup(
            Text("m", font=SERIF, slant=ITALIC, font_size=24, color=C_MASS),
            Text("= 6.00 kg", font=MONO, font_size=18, color=DUST),
        ).arrange(RIGHT, buff=0.12)
        m_balloon = VGroup(
            Text("m", font=SERIF, slant=ITALIC, font_size=20, color=C_MASS),
            Text("= 0.01 kg", font=MONO, font_size=15, color=DUST),
        ).arrange(RIGHT, buff=0.1)

        # final composition: heavy ball low-centre (the Scene-4 transition
        # object), balloon up-right and small. Tags ride WITH each object.
        ball_final = DOWN * 0.4 + LEFT * 0.2
        balloon_final = UP * 1.4 + RIGHT * 3.6
        m_ball.next_to(self.ball, DOWN, buff=0.28)

        self.play(
            FadeOut(self.gauge_ball.track), FadeOut(self.gauge_ball.fill),
            FadeOut(self.gauge_ball.cap),
            FadeOut(self.gauge_balloon.track), FadeOut(self.gauge_balloon.fill),
            FadeOut(self.gauge_balloon.cap),
            FadeOut(num_balloon), FadeOut(unit_balloon),
            ReplacementTransform(VGroup(num_ball, unit_ball), m_ball),
            run_time=1.0, rate_func=rate_functions.ease_in_out_cubic,
        )

        # group each object with its intrinsic tag, then settle the final frame
        ball_grp = VGroup(self.ball, m_ball)
        self.play(
            ball_grp.animate.scale(1.15).move_to(ball_final),
            self.balloon.animate.scale(0.85).move_to(balloon_final),
            mass_word.animate.scale(0.85).to_edge(UP, buff=0.7).set_color(C_MASS),
            run_time=1.1, rate_func=rate_functions.ease_in_out_cubic,
        )
        m_balloon.next_to(self.balloon, DOWN, buff=0.2)
        self.play(FadeIn(m_balloon, shift=UP * 0.06), run_time=0.5)

        # leave it. The tagged bowling ball waits, intrinsic, for Scene 4.
        self.wait(1.6)