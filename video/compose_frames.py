from PIL import Image, ImageDraw, ImageFilter, ImageFont
import os
S = '/home/claude/video/shots'; O = '/home/claude/video/frames'; os.makedirs(O, exist_ok=True)
W, H = 1080, 1920
BOLD = '/usr/share/fonts/opentype/inter/Inter-Bold.otf'
SEMI = '/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'
def bg():
    # soft diagonal pastel gradient (blue -> lilac -> pink)
    stops = [(0, (226, 242, 255)), (0.52, (236, 229, 255)), (1, (255, 229, 236))]
    g = Image.new('RGB', (W, H)); px = g.load()
    for y in range(H):
        for x in range(0, W, 4):
            t = (x / W * 0.35 + y / H * 0.65)
            for i in range(len(stops) - 1):
                a, ca = stops[i]; b, cb = stops[i + 1]
                if a <= t <= b:
                    k = (t - a) / (b - a); c = tuple(int(ca[j] + (cb[j] - ca[j]) * k) for j in range(3)); break
            for dx in range(4):
                if x + dx < W: px[x + dx, y] = c
    return g
BG = bg()
def rounded(img, r):
    m = Image.new('L', img.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, img.size[0] - 1, img.size[1] - 1], r, fill=255)
    out = Image.new('RGBA', img.size); out.paste(img, (0, 0), m); return out
def shadow(canvas, box, r, blur=40, alpha=70):
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle(box, r, fill=(17, 24, 39, alpha))
    canvas.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)))
def header(c, step, title):
    d = ImageDraw.Draw(c)
    f1 = ImageFont.truetype(SEMI, 30); f2 = ImageFont.truetype(BOLD, 62)
    t1 = f'SHOPLIST TUTORIAL  ·  {step}'
    d.text((W / 2, 120), t1, font=f1, fill=(91, 33, 182), anchor='mm')
    d.text((W / 2, 196), title, font=f2, fill=(17, 17, 17), anchor='mm')
def phone(name, step, title):
    c = BG.convert('RGBA'); header(c, step, title)
    s = Image.open(f'{S}/{name}.png').convert('RGB')
    h = 1330; w = int(s.width * h / s.height); s = s.resize((w, h), Image.LANCZOS)
    bez = 16; x = (W - w) // 2; y = 268
    shadow(c, [x - bez, y - bez + 24, x + w + bez, y + h + bez + 24], 76)
    frame = Image.new('RGBA', (w + 2 * bez, h + 2 * bez), (17, 24, 39, 255))
    c.alpha_composite(rounded(frame, 76), (x - bez, y - bez))
    c.alpha_composite(rounded(s, 62), (x, y))
    return c
def desktop(name, step, title):
    c = BG.convert('RGBA'); header(c, step, title)
    s = Image.open(f'{S}/{name}.png').convert('RGB')
    # crop to the area around the product photo, picker and saved toast
    s = s.crop((220, 180, 2560, 1560)); w = 1000; h = int(s.height * w / s.width)
    s = s.resize((w, h), Image.LANCZOS); x = (W - w) // 2; y = 420
    bar = 56
    shadow(c, [x, y + 20, x + w, y + h + bar + 20], 28)
    win = Image.new('RGBA', (w, h + bar), (229, 231, 235, 255)); d = ImageDraw.Draw(win)
    for i, col in enumerate([(248, 113, 113), (251, 191, 36), (52, 211, 153)]):
        d.ellipse([22 + i * 26, 20, 38 + i * 26, 36], fill=col)
    d.rounded_rectangle([120, 12, w - 24, 44], 16, fill=(255, 255, 255))
    d.text((140, 28), 'shopee.sg  ·  ShopBack extension', font=ImageFont.truetype(SEMI, 20), fill=(75, 85, 99), anchor='lm')
    win.paste(s, (0, bar)); c.alpha_composite(rounded(win, 28), (x, y))
    f = ImageFont.truetype(SEMI, 34)
    ImageDraw.Draw(c).text((W / 2, y + h + bar + 90), 'Saved from your computer, synced to the app', font=f, fill=(55, 65, 81), anchor='mm')
    return c
def endcard():
    c = BG.convert('RGBA'); d = ImageDraw.Draw(c)
    x0, y0, sz = (W - 240) // 2, 600, 240
    shadow(c, [x0, y0 + 20, x0 + sz, y0 + sz + 20], 60)
    d.rounded_rectangle([x0, y0, x0 + sz, y0 + sz], 60, fill=(17, 17, 17))
    lw = 14
    for i, yy in enumerate([y0 + 78, y0 + 120, y0 + 162]):
        d.line([x0 + 104, yy, x0 + (196 if i < 2 else 170), yy], fill=(255, 255, 255), width=lw)
    for yy in [y0 + 78, y0 + 120]:
        d.line([x0 + 48, yy, x0 + 60, yy + 12, x0 + 82, yy - 12], fill=(255, 255, 255), width=10, joint='curve')
    d.ellipse([x0 + 54, y0 + 152, x0 + 74, y0 + 172], fill=(255, 255, 255))
    d.text((W / 2, 980), 'Start your ShopList', font=ImageFont.truetype(BOLD, 84), fill=(17, 17, 17), anchor='mm')
    d.text((W / 2, 1080), 'Plan it. Track it. Buy it for less.', font=ImageFont.truetype(SEMI, 44), fill=(55, 65, 81), anchor='mm')
    d.text((W / 2, 1180), 'Only on ShopBack', font=ImageFont.truetype(SEMI, 36), fill=(91, 33, 182), anchor='mm')
    return c
PLAN = [
 ('01', phone, 'SBHome', '1 of 4', 'Your smart shopping list'),
 ('02', phone, 'V2Capture', '1 of 4', 'Add anything, any way'),
 ('03', desktop, 'ExtSave', '1 of 4', 'Add anything, any way'),
 ('04', phone, 'V2Home', '2 of 4', 'Buy Now · Wish List · Recurring'),
 ('05', phone, 'O3Lists', '2 of 4', 'Buy Now · Wish List · Recurring'),
 ('06', phone, 'W1Report', '3 of 4', 'Best price after Cashback'),
 ('07', phone, 'W4Notify', '3 of 4', 'Daily or weekly price check'),
 ('08', phone, 'V2Approve', '3 of 4', 'Buy through ShopBack'),
 ('09', phone, 'V2Bought', '4 of 4', 'Cashback adds up'),
 ('10', phone, 'V2Wish', '4 of 4', 'Toward your Wish List'),
]
for key, fn, name, step, title in PLAN:
    fn(name, step, title).convert('RGB').save(f'{O}/{key}.png')
endcard().convert('RGB').save(f'{O}/11.png')
print('frames ok')
