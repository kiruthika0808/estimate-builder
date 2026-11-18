"""Builds docs/UniqNextGen-Estimate-Builder-User-Guide.pdf.

Usage:  python docs/build_user_guide.py <screenshots-folder>
The screenshots folder holds 01-start.jpg ... 08-phone.jpg and 09-sample-estimate.png.
"""
import io, os, sys
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Image as RLImage,
                                Table, TableStyle, PageBreak, KeepTogether, NextPageTemplate, Flowable)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SHOTS = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'screenshots')
OUT = os.path.join(HERE, 'UniqNextGen-Estimate-Builder-User-Guide.pdf')
LIVE = 'https://estimate-builder-kappa.vercel.app'
VERSION = 'Version 1.7 · November 2026'

# ---------- fonts (Segoe UI has the ₹ sign; the built-in PDF fonts do not) ----------
F = 'C:/Windows/Fonts/'
pdfmetrics.registerFont(TTFont('UI', F + 'segoeui.ttf'))
pdfmetrics.registerFont(TTFont('UI-Semi', F + 'seguisb.ttf'))
pdfmetrics.registerFont(TTFont('UI-Bold', F + 'segoeuib.ttf'))
pdfmetrics.registerFont(TTFont('UI-Italic', F + 'segoeuii.ttf'))
from reportlab.lib.fonts import addMapping
addMapping('UI', 0, 0, 'UI'); addMapping('UI', 1, 0, 'UI-Bold'); addMapping('UI', 0, 1, 'UI-Italic'); addMapping('UI', 1, 1, 'UI-Bold')

# ---------- brand colours ----------
NAVY = colors.HexColor('#1b1f4b'); VIOLET = colors.HexColor('#6c3fd6'); ORANGE = colors.HexColor('#f06a22')
PINK = colors.HexColor('#e3437f'); TEAL = colors.HexColor('#0e8a7d'); MUTED = colors.HexColor('#646189')
SOFT = colors.HexColor('#f5f3fc'); LINE = colors.HexColor('#e4e0f2'); GOOD = colors.HexColor('#138a43')
TIP_BG = colors.HexColor('#ece6ff'); WARN_BG = colors.HexColor('#fff1e8')

PAGE_W, PAGE_H = A4
M = 18 * mm
CONTENT_W = PAGE_W - 2 * M

# ---------- styles ----------
def S(name, **kw):
    base = dict(fontName='UI', fontSize=10, leading=14.5, textColor=NAVY)
    base.update(kw); return ParagraphStyle(name, **base)
body = S('body')
small = S('small', fontSize=8.5, leading=12, textColor=MUTED)
h1 = S('h1', fontName='UI-Bold', fontSize=20, leading=25, spaceBefore=2, spaceAfter=8, textColor=NAVY)
h2 = S('h2', fontName='UI-Bold', fontSize=13, leading=17, spaceBefore=10, spaceAfter=5, textColor=VIOLET)
eyebrow = S('eyebrow', fontName='UI-Bold', fontSize=8.5, leading=11, textColor=ORANGE)
caption = S('caption', fontSize=8.5, leading=11.5, textColor=MUTED, alignment=TA_CENTER, spaceBefore=3, spaceAfter=10)
cell = S('cell', fontSize=9, leading=12.5)
cellb = S('cellb', fontName='UI-Semi', fontSize=9, leading=12.5)
cellh = S('cellh', fontName='UI-Bold', fontSize=9, leading=12.5, textColor=colors.white)
bullet = S('bullet', leftIndent=12, bulletIndent=2, spaceAfter=3)
step_style = S('step', leftIndent=0, spaceAfter=2)

def P(text, style=body): return Paragraph(text, style)
def bullets(items): return [Paragraph(t, bullet, bulletText='•') for t in items]

def shot(name, width=CONTENT_W, cap=None, border=True):
    path = os.path.join(SHOTS, name)
    w, h = Image.open(path).size
    img = RLImage(path, width=width, height=width * h / w)
    t = Table([[img]], colWidths=[width + 2])
    t.setStyle(TableStyle([('BOX', (0, 0), (-1, -1), 0.8 if border else 0, LINE),
                           ('LEFTPADDING', (0, 0), (-1, -1), 1), ('RIGHTPADDING', (0, 0), (-1, -1), 1),
                           ('TOPPADDING', (0, 0), (-1, -1), 1), ('BOTTOMPADDING', (0, 0), (-1, -1), 1)]))
    t.hAlign = 'CENTER'
    out = [t]
    if cap: out.append(P(cap, caption))
    return out

def box(text, kind='tip'):
    bg, label, col = (TIP_BG, 'TIP', VIOLET) if kind == 'tip' else (WARN_BG, 'NOTE', ORANGE)
    t = Table([[P(f'<font name="UI-Bold" color="{col.hexval()}">{label}</font>&nbsp;&nbsp;' + text, cell)]], colWidths=[CONTENT_W])
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), bg), ('LINEBEFORE', (0, 0), (0, -1), 3, col),
                           ('LEFTPADDING', (0, 0), (-1, -1), 10), ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                           ('TOPPADDING', (0, 0), (-1, -1), 7), ('BOTTOMPADDING', (0, 0), (-1, -1), 7)]))
    return [Spacer(1, 4), t, Spacer(1, 6)]

def table(rows, widths, header=True, zebra=True):
    data = []
    for i, r in enumerate(rows):
        st = cellh if (header and i == 0) else cell
        data.append([c if isinstance(c, Flowable) else P(str(c), st) for c in r])
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    style = [('GRID', (0, 0), (-1, -1), 0.5, LINE), ('VALIGN', (0, 0), (-1, -1), 'TOP'),
             ('LEFTPADDING', (0, 0), (-1, -1), 6), ('RIGHTPADDING', (0, 0), (-1, -1), 6),
             ('TOPPADDING', (0, 0), (-1, -1), 4), ('BOTTOMPADDING', (0, 0), (-1, -1), 4)]
    if header: style.append(('BACKGROUND', (0, 0), (-1, 0), NAVY))
    if zebra:
        for i in range(1 if header else 0, len(rows)):
            if i % 2 == 0: style.append(('BACKGROUND', (0, i), (-1, i), SOFT))
    t.setStyle(TableStyle(style)); return t

class StepTitle(Flowable):
    """Numbered coloured badge + heading, like the step cards in the app."""
    def __init__(self, num, title, colour):
        super().__init__(); self.num, self.title, self.colour = num, title, colour
        self.width, self.height = CONTENT_W, 24
    def draw(self):
        c = self.canv
        c.setFillColor(self.colour); c.roundRect(0, 2, 20, 20, 5, fill=1, stroke=0)
        c.setFillColor(colors.white); c.setFont('UI-Bold', 11); c.drawCentredString(10, 8, str(self.num))
        c.setFillColor(NAVY); c.setFont('UI-Bold', 15); c.drawString(28, 7, self.title)

# ---------- logo (cropped from the brand image) ----------
def logo_reader():
    im = Image.open(os.path.join(ROOT, 'web', 'assets', 'uniqnextgen-logo.jpg')).convert('RGB')
    gray = im.convert('L').point(lambda v: 255 if v < 230 else 0)
    bb = gray.getbbox(); im = im.crop((max(bb[0] - 10, 0), max(bb[1] - 10, 0), min(bb[2] + 10, im.width), min(bb[3] + 10, im.height)))
    buf = io.BytesIO(); im.save(buf, 'PNG'); buf.seek(0)
    from reportlab.lib.utils import ImageReader
    return ImageReader(buf), im.size
LOGO, LOGO_SIZE = logo_reader()

def gradient_bar(c, x, y, w, h):
    n = 80
    for i in range(n):
        t = i / (n - 1)
        r = VIOLET.red + (ORANGE.red - VIOLET.red) * t; g = VIOLET.green + (ORANGE.green - VIOLET.green) * t; b = VIOLET.blue + (ORANGE.blue - VIOLET.blue) * t
        c.setFillColorRGB(r, g, b); c.rect(x + w * i / n, y, w / n + 0.3, h, fill=1, stroke=0)

# ---------- page decorations ----------
def cover(c, doc):
    c.saveState()
    c.setFillColor(colors.white); c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    # soft colour field
    c.setFillColor(colors.HexColor('#f3efff')); c.circle(PAGE_W - 30 * mm, PAGE_H - 20 * mm, 85 * mm, fill=1, stroke=0)
    c.setFillColor(colors.HexColor('#fff0e6')); c.circle(25 * mm, 40 * mm, 60 * mm, fill=1, stroke=0)
    lw = 70 * mm; lh = lw * LOGO_SIZE[1] / LOGO_SIZE[0]
    c.drawImage(LOGO, M, PAGE_H - 30 * mm - lh, lw, lh, mask='auto')
    y = PAGE_H - 30 * mm - lh - 22 * mm
    c.setFillColor(ORANGE); c.setFont('UI-Bold', 10); c.drawString(M, y, 'AI & FUTURE-TECH SCHOOL CURRICULUM')
    c.setFillColor(NAVY); c.setFont('UI-Bold', 38); c.drawString(M, y - 18 * mm, 'Estimate Builder')
    c.setFillColor(VIOLET); c.setFont('UI-Semi', 24); c.drawString(M, y - 30 * mm, 'User Guide')
    gradient_bar(c, M, y - 38 * mm, 60 * mm, 2.2)
    c.setFillColor(MUTED); c.setFont('UI', 11.5)
    lines = ['How to build a school estimate, download the branded PDF,',
             'and manage saved estimates, on the web and on Android.']
    for i, t in enumerate(lines): c.drawString(M, y - 50 * mm - i * 6.2 * mm, t)
    # info card
    cy = 52 * mm
    c.setFillColor(colors.white); c.setStrokeColor(LINE); c.roundRect(M, cy, CONTENT_W, 34 * mm, 4 * mm, fill=1, stroke=1)
    c.setFillColor(MUTED); c.setFont('UI-Bold', 8.5)
    c.drawString(M + 8 * mm, cy + 25 * mm, 'OPEN THE APP'); c.drawString(M + 100 * mm, cy + 25 * mm, 'SUPPORT')
    c.setFillColor(NAVY); c.setFont('UI-Semi', 11)
    c.drawString(M + 8 * mm, cy + 18 * mm, LIVE.replace('https://', ''))
    c.drawString(M + 100 * mm, cy + 18 * mm, 'admin@uniqnextgen.in')
    c.setFont('UI', 9.5); c.setFillColor(MUTED)
    c.drawString(M + 8 * mm, cy + 11.5 * mm, 'Works on computers and phones.')
    c.drawString(M + 8 * mm, cy + 6 * mm, 'Android app: UniqNextGen Estimates (APK).')
    c.drawString(M + 100 * mm, cy + 11.5 * mm, 'www.uniqnextgen.in')
    c.setFillColor(MUTED); c.setFont('UI', 9)
    c.drawString(M, 20 * mm, VERSION + '  ·  For UniqNextGen staff')
    gradient_bar(c, 0, 0, PAGE_W, 3.5)
    c.restoreState()

def inner(c, doc):
    c.saveState()
    lw = 26 * mm; lh = lw * LOGO_SIZE[1] / LOGO_SIZE[0]
    c.drawImage(LOGO, M, PAGE_H - 9 * mm - lh, lw, lh, mask='auto')
    c.setFillColor(MUTED); c.setFont('UI', 8.5)
    c.drawRightString(PAGE_W - M, PAGE_H - 15 * mm, 'Estimate Builder · User Guide')
    gradient_bar(c, M, PAGE_H - 11 * mm - lh, CONTENT_W, 1.2)
    c.setStrokeColor(LINE); c.line(M, 14 * mm, PAGE_W - M, 14 * mm)
    c.setFont('UI', 8.5); c.setFillColor(MUTED)
    c.drawString(M, 9 * mm, 'www.uniqnextgen.in  ·  admin@uniqnextgen.in')
    c.drawRightString(PAGE_W - M, 9 * mm, f'Page {doc.page}')
    c.restoreState()

doc = BaseDocTemplate(OUT, pagesize=A4, leftMargin=M, rightMargin=M, topMargin=34 * mm, bottomMargin=20 * mm,
                      title='UniqNextGen Estimate Builder - User Guide', author='UniqNextGen',
                      subject='How to use the school estimate builder')
frame = Frame(M, 20 * mm, CONTENT_W, PAGE_H - 54 * mm, id='f', leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
doc.addPageTemplates([PageTemplate(id='cover', frames=[frame], onPage=cover),
                      PageTemplate(id='inner', frames=[frame], onPage=inner)])

st = [NextPageTemplate('inner'), PageBreak()]

# ---------- Contents ----------
st += [P('Contents', h1)]
toc = [('1', 'What the app does', '3'), ('2', 'Quick start', '3'), ('3', 'Step 1 – School details', '4'),
       ('4', 'Step 2 – Training model', '5'), ('5', 'Step 3 – Choose items and additional service', '5'),
       ('6', 'Step 4 – Adjustments and grand total', '7'), ('7', 'Generate the estimate', '8'),
       ('8', 'Download the PDF estimate', '10'), ('9', 'Saved estimates: edit, re-download, delete', '11'),
       ('10', 'Using the app on a phone, and the Android app', '12'), ('11', 'How prices are worked out', '13'),
       ('12', 'Questions and troubleshooting', '14')]
TOC = table([['', 'Section', 'Page']] + [[a, b, c] for a, b, c in toc], [12 * mm, CONTENT_W - 32 * mm, 20 * mm])
st += [TOC, PageBreak()]

# ---------- 1. What it does ----------
st += [P('SECTION 1', eyebrow), P('What the app does', h1)]
st += [P('The Estimate Builder prepares a price estimate for a school taking the <b>AI &amp; Future-Tech School Curriculum</b>. '
         'You enter the school\'s details, choose who our developer will train and which items the school wants, and the app '
         'works out the <b>final amount per student</b>. You then download a branded PDF estimate to send to the school.')]
st += [Spacer(1, 4)] + bullets([
    '<b>Picks the right price automatically.</b> It finds the lowest-priced programme that covers every item you tick.',
    '<b>Never goes above ₹2,500 per student</b> before discount and tax, whatever is selected.',
    '<b>Branded PDF</b> with the UniqNextGen logo, estimate number, date, the school\'s in-charge and the executive who prepared it.',
    '<b>Every estimate is saved</b> so you can edit it or download it again later.',
    '<b>Works anywhere:</b> in a web browser on a computer or phone, and as an Android app.'])
st += [P('Where to open it', h2)]
st += [table([['Where', 'How to open', 'Saved estimates are kept'],
              ['Website (recommended)', f'<font name="UI-Semi">{LIVE.replace("https://", "")}</font> in any browser', 'In that browser, on that device'],
              ['Android app', 'Install <b>UniqNextGen-Estimates</b> APK (see section 10)', 'On that phone'],
              ['Offline on a computer', 'Double-click <b>Start Estimate Builder.bat</b> in the app folder', 'In that browser, on that computer']],
             [40 * mm, 78 * mm, CONTENT_W - 118 * mm])]

# ---------- 2. Quick start ----------
st += [P('SECTION 2', eyebrow), P('Quick start', h1), P('Making an estimate takes about a minute:')]
qs = [('Type the school details', 'School name, in-charge name and number of students. Your own name and email are remembered.'),
      ('Choose the training model', 'Students, computer teachers, or no preference.'),
      ('Tick the items', 'Printed Books, Notebook, Competitions, Robotics Lab, and the additional service if needed.'),
      ('Set adjustments (optional)', 'Discount %, GST %, and whether the PDF shows the grand total.'),
      ('Press Generate estimate', 'The final amount per student appears, and the estimate is saved.'),
      ('Press Download PDF', 'The PDF is saved to your Downloads folder and the form clears for the next school.')]
rows = []
for i, (a, b) in enumerate(qs, 1):
    badge = Table([[P(f'<font color="white"><b>{i}</b></font>', S('n', alignment=TA_CENTER, fontSize=10, leading=12))]], colWidths=[8 * mm], rowHeights=[8 * mm])
    badge.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), [VIOLET, PINK, ORANGE, TEAL, VIOLET, GOOD][i - 1]),
                               ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('LEFTPADDING', (0, 0), (-1, -1), 0), ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                               ('TOPPADDING', (0, 0), (-1, -1), 0), ('BOTTOMPADDING', (0, 0), (-1, -1), 0), ('ROUNDEDCORNERS', [5, 5, 5, 5])]))
    rows.append([badge, P(f'<b>{a}</b><br/><font color="{MUTED.hexval()}">{b}</font>', cell)])
q = Table(rows, colWidths=[12 * mm, CONTENT_W - 12 * mm])
q.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('BOTTOMPADDING', (0, 0), (-1, -1), 6), ('LEFTPADDING', (0, 0), (-1, -1), 0)]))
st += [q] + box('Fields marked with a red <font color="#e3437f">*</font> are required. If one is missing, the app highlights it and does not generate the estimate.')
st += [PageBreak()]

# ---------- 3. Step 1 ----------
st += [P('SECTION 3', eyebrow), StepTitle(1, 'School details', VIOLET), Spacer(1, 6)]
st += shot('01-start.jpg', cap='The top of the app: brand bar, Step 1 on the left, and the Generate estimate button on the right.')
st += [table([['Field', 'What to enter'],
              ['School name *', 'The school\'s full name, as it should appear on the estimate.'],
              ['School in-charge name *', 'The person the estimate is for, e.g. "Mrs. R. Lakshmi, Principal". Printed as "Attn:" on the PDF.'],
              ['Number of students *', 'Type it, or drag the slider (50 to 3,000). It also sets the additional-service rate.'],
              ['Estimate date / number', 'Filled in automatically, e.g. UNG-261118-004 (year, month, day, then a running number).'],
              ['Executive name * and email *', 'Your own details, printed under "Prepared by". The app remembers them for your next estimate.']],
             [48 * mm, CONTENT_W - 48 * mm])]
st += [PageBreak()]

# ---------- 4 + 5 ----------
st += [P('SECTIONS 4 AND 5', eyebrow), StepTitle(2, 'Training model', PINK), Spacer(1, 4)]
st += [P('Choose who our developer will train. <b>Students</b>: the developer teaches the students directly. '
         '<b>Computer teachers</b>: the developer trains the school\'s computer teachers, which lowers the price. '
         '<b>No preference</b>: the app picks whichever is cheaper for the items you tick.')]
st += [Spacer(1, 6), StepTitle(3, 'Choose items and additional service', ORANGE), Spacer(1, 6)]
st += shot('02-training-items.jpg', width=CONTENT_W * 0.92, cap='Step 2 (training model) and Step 3 (items). Ticked items have an orange border.')
st += [P('Tick every item the school wants: <b>Printed Books</b>, <b>Notebook</b>, <b>Competitions</b> (all 18) and <b>Robotics Lab Setup</b>. '
         '<b>Tick all</b> and <b>Clear all</b> are shortcuts. Assessment File, Tickora Parental App and Industrial Visit are always included.')]
st += box('Sometimes the cheapest programme covering your ticks also includes extra items. They are marked <b>Bonus</b> in the app at no extra cost.')
st += [PageBreak()]
st += [P('Additional service', h2)]
st += shot('03-service.jpg', width=CONTENT_W * 0.92, cap='Tick Additional Service, then type what the service is. The rate that applies is highlighted.')
st += [P('The additional service is an optional add-on charged <b>per student</b>. Type its name (for example "AI Lab Maintenance"); '
         'the name appears in the estimate and the PDF. Typing a name ticks the box for you. The rate depends on the school\'s size:'), Spacer(1, 4)]
st += [table([['Number of students', 'Rate per student'], ['Up to 1,500', '₹150'], ['1,501 to 2,500', '₹135 (10% less)'], ['Above 2,500', '₹100']],
             [70 * mm, 60 * mm])]
st += box('If the service is ticked but its name is empty, the app asks you to type it before generating.', 'note')

# ---------- 6. Step 4 ----------
st += [PageBreak(), P('SECTION 6', eyebrow), StepTitle(4, 'Adjustments and grand total', TEAL), Spacer(1, 6)]
st += shot('04-adjustments.jpg', width=CONTENT_W * 0.92, cap='Step 4: discount, GST and the "Show grand total in the estimate" checkbox.')
st += [table([['Setting', 'What it does'],
              ['Special discount (%)', 'Taken off the per-student price. The app and PDF show the discount per student, and the total discount when the grand total is shown.'],
              ['Tax / GST (%)', 'Added on top after the discount. Leave at 0 if the price is quoted without tax.'],
              ['Show grand total in the estimate', '<b>Unticked (default):</b> the PDF shows per-student amounts only, with the amount per student in words.<br/>'
               '<b>Ticked:</b> the PDF also shows the grand total, the total discount and the grand total in words.']],
             [52 * mm, CONTENT_W - 52 * mm])]

# ---------- 7. Generate ----------
st += [PageBreak(), P('SECTION 7', eyebrow), P('Generate the estimate', h1)]
st += [P('Press <b>Generate estimate</b>. The price appears on the right (below the form on a phone), and the estimate is saved straight away. '
         'If you change anything afterwards, the price hides again and the button reads <b>Generate updated estimate</b>, so you never send an out-of-date price.')]
st += [Spacer(1, 6)] + shot('05-quote.jpg', cap='After Generate: the final amount per student, the total for all students in figures and words, and the Download PDF button.')
st += [KeepTogether([P('Price breakdown', h2)] + shot('06-breakdown.jpg', width=CONTENT_W * 0.92,
        cap='The breakdown shows every step from programme price to grand total, and the checklist of what the school gets.'))]

# ---------- 8. PDF ----------
st += [PageBreak(), P('SECTION 8', eyebrow), P('Download the PDF estimate', h1)]
st += [P('Press <b>Download PDF</b>. The file is named like <font name="UI-Semi">Estimate_UNG-261118-004_School_Name.pdf</font> and saved to your '
         '<b>Downloads</b> folder. The form then clears, ready for the next school; your executive name and email stay filled in.')]
sample = Table([[shot('09-sample-estimate.png', width=88 * mm)[0],
                 [P('What the PDF contains', h2)] + bullets([
                     'UniqNextGen logo, <b>estimate number</b> and <b>date</b> (and a "Revised" date after an edit).',
                     '<b>Prepared for</b>: school, in-charge (Attn:) and number of students.',
                     '<b>Programme</b>: training model, and <b>Prepared by</b>: executive name and email.',
                     'A table of all <b>deliverables</b>, each marked Included or Not Included.',
                     'The <b>price summary</b>: programme price, additional service, discount, GST and the <b>final amount per student</b>.',
                     'The <b>grand total</b> and total discount, only when that box is ticked.',
                     'Notes, and the amount <b>in words</b> in Indian style (lakh, crore).',
                     'Website and email in the footer.'])]],
               colWidths=[92 * mm, CONTENT_W - 92 * mm])
sample.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LEFTPADDING', (0, 0), (-1, -1), 0)]))
st += [Spacer(1, 6), sample, P('A sample estimate: 450 students, students trained, books, notebook, competitions, AI Lab Maintenance, 5% discount, grand total shown.', caption)]
st += box('The PDF writes amounts as "Rs." because the PDF font has no ₹ symbol. The app itself shows ₹.')

# ---------- 9. Saved ----------
st += [PageBreak(), P('SECTION 9', eyebrow), P('Saved estimates: edit, re-download, delete', h1)]
st += shot('07-saved.jpg', cap='Saved estimates, newest first, with the in-charge, executive, estimate number, date and price.')
st += [table([['Button', 'What it does'],
              ['Edit', 'Loads the estimate back into the form. Change anything, then press <b>Generate updated estimate</b>. '
                       'The estimate number and original date stay the same; the PDF shows a "Revised" date.'],
              ['PDF', 'Downloads that estimate\'s PDF again, exactly as saved.'],
              ['Delete', 'Removes the estimate. Click once, then click <b>Confirm delete</b> within 4 seconds. This cannot be undone.'],
              ['Search box', 'Finds estimates by school, in-charge, executive or estimate number.']],
             [30 * mm, CONTENT_W - 30 * mm])]
st += box('Saved estimates stay <b>in the browser and device where you made them</b>. They do not move to another computer or phone, '
          'and clearing the browser\'s data deletes them. Keep the downloaded PDFs as your permanent copy.', 'note')

# ---------- 10. Phone + Android ----------
st += [PageBreak(), P('SECTION 10', eyebrow), P('Using the app on a phone, and the Android app', h1)]
phone = Table([[shot('08-phone.jpg', width=62 * mm)[0],
                [P('On a phone browser', h2),
                 P('Open the same website on your phone. The layout stacks into one column: fill in the steps from top to bottom, then press '
                   '<b>Generate estimate</b>; the page scrolls to the price automatically.'),
                 P('Android app', h2)] + bullets([
                    'Copy <b>UniqNextGen-Estimates-v1.7.apk</b> to the phone (Android 7.0 or newer) and tap it.',
                    'The first time, allow installing from that source when Android asks.',
                    'Open <b>UniqNextGen Estimates</b> from the app list. It works without internet.',
                    '<b>Download PDF</b> saves straight to the phone\'s <b>Downloads</b> folder. On Android 9 or older, allow storage access once, then tap Download again.',
                    'To update, install the newer APK over the old one. Saved estimates are kept.'])]],
              colWidths=[66 * mm, CONTENT_W - 66 * mm])
phone.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LEFTPADDING', (0, 0), (-1, -1), 0), ('LEFTPADDING', (1, 0), (1, 0), 8)]))
st += [phone]

# ---------- 11. Pricing ----------
st += [PageBreak(), P('SECTION 11', eyebrow), P('How prices are worked out', h1)]
st += [P('This section is for reference. The app applies these rules automatically.'), P('Programme prices (per student)', h2)]
Y, N = '<font color="#138a43"><b>Yes</b></font>', '<font color="#d23b30">No</font>'
pk = [['Price', 'Developer trains', 'Books', 'Notebook', 'Competitions', 'Robotics Lab'],
      ['₹2,500', 'Students', Y, Y, Y, Y], ['₹2,000', 'Students', Y, Y, Y, N], ['₹2,000 *', 'Computer teachers', Y, Y, Y, Y],
      ['₹1,750', 'Computer teachers', N, Y, Y, Y], ['₹1,500', 'Computer teachers', Y, Y, Y, N], ['₹1,200', 'Students', N, N, N, N],
      ['₹1,200', 'Computer teachers', N, N, Y, N], ['₹1,000', 'Computer teachers', N, N, N, N]]
st += [table(pk, [22 * mm, 38 * mm] + [(CONTENT_W - 60 * mm) / 4] * 4)]
st += [P('All programmes include Trainer Allocation, Assessment File, Tickora Parental App and Industrial Visit. '
         '* Computer teachers with all materials is worked out from the annexures: the all-materials price (₹2,500) minus the '
         '₹500 saved when the developer trains teachers instead of students.', small)]
st += [P('The rules, in order', h2)]
st += [table([['#', 'Rule', 'Example (450 students)'],
              ['1', 'The <b>lowest programme price</b> that covers every ticked item and the chosen training model.', 'Students + Books, Notebook, Competitions → ₹2,000'],
              ['2', '<b>Additional service</b> added per student by school size (₹150 / ₹135 / ₹100).', '+ ₹150 → ₹2,150'],
              ['3', '<b>Maximum ₹2,500</b> per student. Anything above is held at ₹2,500.', '₹2,500 + ₹150 → ₹2,500'],
              ['4', '<b>Discount</b> taken off.', '5% of ₹2,150 = − ₹107.50 → ₹2,042.50'],
              ['5', '<b>GST</b> added on top (it can take the final amount above ₹2,500).', '0% → ₹2,042.50'],
              ['6', '<b>Grand total</b> = final amount per student × number of students.', '₹2,042.50 × 450 = ₹9,19,125']],
             [8 * mm, 92 * mm, CONTENT_W - 100 * mm])]

# ---------- 12. FAQ ----------
st += [PageBreak(), P('SECTION 12', eyebrow), P('Questions and troubleshooting', h1)]
faq = [('The app switched to a different training model.',
        'No programme offers that training model with exactly those items. The app shows a warning and uses the closest option; '
        'press the "Switch to…" link in the warning, or change your ticks.'),
       ('An item I did not tick says "Bonus".', 'The cheapest programme for your ticks already includes it, at no extra cost.'),
       ('The price disappeared after I changed something.', 'That is deliberate. Press <b>Generate updated estimate</b> to recalculate.'),
       ('Generate does nothing.', 'A required field is empty or the email is not valid. The field is highlighted in red with a message.'),
       ('Where did the PDF go?', 'Your browser\'s <b>Downloads</b> folder (or the phone\'s Downloads folder in the Android app). '
        'If your browser asks where to save files, choose a folder.'),
       ('I cannot see my saved estimates.', 'They are kept in the browser and device where you made them. Open the app in the same browser on the same device.'),
       ('Can I change an estimate after sending it?', 'Yes. Use <b>Edit</b>, generate again and download the new PDF. It keeps the same number and shows a Revised date.'),
       ('The grand total is not on the PDF.', 'Tick <b>Show grand total in the estimate</b> in Step 4, generate again and download.')]
for qn, an in faq:
    st += [KeepTogether([P(f'<b>{qn}</b>', S('q', spaceBefore=6, spaceAfter=1)), P(an)])]
st += [Spacer(1, 10)] + box('For help, email <b>admin@uniqnextgen.in</b> with the estimate number (for example UNG-261118-004) and a short description.')

doc.build(st)
print('Wrote', OUT)
