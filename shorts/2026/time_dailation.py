from manim import *
import numpy as np

# ═════════════════════════════════════════════════════════════════════════
#  THE PHYSICS FRAME · SHORT — "Your Head Lives in the Future"
#  Vertical 9:16. Manim used as a kinetic graphic-design tool, not a diagram.
#  Seven acts, ~60–90 s. Stripped palette, big type, punchline visuals.
# ═════════════════════════════════════════════════════════════════════════

# ── VERTICAL CANVAS (1080×1920). frame 4.5 wide × 8.0 tall. ──
config.pixel_width   = 1080
config.pixel_height  = 1920
config.frame_width   = 4.5
config.frame_height  = 8.0
FRAME_W, FRAME_H = 4.5, 8.0

# ── PALETTE (series, reduced to essentials) ──
COLOR_BG     = "#0E1117"
COLOR_WHITE  = "#E5E5EA"
COLOR_AMBER  = "#FFCC00"   # grounded / past / gravity-heavy / causal arrows
COLOR_CYAN   = "#32ADE6"   # elevated / future / faster time
COLOR_VEC_F  = "#FF3B30"   # red — gravity force vectors (Acts 3 & 5)
COLOR_GREEN  = "#34C759"   # muted green — the punchline
COLOR_ORANGE = "#FF9500"   # the half-beat "slightly behind" flicker
COLOR_GROUND = "#8E8E93"
COLOR_BLUE   = "#1B3A6B"   # dark-blue Earth body
COLOR_BLUE_HI = "#3E6FB0"  # Earth rim/sheen

FONT       = "Segoe UI"
CLOCK_FONT = "Consolas"    # monospace → digits don't jitter (swap if unavailable)

config.background_color = COLOR_BG

# ── ON-SCREEN COPY (English only, per series rule). Flip here if needed. ──
WORD_PUNCH = "True."        # was "Sach." — on-screen text stays English
LABEL_LIFE = "Full Life"    # was "Poori Zindagi"

# Head-clock lead. Exaggerated far past real GR so the last decimals visibly
# drift inside the 3 s hold. Lower it toward 0 to make the divergence subtler.
EPS = 0.0013


# ═════════════════════════════════════════════════════════════════════════
#  HELPERS
# ═════════════════════════════════════════════════════════════════════════
def fit_w(mob, frac=0.90):
    """Clamp a mobject to the narrow vertical frame so type never bleeds off."""
    maxw = FRAME_W * frac
    if mob.width > maxw:
        mob.scale_to_fit_width(maxw)
    return mob


def fmt_clock(secs):
    """Seconds → HH:MM:SS.mmm (monospace, stable width)."""
    secs = max(float(secs), 0.0)
    h = int(secs // 3600)
    m = int((secs % 3600) // 60)
    s = int(secs % 60)
    ms = int(round((secs - np.floor(secs)) * 1000.0))
    if ms >= 1000:
        ms -= 1000
        s += 1
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


def clock_text(secs, color, fs, anchor=None):
    t = Text(fmt_clock(secs), font=CLOCK_FONT, font_size=fs, color=color)
    fit_w(t, 0.92)
    if anchor is not None:
        t.move_to(anchor)
    return t


def fmt_short(secs):
    """Seconds → SS.cc (compact ticking readout for the satellite act)."""
    secs = max(float(secs), 0.0)
    s = int(secs)
    cs = int((secs - s) * 100)
    return f"{s:02d}.{cs:02d}"


def human_silhouette(height=5.0, color=COLOR_WHITE, sw=4.0):
    """Clean white-outline upright figure: head + capsule torso + limbs.
    Optional override: drop silhouette.png next to the script and it is used."""
    try:
        return ImageMobject("silhouette.png").scale_to_fit_height(height)
    except Exception:
        pass
    g = VGroup()
    head = Circle(radius=0.40, color=color, stroke_width=sw,
                  fill_opacity=0).move_to([0, 2.45, 0])
    neck = Line([0, 2.05, 0], [0, 1.85, 0], color=color, stroke_width=sw)
    torso = RoundedRectangle(width=1.0, height=2.0, corner_radius=0.34,
                             stroke_color=color, stroke_width=sw,
                             fill_opacity=0).move_to([0, 0.85, 0])
    arms = VGroup(
        Line([-0.48, 1.62, 0], [-0.60, -0.05, 0], color=color, stroke_width=sw),
        Line([0.48, 1.62, 0],  [0.60, -0.05, 0],  color=color, stroke_width=sw),
    )
    legs = VGroup(
        Line([-0.20, -0.15, 0], [-0.26, -2.45, 0], color=color, stroke_width=sw),
        Line([0.20, -0.15, 0],  [0.26, -2.45, 0],  color=color, stroke_width=sw),
    )
    g.add(torso, arms, legs, neck, head)
    g.scale_to_fit_height(height)
    return g


def make_earth(width=1.7):
    """Minimal dark-blue Earth disc with a soft rim highlight (no texture)."""
    r = width / 2
    body = Circle(radius=r, color=COLOR_BLUE, fill_opacity=1.0, stroke_width=0)
    body.set_sheen(0.25, UL)
    rim = Circle(radius=r, fill_opacity=0,
                 stroke_color=COLOR_BLUE_HI, stroke_width=2.5, stroke_opacity=0.7)
    return VGroup(body, rim)


def make_pin(color, scale=1.0):
    """A map-style location pin: round head with a hole + a downward tip."""
    head = Circle(radius=0.16 * scale, color=color, fill_opacity=1.0,
                  stroke_width=0)
    hole = Dot(radius=0.06 * scale, color=COLOR_BG).move_to(head)
    tip = Triangle(color=color, fill_opacity=1.0, stroke_width=0)
    tip.scale(0.14 * scale).rotate(PI)            # point downward
    tip.next_to(head, DOWN, buff=-0.05 * scale)
    g = VGroup(tip, head, hole)
    g.head = head
    return g


def causal_chain(tokens, fs, arrow_color=COLOR_AMBER, word_color=COLOR_WHITE):
    """Build a horizontal token chain (words white, ↑↓→ amber) for Act 2."""
    g = VGroup()
    for tok in tokens:
        col = arrow_color if tok in ("↑", "↓", "→") else word_color
        g.add(Text(tok, font=FONT, font_size=fs, weight=BOLD, color=col))
    g.arrange(RIGHT, buff=0.12)
    return fit_w(g)


def curved_spine(bottom, top, curv, color, sw=4.0, n=32):
    """A vertical line bowed sideways by `curv` (amount of arc at mid-height)."""
    pts = []
    for i in range(n + 1):
        s = i / n
        y = interpolate(bottom[1], top[1], s)
        x = bottom[0] + curv * np.sin(PI * s)
        pts.append([x, y, 0])
    v = VMobject(stroke_color=color, stroke_width=sw)
    v.set_points_smoothly(pts)
    return v


# ═════════════════════════════════════════════════════════════════════════
class Short_TimeDilation(MovingCameraScene):
    def construct(self):
        self.act1_hook()
        self.act2_chain()
        self.act3_body_closeup()
        self.act4_delta()
        self.act5_satellites()
        self.act6_gps()
        self.act7_close()

    # ───────────────────────────────────────────────────────── ACT 1 · HOOK
    def act1_hook(self):
        # One unforgettable image: a figure, two clocks, the head one ahead.
        fig = human_silhouette(height=5.0).move_to(DOWN * 0.1).set_z_index(2)
        self.play(FadeIn(fig, scale=0.97), run_time=0.8,
                  rate_func=rate_functions.ease_out_cubic)

        t = ValueTracker(0.0)
        head_anchor = fig.get_top() + UP * 0.55
        feet_anchor = fig.get_bottom() + DOWN * 0.55
        # head = future-leaning cyan, ticks fractionally faster; feet = amber.
        head_clock = always_redraw(
            lambda: clock_text(t.get_value() * (1 + EPS), COLOR_CYAN, 30,
                               head_anchor))
        feet_clock = always_redraw(
            lambda: clock_text(t.get_value(), COLOR_AMBER, 30, feet_anchor))

        # snap into existence simultaneously, both at 00:00:00.000
        self.add(head_clock, feet_clock)
        self.wait(0.4)
        # tick at real rate (linear — physics demands constant time); last
        # decimals drift apart on their own. No narration over this beat.
        self.play(t.animate.set_value(3.0), run_time=3.0, rate_func=linear)
        self.wait(0.5)

        head_clock.clear_updaters()
        feet_clock.clear_updaters()
        self.play(FadeOut(VGroup(fig, head_clock, feet_clock)), run_time=0.5)

    # ──────────────────────────────────────────────────────── ACT 2 · CHAIN
    def act2_chain(self):
        # Text is the visual. No diagram. Just the causal relationship, raw.
        line1 = Text("Gravity ↑ → Time ↓", font=FONT, font_size=42, weight=BOLD,
                     t2c={"↑": COLOR_AMBER, "→": COLOR_AMBER, "↓": COLOR_AMBER})
        fit_w(line1).move_to(UP * 0.9)
        # fast typewriter (~0.4s)
        self.play(AddTextLetterByLetter(line1), run_time=0.45)
        self.wait(0.6)

        # the full chain, dropping in like dominoes (left→right with a shift)
        line2 = causal_chain(
            ["Height", "↑", "→", "Gravity", "↓", "→", "Time", "↑"], fs=30)
        line2.move_to(DOWN * 0.5)
        self.play(LaggedStart(*[FadeIn(tok, shift=DOWN * 0.16) for tok in line2],
                              lag_ratio=0.14),
                  run_time=1.1, rate_func=rate_functions.ease_out_cubic)
        self.wait(1.5)   # let the viewer parse the chain in silence

        self.play(FadeOut(VGroup(line1, line2), shift=UP * 0.15), run_time=0.5)

    # ─────────────────────────────────────────────────── ACT 3 · BODY CLOSE-UP
    def act3_body_closeup(self):
        fig = human_silhouette(height=5.0).move_to(DOWN * 0.1).set_z_index(2)
        mid_y = fig.get_center()[1]

        # subtle two-zone field: warmer below the midpoint, cooler above it.
        lower = Rectangle(width=FRAME_W, height=(mid_y + FRAME_H / 2),
                          stroke_width=0, fill_color=COLOR_AMBER, fill_opacity=0.07)
        lower.move_to([0, (mid_y - FRAME_H / 2) / 2, 0]).set_z_index(0)
        upper = Rectangle(width=FRAME_W, height=(FRAME_H / 2 - mid_y),
                          stroke_width=0, fill_color=COLOR_CYAN, fill_opacity=0.07)
        upper.move_to([0, (mid_y + FRAME_H / 2) / 2, 0]).set_z_index(0)

        self.play(FadeIn(lower), FadeIn(upper),
                  FadeIn(fig, scale=0.97), run_time=0.7)

        # gravity differential drawn on the body: feet vector long/thick,
        # head vector short/thin (no external Earth needed).
        side_x = 0.95
        feet_vec = Arrow([side_x, mid_y - 1.4, 0], [side_x, mid_y - 2.3, 0],
                         buff=0, color=COLOR_VEC_F, stroke_width=7,
                         max_tip_length_to_length_ratio=0.30).set_z_index(3)
        head_vec = Arrow([side_x, mid_y + 1.9, 0], [side_x, mid_y + 1.45, 0],
                         buff=0, color=COLOR_VEC_F, stroke_width=3,
                         max_tip_length_to_length_ratio=0.34).set_z_index(3)
        self.play(GrowArrow(feet_vec), GrowArrow(head_vec), run_time=0.6)

        # the two clocks have been here all along — head faster, feet slower.
        t = ValueTracker(0.0)
        head_anchor = fig.get_top() + UP * 0.50
        feet_anchor = fig.get_bottom() + DOWN * 0.50
        head_clock = always_redraw(
            lambda: clock_text(t.get_value() * 1.018, COLOR_CYAN, 26, head_anchor))
        feet_clock = always_redraw(
            lambda: clock_text(t.get_value(), COLOR_AMBER, 26, feet_anchor))
        self.add(head_clock, feet_clock)
        self.play(t.animate.set_value(2.2), run_time=2.0, rate_func=linear)

        head_clock.clear_updaters()
        feet_clock.clear_updaters()

        # "...your feet live in the past" — feet clock flickers orange, a
        # heartbeat one beat late, then settles back.
        self.play(feet_clock.animate.set_color(COLOR_ORANGE).set_opacity(0.8),
                  run_time=0.25, rate_func=rate_functions.ease_out_sine)
        self.play(feet_clock.animate.set_color(COLOR_AMBER).set_opacity(1.0),
                  run_time=0.25, rate_func=rate_functions.ease_in_sine)
        self.wait(0.6)

        self.play(FadeOut(VGroup(fig, feet_vec, head_vec,
                                 head_clock, feet_clock)),
                  FadeOut(lower), FadeOut(upper), run_time=0.5)

    # ──────────────────────────────────────────────────────── ACT 4 · DELTA
    def act4_delta(self):
        # The reality check. Deadpan. Two clocks, then the absurdly small gap.
        head = clock_text(0.0, COLOR_CYAN, 30, UP * 1.55)
        feet = clock_text(0.0, COLOR_AMBER, 30, UP * 0.65)
        self.play(FadeIn(head, shift=DOWN * 0.1),
                  FadeIn(feet, shift=UP * 0.1), run_time=0.6)

        # the lifetime axis: a thin dotted span labelled "Full Life".
        life = DashedLine([-FRAME_W / 2 + 0.4, -0.4, 0],
                          [FRAME_W / 2 - 0.4, -0.4, 0],
                          color=COLOR_GROUND, stroke_width=2, dash_length=0.12)
        life_lab = Text(LABEL_LIFE, font=FONT, font_size=22, slant=ITALIC,
                        color=COLOR_GROUND).next_to(life, DOWN, buff=0.18)
        self.play(Create(life), FadeIn(life_lab), run_time=0.6)
        self.wait(0.8)

        # collapse the whole frame into one number: a counter spins up and locks.
        self.play(FadeOut(VGroup(head, feet, life, life_lab)), run_time=0.4)

        cnt = ValueTracker(0.0)
        number = always_redraw(
            lambda: Text(f"≈ {int(round(cnt.get_value()))}", font=FONT,
                         font_size=96, weight=BOLD, color=COLOR_WHITE)
            .move_to(UP * 0.45))
        self.add(number)
        # slot-machine spin → lock (ease-out so it snaps to a stop)
        self.play(cnt.animate.set_value(90), run_time=0.8,
                  rate_func=rate_functions.ease_out_expo)
        number.clear_updaters()
        ns = Text("nanoseconds", font=FONT, font_size=40, weight=BOLD,
                  color=COLOR_WHITE).next_to(number, DOWN, buff=0.30)
        self.play(FadeIn(ns, shift=UP * 0.1), run_time=0.4)
        self.wait(0.7)

        # the smallness + the blunt word land together: a joke and a fact.
        full = VGroup(number, ns)
        self.play(full.animate.scale(0.45).move_to(UP * 0.9), run_time=0.6,
                  rate_func=rate_functions.ease_in_out_sine)
        punch = Text(WORD_PUNCH, font=FONT, font_size=84, weight=BOLD,
                     color=COLOR_GREEN).move_to(DOWN * 0.6)
        self.play(FadeIn(punch, scale=0.6), run_time=0.4)
        # sub-bass thud: one instant 1.0 → 1.03 nudge, then rest.
        self.play(punch.animate.scale(1.03), run_time=0.06)
        self.play(punch.animate.scale(1 / 1.03), run_time=0.06)
        self.wait(1.1)

        self.play(FadeOut(VGroup(full, punch)), run_time=0.5)

    # ───────────────────────────────────────────────────── ACT 5 · SATELLITES
    def act5_satellites(self):
        # Same two-clocks-two-altitudes grammar, scaled to planetary geometry.
        C = DOWN * 1.6
        earth = make_earth(1.7).move_to(C).set_z_index(2)
        R = 1.75
        ring = DashedVMobject(
            Circle(radius=R, color=COLOR_GROUND, stroke_width=1.6),
            num_dashes=64).set_stroke(opacity=0.5).move_to(C)

        ground_dot = Dot(C + UP * 0.85, radius=0.07, color=COLOR_WHITE
                         ).set_z_index(3)
        ang = ValueTracker(105 * DEGREES)
        sat = always_redraw(lambda: Dot(
            C + R * np.array([np.cos(ang.get_value()),
                             np.sin(ang.get_value()), 0]),
            radius=0.08, color=COLOR_WHITE).set_z_index(3))

        self.play(FadeIn(earth, scale=0.7), Create(ring), run_time=0.8)
        self.play(FadeIn(ground_dot, scale=0.5), run_time=0.3)
        self.add(sat)

        # the real-number tag on the satellite (cyan = faster).
        tag = Text("+38 µs/day", font=FONT, font_size=24, weight=BOLD,
                   color=COLOR_CYAN).to_edge(UP, buff=0.6)
        self.play(FadeIn(tag, shift=DOWN * 0.1), run_time=0.4)

        # two ticking clocks: satellite obviously faster than the ground.
        tt = ValueTracker(0.0)
        sat_clock = always_redraw(lambda: Text(
            fmt_short(tt.get_value() * 1.7), font=CLOCK_FONT, font_size=24,
            color=COLOR_CYAN).move_to(
                C + (R + 0.55) * np.array([np.cos(ang.get_value()),
                                           np.sin(ang.get_value()), 0])))
        gnd_clock = always_redraw(lambda: Text(
            fmt_short(tt.get_value()), font=CLOCK_FONT, font_size=24,
            color=COLOR_AMBER).next_to(earth, RIGHT, buff=0.15).shift(UP * 0.1))
        self.add(sat_clock, gnd_clock)

        # let the satellite sweep while both clocks run — the gap is legible.
        self.play(ang.animate.set_value(105 * DEGREES - PI),
                  tt.animate.set_value(4.0),
                  run_time=3.4, rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.6)

        for m in (sat, sat_clock, gnd_clock):
            m.clear_updaters()
        self.play(FadeOut(VGroup(earth, ring, ground_dot, sat, tag,
                                 sat_clock, gnd_clock)), run_time=0.6)

    # ─────────────────────────────────────────────────────────── ACT 6 · GPS
    def act6_gps(self):
        # The scroll-stopper. One Manim-drawn phone, two pins, a 10 km gap.
        phone = RoundedRectangle(width=FRAME_W * 0.72, height=FRAME_H * 0.62,
                                 corner_radius=0.28, stroke_color=COLOR_GROUND,
                                 stroke_width=3, fill_color="#11161D",
                                 fill_opacity=1.0).move_to(ORIGIN)
        notch = RoundedRectangle(width=0.9, height=0.14, corner_radius=0.07,
                                 stroke_width=0, fill_color=COLOR_GROUND,
                                 fill_opacity=0.5).next_to(phone.get_top(),
                                                           DOWN, buff=0.16)
        # faint map texture — a couple of restrained "roads".
        roads = VGroup(
            Line(phone.get_left() + RIGHT * 0.3 + UP * 0.4,
                 phone.get_right() + LEFT * 0.3 + DOWN * 0.6,
                 color=COLOR_GROUND, stroke_width=2, stroke_opacity=0.18),
            Line(phone.get_top() + DOWN * 0.9 + LEFT * 0.4,
                 phone.get_bottom() + UP * 0.9 + RIGHT * 0.5,
                 color=COLOR_GROUND, stroke_width=2, stroke_opacity=0.18),
        )
        self.play(FadeIn(phone, scale=0.96), FadeIn(notch), run_time=0.7)
        self.play(Create(roads), run_time=0.5)

        # the correct pin is placed first.
        pin_ok = make_pin(COLOR_GREEN, scale=1.1).move_to(LEFT * 0.55 + UP * 0.4)
        lbl_ok = Text("You (actual)", font=FONT, font_size=20, weight=BOLD,
                      color=COLOR_GREEN).next_to(pin_ok, UP, buff=0.12)
        fit_w(lbl_ok, 0.42)
        self.play(FadeIn(pin_ok, shift=DOWN * 0.2),
                  FadeIn(lbl_ok, shift=DOWN * 0.1), run_time=0.6)
        self.wait(0.3)

        # the wrong pin SLIDES in — you feel the wrongness as motion.
        pin_bad = make_pin(COLOR_VEC_F, scale=1.1)
        pin_bad.move_to(RIGHT * 0.85 + DOWN * 1.4)
        lbl_bad = Text("You (no GR fix)", font=FONT, font_size=20, weight=BOLD,
                       color=COLOR_VEC_F).next_to(pin_bad, DOWN, buff=0.12)
        fit_w(lbl_bad, 0.46)
        pin_bad_start = pin_bad.copy().shift(RIGHT * 2.0 + UP * 0.3).set_opacity(0)
        pin_bad.become(pin_bad_start)
        self.add(pin_bad)
        self.play(pin_bad.animate.move_to(RIGHT * 0.85 + DOWN * 1.4)
                  .set_opacity(1.0),
                  FadeIn(lbl_bad, shift=UP * 0.1),
                  run_time=0.7, rate_func=rate_functions.ease_out_cubic)

        # the 10 km gap snaps in between them.
        gap = DoubleArrow(pin_ok.head.get_center(), pin_bad.head.get_center(),
                          buff=0.18, color=COLOR_VEC_F, stroke_width=3,
                          max_tip_length_to_length_ratio=0.14)
        km = Text("10 km", font=FONT, font_size=32, weight=BOLD,
                  color=COLOR_VEC_F).move_to(gap.get_center() + UP * 0.28
                                             + RIGHT * 0.1)
        self.play(GrowFromCenter(gap), FadeIn(km, scale=0.6), run_time=0.5)
        self.wait(1.5)

        self.play(FadeOut(VGroup(phone, notch, roads, pin_ok, lbl_ok,
                                 pin_bad, lbl_bad, gap, km)), run_time=0.6)

    # ───────────────────────────────────────────────────────── ACT 7 · CLOSE
    def act7_close(self):
        # The emotional landing. Time is not a flat river; it curves.
        fig = human_silhouette(height=5.0).move_to(DOWN * 0.1).set_z_index(2)
        self.play(FadeIn(fig, scale=0.97), run_time=0.8,
                  rate_func=rate_functions.ease_out_sine)

        bottom = fig.get_bottom()
        top = fig.get_top()
        curv = ValueTracker(0.30)   # a subtle initial bow along the body
        spine = always_redraw(
            lambda: curved_spine(bottom, top, curv.get_value(),
                                 COLOR_CYAN, sw=4.0).set_z_index(3))
        self.play(fig.animate.set_opacity(0.45), FadeIn(spine), run_time=0.8)
        self.wait(0.5)

        # "...it curves" — the only truly slow beat: it warps, then settles.
        self.play(curv.animate.set_value(0.62), run_time=1.5,
                  rate_func=rate_functions.ease_in_out_sine)
        self.play(curv.animate.set_value(0.50), run_time=0.8,
                  rate_func=rate_functions.ease_in_out_sine)

        # the figure fades, leaving only the curve.
        spine.clear_updaters()
        self.play(FadeOut(fig), run_time=0.9)

        # the head — top of the curve — pulses once, warmly, a little ahead.
        head_pt = spine.get_end()
        glow = Dot(head_pt, radius=0.5, color=COLOR_CYAN,
                   fill_opacity=0.0, stroke_width=0).set_z_index(2)
        dot = Dot(head_pt, radius=0.09, color=COLOR_CYAN).set_z_index(4)
        self.add(glow)
        self.play(FadeIn(dot, scale=0.5), run_time=0.4)
        self.play(dot.animate.scale(1.5), glow.animate.set_opacity(0.35),
                  run_time=0.5, rate_func=rate_functions.ease_out_sine)
        self.play(dot.animate.scale(1 / 1.5), glow.animate.set_opacity(0.0),
                  run_time=0.5, rate_func=rate_functions.ease_in_out_sine)

        # final frame: just the curved line and the dot. Hold — let it land.
        self.wait(1.5)
        self.play(FadeOut(VGroup(spine, dot, glow)), run_time=1.0,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.5)   # hard cut to black happens in Premiere
