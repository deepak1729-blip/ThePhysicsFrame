from manim import *
import numpy as np
import os

ASSET_DIR = os.path.dirname(os.path.abspath(__file__))

# ── BRAND PALETTE (series canvas, verbatim) ──
COLOR_BG     = "#0E1117"
COLOR_GROUND = "#8E8E93"
COLOR_WHITE  = "#E5E5EA"
COLOR_DIM    = "#3A3F47"


COLOR_CUE      = "#E5E5EA"   # cue ball A — clean white
COLOR_TARGET   = "#FF5A5F"   # target ball B — warm coral-red
COLOR_ENERGY   = "#FFD166"   # ENERGY, the tempting false lead — gold
COLOR_VEL      = "#3DDC97"   # velocity — green (one-frame cameo only here)
COLOR_MOMENTUM = "#A66BFF"   # the hero — electric violet, ONE subliminal pulse

FONT = "Segoe UI"
config.background_color = COLOR_BG
RNG = np.random.default_rng(7)   # deterministic → stable render cache


# ═══════════════════════════════════════════════════════════════════════════
#  HELPERS — same construction vocabulary as the rest of the series
# ═══════════════════════════════════════════════════════════════════════════
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
            t = (i + 0.5) / N
            op = peak_op * 0.35 * (1 - (2 * t - 1) ** 2)
            segs.add(Line(p1, p2, stroke_opacity=op,
                          stroke_width=1, color=COLOR_WHITE))
        return segs

    for x in np.arange(-max_x, max_x + 0.1, spacing):
        peak = 0.30 * (1 - (abs(x) / max_x) ** 1.5)
        if peak > 0:
            grid.add(fading_line(UP * max_y + RIGHT * x,
                                 DOWN * max_y + RIGHT * x, peak))
    for y in np.arange(-max_y, max_y + 0.1, spacing):
        peak = 0.30 * (1 - (abs(y) / max_y) ** 1.5)
        if peak > 0:
            grid.add(fading_line(LEFT * max_x + UP * y,
                                 RIGHT * max_x + UP * y, peak))
    return grid


def make_cue_stick(tip_point, length=2.8):
    """Cue stick image, sized to `length` with its tip at `tip_point`."""
    stick = ImageMobject("stick.png")
    stick.set(width=length)
    stick.move_to(tip_point + LEFT * (length / 2))
    return stick


def make_pool_ball(color, radius=0.28):
    """Top-down ball: base disc + sheen + specular (series shading vocabulary)."""
    g = VGroup()
    sphere = Circle(radius=radius)
    sphere.set_fill(color, opacity=1.0)
    sphere.set_sheen(-0.40, DR)
    sphere.set_stroke(color=COLOR_WHITE, width=1.4, opacity=0.18)
    g.add(sphere)
    rim = Circle(radius=radius)
    rim.set_fill(opacity=0)
    rim.set_stroke(color=color, width=2.6, opacity=0.45)
    g.add(rim)
    spec = Ellipse(width=radius * 0.50, height=radius * 0.32)
    spec.set_fill(COLOR_WHITE, opacity=0.62)
    spec.set_stroke(width=0)
    spec.move_to(np.array([-radius * 0.28, radius * 0.30, 0]))
    spec.rotate(-20 * DEGREES)
    g.add(spec)
    return g


def check_mark(color=COLOR_ENERGY, scale=0.9):
    """The series' satisfying tick."""
    m = VMobject(stroke_color=color, stroke_width=6)
    m.set_points_as_corners([
        LEFT * 0.18 + DOWN * 0.02, DOWN * 0.20, RIGHT * 0.30 + UP * 0.26,
    ])
    return m.scale(scale)


def impact_ring(point, color=COLOR_WHITE, r0=0.06, sw=3.5):
    """Tiny ring that the caller expands+fades — the visual 'clack'."""
    return Circle(radius=r0, color=color, stroke_width=sw,
                  fill_opacity=0).move_to(point).set_z_index(6)


def ledger_panel(header_text, w=3.05, h=2.10):
    """Slim BEFORE/AFTER ledger card. Quiet, near-opaque, series pill styling."""
    box = RoundedRectangle(width=w, height=h, corner_radius=0.18,
                           stroke_color=COLOR_GROUND, stroke_width=1.5,
                           stroke_opacity=0.55,
                           fill_color="#11151C", fill_opacity=0.92)
    head = Text(header_text, font=FONT, font_size=22, color=COLOR_GROUND,
                weight=BOLD)
    head.move_to(box.get_top() + DOWN * 0.36)
    g = VGroup(box, head)
    g.box, g.head = box, head
    return g


def motion_icon(mover_color, still_color, mover_left=True, r=0.155):
    """One moving ball (with grey speed-dashes trailing it) + one dim, still
    partner. Encodes 'who carries the motion' without touching the reserved
    velocity green — arrows stay out of this act."""
    mover = make_pool_ball(mover_color, radius=r)
    still = make_pool_ball(still_color, radius=r).set_opacity(0.28)
    dashes = VGroup(*[
        Line(ORIGIN, RIGHT * 0.15, stroke_width=3, color=COLOR_GROUND,
             stroke_opacity=op)
        for op in (0.55, 0.34, 0.16)
    ])
    for i, d in enumerate(dashes):
        d.next_to(mover, LEFT, buff=0.12 + i * 0.27)
    if mover_left:
        still.next_to(mover, RIGHT, buff=0.55)
        g = VGroup(dashes, mover, still)
    else:
        still.next_to(mover, LEFT, buff=0.55)
        # dashes still trail behind the mover (to its left)
        g = VGroup(still, dashes, mover)
    return g


# ═══════════════════════════════════════════════════════════════════════════
class Scene_1_TheBreak(MovingCameraScene):

    # ── locked geometry (every act reads from these) ──
    R         = 0.28                          # ball radius
    TABLE_Y   = -0.35                         # the play line
    CUE_START = np.array([-4.6, -0.35, 0.0])
    TARGET_0  = np.array([0.2, -0.35, 0.0])   # target's resting spot
    SPEED     = 4.15                           # units/s — ONE speed, handed over
    FREEZE_D  = 2.2                           # how far the target gets pre-freeze

    def construct(self):
        self.camera.frame.save_state()
        grid = build_grid()
        grid.set_z_index(-10)
        self.add(grid)
        self.grid = grid

        # derived anchors
        self.CONTACT_CUE = self.TARGET_0 + LEFT * (2 * self.R)   # cue's rest
        self.CLACK_PT    = self.TARGET_0 + LEFT * self.R         # surfaces meet
        self.FREEZE_POS  = self.TARGET_0 + RIGHT * self.FREEZE_D
        self.GAP_MID     = (self.CONTACT_CUE + self.FREEZE_POS) / 2

        self.FC = np.array([self.GAP_MID[0], 0.15, 0.0])

        self.act1_the_break()
        self.act2_freeze_and_interrogate()
        self.act3_the_tempting_answer()
        self.act4_the_promise()

    # ===================================================================== A1
    def act1_the_break(self):
        # >>> POST: open on a black frame; the CLACK lands a beat BEFORE any
        #     visual (audio-first hook). This opening hold is that beat.
        self.wait(0.6)

        # The implied table: a top-down pool table image.
        cushion = ImageMobject("table.png")
        cushion.set(width=12.4)
        cushion.set_z_index(-6)
        cushion.set_opacity(0.0)
        self.cushion = cushion
        self.add(cushion)
        self.play(cushion.animate.set_opacity(1.0), run_time=1.0,
                  rate_func=rate_functions.ease_in_out_sine)

        # The two characters, dead still.
        cue    = make_pool_ball(COLOR_CUE, self.R).move_to(self.CUE_START)
        target = make_pool_ball(COLOR_TARGET, self.R).move_to(self.TARGET_0)
        cue.set_z_index(5)
        target.set_z_index(5)
        self.cue, self.target = cue, target
        self.play(LaggedStart(FadeIn(cue, scale=0.85),
                              FadeIn(target, scale=0.85), lag_ratio=0.25),
                  run_time=0.8, rate_func=rate_functions.ease_out_cubic)
        self.wait(0.5)

        # The cue stick — entering with intent.
        tip_ready = self.CUE_START + LEFT * (self.R + 0.45)
        stick = make_cue_stick(tip_ready)
        stick.set_z_index(5)
        stick.shift(LEFT * 5.5)
        self.add(stick)
        self.play(stick.animate.shift(RIGHT * 5.5),
                  rate_func=rate_functions.ease_out_cubic)
        self.wait(0.25)

        # Anticipation: the wind-up. Pull back a hair...
        self.play(stick.animate.shift(LEFT * 0.42), run_time=0.45,
                  rate_func=rate_functions.ease_in_out_sine)
        # ...then SNAP into the ball. ease_in = accelerating strike.
        self.play(stick.animate.shift(RIGHT * (0.42 + 0.45 - 0.04)),
                  run_time=0.2, rate_func=rate_functions.ease_in_quad)

        # Contact #1: impact ring at the strike point + the cue launches.
        # The handoff of the eye: a fading trail rides behind the cue.
        ring1 = impact_ring(self.CUE_START + LEFT * self.R)
        self.add(ring1)

        t_cue = float(np.linalg.norm(self.CONTACT_CUE - self.CUE_START)) / self.SPEED
        self.play(
            cue.animate(rate_func=linear, run_time=t_cue)
               .move_to(self.CONTACT_CUE),                       # constant v — honest
            ring1.animate(rate_func=rate_functions.ease_out_quad,
                          run_time=0.28).scale(9).set_stroke(opacity=0.0),
            FadeOut(stick, shift=LEFT * 0.6, run_time=0.5),
        )
        self.remove(ring1)

        ring2 = impact_ring(self.CLACK_PT)
        self.add(ring2)

        t_tgt = self.FREEZE_D / self.SPEED
        self.play(
            target.animate(rate_func=linear, run_time=t_tgt)
                  .move_to(self.FREEZE_POS),                     # same constant v
            ring2.animate(rate_func=rate_functions.ease_out_quad,
                          run_time=0.30).scale(9).set_stroke(opacity=0.0),
        )
        self.remove(ring2)

    # ===================================================================== A2
    def act2_freeze_and_interrogate(self):
        vignette = Rectangle(width=30, height=18, fill_color=COLOR_BG,
                             fill_opacity=0.0, stroke_width=0)
        vignette.set_z_index(1)
        self.vignette = vignette
        self.add(vignette)

        self.play(
            vignette.animate.set_opacity(0.75),
            self.camera.frame.animate.scale(0.62)
                .move_to(self.GAP_MID + UP * 0.12),
            run_time=1.5, rate_func=rate_functions.ease_in_out_cubic,
        )

        self.wait(0.5)

        # Word-timed interrogation. Large, lots of air.
        q1 = Text("What just happened?", font=FONT, font_size=34,
                  color=COLOR_WHITE, weight=BOLD)
        q1.move_to(self.GAP_MID + UP * 1.62).set_z_index(10)
        self.play(FadeIn(q1, shift=DOWN * 0.12), run_time=0.5,
                  rate_func=rate_functions.ease_out_cubic)
        self.wait(0.5)

        q2 = Text("One ball stopped.   The other moved.", font=FONT,
                  font_size=24, color=COLOR_GROUND)
        q2.next_to(q1, DOWN, buff=0.30).set_z_index(10)
        self.play(FadeIn(q2, shift=DOWN * 0.10), run_time=0.5,
                  rate_func=rate_functions.ease_out_cubic)
        self.wait(0.5)

        hop_y = UP * 0.62
        v_ghost = Arrow(self.CONTACT_CUE + hop_y + LEFT * 0.10,
                        self.CONTACT_CUE + hop_y + RIGHT * 0.70,
                        buff=0, color=COLOR_VEL, stroke_width=4,
                        max_tip_length_to_length_ratio=0.32)
        v_ghost.set_z_index(6)
        self.play(FadeIn(v_ghost), run_time=0.5)
        self.wait(0.5)
        span = self.FREEZE_POS - self.CONTACT_CUE
        # the hop: up on the way out, settling down onto the target
        self.play(v_ghost.animate.shift(span * 0.5 + UP * 0.22),
                  run_time=0.5, rate_func=rate_functions.ease_out_sine)
        self.play(v_ghost.animate.shift(span * 0.5 + DOWN * 0.22),
                  run_time=0.5, rate_func=rate_functions.ease_in_sine)
        self.wait(0.5)
        self.play(FadeOut(v_ghost), run_time=0.5)
        self.wait(0.5)

        self.q_group = VGroup(q1, q2)

    # ===================================================================== A3
    def act3_the_tempting_answer(self):

        self.play(
            self.camera.frame.animate.set(width=config.frame_width)
                .move_to(self.FC),
            FadeOut(self.q_group, shift=UP * 0.15),
            rate_func=rate_functions.ease_in_out_cubic)

        # The warm gold glow wraps the whole system — ENERGY takes the stage.
        halo = RoundedRectangle(
            width=float(np.linalg.norm(self.FREEZE_POS - self.CONTACT_CUE)) + 1.6,
            height=1.5, corner_radius=0.75, stroke_width=0,
            fill_color=COLOR_ENERGY, fill_opacity=0.0)
        halo.move_to(self.GAP_MID).set_z_index(2)
        self.halo = halo

        energy_word = Text("ENERGY", font=FONT, font_size=42,
                           color=COLOR_ENERGY, weight=BOLD)
        energy_word.move_to(self.FC + UP * 2.45).set_z_index(10)
        self.energy_word = energy_word

        # The two-column ledger materialises on either side of the freeze.
        before = ledger_panel("BEFORE").move_to(self.FC + LEFT * 4.0 + DOWN * 0.15)
        after  = ledger_panel("AFTER").move_to(self.FC + RIGHT * 4.0 + DOWN * 0.15)
        for p in (before, after):
            p.set_z_index(10)

        # Who carries the motion: white mover before, coral mover after.
        icon_b = motion_icon(COLOR_CUE, COLOR_TARGET, mover_left=True)
        icon_b.move_to(before.box.get_center() + UP * 0.05).set_z_index(11)
        icon_a = motion_icon(COLOR_TARGET, COLOR_CUE, mover_left=False)
        icon_a.move_to(after.box.get_center() + UP * 0.05).set_z_index(11)

        self.wait(0.4)

        val_b = MathTex(r"E = \tfrac{1}{2}mv^2", font_size=34,
                        color=COLOR_ENERGY)
        val_b.move_to(before.box.get_center() + DOWN * 0.62).set_z_index(11)
        val_a = MathTex(r"E = \tfrac{1}{2}mv^2", font_size=34,
                        color=COLOR_ENERGY)
        val_a.move_to(after.box.get_center() + DOWN * 0.62).set_z_index(11)

        self.play(FadeIn(val_a, shift=UP * 0.12),
                  FadeIn(val_b, shift=UP * 0.12),
                  FadeIn(icon_b, shift=RIGHT * 0.10),
                  FadeIn(icon_a, shift=RIGHT * 0.10),
                  halo.animate.set_opacity(0.10),
                  FadeIn(energy_word, shift=DOWN * 0.15),
                  LaggedStart(FadeIn(before, scale=0.94),
                              FadeIn(after, scale=0.94), lag_ratio=0.20),
                  rate_func=rate_functions.ease_out_cubic)
        self.wait(0.3)

        self.ledger = VGroup(before, after, icon_b, icon_a, val_b, val_a)

    def act4_the_promise(self):

        self.play(
            FadeOut(self.ledger), FadeOut(self.energy_word),
            self.halo.animate.set_opacity(0.0),
            self.vignette.animate.set_opacity(0.0),
            Restore(self.camera.frame),
            run_time=1.5, rate_func=rate_functions.ease_in_out_cubic,
        )
        self.remove(self.halo, self.vignette)

        # The system resets ITSELF: both balls glide back to their pre-strike
        # marks. Not a scene reset — the same objects, returning.
        self.play(
            self.cue.animate.move_to(self.CUE_START),
            self.target.animate.move_to(self.TARGET_0),
            rate_func=rate_functions.ease_in_out_sine,
        )
        self.wait(0.3)

        tip_ready = self.CUE_START + LEFT * (self.R + 0.45)
        stick = make_cue_stick(tip_ready)
        stick.set_z_index(5)
        stick.shift(LEFT * 5.5)
        self.add(stick)
        self.play(stick.animate.shift(RIGHT * 5.5), run_time=0.9,
                  rate_func=rate_functions.ease_out_cubic)
        self.play(stick.animate.shift(LEFT * 0.18), run_time=0.6,
                  rate_func=rate_functions.ease_in_out_sine)   # the re-cock

        title = Text("What stays constant?", font=FONT, font_size=50,
                     color=COLOR_WHITE, weight=BOLD)
        title.move_to(UP * 2.25).set_z_index(10)
        self.play(FadeIn(title, shift=UP * 0.12),
                  rate_func=rate_functions.ease_out_cubic)

        # Hold the about-to-strike frame. Scene 2 inherits this tension.
        self.wait()
