#!/usr/bin/env python3
"""news-image-20261118 round 4 — one-page broadsheet of 18 Nov 2026 world news.
Draws everything from scratch with PIL. Deterministic: no randomness, no time.
Usage: python3 render.py  -> writes entry.png next to this file.
"""
import os, math
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024
CREAM = (247, 243, 232)
PAPER = (251, 248, 240)
INK = (24, 28, 36)
NAVY = (18, 32, 56)
NAVY2 = (28, 48, 84)
RED = (178, 34, 34)
RED2 = (205, 60, 50)
TEAL = (14, 110, 110)
GOLD = (198, 148, 42)
GREY = (110, 108, 100)
RULE = (150, 142, 122)

def F(name, size):
    return ImageFont.truetype(os.path.join(HERE, "fonts", name + ".ttf"), size)

SERIF = lambda s: F("LiberationSerif-Regular", s)
SERIFB = lambda s: F("LiberationSerif-Bold", s)
SERIFI = lambda s: F("LiberationSerif-Italic", s)
SANS = lambda s: F("LiberationSans-Regular", s)
SANSB = lambda s: F("LiberationSans-Bold", s)

def wrap(draw, text, font, maxw):
    words = text.split()
    lines, cur = [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if draw.textlength(t, font=font) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines

def vgrad(img, box, top, bot):
    x0, y0, x1, y1 = box
    h = max(1, y1 - y0)
    strip = Image.new("RGB", (1, h))
    px = strip.load()
    for i in range(h):
        t = i / (h - 1)
        px[0, i] = tuple(int(top[c] + (bot[c] - top[c]) * t) for c in range(3))
    img.paste(strip.resize((x1 - x0, h)), (x0, y0))

def hgrad(img, box, left, right):
    x0, y0, x1, y1 = box
    w = max(1, x1 - x0)
    strip = Image.new("RGB", (w, 1))
    px = strip.load()
    for i in range(w):
        t = i / (w - 1)
        px[i, 0] = tuple(int(left[c] + (right[c] - left[c]) * t) for c in range(3))
    img.paste(strip.resize((w, y1 - y0)), (x0, y0))

def stars(d, box, n, seed, ymax=None):
    x0, y0, x1, y1 = box
    if ymax is not None:
        y1 = min(y1, ymax)
    s = seed
    for _ in range(n):
        s = (s * 1103515245 + 12345) & 0x7FFFFFFF
        x = x0 + s % max(1, (x1 - x0))
        s = (s * 1103515245 + 12345) & 0x7FFFFFFF
        y = y0 + s % max(1, (y1 - y0))
        s = (s * 1103515245 + 12345) & 0x7FFFFFFF
        r = 1 + s % 2
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 240))

def chip(d, x, y, text, font, bg=RED, fg=(255, 255, 255), pad=5):
    w = int(d.textlength(text, font=font)) + pad * 2
    h = font.size + pad
    d.rounded_rectangle([x, y, x + w, y + h], radius=3, fill=bg)
    d.text((x + pad, y + pad // 2 - 1), text, font=font, fill=fg)
    return w, h

def tagline(d, x, y, text, font, color=RED):
    d.text((x, y), text, font=font, fill=color)

def headline(d, x, y, text, font, maxw, color=INK, lh=None):
    lines = wrap(d, text, font, maxw)
    lh = lh or int(font.size * 1.08)
    for ln in lines:
        d.text((x, y), ln, font=font, fill=color)
        y += lh
    return y

def deck(d, x, y, text, font, maxw, color=(52, 54, 58), lh=None):
    lines = wrap(d, text, font, maxw)
    lh = lh or int(font.size * 1.25)
    for ln in lines:
        d.text((x, y), ln, font=font, fill=color)
        y += lh
    return y

# ---------------------------------------------------------------- data
REGIONS = [("EUROPE", 15, (38, 70, 130)), ("AMERICAS", 9, (178, 34, 34)),
           ("ASIA", 6, (14, 110, 110)), ("MIDDLE EAST", 4, (198, 120, 30)),
           ("OCEANIA", 4, (46, 130, 80)), ("GLOBAL", 4, (110, 70, 150)),
           ("AFRICA", 2, (120, 84, 50))]

FEATURES = [
 dict(n=1, tag="MIDDLE EAST · GULF WAR", scene="gulf",
      head="U.S. JETS HIT IRAN; GULF STATES UNDER FIRE", chip="DRONES DOWNED",
      deck="U.S. jets hit an IRGC site on Qeshm; Iran's drones hit a U.S. radar in Bahrain — third attack in a week — and Kuwait."),
 dict(n=2, tag="EUROPE · UKRAINE", scene="kerch",
      head="KERCH BRIDGE'S ROAD ARCH FALLS INTO THE SEA", chip="SPAN DOWN",
      deck="A second strike in two days brings down the 19-km bridge's road arch; 270 m of roadway in the water. Two killed."),
 dict(n=3, tag="ASIA · APEC SUMMIT", scene="apec",
      head="XI AND PUTIN OPEN APEC AS TRUMP LANDS", chip="3-WAY TALKS · THU",
      deck="Xi and Putin denounce protectionism and sanctions in Shenzhen. Trump arrives from Manila; the three meet Thursday."),
 dict(n=4, tag="AMERICAS · U.S. SENATE", scene="alaska",
      head="PELTOLA WINS ALASKA; SENATE NOW 56–44", chip="9TH FLIP",
      deck="AP called it 144,302 to 131,844 — Democrats' 9th flip, largest majority since 2009."),
 dict(n=5, tag="AMERICAS · TECH", scene="nvidia",
      head="NVIDIA: $115.8B QUARTER", chip="$115.8BN",
      deck="Revenue up 103%; net income $65.3bn. First results since Huang resigned."),
 dict(n=6, tag="ASIA · WEATHER", scene="akvan",
      head="CYCLONE AKVAN BEARS DOWN ON INDIA", chip="LANDFALL FRI",
      deck="Landfall in Andhra Pradesh on Friday, gusts to 145 km/h; Odisha moves 200,000."),
 dict(n=7, tag="OCEANIA · WEATHER", scene="xavier",
      head="CYCLONE XAVIER, CAT 5, HITS COOK ISLANDS", chip="GUSTS 315 KM/H",
      deck="Winds 220 km/h, gusts to 315 km/h. First Cat 5 in the region since Lola in 2023."),
 dict(n=8, tag="GLOBAL · SPACE", scene="voyager",
      head="VOYAGER 1 — ONE LIGHT-DAY OUT", chip="25.9BN KM",
      deck="First human-made object one light-day out: 25.9bn km. A signal now takes 24 hours."),
 dict(n=9, tag="MIDDLE EAST · GAZA", scene="gaza",
      head="GAZA TRUCE MAY COLLAPSE", chip="WINTER IN TENTS",
      deck="The ceasefire could fall apart. Two million face another winter in tents; 70,000 flooded."),
 dict(n=10, tag="EUROPE · ECONOMY", scene="uk",
      head="UK INFLATION 3.6%, HIGHEST IN A YEAR", chip="DIESEL 199.5P",
      deck="October CPI up from 3.5% (ONS). Motor fuel up 33.2% in a year; diesel a record 199.5p."),
 dict(n=11, tag="AFRICA · SUDAN", scene="sudan",
      head="SUDAN DRONE TOLL: 1,630 CIVILIANS", chip="UN: 2,230 DEAD",
      deck="UN: drone strikes killed 1,630 civilians this year; 2,230 confirmed dead Jan–Oct."),
 dict(n=12, tag="AMERICAS · GAMES", scene="gta",
      head="GTA VI GOES ON SALE", chip="METACRITIC 99",
      deck="After a 13-year wait, the midnight launch rolls out from New Zealand. Metacritic 99."),
 dict(n=13, tag="GLOBAL · HEALTH", scene="health",
      head="MEASLES BACK; EBOLA PASSES 11,400", chip="5,412 CASES",
      deck="U.S. loses measles-free status held since 2000. Ebola in DR Congo: 11,432 cases, 5,593 dead."),
]

NUMBERS = [
 ("$115.8bn", "Nvidia quarterly revenue, up 103%"),
 ("145 km/h", "Akvan forecast gusts at landfall"),
 ("200,000", "people Odisha is moving from the coast"),
 ("25.9bn km", "Voyager 1 from Earth: one light-day"),
]

BRIEFS = [
 (14, "World Court to rule Thursday", "ICJ decides the Myanmar genocide case over the Rohingya."),
 (15, "Russian plane crashes", "An-12 down in Siberia, Kemerovo; 19 dead, ministry blames a fault."),
 (16, "Two earthquakes", "M6.0 in Papua New Guinea (GFZ); M5.3 in Romania, two hurt."),
 (17, "146,000 march in France", "Unions strike over pay and the cost of living; CGT claims 500,000."),
 (18, "Trump in Manila", "Meets Marcos and Quad partners; Thailand trade statement signed."),
 (19, "Mossad tip foils plot", "Greece and N. Macedonia break up an Iranian-run murder plot; 5 held."),
 (20, "U.S. tech outages", "Banks, flights and the NSA hit; at least 8 major outages in a week."),
 (21, "New Knesset president", "Matan Kahana elected 66–52 over Ofir Katz, a blow to Netanyahu."),
 (22, "Britain and Australia act", "UK blacklists 8 builders; Australia lists Weiss, Amana, Nachala."),
 (23, "Markets slide", "S&P 500 −1.03%, Nasdaq −0.74% at Tuesday's close; VIX 25.46 (+11%)."),
 (24, "Houthis press on Aden", "Fighters now ~60 km from Yemen's seat of government."),
 (25, "U.S. criticises Kyiv strikes", "Pentagon faults deep strikes; Germany calls that 'stupid'."),
 (26, "Waymo off the freeways", "Driverless taxi rides halted on all U.S. freeways after a California ban."),
 (27, "Spy suspect moved", "U.S. soldier held in the UK over Russia spy suspicion moved to U.S. custody."),
 (28, "Turkey seizes Sozcu TV", "Government takes control of the opposition broadcaster; 4 detained."),
 (29, "Ethiopia–Eritrea fighting", "Border clashes resume, raising fears of a wider war."),
 (30, "South Korea lifts forecast", "Seoul's KDI raises 2027 growth forecast to 3.9% on the chip boom."),
 (31, "Serbia's new parliament", "Student List majority convenes; EU referendum planned."),
 (32, "Anthropic to list", "AI lab set to list on Nasdaq on Thursday 19 November as ANT, $70–$78."),
 (33, "M1.1 solar flare", "M1.1-class flare recorded on the Sun, with a CME behind it."),
 (34, "EU return hubs", "Council of Europe chief warns five states' Rwanda hub plan must meet rights law."),
 (35, "France–Malaysia deal", "Strategic partnership agreed, including rare-earths cooperation."),
 (36, "Brazilian real falls", "Real slides as Lula's fiscal plan disappoints investors; R$5.78 to the dollar."),
 (37, "Fiji declares disaster", "National disaster declared over the El Niño drought; $20m for water."),
 (38, "Pattinson is the new Bond", "Amazon MGM names Robert Pattinson 007; Villeneuve directs Bond 26."),
 (39, "Zverev into ATP Finals knockouts", "Beats Shelton 6-2, 7-6(4) in Turin; first semi-finalist."),
 (40, "Northern Ireland up", "1-1 draw in Hungary seals promotion to the Nations League top tier."),
 (41, "Tiger Woods to return", "Will play the Hero World Challenge, Dec 3–6, after two years out."),
 (42, "Cambridge Dictionary", "'human' is word of the year, chosen as AI blurs what it means to be human."),
 (43, "Tame Impala sweeps the ARIAs", "Seven awards in Sydney, incl. Album of the Year for Deadbeat."),
 (44, "Peru quake, no damage", "Magnitude 5.9 quake off Peru's south coast, no damage reported."),
]

def draw_scene(name, img, box):
    """Render a scene into a temp image so nothing can bleed outside its box."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    tmp = Image.new("RGB", (w, h), CREAM)
    td = ImageDraw.Draw(tmp)
    SCENES[name](tmp, td, (0, 0, w, h))
    img.paste(tmp, (x0, y0))
def scene_gulf(img, d, b):
    x0, y0, x1, y1 = b
    vgrad(img, b, (8, 16, 40), (20, 42, 78))
    stars(d, b, 60, 7, ymax=y0 + (y1 - y0) // 2)
    d.ellipse([x1 - 44, y0 + 4, x1 - 14, y0 + 34], fill=(232, 228, 200))
    # sea
    sy = y0 + int((y1 - y0) * 0.58)
    d.rectangle([x0, sy, x1, y1], fill=(10, 30, 58))
    for i, yy in enumerate(range(sy + 6, y1 - 4, 9)):
        off = (i % 3) * 14
        for xx in range(x0 + 6 + off, x1 - 20, 46):
            d.arc([xx, yy, xx + 26, yy + 7], 200, 340, fill=(70, 110, 160), width=2)
    # coastline silhouette (top of sea) with markers
    d.polygon([(x0, sy), (x0 + 40, sy - 14), (x0 + 90, sy - 6), (x0 + 150, sy - 16),
               (x0 + 210, sy - 8), (x1, sy - 12), (x1, sy), (x0, sy)], fill=(16, 26, 48))
    # burning rig, right (kept inside the box)
    rx, ry = x1 - 112, sy - 40
    d.rectangle([rx, ry + 22, rx + 56, sy], fill=(30, 34, 40))
    for lx in (rx + 6, rx + 26, rx + 46):
        d.line([lx, ry + 22, lx, ry], fill=(30, 34, 40), width=3)
    d.rectangle([rx - 4, ry - 2, rx + 60, ry + 4], fill=(30, 34, 40))
    d.polygon([(rx + 14, ry - 2), (rx + 24, ry - 24), (rx + 34, ry - 2)], fill=(255, 170, 40))
    d.polygon([(rx + 24, ry - 2), (rx + 30, ry - 18), (rx + 38, ry - 2)], fill=(255, 90, 20))
    d.ellipse([rx + 6, ry - 34, rx + 50, ry - 4], outline=(255, 150, 60), width=2)
    for i in range(3):
        d.ellipse([rx + 10 + i * 12, ry - 40 - i * 6, rx + 34 + i * 12, ry - 22 - i * 6],
                  fill=(70, 70, 78))
    # warship, left
    wx, wy = x0 + 14, sy - 6
    d.polygon([(wx, wy), (wx + 118, wy), (wx + 104, wy + 12), (wx + 8, wy + 12)], fill=(22, 26, 34))
    d.rectangle([wx + 34, wy - 16, wx + 58, wy], fill=(22, 26, 34))
    d.line([wx + 44, wy - 16, wx + 44, wy - 34], fill=(22, 26, 34), width=3)
    d.ellipse([wx + 38, wy - 40, wx + 50, wy - 28], outline=(200, 200, 200), width=2)
    d.line([wx + 62, wy - 12, wx + 62, wy - 26], fill=(22, 26, 34), width=2)
    # drone + intercept flash
    dx, dy = x0 + 150, y0 + 26
    d.ellipse([dx - 8, dy - 3, dx + 8, dy + 3], fill=(220, 220, 220))
    d.line([dx - 16, dy, dx + 16, dy], fill=(220, 220, 220), width=2)
    d.line([dx + 26, dy + 10, dx + 46, dy + 26], fill=(255, 200, 80), width=2)
    d.ellipse([dx + 42, dy + 22, dx + 54, dy + 34], fill=(255, 190, 60))
    # markers
    for mx, lab in ((x0 + 46, "QESHM"), (x0 + 168, "BAHRAIN"), (x1 - 30, "KUWAIT")):
        d.ellipse([mx - 3, sy - 20, mx + 3, sy - 14], fill=(255, 210, 90), outline=(0, 0, 0))
        d.text((mx - 14, sy - 30), lab, font=SANSB(7), fill=(255, 230, 150))

def scene_kerch(img, d, b):
    x0, y0, x1, y1 = b
    vgrad(img, b, (250, 190, 110), (235, 120, 70))
    d.ellipse([x1 - 70, y0 + 6, x1 - 26, y0 + 50], fill=(255, 226, 140))
    sy = y0 + int((y1 - y0) * 0.62)
    d.rectangle([x0, sy, x1, y1], fill=(36, 84, 116))
    for i, yy in enumerate(range(sy + 5, y1 - 4, 8)):
        off = (i % 3) * 12
        for xx in range(x0 + 4 + off, x1 - 18, 40):
            d.arc([xx, yy, xx + 22, yy + 6], 200, 340, fill=(110, 170, 200), width=2)
    # bridge deck, left intact
    dy = sy - 44
    d.rectangle([x0, dy, x0 + 150, dy + 8], fill=(70, 74, 80))
    d.rectangle([x0 + 8, dy - 26, x0 + 16, dy], fill=(70, 74, 80))
    d.rectangle([x0 + 78, dy - 26, x0 + 86, dy], fill=(70, 74, 80))
    d.arc([x0 + 8, dy - 34, x0 + 150, dy + 6], 180, 360, fill=(70, 74, 80), width=4)
    # collapsed span: tilted deck falling into sea
    d.polygon([(x0 + 158, dy + 2), (x0 + 250, dy + 34), (x0 + 246, dy + 42),
               (x0 + 154, dy + 10)], fill=(90, 94, 100))
    d.polygon([(x0 + 252, dy + 36), (x0 + 296, sy + 2), (x0 + 288, sy + 8),
               (x0 + 246, dy + 44)], fill=(70, 74, 80))
    d.line([x0 + 158, dy + 2, x0 + 250, dy + 34], fill=(50, 54, 60), width=2)
    # splash + smoke (kept inside the box)
    for sx, sr in ((x0 + 268, 14), (x0 + 288, 10), (x0 + 252, 8)):
        d.ellipse([sx - sr, sy - 6, sx + sr, sy + 8], fill=(220, 235, 240))
    for i in range(4):
        d.ellipse([x0 + 196 + i * 16, dy - 40 - i * 6, x0 + 228 + i * 16, dy - 12 - i * 6],
                  fill=(90, 88, 84))
    d.ellipse([x0 + 210, dy - 52, x0 + 246, dy - 24], fill=(70, 68, 64))
    # right pillar standing
    d.rectangle([x1 - 26, dy - 30, x1 - 18, sy], fill=(70, 74, 80))

def scene_apec(img, d, b):
    x0, y0, x1, y1 = b
    vgrad(img, b, (52, 38, 86), (214, 110, 80))
    d.ellipse([x0 + 30, y0 + 10, x0 + 74, y0 + 54], fill=(255, 210, 130))
    gy = y0 + int((y1 - y0) * 0.66)
    # skyline
    heights = [34, 50, 38, 60, 44, 54, 36, 64, 42, 52, 32]
    bw = (x1 - x0) // len(heights)
    for i, hh in enumerate(heights):
        bx = x0 + i * bw
        d.rectangle([bx + 1, gy - hh, bx + bw - 1, gy], fill=(34, 26, 58))
        for wy in range(gy - hh + 8, gy - 6, 12):
            for wx in range(bx + 5, bx + bw - 5, 9):
                if (wx + wy) % 23 < 11:
                    d.rectangle([wx, wy, wx + 3, wy + 4], fill=(255, 205, 110))
    # ground + red carpet
    d.rectangle([x0, gy, x1, y1], fill=(46, 34, 60))
    d.polygon([(x0 + 60, y1), (x0 + 130, gy + 6), (x0 + 210, gy + 6), (x0 + 280, y1)],
              fill=(178, 34, 34))
    d.line([x0 + 60, y1, x0 + 130, gy + 6], fill=(255, 220, 120), width=2)
    d.line([x0 + 280, y1, x0 + 210, gy + 6], fill=(255, 220, 120), width=2)
    # three flags on poles
    flags = [((210, 40, 40), "CN"), ((240, 240, 240), "RU"), ((60, 80, 180), "US")]
    fx = x0 + 34
    for col, _ in flags:
        d.line([fx, gy - 48, fx, gy + 2], fill=(220, 220, 220), width=2)
        d.rectangle([fx, gy - 48, fx + 34, gy - 32], fill=col, outline=(255, 255, 255))
        if col == (240, 240, 240):
            d.rectangle([fx, gy - 43, fx + 34, gy - 38], fill=(30, 60, 180))
            d.rectangle([fx, gy - 38, fx + 34, gy - 32], fill=(200, 30, 30))
        if col == (60, 80, 180):
            for s in range(3):
                d.rectangle([fx, gy - 48 + s * 5, fx + 34, gy - 45 + s * 5], fill=(255, 255, 255))
            d.rectangle([fx, gy - 48, fx + 14, gy - 38], fill=(30, 40, 110))
        fx += 52
    # plane silhouette
    px, py = x1 - 96, y0 + 22
    d.ellipse([px, py, px + 56, py + 10], fill=(20, 20, 30))
    d.polygon([(px + 44, py + 2), (px + 66, py - 8), (px + 66, py + 4)], fill=(20, 20, 30))
    d.polygon([(px + 18, py + 8), (px + 30, py + 20), (px + 36, py + 8)], fill=(20, 20, 30))
    d.polygon([(px + 34, py + 8), (px + 44, py + 18), (px + 48, py + 8)], fill=(20, 20, 30))

def scene_alaska(img, d, b):
    x0, y0, x1, y1 = b
    h = y1 - y0
    vgrad(img, b, (176, 208, 228), (238, 240, 232))
    # mountains
    d.polygon([(x0, y1), (x0 + 60, y0 + 18), (x0 + 120, y1)], fill=(140, 160, 180))
    d.polygon([(x0 + 60, y0 + 18), (x0 + 78, y0 + 34), (x0 + 44, y0 + 34)], fill=(255, 255, 255))
    d.polygon([(x0 + 90, y1), (x0 + 170, y0 + 28), (x1, y1)], fill=(120, 142, 165))
    d.polygon([(x0 + 170, y0 + 28), (x0 + 184, y0 + 42), (x0 + 156, y0 + 42)], fill=(255, 255, 255))
    gy = y1 - int(h * 0.30)
    d.rectangle([x0, gy, x1, y1], fill=(232, 234, 228))
    # capitol dome
    cx = x0 + (x1 - x0) // 2
    d.rectangle([cx - 52, gy - 20, cx + 52, gy], fill=(240, 236, 222))
    d.rectangle([cx - 30, gy - 34, cx + 30, gy - 20], fill=(240, 236, 222))
    d.pieslice([cx - 26, gy - 52, cx + 26, gy - 18], 180, 360, fill=(240, 236, 222))
    d.line([cx, gy - 56, cx, gy - 52], fill=(120, 110, 90), width=2)
    d.ellipse([cx - 3, gy - 60, cx + 3, gy - 54], fill=(198, 148, 42))
    for i in range(-2, 3):
        d.rectangle([cx + i * 16 - 4, gy - 16, cx + i * 16 + 4, gy], fill=(150, 142, 122))
    # seat grid 10x10 = 100 seats, 56 blue / 44 red (small, top right)
    gx, gy2 = x1 - 46, y0 + 6
    for i in range(100):
        r, c = divmod(i, 10)
        col = (38, 70, 150) if i < 56 else (178, 40, 40)
        d.rectangle([gx + c * 4, gy2 + r * 4, gx + c * 4 + 3, gy2 + r * 4 + 3], fill=col)

def scene_nvidia(img, d, b):
    x0, y0, x1, y1 = b
    vgrad(img, b, (10, 40, 24), (16, 90, 52))
    # circuit traces
    for i in range(6):
        yy = y0 + 12 + i * 12
        d.line([x0, yy, x1 - 30, yy], fill=(40, 140, 90), width=1)
        d.ellipse([x1 - 32, yy - 3, x1 - 26, yy + 3], outline=(60, 200, 120), width=2)
    for i in range(5):
        xx = x0 + 18 + i * 26
        d.line([xx, y0, xx, y1 - 40], fill=(40, 140, 90), width=1)
    # chip
    cx, cy = x0 + (x1 - x0) // 2 - 34, y0 + (y1 - y0) // 2 - 26
    d.rectangle([cx - 6, cy - 6, cx + 74, cy + 58], fill=(8, 26, 18))
    d.rectangle([cx, cy, cx + 68, cy + 52], fill=(18, 90, 50), outline=(120, 230, 160), width=2)
    d.text((cx + 12, cy + 14), "NVDA", font=SANSB(16), fill=(220, 255, 230))
    d.text((cx + 12, cy + 32), "H200", font=SANSB(9), fill=(160, 230, 180))
    for i in range(6):
        d.line([cx + 8 + i * 11, cy - 6, cx + 8 + i * 11, cy], fill=(120, 230, 160), width=2)
        d.line([cx + 8 + i * 11, cy + 52, cx + 8 + i * 11, cy + 58], fill=(120, 230, 160), width=2)
    # rising bars + arrow
    pts = [(x0 + 12, y1 - 14), (x0 + 44, y1 - 26), (x0 + 76, y1 - 20),
           (x0 + 108, y1 - 38), (x0 + 140, y1 - 46), (x0 + 172, y1 - 62)]
    d.line(pts, fill=(255, 210, 90), width=3, joint="curve")
    d.polygon([(x0 + 172, y1 - 62), (x0 + 160, y1 - 60), (x0 + 170, y1 - 50)], fill=(255, 210, 90))

def _spiral(d, cx, cy, rmax, turns, color, width):
    pts = []
    steps = int(turns * 40)
    for i in range(steps + 1):
        t = i / steps
        ang = t * turns * 2 * math.pi
        r = rmax * (1 - t * 0.85)
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    d.line(pts, fill=color, width=width, joint="curve")

def scene_akvan(img, d, b):
    x0, y0, x1, y1 = b
    vgrad(img, b, (14, 90, 110), (120, 190, 205))
    # coastline (India east coast, stylised)
    d.polygon([(x0 + 150, y0), (x1, y0), (x1, y1), (x0 + 128, y1), (x0 + 138, y0 + 40),
               (x0 + 158, y0 + 70), (x0 + 146, y0 + 110)], fill=(206, 188, 140))
    d.text((x1 - 50, y0 + 58), "INDIA", font=SANSB(8), fill=(110, 90, 50))
    d.text((x1 - 58, y0 + 84), "ODISHA", font=SANSB(7), fill=(110, 90, 50))
    # sea waves
    for i, yy in enumerate(range(y0 + (y1 - y0) // 2, y1 - 6, 10)):
        off = (i % 3) * 12
        for xx in range(x0 + 4 + off, x0 + 130, 40):
            d.arc([xx, yy, xx + 22, yy + 6], 200, 340, fill=(200, 235, 245), width=2)
    # cyclone spiral over sea
    cx, cy = x0 + 62, y0 + 44
    _spiral(d, cx, cy, 42, 2.2, (255, 255, 255), 3)
    _spiral(d, cx, cy, 30, 2.2, (200, 235, 245), 2)
    d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=(255, 255, 255))
    # rain streaks
    for i in range(14):
        rx = x0 + 8 + (i * 37) % 150
        ry = y0 + 60 + (i * 23) % 40
        d.line([rx, ry, rx - 4, ry + 10], fill=(220, 240, 250), width=2)
    # landfall arrow
    d.line([cx + 40, cy + 26, x0 + 138, cy + 44], fill=(255, 210, 90), width=3)
    d.polygon([(x0 + 138, cy + 44), (x0 + 126, cy + 38), (x0 + 126, cy + 50)], fill=(255, 210, 90))
    d.text((x0 + 96, cy + 52), "FRI", font=SANSB(9), fill=(255, 230, 150))

def scene_xavier(img, d, b):
    x0, y0, x1, y1 = b
    vgrad(img, b, (24, 26, 52), (90, 60, 90))
    stars(d, b, 30, 11, ymax=y0 + 30)
    cx, cy = x0 + (x1 - x0) // 2, y0 + (y1 - y0) // 2 - 6
    rm = min(46, int((y1 - y0) * 0.58))
    _spiral(d, cx, cy, rm, 2.6, (240, 240, 250), 4)
    _spiral(d, cx, cy, int(rm * 0.7), 2.6, (255, 200, 120), 3)
    _spiral(d, cx, cy, int(rm * 0.42), 2.6, (255, 120, 80), 2)
    d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=(255, 255, 255))
    # sea + palms
    sy = y1 - 22
    d.rectangle([x0, sy, x1, y1], fill=(18, 60, 80))
    for i, yy in enumerate(range(sy + 4, y1 - 2, 7)):
        off = (i % 2) * 16
        for xx in range(x0 + 4 + off, x1 - 16, 36):
            d.arc([xx, yy, xx + 20, yy + 5], 200, 340, fill=(120, 190, 210), width=2)
    for px in (x0 + 16, x1 - 26):
        d.line([px, sy, px + 6, sy - 18], fill=(40, 90, 60), width=3)
        for ang in (-50, -20, 10, 40):
            a = math.radians(ang - 90)
            d.line([px + 6, sy - 18, px + 6 + 14 * math.cos(a), sy - 18 + 14 * math.sin(a)],
                   fill=(50, 140, 80), width=2)
    # rain
    for i in range(12):
        rx = x0 + 10 + (i * 41) % 170
        ry = y0 + 8 + (i * 19) % 46
        d.line([rx, ry, rx - 5, ry + 11], fill=(200, 210, 235), width=2)

def scene_voyager(img, d, b):
    x0, y0, x1, y1 = b
    vgrad(img, b, (2, 4, 16), (10, 16, 44))
    stars(d, b, 90, 23)
    # sun glow left
    sx, sy = x0 - 26, y0 + (y1 - y0) // 2
    for r, col in ((64, (60, 50, 20)), (44, (140, 110, 30)), (26, (255, 200, 90))):
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=col)
    # earth small, right
    ex, ey = x1 - 30, y0 + 20
    d.ellipse([ex - 10, ey - 10, ex + 10, ey + 10], fill=(60, 120, 200))
    d.ellipse([ex - 10, ey - 4, ex + 2, ey + 2], fill=(60, 170, 90))
    d.ellipse([ex - 2, ey + 4, ex + 10, ey + 10], fill=(60, 170, 90))
    d.ellipse([ex - 10, ey - 10, ex + 10, ey + 10], outline=(150, 200, 255), width=1)
    # dotted signal path earth -> probe
    px, py = x0 + (x1 - x0) // 2 + 8, y0 + (y1 - y0) // 2 + 6
    steps = 24
    for i in range(steps):
        t = i / steps
        xx = ex + (px - ex) * t
        yy = ey + (py - ey) * t
        d.ellipse([xx - 1, yy - 1, xx + 1, yy + 1], fill=(255, 220, 130))
    # probe: dish + boom + body
    d.line([px - 4, py - 4, px + 14, py - 16], fill=(200, 200, 210), width=2)
    d.ellipse([px + 12, py - 24, px + 30, py - 8], outline=(220, 220, 230), width=2)
    d.line([px - 4, py - 4, px + 16, py + 10], fill=(200, 200, 210), width=2)
    d.rectangle([px - 8, py - 6, px + 6, py + 6], fill=(200, 200, 210), outline=(120, 120, 130))
    d.line([px - 22, py - 2, px - 8, py - 2], fill=(200, 200, 210), width=3)
    d.ellipse([px - 26, py - 5, px - 20, py + 1], fill=(255, 200, 90))
    d.text((x0 + 8, y1 - 16), "ONE LIGHT-DAY FROM EARTH", font=SANSB(8), fill=(200, 210, 240))

def scene_gaza(img, d, b):
    x0, y0, x1, y1 = b
    vgrad(img, b, (96, 104, 122), (168, 158, 138))
    # broken buildings
    d.rectangle([x0 + 8, y0 + 30, x0 + 44, y1 - 30], fill=(70, 66, 60))
    d.polygon([(x0 + 8, y0 + 30), (x0 + 26, y0 + 18), (x0 + 44, y0 + 30)], fill=(70, 66, 60))
    d.rectangle([x1 - 46, y0 + 44, x1 - 8, y1 - 30], fill=(80, 76, 70))
    d.polygon([(x1 - 46, y0 + 44), (x1 - 27, y0 + 32), (x1 - 8, y0 + 44)], fill=(80, 76, 70))
    for bx, by in ((x0 + 16, y0 + 44), (x0 + 30, y0 + 60), (x1 - 36, y0 + 58), (x1 - 20, y0 + 74)):
        d.rectangle([bx, by, bx + 7, by + 9], fill=(220, 190, 110))
    # ground
    gy = y1 - 30
    d.rectangle([x0, gy, x1, y1], fill=(120, 108, 88))
    # tents row
    for i, tx in enumerate(range(x0 + 52, x1 - 52, 44)):
        ty = gy - 4 - (i % 2) * 6
        d.polygon([(tx, ty), (tx + 18, ty - 18), (tx + 36, ty)], fill=(226, 218, 196))
        d.polygon([(tx + 18, ty - 18), (tx + 26, ty - 6), (tx + 18, ty)], fill=(200, 190, 166))
        d.line([tx + 18, ty - 18, tx + 18, ty], fill=(140, 130, 110), width=1)
    # lantern glow
    lx, ly = x0 + (x1 - x0) // 2, gy - 26
    d.ellipse([lx - 14, ly - 14, lx + 14, ly + 14], fill=(255, 190, 90))
    d.ellipse([lx - 6, ly - 8, lx + 6, ly + 8], fill=(255, 220, 140))
    # rain
    for i in range(16):
        rx = x0 + 6 + (i * 43) % 180
        ry = y0 + 6 + (i * 17) % 44
        d.line([rx, ry, rx - 3, ry + 9], fill=(210, 215, 225), width=2)
    # puddle
    d.ellipse([x0 + 60, y1 - 12, x0 + 130, y1 - 4], fill=(90, 100, 115))

def scene_uk(img, d, b):
    x0, y0, x1, y1 = b
    vgrad(img, b, (250, 244, 230), (240, 214, 180))
    # chart bars rising
    base = y1 - 34
    for i, hh in enumerate((14, 22, 18, 30, 38)):
        bx = x0 + 12 + i * 22
        d.rectangle([bx, base - hh, bx + 14, base], fill=(178, 34, 34) if i == 4 else (200, 120, 100))
    d.line([(x0 + 10, base - 14), (x0 + 54, base - 22), (x0 + 98, base - 30), (x0 + 120, base - 44)],
           fill=(120, 30, 30), width=3, joint="curve")
    d.polygon([(x0 + 120, base - 44), (x0 + 110, base - 40), (x0 + 118, base - 32)], fill=(120, 30, 30))
    d.text((x0 + 12, y0 + 6), "CPI 3.6%", font=SANSB(11), fill=(120, 30, 30))
    # fuel pump
    px, py = x1 - 62, y1 - 62
    d.rectangle([px, py, px + 44, py + 56], fill=(34, 34, 40), outline=(200, 200, 200), width=2)
    d.rectangle([px + 8, py + 8, px + 36, py + 24], fill=(220, 230, 200))
    d.text((px + 11, py + 11), "199.5", font=SANSB(10), fill=(20, 20, 20))
    d.text((px + 11, py + 26), "p / litre", font=SANSB(8), fill=(220, 220, 220))
    d.rectangle([px + 14, py + 38, px + 30, py + 46], fill=(200, 40, 40))
    d.arc([px + 40, py + 6, px + 62, py + 40], 270, 90, fill=(34, 34, 40), width=3)
    d.rectangle([px + 56, py + 34, px + 62, py + 48], fill=(34, 34, 40))
    # pound coins
    for cx in (x0 + 130, x0 + 150, x0 + 170):
        d.ellipse([cx, y1 - 26, cx + 18, y1 - 8], fill=(198, 148, 42), outline=(140, 100, 20))
        d.text((cx + 5, y1 - 25), "£", font=SANSB(11), fill=(90, 60, 10))

def scene_sudan(img, d, b):
    x0, y0, x1, y1 = b
    vgrad(img, b, (60, 40, 30), (214, 130, 70))
    d.ellipse([x1 - 52, y0 + 8, x1 - 14, y0 + 46], fill=(255, 200, 120))
    # drone
    dx, dy = x0 + (x1 - x0) // 2, y0 + 22
    d.rectangle([dx - 16, dy - 3, dx + 16, dy + 3], fill=(30, 30, 34))
    d.line([dx - 26, dy - 8, dx - 16, dy], fill=(30, 30, 34), width=2)
    d.line([dx + 16, dy, dx + 26, dy - 8], fill=(30, 30, 34), width=2)
    d.ellipse([dx - 30, dy - 12, dx - 20, dy - 6], outline=(30, 30, 34), width=2)
    d.ellipse([dx + 20, dy - 12, dx + 30, dy - 6], outline=(30, 30, 34), width=2)
    d.ellipse([dx - 2, dy + 2, dx + 2, dy + 6], fill=(30, 30, 34))
    # ground + huts
    gy = y1 - 26
    d.rectangle([x0, gy, x1, y1], fill=(140, 96, 56))
    for hx in (x0 + 14, x0 + 62, x1 - 52):
        d.rectangle([hx, gy - 14, hx + 26, gy], fill=(90, 62, 40))
        d.polygon([(hx - 3, gy - 14), (hx + 13, gy - 28), (hx + 29, gy - 14)], fill=(60, 42, 28))
    # smoke columns (kept inside the box)
    for sx in (x0 + 34, x0 + 108, x1 - 30):
        for i in range(3):
            d.ellipse([sx - 8 + i * 3, gy - 30 - i * 10, sx + 12 + i * 3, gy - 14 - i * 10],
                      fill=(120, 110, 100))
    # acacia tree
    tx, ty = x0 + 96, gy
    d.line([tx, ty, tx, ty - 26], fill=(50, 36, 24), width=3)
    d.ellipse([tx - 18, ty - 34, tx + 18, ty - 22], fill=(70, 100, 50))

def scene_gta(img, d, b):
    x0, y0, x1, y1 = b
    vgrad(img, b, (40, 20, 80), (255, 120, 90))
    d.ellipse([x0 + (x1 - x0) // 2 - 26, y0 + 8, x0 + (x1 - x0) // 2 + 26, y0 + 60],
              fill=(255, 220, 140))
    # skyline (heights scaled to box height)
    gy = y1 - 30
    hs = (y1 - y0) / 112
    heights = [int(v * hs) for v in (40, 62, 48, 76, 54, 68, 44, 80, 58)]
    bw = (x1 - x0) // len(heights)
    for i, hh in enumerate(heights):
        bx = x0 + i * bw
        d.rectangle([bx + 1, gy - hh, bx + bw - 1, gy], fill=(24, 12, 44))
        for wy in range(gy - hh + 8, gy - 6, 12):
            for wx in range(bx + 5, bx + bw - 5, 9):
                if (wx * 7 + wy) % 29 < 12:
                    d.rectangle([wx, wy, wx + 3, wy + 4], fill=(255, 120, 180))
    # street + car
    d.rectangle([x0, gy, x1, y1], fill=(30, 16, 50))
    d.line([x0, gy + 14, x1, gy + 14], fill=(255, 210, 90), width=2)
    cx, cy = x0 + (x1 - x0) // 2 - 34, gy + 6
    d.polygon([(cx, cy + 12), (cx + 8, cy), (cx + 52, cy), (cx + 68, cy + 12)], fill=(220, 40, 90))
    d.rectangle([cx + 2, cy + 12, cx + 66, cy + 20], fill=(180, 20, 70))
    d.ellipse([cx + 12, cy + 16, cx + 24, cy + 28], fill=(20, 20, 24))
    d.ellipse([cx + 44, cy + 16, cx + 56, cy + 28], fill=(20, 20, 24))
    # palms
    for px in (x0 + 10, x1 - 20):
        d.line([px, gy, px + 4, gy - 26], fill=(40, 70, 40), width=3)
        for ang in (-60, -25, 10, 45):
            a = math.radians(ang - 90)
            d.line([px + 4, gy - 26, px + 4 + 13 * math.cos(a), gy - 26 + 13 * math.sin(a)],
                   fill=(40, 120, 70), width=2)
    # big VI
    d.text((x0 + 8, y0 + 4), "VI", font=SERIFB(30), fill=(255, 255, 255))

def scene_health(img, d, b):
    x0, y0, x1, y1 = b
    vgrad(img, b, (14, 60, 70), (20, 110, 100))
    # measles virus (red spiked ball), left
    def virus(cx, cy, r, col, spike):
        for i in range(12):
            a = i * math.pi / 6
            d.line([cx + (r - 2) * math.cos(a), cy + (r - 2) * math.sin(a),
                    cx + (r + spike) * math.cos(a), cy + (r + spike) * math.sin(a)],
                   fill=col, width=2)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
        d.ellipse([cx - r + 5, cy - r + 4, cx - r + 12, cy - r + 11], fill=(255, 255, 255))
    virus(x0 + 44, y0 + 36, 20, (200, 50, 50), 7)
    virus(x0 + 84, y0 + 58, 13, (220, 80, 60), 5)
    virus(x1 - 40, y0 + 34, 18, (120, 190, 80), 7)
    virus(x1 - 76, y0 + 60, 11, (90, 160, 60), 5)
    # cross / clinic
    cx, cy = x0 + (x1 - x0) // 2, y1 - 24
    d.rectangle([cx - 22, cy - 6, cx + 22, cy + 6], fill=(255, 255, 255))
    d.rectangle([cx - 6, cy - 22, cx + 6, cy + 22], fill=(255, 255, 255))
    d.text((x0 + 10, y0 + 6), "MEASLES", font=SANSB(9), fill=(255, 180, 170))
    d.text((x1 - 52, y0 + 6), "EBOLA", font=SANSB(9), fill=(190, 240, 170))

SCENES = dict(gulf=scene_gulf, kerch=scene_kerch, apec=scene_apec,
              alaska=scene_alaska, nvidia=scene_nvidia, akvan=scene_akvan,
              xavier=scene_xavier, voyager=scene_voyager, gaza=scene_gaza,
              uk=scene_uk, sudan=scene_sudan, gta=scene_gta, health=scene_health)

# ---------------------------------------------------------------- world map
NA = [(-168,66),(-158,58),(-140,60),(-130,54),(-125,49),(-124,42),(-120,34),(-114,29),
      (-110,24),(-105,20),(-97,16),(-92,15),(-86,12),(-83,9),(-79,9),(-80,8),(-77,7),
      (-75,10),(-72,12),(-68,18),(-65,18),(-60,46),(-65,49),(-55,52),(-60,55),(-65,60),
      (-68,58),(-78,62),(-85,66),(-95,69),(-110,68),(-125,70),(-140,70),(-155,71)]
GREENLAND = [(-58,64),(-52,60),(-43,60),(-40,64),(-32,68),(-22,70),(-30,76),(-45,76),(-58,74)]
SA = [(-77,7),(-72,12),(-64,10),(-60,8),(-52,5),(-50,0),(-44,-3),(-35,-8),(-40,-20),
      (-48,-28),(-58,-34),(-65,-41),(-68,-52),(-70,-54),(-73,-50),(-73,-40),(-72,-30),
      (-70,-18),(-77,-12),(-80,-5),(-81,0)]
AFRICA = [(-17,15),(-17,21),(-15,27),(-10,31),(-5,35),(0,36),(10,37),(11,34),(20,32),
          (30,31),(32,31),(34,28),(37,22),(39,18),(43,11),(48,11),(51,12),(46,5),(41,-2),
          (40,-10),(36,-18),(33,-26),(28,-33),(20,-35),(17,-29),(14,-22),(12,-15),
          (13,-8),(9,4),(4,6),(-8,5),(-13,8)]
EURASIA = [(-10,36),(-9,43),(-2,44),(-4,48),(-1,50),(3,53),(8,57),(10,59),(5,60),(5,62),
           (12,64),(18,69),(25,71),(30,70),(35,68),(44,68),(52,68),(60,69),(68,73),
           (75,73),(85,75),(95,76),(105,77),(115,76),(125,74),(135,72),(145,72),(155,70),
           (162,66),(170,66),(178,65),(170,62),(162,60),(158,55),(156,51),(150,46),
           (144,42),(140,40),(135,35),(131,33),(127,35),(122,38),(120,32),(122,28),
           (118,25),(110,20),(108,18),(105,10),(103,7),(100,7),(98,10),(97,15),(94,17),
           (92,21),(88,22),(85,19),(80,15),(77,8),(74,12),(72,20),(68,23),(62,25),
           (58,26),(54,27),(50,29),(46,29),(40,24),(38,18),(42,13),(48,14),(55,17),
           (58,21),(57,25),(52,26),(48,29),(44,29),(39,21),(35,17),(33,25),(32,31),
           (30,31),(20,32),(11,34),(10,37),(0,36),(-5,35),(-9,37)]
AUSTRALIA = [(113,-22),(114,-30),(115,-35),(120,-34),(129,-32),(132,-32),(135,-35),(138,-35),
             (140,-38),(145,-38),(150,-37),(153,-32),(153,-27),(150,-23),(146,-19),(142,-15),
             (142,-11),(137,-12),(135,-15),(132,-12),(130,-13),(126,-14),(122,-17),(118,-20)]
UK = [(-5,50),(-3,53),(-5,56),(-3,58),(-1,57),(0,53),(1,51)]
JAPAN = [(130,31),(132,33),(135,34),(137,35),(139,36),(140,38),(141,41),(143,43),(145,44),
         (142,42),(140,39),(138,36),(136,34),(133,34),(131,32)]
NZ = [(167,-45),(170,-43),(173,-41),(175,-38),(177,-38),(174,-36),(172,-35),(174,-39),(168,-46)]

PINS = {1: (57, 26.5), 2: (36.5, 45.3), 3: (114, 22.5), 4: (-152, 64),
        5: (-122, 37.4), 6: (80.5, 16), 7: (-160, -10), 9: (34.5, 31.5),
        10: (-0.1, 51.5), 11: (30, 13), 12: (-81, 27.5), 13: (23, -2)}
DOTS = {14: (4.3, 52.1), 15: (86, 55.4), 16: (147, -6), 17: (2.35, 48.85),
        18: (121, 14.6), 19: (21.4, 42), 20: (-77, 38.9), 21: (35.2, 31.8),
        22: (-2, 51.5), 23: (-74, 40.7), 24: (45, 12.8), 25: (4.35, 50.85),
        26: (-124, 37), 27: (-2.2, 51.9), 28: (29, 41), 29: (39, 14.5),
        30: (127, 37.5), 31: (20.5, 44.8), 32: (-122.4, 37.8), 34: (16.4, 48.2),
        35: (101.7, 3.1), 36: (-47.9, -15.8), 37: (178, -17.7), 38: (0.5, 51.5),
        39: (7.7, 45.1), 40: (19, 47.5), 41: (-77.4, 25), 42: (0.12, 52.2),
        43: (151.2, -33.9), 44: (-76, -15)}

def draw_map(d, box):
    mx0, my0, mx1, my1 = box
    d.rectangle(box, fill=(214, 226, 228))
    def ll(lon, lat):
        return (mx0 + (lon + 180) / 370 * (mx1 - mx0),
                my0 + (78 - lat) / 136 * (my1 - my0))
    land = (196, 186, 152)
    for poly in (NA, GREENLAND, SA, AFRICA, EURASIA, AUSTRALIA, UK, JAPAN, NZ):
        d.polygon([ll(lo, la) for lo, la in poly], fill=land)
    # graticule
    for lon in range(-150, 181, 30):
        x = ll(lon, 0)[0]
        d.line([x, my0, x, my1], fill=(196, 210, 214), width=1)
    # dots for briefs 14-44 (33 = solar flare, marked as a sun at top right)
    for n, (lon, lat) in DOTS.items():
        x, y = ll(lon, lat)
        d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=NAVY, outline=(255, 255, 255))
    # sun marker for story 33
    sx, sy = mx1 - 26, my0 + 10
    d.ellipse([sx - 5, sy - 5, sx + 5, sy + 5], fill=(255, 180, 60), outline=(200, 120, 20))
    d.text((sx - 22, sy + 6), "33", font=SANSB(8), fill=(120, 80, 10))
    # numbered pins for features 1-13 (8 = Voyager, off map)
    for n, (lon, lat) in PINS.items():
        x, y = ll(lon, lat)
        d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=RED, outline=(255, 255, 255), width=1)
        f = SANSB(8)
        tw = d.textlength(str(n), font=f)
        d.text((x - tw / 2, y - 5), str(n), font=f, fill=(255, 255, 255))
    # Voyager off-map star, top right area
    vx, vy = mx1 - 60, my0 + 34
    d.ellipse([vx - 6, vy - 6, vx + 6, vy + 6], fill=(255, 255, 255), outline=RED, width=2)
    d.text((vx - 3, vy - 5), "8", font=SANSB(8), fill=RED)

# ---------------------------------------------------------------- layout
def build():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    M = 16
    CW = W - 2 * M  # 992

    # masthead
    d.rectangle([0, 0, W, 118], fill=NAVY)
    d.rectangle([0, 118, W, 120], fill=GOLD)
    k = SANSB(12)
    kt = "T H E   D A Y   I N   W O R L D   N E W S"
    d.text(((W - d.textlength(kt, font=k)) / 2, 10), kt, font=k, fill=(255, 210, 90))
    df = SERIFB(46)
    dt = "Wednesday 18 November 2026"
    d.text(((W - d.textlength(dt, font=df)) / 2, 30), dt, font=df, fill=(255, 255, 255))
    cf = SANSB(12)
    ct = "44 STORIES  ·  6 CONTINENTS  ·  ONE PAGE"
    d.text(((W - d.textlength(ct, font=cf)) / 2, 82), ct, font=cf, fill=(220, 226, 240))
    sf = SERIFI(13)
    st = "Every story on this page happened, or was first reported, on Wednesday 18 November 2026."
    d.text(((W - d.textlength(st, font=sf)) / 2, 100), st, font=sf, fill=(200, 208, 224))

    # region-count bar
    x = M
    yb, hb = 126, 18
    for name, cnt, col in REGIONS:
        wseg = CW * cnt / 44
        d.rectangle([x, yb, x + wseg, yb + hb], fill=col)
        lab = f"{name} {cnt}"
        lf = SANSB(8)
        tw = d.textlength(lab, font=lf)
        if tw <= wseg - 4:
            d.text((x + (wseg - tw) / 2, yb + 4), lab, font=lf, fill=(255, 255, 255))
        x += wseg
    d.rectangle([M, yb, M + CW, yb + hb], outline=(0, 0, 0))

    # leads row (3)
    ly, lh = 152, 196
    scene_h = 112
    colw = (CW - 20) // 3
    for i, f in enumerate(FEATURES[:3]):
        x0 = M + i * (colw + 10)
        x1 = x0 + colw
        draw_scene(f["scene"], img, (x0, ly, x1, ly + scene_h))
        d.rectangle([x0, ly, x1, ly + scene_h], outline=(60, 60, 60))
        chip(d, x0 + 6, ly + 6, f["chip"], SANSB(9))
        ty = ly + scene_h + 6
        tagline(d, x0, ty, f["tag"], SANSB(9))
        hy = ty + 13
        hy = headline(d, x0, hy, f["head"], SERIFB(16), colw, lh=17)
        deck(d, x0, hy + 2, f["deck"], SANS(10), colw, lh=12)

    # medium rows (10), 5 per row
    my, mh = 354, 146
    mscene = 80  # 55% of panel
    mcolw = (CW - 32) // 5
    for row in range(2):
        for c in range(5):
            f = FEATURES[3 + row * 5 + c]
            x0 = M + c * (mcolw + 8)
            x1 = x0 + mcolw
            y0 = my + row * (mh + 6)
            draw_scene(f["scene"], img, (x0, y0, x1, y0 + mscene))
            d.rectangle([x0, y0, x1, y0 + mscene], outline=(60, 60, 60))
            chip(d, x0 + 4, y0 + 4, f["chip"], SANSB(7))
            ty = y0 + mscene + 4
            tagline(d, x0, ty, f["tag"], SANSB(8))
            hy = ty + 10
            hl = wrap(d, f["head"], SERIFB(13), mcolw)
            hy = headline(d, x0, hy, f["head"], SERIFB(13), mcolw, lh=14)
            # deck: as many lines as fit in the remaining space (max 3)
            remain = y0 + mh - (hy + 2)
            maxlines = max(1, remain // 10)
            dl = wrap(d, f["deck"], SANS(9), mcolw)
            if len(dl) > maxlines:
                dl = dl[:maxlines]
                dl[-1] = dl[-1].rsplit(" ", 1)[0] + " …" if " " in dl[-1] else dl[-1] + "…"
            yy = hy + 2
            for ln in dl:
                d.text((x0, yy), ln, font=SANS(9), fill=(52, 54, 58))
                yy += 10

    # numbers strip
    ny = 656
    d.line([M, ny, M + CW, ny], fill=RULE, width=2)
    d.line([M, ny + 47, M + CW, ny + 47], fill=RULE, width=2)
    tf = SANSB(10)
    d.text((M, ny + 2), "BY THE NUMBERS", font=tf, fill=RED)
    cellw = CW // 4
    for i, (num, cap) in enumerate(NUMBERS):
        cx = M + i * cellw + cellw // 2
        nf = SERIFB(19)
        d.text((cx - d.textlength(num, font=nf) / 2, ny + 15), num, font=nf, fill=NAVY)
        cfa = SANS(8)
        d.text((cx - d.textlength(cap, font=cfa) / 2, ny + 36), cap, font=cfa, fill=(70, 70, 70))
        if i:
            d.line([M + i * cellw, ny + 15, M + i * cellw, ny + 44], fill=RULE, width=1)
    d.text((M + CW - d.textlength("4 numbers that tell the day", font=SANS(9)), ny + 2),
           "4 numbers that tell the day", font=SANS(9), fill=GREY)

    # map
    my2 = 710
    d.text((M, my2), "WHERE IT HAPPENED", font=SANSB(11), fill=RED)
    note = "Pins: stories 1–13  ·  dots: 14–44  ·  8 and 33 are off the map"
    d.text((M + CW - d.textlength(note, font=SANS(9)), my2 + 1), note, font=SANS(9), fill=GREY)
    draw_map(d, (M, my2 + 16, M + CW, my2 + 90))
    d.rectangle([M, my2 + 16, M + CW, my2 + 90], outline=(60, 60, 60))
    kf = SANS(8)
    k1 = "1 Qeshm  ·  2 Kerch  ·  3 Shenzhen  ·  4 Alaska  ·  5 California  ·  6 Andhra  ·  7 Cook Is.  ·  8 Voyager 1*  ·  9 Gaza  ·  10 London  ·  11 Sudan  ·  12 Florida  ·  13 Congo"
    k2 = "*Voyager 1 is one light-day out (25.9bn km) — marked off the map.  33 is a solar flare on the Sun.  Europe is crowded: dots overlap where stories cluster."
    d.text((M, my2 + 94), k1, font=kf, fill=(60, 60, 60))
    d.text((M, my2 + 105), k2, font=kf, fill=(60, 60, 60))

    # briefs
    by = 826
    d.text((M, by), "ALSO ON WEDNESDAY 18 NOVEMBER", font=SANSB(11), fill=RED)
    d.line([M, by + 15, M + CW, by + 15], fill=RULE, width=1)
    bf = SANSB(9)
    rf = SANS(9)
    rows = 16
    rh = 10
    y0 = by + 20
    colw2 = (CW - 24) // 2
    for idx, (n, lead, rest) in enumerate(BRIEFS):
        col = 0 if idx < 16 else 1
        r = idx if idx < 16 else idx - 16
        x0 = M + col * (colw2 + 24)
        y = y0 + r * rh
        num = f"{n}. "
        d.text((x0, y), num, font=bf, fill=RED)
        tx = x0 + d.textlength(num, font=bf)
        avail = colw2 - (tx - x0)
        rest2 = rest
        while (d.textlength(lead, font=bf) + d.textlength(" — " + rest2, font=rf) > avail
               and len(rest2) > 12):
            rest2 = rest2[:-4].rstrip() + "…"
        d.text((tx, y), lead, font=bf, fill=INK)
        tx2 = tx + d.textlength(lead, font=bf)
        d.text((tx2, y), " — " + rest2, font=rf, fill=(52, 54, 58))

    # footer
    fy = 1009
    d.line([M, fy, M + CW, fy], fill=RULE, width=1)
    ff = SANS(9)
    f1 = "Every story happened or was first reported on Wednesday 18 November 2026. Disputed claims are attributed. Sources: Reuters, AP, AFP, BBC, Al Jazeera, NASA, UN, WHO, IMD, ONS. Original drawings. 44 stories."
    d.text(((W - d.textlength(f1, font=ff)) / 2, fy + 4), f1, font=ff, fill=(70, 70, 70))
    return img

if __name__ == "__main__":
    out = os.path.join(HERE, "entry.png")
    build().save(out, optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")
