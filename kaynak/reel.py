#!/usr/bin/env python3
"""Maay Filo One dikey Reels üretici.
Kullanım: python3 reel.py spec.json cikti.mp4
spec: {"scenes":[{"type":"hook","bg":path,"lines":[...],"accent":idx,"dur":3.5},
                 {"type":"phone","img":path,"title":str,"sub":str,"dur":3},
                 {"type":"cta","dur":4}], "music_seed":1}
"""
import json, os, subprocess, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
RED = (200, 22, 40)
DARK = (18, 18, 20)
FD = '/usr/share/fonts/opentype/inter/'
F = lambda s, n='InterDisplay-Black.otf': ImageFont.truetype(FD + n, s)
HERE = os.path.dirname(os.path.abspath(__file__))
LOGO_W = Image.open(os.path.join(HERE, 'logo_beyaz.png')).convert('RGBA')
LOGO_W = LOGO_W.crop(LOGO_W.getbbox())

def ease(t):  # easeOutCubic
    t = max(0.0, min(1.0, t)); return 1 - (1 - t) ** 3

def cover(im, w, h):
    r = max(w / im.width, h / im.height)
    im = im.resize((math.ceil(im.width * r), math.ceil(im.height * r)), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))

def zoomed(base, z):
    """base is larger-than-frame image; crop centre to W/z x H/z then resize."""
    cw, ch = W / z, H / z
    x, y = (base.width - cw) / 2, (base.height - ch) / 2
    return base.resize((W, H), Image.BICUBIC, box=(x, y, x + cw, y + ch))

def text_w(d, s, f):
    b = d.textbbox((0, 0), s, font=f); return b[2] - b[0]

def gradient(h0, h1, alpha):
    g = Image.new('L', (1, H), 0)
    for y in range(H):
        a = 0 if y < h0 else min(1, (y - h0) / max(1, h1 - h0))
        g.putpixel((0, y), int(alpha * a))
    return g.resize((W, H))

def pill(draw, xy, r, fill):
    draw.rounded_rectangle(xy, r, fill=fill)

def wrap(d, s, f, maxw):
    words, lines, cur = s.split(), [], ''
    for w_ in words:
        t = (cur + ' ' + w_).strip()
        if text_w(d, t, f) <= maxw: cur = t
        else: lines.append(cur); cur = w_
    if cur: lines.append(cur)
    return lines

# ---------- scenes ----------
def scene_hook(sc):
    bg = cover(Image.open(sc['bg']).convert('RGB'), int(W * 1.12), int(H * 1.12))
    shade = gradient(int(H * 0.30), int(H * 0.62), 215)
    lines, acc = sc['lines'], sc.get('accent', -1)
    f = F(118)
    n = int(sc['dur'] * FPS)
    for i in range(n):
        t = i / FPS
        z = 1.0 + 0.06 * (i / n)
        fr = zoomed(bg, z * 1.0)
        fr = Image.composite(Image.new('RGB', (W, H), (0, 0, 0)), fr, shade)
        d = ImageDraw.Draw(fr)
        y = int(H * 0.50)
        for k, ln in enumerate(lines):
            p = ease((t - 0.15 - k * 0.22) / 0.45)
            if p <= 0: y += 150; continue
            tw = text_w(d, ln, f); x = (W - tw) // 2
            dy = int((1 - p) * 60)
            layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
            if k == acc:
                ld.rounded_rectangle((x - 30, y - 8 + dy, x + tw + 30, y + 140 + dy), 22, fill=RED + (int(255 * p),))
            ld.text((x, y + dy), ln, font=f, fill=(255, 255, 255, int(255 * p)))
            fr.paste(layer, (0, 0), layer)
            y += 150
        # small brand tag top
        tag = LOGO_W.resize((300, int(300 * LOGO_W.height / LOGO_W.width)))
        fr.paste(tag, ((W - tag.width) // 2, 150), tag)
        yield fr

def phone_frame(img, h):
    sc = img.convert('RGB')
    w = int(h * sc.width / sc.height)
    sc = sc.resize((w, h), Image.LANCZOS)
    pad, r = 22, 70
    fw, fh = w + 2 * pad, h + 2 * pad
    out = Image.new('RGBA', (fw + 80, fh + 80), (0, 0, 0, 0))
    sh = Image.new('L', out.size, 0); ImageDraw.Draw(sh).rounded_rectangle((40, 60, 40 + fw, 60 + fh), r, fill=150)
    out.putalpha(0); shadow = Image.new('RGBA', out.size, (0, 0, 0, 255)); shadow.putalpha(sh.filter(ImageFilter.GaussianBlur(28)))
    out = Image.alpha_composite(out, shadow)
    body = Image.new('RGBA', (fw, fh), (0, 0, 0, 0)); ImageDraw.Draw(body).rounded_rectangle((0, 0, fw - 1, fh - 1), r, fill=(22, 22, 24, 255))
    m = Image.new('L', (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), r - pad, fill=255)
    body.paste(sc, (pad, pad), m)
    out.alpha_composite(body, (40, 40))
    return out

def scene_phone(sc):
    src = Image.open(sc['img'])
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H * 0.68) / H) ** 2)
    glow = np.clip(1 - r * 2.2, 0, 1)[..., None]
    base = np.array(DARK, float) * (1 - glow) + np.array((150, 14, 30), float) * glow
    bg = Image.fromarray(base.astype('uint8'))
    ph = phone_frame(src, int(H * 0.60))
    ft, fs = F(84), F(46, 'InterDisplay-SemiBold.otf')
    n = int(sc['dur'] * FPS)
    d0 = ImageDraw.Draw(bg)
    tl = wrap(d0, sc['title'], ft, W - 160)
    for i in range(n):
        t = i / FPS
        fr = bg.copy(); d = ImageDraw.Draw(fr)
        # title
        p = ease((t - 0.05) / 0.4); y = 230
        for ln in tl:
            tw = text_w(d, ln, ft); x = (W - tw) // 2
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
            ld.text((x, y + int((1 - p) * 40)), ln, font=ft, fill=(255, 255, 255, int(255 * p)))
            fr.paste(lay, (0, 0), lay); y += 100
        if sc.get('sub'):
            p2 = ease((t - 0.3) / 0.4)
            sw = text_w(d, sc['sub'], fs) + 60; sx = (W - sw) // 2; sy = y + 20
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
            ld.rounded_rectangle((sx, sy, sx + sw, sy + 76), 38, fill=RED + (int(255 * p2),))
            ld.text((sx + 30, sy + 12), sc['sub'], font=fs, fill=(255, 255, 255, int(255 * p2)))
            fr.paste(lay, (0, 0), lay); y = sy + 76
        # phone slides up + gentle float
        p3 = ease((t - 0.1) / 0.6)
        py = int(y + 60 + (1 - p3) * 500 + 6 * math.sin(t * 2.2))
        px = (W - ph.width) // 2
        fr.paste(ph, (px, py), ph)
        yield fr

def scene_cta(sc):
    n = int(sc['dur'] * FPS)
    fb, fm, fs = F(96), F(70), F(44, 'InterDisplay-SemiBold.otf')
    logo = LOGO_W.resize((760, int(760 * LOGO_W.height / LOGO_W.width)))
    for i in range(n):
        t = i / FPS
        fr = Image.new('RGB', (W, H), RED); d = ImageDraw.Draw(fr)
        # subtle moving diagonal stripes
        for k in range(-6, 14):
            x0 = k * 160 + int(t * 40) % 160
            d.polygon([(x0, 0), (x0 + 60, 0), (x0 - 640, H), (x0 - 700, H)], fill=(188, 18, 36))
        p = ease(t / 0.5)
        lg = logo.copy(); a = lg.getchannel('A').point(lambda v: int(v * p)); lg.putalpha(a)
        fr.paste(lg, ((W - lg.width) // 2, 420 + int((1 - p) * 40)), lg)
        def ctext(s, f, y, delay, col=(255, 255, 255), box=None):
            q = ease((t - delay) / 0.4)
            if q <= 0: return
            tw = text_w(d, s, f); x = (W - tw) // 2
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
            if box: ld.rounded_rectangle((x - 40, y - 18, x + tw + 40, y + f.size + 30), 30, fill=box + (int(255 * q),))
            ld.text((x, y + int((1 - q) * 30)), s, font=f, fill=col + (int(255 * q),))
            fr.paste(lay, (0, 0), lay)
        ctext(sc.get('gun', '7 GÜN'), fb, 860, 0.35)
        ctext('ÜCRETSİZ DENE', fb, 1040, 0.5, col=RED, box=(255, 255, 255))
        ctext('Demo ve bilgi için', fs, 1260, 0.8)
        ctext('0543 952 22 43', fm, 1330, 0.95)
        yield fr


def glow_bg():
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H * 0.68) / H) ** 2)
    glow = np.clip(1 - r * 2.2, 0, 1)[..., None]
    base = np.array(DARK, float) * (1 - glow) + np.array((150, 14, 30), float) * glow
    return Image.fromarray(base.astype('uint8'))

def draw_titles(fr, t, title, sub, y=230):
    d = ImageDraw.Draw(fr); ft, fs = F(84), F(46, 'InterDisplay-SemiBold.otf')
    p = ease((t - 0.05) / 0.4)
    for ln in wrap(d, title, ft, W - 160):
        tw = text_w(d, ln, ft); x = (W - tw) // 2
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.text((x, y + int((1 - p) * 40)), ln, font=ft, fill=(255, 255, 255, int(255 * p)))
        fr.paste(lay, (0, 0), lay); y += 100
    if sub:
        p2 = ease((t - 0.3) / 0.4)
        sw = text_w(d, sub, fs) + 60; sx = (W - sw) // 2; sy = y + 20
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle((sx, sy, sx + sw, sy + 76), 38, fill=RED + (int(255 * p2),))
        ld.text((sx + 30, sy + 12), sub, font=fs, fill=(255, 255, 255, int(255 * p2)))
        fr.paste(lay, (0, 0), lay); y = sy + 76
    return y

def scene_screen(sc):
    src = Image.open(sc['img']).convert('RGB')
    bg = glow_bg(); n = int(sc['dur'] * FPS)
    w0 = W - 60; h0 = int(w0 * src.height / src.width)
    big = src.resize((int(w0 * 1.6), int(h0 * 1.6)), Image.LANCZOS)
    m = Image.new('L', (w0, h0), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w0 - 1, h0 - 1), 26, fill=255)
    for i in range(n):
        t = i / FPS; fr = bg.copy()
        y = draw_titles(fr, t, sc['title'], sc.get('sub'))
        z = 1.0 + 0.35 * ease(max(0, t - 0.9) / max(0.1, sc['dur'] - 1.0))
        fx, fy = sc.get('focus', (0.5, 0.45))
        cw, ch = big.width / (1.6 * z) * 1.6 / 1.6, big.height / (1.6 * z) * 1.6 / 1.6
        cw, ch = big.width / z, big.height / z
        x0 = (big.width - cw) * fx; y0 = (big.height - ch) * fy
        view = big.resize((w0, h0), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))
        p = ease((t - 0.1) / 0.6)
        px = 30 + int((1 - p) * W); py = y + 90 + max(0, (1500 - y - h0) // 3)
        sh = Image.new('RGBA', (w0 + 80, h0 + 80), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((40, 50, 40 + w0, 50 + h0), 26, fill=(0, 0, 0, 150))
        sh = sh.filter(ImageFilter.GaussianBlur(22)); fr.paste(sh, (px - 40, py - 40), sh)
        fr.paste(view, (px, py), m)
        yield fr

def scene_photo(sc):
    bg = cover(Image.open(sc['bg']).convert('RGB'), int(W * 1.12), int(H * 1.12))
    shade = gradient(int(H * 0.45), int(H * 0.80), 230)
    ft, fs = F(92), F(46, 'InterDisplay-SemiBold.otf'); n = int(sc['dur'] * FPS)
    for i in range(n):
        t = i / FPS; fr = zoomed(bg, 1.0 + 0.07 * i / n)
        fr = Image.composite(Image.new('RGB', (W, H), (0, 0, 0)), fr, shade); d = ImageDraw.Draw(fr)
        lines = wrap(d, sc['title'], ft, W - 140); y = int(H * 0.60)
        if sc.get('sub'):
            p2 = ease((t - 0.1) / 0.4); sw = text_w(d, sc['sub'], fs) + 60; sx = (W - sw) // 2
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
            ld.rounded_rectangle((sx, y, sx + sw, y + 76), 38, fill=RED + (int(255 * p2),))
            ld.text((sx + 30, y + 12), sc['sub'], font=fs, fill=(255, 255, 255, int(255 * p2))); fr.paste(lay, (0, 0), lay)
            y += 110
        for k, ln in enumerate(lines):
            p = ease((t - 0.3 - 0.15 * k) / 0.45); tw = text_w(d, ln, ft)
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
            ld.text(((W - tw) // 2, y + int((1 - p) * 40)), ln, font=ft, fill=(255, 255, 255, int(255 * p))); fr.paste(lay, (0, 0), lay)
            y += 110
        yield fr

SCENES = {'hook': scene_hook, 'phone': scene_phone, 'cta': scene_cta, 'screen': scene_screen, 'photo': scene_photo}

def encode(frames, out):
    tmp = out + '.tmp.mp4'
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', str(FPS), tmp], stdin=subprocess.PIPE)
    for fr in frames: p.stdin.write(fr.tobytes())
    p.stdin.close(); assert p.wait() == 0
    os.replace(tmp, out)

# ---------- music (synthesised, royalty-free) ----------
def music(dur, seed, path, sr=44100):
    rng = np.random.default_rng(seed)
    bpm = 118; beat = 60 / bpm
    t = np.arange(int(dur * sr)) / sr
    out = np.zeros_like(t)
    roots = [[48, 55, 60, 64], [43, 50, 59, 62], [45, 52, 57, 60], [41, 48, 57, 60]]  # C G Am F
    rng.shuffle(roots[1:])
    hz = lambda m: 440 * 2 ** ((m - 69) / 12)
    bar = 4 * beat
    for bi in range(int(dur / bar) + 1):
        ch = roots[bi % 4]; s0 = int(bi * bar * sr); s1 = min(len(t), int((bi + 1) * bar * sr))
        if s0 >= len(t): break
        tt = t[s0:s1] - bi * bar
        env = np.minimum(1, tt / 0.08) * np.exp(-tt * 0.25)
        pad = sum(np.sin(2 * np.pi * hz(m) * tt) + 0.3 * np.sin(4 * np.pi * hz(m) * tt + 0.3) for m in ch[1:])
        out[s0:s1] += 0.05 * pad * env
        out[s0:s1] += 0.16 * np.sin(2 * np.pi * hz(ch[0] - 12) * tt) * np.minimum(1, tt / 0.02)
        # arpeggio 8ths
        for k in range(8):
            a0 = s0 + int(k * beat / 2 * sr); a1 = min(s1, a0 + int(0.22 * sr))
            if a0 >= s1: break
            ta = (np.arange(a1 - a0)) / sr; m = ch[1 + (k % 3)] + 12
            out[a0:a1] += 0.055 * np.sin(2 * np.pi * hz(m) * ta) * np.exp(-ta * 14)
    nb = int(dur / beat) + 1
    for b in range(nb):
        s = int(b * beat * sr)
        if s >= len(t): break
        L = min(len(t) - s, int(0.35 * sr)); tk = np.arange(L) / sr
        f = 50 + 90 * np.exp(-tk * 30)
        out[s:s + L] += 0.5 * np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-tk * 9)
        hs = s + int(beat / 2 * sr); Lh = min(len(t) - hs, int(0.05 * sr))
        if Lh > 0:
            out[hs:hs + Lh] += 0.05 * rng.standard_normal(Lh) * np.exp(-np.arange(Lh) / sr * 80)
        if b % 2 == 1:
            Lc = min(len(t) - s, int(0.15 * sr)); out[s:s + Lc] += 0.08 * rng.standard_normal(Lc) * np.exp(-np.arange(Lc) / sr * 30)
    fade = np.minimum(1, np.minimum(t / 0.3, (dur - t) / 1.2)); out *= np.clip(fade, 0, 1)
    out = np.tanh(out * 1.3) / np.tanh(1.3) * 0.85
    import wave
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((out * 32767).astype(np.int16).tobytes())

def main(spec_path, out):
    out = os.path.abspath(out); spec = json.load(open(spec_path)); wd = out + '_parts'; os.makedirs(wd, exist_ok=True)
    parts = []
    for i, sc in enumerate(spec['scenes']):
        pth = os.path.join(wd, f's{i:02d}.mp4'); encode(SCENES[sc['type']](sc), pth); parts.append(pth)
    lst = os.path.join(wd, 'list.txt'); open(lst, 'w').write(''.join(f"file '{p}'\n" for p in parts))
    silent = os.path.join(wd, 'silent.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', silent], check=True)
    dur = sum(s['dur'] for s in spec['scenes'])
    wav = os.path.join(wd, 'm.wav'); music(dur, spec.get('music_seed', 1), wav)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', silent, '-i', wav, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out + '.tmp.mp4'], check=True)
    os.replace(out + '.tmp.mp4', out)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
