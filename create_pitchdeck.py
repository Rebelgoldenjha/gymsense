#!/usr/bin/env python3
"""
Create GYMSENSE Startup Bihar Pitch Deck using python-pptx
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
import os

# Color palette
NAVY = RGBColor(0x2F, 0x3C, 0x7E)        # 2F3C7E
CORAL = RGBColor(0xF9, 0x61, 0x67)       # F96167
GOLD = RGBColor(0xF9, 0xE7, 0x95)        # F9E795
DEEP_BLUE = RGBColor(0x06, 0x5A, 0x82)   # 065A82
TEAL = RGBColor(0x1C, 0x72, 0x93)        # 1C7293
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_GRAY = RGBColor(0xF5, 0xF5, 0xF5)
MED_GRAY = RGBColor(0x88, 0x88, 0x88)
DARK_TEXT = RGBColor(0x2F, 0x3C, 0x7E)
LIGHT_PINK = RGBColor(0xFF, 0xF8, 0xF8)
LIGHT_CORAL = RGBColor(0xFF, 0xF0, 0xF0)

prs = Presentation()
prs.slide_width = Inches(10)
prs.slide_height = Inches(5.625)

# Helper functions
def add_background(slide, color):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_shape_bg(slide, left, top, width, height, fill_color, line_color=None, line_width=None):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if line_color:
        shape.line.color.rgb = line_color
        shape.line.width = line_width or Pt(1)
    else:
        shape.line.fill.background()
    return shape

def add_text_box(slide, left, top, width, height, text, font_size=14, bold=False, color=DARK_TEXT, alignment=PP_ALIGN.LEFT, font_name='Calibri', line_spacing=1.0):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.bold = bold
    p.font.color.rgb = color
    p.font.name = font_name
    p.alignment = alignment
    if line_spacing != 1.0:
        p.line_spacing = Pt(int(font_size * line_spacing))
    return txBox

def add_rich_text_box(slide, left, top, width, height, runs, alignment=PP_ALIGN.LEFT, line_spacing=1.0):
    """runs = list of dicts: {text, font_size, bold, color, font_name}"""
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = alignment
    if line_spacing != 1.0:
        p.line_spacing = Pt(int(runs[0]['font_size'] * line_spacing)) if runs else Pt(14)
    for run_data in runs:
        run = p.add_run()
        run.text = run_data['text']
        run.font.size = Pt(run_data.get('font_size', 14))
        run.font.bold = run_data.get('bold', False)
        run.font.color.rgb = run_data.get('color', DARK_TEXT)
        run.font.name = run_data.get('font_name', 'Calibri')
    return txBox

def add_bullet_list(slide, left, top, width, height, items, font_size=13, color=DARK_TEXT, font_name='Calibri', spacing=4):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = item
        p.font.size = Pt(font_size)
        p.font.color.rgb = color
        p.font.name = font_name
        p.level = 0
        p.space_after = Pt(spacing)
    return txBox

def add_footer(slide):
    # Footer bar
    add_shape_bg(slide, Inches(0), Inches(5.2), Inches(10), Inches(0.425), LIGHT_GRAY, RGBColor(0xE0,0xE0,0xE0), Pt(1))
    add_text_box(slide, Inches(0.5), Inches(5.25), Inches(9), Inches(0.35),
                 "GYMSENSE  |  Startup Bihar Pitch  |  Confidential",
                 font_size=9, color=MED_GRAY, font_name='Calibri')
    # Slide number placeholder
    slide_num_box = add_text_box(slide, Inches(9.2), Inches(5.25), Inches(0.6), Inches(0.35),
                 "{slide_number}",
                 font_size=9, color=MED_GRAY, font_name='Calibri', alignment=PP_ALIGN.RIGHT)

def add_slide_number(slide, num):
    # Update the slide number placeholder
    for shape in slide.shapes:
        if shape.has_text_frame and shape.text_frame.text == "{slide_number}":
            shape.text_frame.text = str(num)
            shape.text_frame.paragraphs[0].font.size = Pt(9)
            shape.text_frame.paragraphs[0].font.color.rgb = MED_GRAY
            shape.text_frame.paragraphs[0].font.name = 'Calibri'
            shape.text_frame.paragraphs[0].alignment = PP_ALIGN.RIGHT
            break

# ============================================================
# SLIDE 1: TITLE SLIDE
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank layout
add_background(slide, NAVY)
add_text_box(slide, Inches(1), Inches(1.5), Inches(8), Inches(1.5),
             "GYMSENSE", font_size=48, bold=True, color=WHITE,
             alignment=PP_ALIGN.CENTER, font_name='Cambria')
add_text_box(slide, Inches(1), Inches(3.2), Inches(8), Inches(1),
             "Your AI Form Coach in the Browser\nNo Hardware \u2022 No Wearable \u2022 Just Your Camera",
             font_size=22, color=GOLD, alignment=PP_ALIGN.CENTER, font_name='Calibri', line_spacing=1.3)
add_text_box(slide, Inches(1), Inches(4.8), Inches(8), Inches(0.5),
             "Startup Bihar Pitch Deck  |  November 2026",
             font_size=16, color=CORAL, alignment=PP_ALIGN.CENTER, font_name='Cambria')

# ============================================================
# SLIDE 2: EXECUTIVE SUMMARY
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_footer(slide)
add_text_box(slide, Inches(0.5), Inches(0.4), Inches(9), Inches(0.8),
             "Executive Summary", font_size=36, bold=True, color=NAVY, font_name='Cambria')

add_rich_text_box(slide, Inches(0.5), Inches(1.4), Inches(9), Inches(0.8), [
    {'text': 'The Problem: ', 'bold': True, 'color': NAVY, 'font_size': 15, 'font_name': 'Calibri'},
    {'text': '73% of home exercisers use incorrect form, risking injury and wasting effort. Personal trainers cost $150-300/mo. Free apps (Nike, YouTube) offer zero feedback.', 'color': NAVY, 'font_size': 15, 'font_name': 'Calibri'}
], line_spacing=1.3)

add_rich_text_box(slide, Inches(0.5), Inches(2.2), Inches(9), Inches(0.8), [
    {'text': 'The Solution: ', 'bold': True, 'color': CORAL, 'font_size': 15, 'font_name': 'Calibri'},
    {'text': 'GYMSENSE runs MediaPipe pose estimation in-browser. Select an exercise - camera auto-starts - 33 keypoints tracked - real-time joint angles - rep counting - instant form feedback (Knees caving - push out!). 7 exercises at launch.', 'color': NAVY, 'font_size': 15, 'font_name': 'Calibri'}
], line_spacing=1.3)

add_rich_text_box(slide, Inches(0.5), Inches(3.1), Inches(9), Inches(1), [
    {'text': 'The Pivot (Our Moat): ', 'bold': True, 'color': DEEP_BLUE, 'font_size': 15, 'font_name': 'Calibri'},
    {'text': 'B2C fitness apps have 8% monthly churn and $45 CAC. We are building a B2B2C Trainer OS: trainers pay $50/mo for client management + AI form analysis; their clients get free access. Trainers become our distribution channel. Network effects + switching costs + data flywheel.', 'color': NAVY, 'font_size': 15, 'font_name': 'Calibri'}
], line_spacing=1.3)

# Score cards
scores = [
    ("Uniqueness", "4/10", CORAL),
    ("Scalability", "6/10", GOLD),
    ("Profitability", "5/10", DEEP_BLUE),
    ("Defensibility", "3/10 \u2192 8/10*", TEAL),
    ("Execution", "4/10", NAVY)
]
for i, (label, value, color) in enumerate(scores):
    add_text_box(slide, Inches(0.5 + i * 1.85), Inches(4.2), Inches(1.6), Inches(0.7),
                 value, font_size=28, bold=True, color=color, alignment=PP_ALIGN.CENTER, font_name='Cambria')
    add_text_box(slide, Inches(0.5 + i * 1.85), Inches(4.85), Inches(1.6), Inches(0.4),
                 label, font_size=11, color=NAVY, alignment=PP_ALIGN.CENTER, font_name='Calibri')
add_text_box(slide, Inches(0.5), Inches(5.0), Inches(9), Inches(0.3),
             "*With Trainer Platform pivot", font_size=9, color=MED_GRAY, alignment=PP_ALIGN.CENTER, font_name='Calibri')

# ============================================================
# SLIDE 3: PROBLEM VALIDATION
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_footer(slide)
add_text_box(slide, Inches(0.5), Inches(0.4), Inches(9), Inches(0.8),
             "Problem Validation", font_size=36, bold=True, color=NAVY, font_name='Cambria')

problems = [
    "73% of home exercisers use incorrect form (ACSM data)",
    "Form errors \u2192 injury (3.5M gym injuries/yr in US) + wasted reps",
    "Personal trainers: $150-300/mo - unaffordable for most",
    "Free apps (Nike Training Club, YouTube) = zero feedback loop",
    "Mirror/checking phone = subjective, inconsistent, no rep counting",
    "Pain is chronic (injury later), not acute - hard to sell urgency"
]
add_bullet_list(slide, Inches(0.5), Inches(1.3), Inches(9), Inches(3), problems,
                font_size=15, color=NAVY, font_name='Calibri', spacing=6)

add_text_box(slide, Inches(0.5), Inches(4.7), Inches(9), Inches(0.5),
             "Verdict: Real problem, but 'nice-to-have' for most. Must-have only after injury.",
             font_size=14, bold=True, color=CORAL, font_name='Calibri')

# ============================================================
# SLIDE 4: TARGET AUDIENCE
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_footer(slide)
add_text_box(slide, Inches(0.5), Inches(0.4), Inches(9), Inches(0.8),
             "Target Audience", font_size=36, bold=True, color=NAVY, font_name='Cambria')

# Primary
add_text_box(slide, Inches(0.5), Inches(1.3), Inches(4), Inches(0.4),
             "PRIMARY: Marcus - Home Strength Enthusiast", font_size=18, bold=True, color=CORAL, font_name='Cambria')
add_bullet_list(slide, Inches(0.5), Inches(1.7), Inches(4), Inches(2.5), [
    "Age 25-40, $75k+ HHI, remote/hybrid worker",
    "Owns dumbbells/kettlebells or bodyweight-only",
    "Works out 3-5x/week, follows programs",
    "Tried Peloton (too cardio), Freeletics (no form feedback)",
    "Willing to pay $12-20/mo for form confidence",
    "TAM: ~18M US | SAM: ~$2.5B (AI form-coaching niche)"
], font_size=13, color=NAVY, font_name='Calibri', spacing=4)

# Secondary
add_text_box(slide, Inches(5), Inches(1.3), Inches(4), Inches(0.4),
             "SECONDARY: New Year Resolution Beginners", font_size=18, bold=True, color=GOLD, font_name='Cambria')
add_bullet_list(slide, Inches(5), Inches(1.7), Inches(4), Inches(2), [
    "Age 20-35, sporadic exercisers, high churn",
    "Price sensitive ($0-10/mo)",
    "Need habit formation + basic guidance",
    "TAM: ~35M US | Low LTV, high volume"
], font_size=13, color=NAVY, font_name='Calibri', spacing=4)

# Early adopters
add_text_box(slide, Inches(0.5), Inches(3.8), Inches(4), Inches(0.4),
             "EARLY ADOPTERS: Quantified-Self / Biohackers", font_size=18, bold=True, color=DEEP_BLUE, font_name='Cambria')
add_bullet_list(slide, Inches(0.5), Inches(4.2), Inches(4), Inches(1.2), [
    "Track HRV, sleep, macros, now: form quality",
    "Willing to pay $20-30/mo for data",
    "TAM: ~2M US | High referral potential"
], font_size=13, color=NAVY, font_name='Calibri', spacing=4)

# B2B persona
add_text_box(slide, Inches(5), Inches(3.8), Inches(4), Inches(0.4),
             "B2B PERSONA: Sarah - Independent Trainer", font_size=18, bold=True, color=TEAL, font_name='Cambria')
add_bullet_list(slide, Inches(5), Inches(4.2), Inches(4), Inches(1.8), [
    "300k+ certified trainers in US",
    "Capped at ~30 1:1 clients ($3k-6k/mo ceiling)",
    "No tools to scale form coaching",
    "Pays $50-100/mo for Trainer OS",
    "Brings 10-30 clients each = distribution"
], font_size=13, color=NAVY, font_name='Calibri', spacing=4)

# ============================================================
# SLIDE 5: MARKET SIZE
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_footer(slide)
add_text_box(slide, Inches(0.5), Inches(0.4), Inches(9), Inches(0.8),
             "Market Sizing", font_size=36, bold=True, color=NAVY, font_name='Cambria')

add_rich_text_box(slide, Inches(0.5), Inches(1.3), Inches(9), Inches(0.5), [
    {'text': 'TAM (Global Digital Fitness): ', 'bold': True, 'color': NAVY, 'font_size': 16, 'font_name': 'Calibri'},
    {'text': '$59B (2023) to $140B (2030 CAGR 12.5%)', 'color': NAVY, 'font_size': 16, 'font_name': 'Calibri'}
])
add_rich_text_box(slide, Inches(0.5), Inches(1.9), Inches(9), Inches(0.5), [
    {'text': 'SAM (AI Form-Coaching Niche): ', 'bold': True, 'color': CORAL, 'font_size': 16, 'font_name': 'Calibri'},
    {'text': '~$2.5B (3% of digital fitness, growing 25% YoY)', 'color': NAVY, 'font_size': 16, 'font_name': 'Calibri'}
])
add_rich_text_box(slide, Inches(0.5), Inches(2.5), Inches(9), Inches(0.5), [
    {'text': 'SOM (Realistic 5-Year Capture): ', 'bold': True, 'color': DEEP_BLUE, 'font_size': 16, 'font_name': 'Calibri'},
    {'text': '$5-15M ARR (0.2-0.6% SAM) with Trainer Platform', 'color': NAVY, 'font_size': 16, 'font_name': 'Calibri'}
])

# Visual TAM/SAM/SOM boxes
for x_val, label, value in [(1, "TAM", "$140B"), (3.75, "SAM", "$2.5B"), (6.5, "SOM (5yr)", "$15M")]:
    box = add_shape_bg(slide, Inches(x_val), Inches(3.3), Inches(2.5), Inches(1.2), NAVY, CORAL, Pt(2))
    add_text_box(slide, Inches(x_val), Inches(3.3), Inches(2.5), Inches(0.5),
                 label, font_size=14, bold=True, color=WHITE, alignment=PP_ALIGN.CENTER, font_name='Cambria')
    add_text_box(slide, Inches(x_val), Inches(3.7), Inches(2.5), Inches(0.6),
                 value, font_size=28, bold=True, color=WHITE, alignment=PP_ALIGN.CENTER, font_name='Cambria')

# ============================================================
# SLIDE 6: TOP 10 COMPETITORS
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_footer(slide)
add_text_box(slide, Inches(0.5), Inches(0.4), Inches(9), Inches(0.8),
             "Top 10 Competitors", font_size=36, bold=True, color=NAVY, font_name='Cambria')

comp_headers = ["#", "Company", "Model", "Pricing", "Funding", "Revenue", "Users", "Gap They Leave"]
comp_rows = [
    ["1", "Tempo", "Hardware + Sub", "$395+ HW + $39/mo", "$220M", "~$100M", "~50k", "Portable/bodyweight; $400 barrier"],
    ["2", "Zenia", "Freemium App", "$14.99/mo", "$1.2M", "~$2M", "~200k", "Yoga/pilates only; no strength"],
    ["3", "Kaia Health", "B2B2C (Insurers)", "Free to patient", "$120M+", "~$50M", "600k+", "Clinical only; not for healthy users"],
    ["4", "Fitbod", "Sub (no camera)", "$12.99/mo", "$12M", "~$30M", "1M+", "No form feedback; no camera"],
    ["5", "Freeletics", "Freemium HIIT", "$11.99/mo", "$25M", "~$60M", "50M+ DL", "No camera form analysis"],
    ["6", "JuggernautAI", "Sub (powerlifting)", "$29.99/mo", "Bootstrapped", "~$5M", "~30k", "Niche; no form tech"],
    ["7", "Nike Training Club", "Free (brand)", "Free", "N/A", "N/A", "50M+", "No AI; no personalization"],
    ["8", "Mirror/Lululemon", "Hardware + Sub", "$995+ HW + $39/mo", "Acquired $500M", "~$150M", "~200k", "Class-based; trainer can't see you"],
    ["9", "Strong/Hevy", "Freemium Logger", "$5-8/mo", "Minimal", "~$3M", "2M+", "No AI; manual entry only"],
    ["10", "Caliber", "Human Remote Coach", "$199/mo", "$12M", "~$10M", "~5k", "Too expensive; doesn't scale"]
]

table_data = [comp_headers] + comp_rows
rows = len(table_data)
cols = len(comp_headers)

table_shape = slide.shapes.add_table(rows, cols, Inches(0.3), Inches(1.1), Inches(9.4), Inches(4.2))
table = table_shape.table

# Set column widths
col_widths = [Inches(0.3), Inches(1.2), Inches(1.1), Inches(1.1), Inches(0.9), Inches(0.9), Inches(0.8), Inches(2.1)]
for i, w in enumerate(col_widths):
    table.columns[i].width = w

for row_idx, row_data in enumerate(table_data):
    for col_idx, cell_text in enumerate(row_data):
        cell = table.cell(row_idx, col_idx)
        cell.text = cell_text
        for paragraph in cell.text_frame.paragraphs:
            paragraph.font.size = Pt(9.5)
            paragraph.font.name = 'Calibri'
            if row_idx == 0:
                paragraph.font.bold = True
                paragraph.font.color.rgb = WHITE
            else:
                paragraph.font.color.rgb = NAVY

# Style header row
for col_idx in range(cols):
    cell = table.cell(0, col_idx)
    cell.fill.solid()
    cell.fill.fore_color.rgb = NAVY

# Alternate row colors
for row_idx in range(1, rows):
    for col_idx in range(cols):
        cell = table.cell(row_idx, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = WHITE if row_idx % 2 == 1 else LIGHT_PINK

# ============================================================
# SLIDE 7: MARKET GAP ANALYSIS
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_footer(slide)
add_text_box(slide, Inches(0.5), Inches(0.4), Inches(9), Inches(0.8),
             "Market Gap Analysis: Where Competitors Miss", font_size=36, bold=True, color=NAVY, font_name='Cambria')

gaps = [
    ("No Duolingo for Form",
     "All competitors are: (a) hardware-gated $400+, (b) human-coach-gated $150+/mo, (c) no form feedback, or (d) single-modality (yoga only). Mass market wants <$20/mo, no hardware, strength + mobility.",
     "LARGE"),
    ("Form Feedback for Compound Movements",
     "Tempo does this but requires hardware. Zenia only yoga. Kaia focuses on rehab, not performance. Squat/deadlift/bench = highest injury risk + highest demand.",
     "MEDIUM"),
    ("Privacy-First Local Processing",
     "All cloud AI fitness apps upload video. GYMSENSE can run MediaPipe in-browser (WebAssembly) - zero video leaves device.",
     "GROWING"),
    ("Travel/Zero-Equipment Mode",
     "Hardware solutions fail here. App solutions exist but lack form feedback. 60M+ business travelers/yr + hotel gym constraints.",
     "MEDIUM"),
    ("Coach/Trainer Tools (B2B2C)",
     "No platform lets human trainers USE AI form analysis to scale 1:many. 300k+ certified trainers in US, each capped at ~30 clients.",
     "LARGE - $1B OPPORTUNITY")
]

for i, (gap, evidence, size) in enumerate(gaps):
    y = Inches(1.3 + i * 0.85)
    add_text_box(slide, Inches(0.5), y, Inches(9), Inches(0.35),
                 f"{i+1}. {gap}", font_size=16, bold=True, color=CORAL, font_name='Cambria')
    add_text_box(slide, Inches(0.5), Inches(y.inches + 0.35), Inches(7.5), Inches(0.45),
                 evidence, font_size=12, color=NAVY, font_name='Calibri')
    size_color = CORAL if "LARGE - $1B" in size else (GOLD if size == "LARGE" else DEEP_BLUE)
    add_text_box(slide, Inches(8.2), y, Inches(1.5), Inches(0.35),
                 size, font_size=12, bold=True, color=size_color, alignment=PP_ALIGN.RIGHT, font_name='Cambria')

add_text_box(slide, Inches(0.5), Inches(5.0), Inches(9), Inches(0.5),
             "The $1B Company: B2B2C Platform for Trainers - Shopify for Personal Trainers with AI Form Analysis as Killer Feature",
             font_size=14, bold=True, color=CORAL, font_name='Calibri')

# ============================================================
# SLIDE 8: RECOMMENDED USP
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_footer(slide)
add_text_box(slide, Inches(0.5), Inches(0.4), Inches(9), Inches(0.8),
             "Recommended Unique Selling Proposition", font_size=36, bold=True, color=NAVY, font_name='Cambria')

add_text_box(slide, Inches(0.5), Inches(1.5), Inches(9), Inches(1.2),
             "The only AI form coach that works on any device, requires zero equipment, and lets your actual human trainer see your reps in real-time - for the price of a coffee.",
             font_size=24, bold=True, color=CORAL, alignment=PP_ALIGN.CENTER, font_name='Cambria', line_spacing=1.3)

usp_reasons = [
    ("Hard to Copy", "Requires trainer dashboard, client management, video review workflow, payment splitting - not just pose estimation."),
    ("High Value", "Solves trainer's scaling problem (income ceiling) + client's accountability problem. Two-sided value."),
    ("One Sentence", "Passes the grandmother test. Clear, memorable, shareable."),
    ("Long-Term Moat", "Network effects (trainer<->client), data flywheel (labeled reps from pros), switching costs (trainer's business runs on it).")
]

for i, (label, detail) in enumerate(usp_reasons):
    y = Inches(3.0 + i * 0.5)
    add_text_box(slide, Inches(1), y, Inches(2.5), Inches(0.4),
                 f"{i+1}. {label}", font_size=15, bold=True, color=NAVY, font_name='Cambria')
    add_text_box(slide, Inches(3.5), y, Inches(6), Inches(0.4),
                 detail, font_size=13, color=NAVY, font_name='Calibri')

add_text_box(slide, Inches(0.5), Inches(4.9), Inches(9), Inches(0.5),
             "Stronger than competitors: Tempo sells hardware; Zenia sells yoga; Kaia sells rehab; Caliber sells humans. Nobody sells the trainer-tool + client-app loop.",
             font_size=13, bold=True, color=CORAL, alignment=PP_ALIGN.CENTER, font_name='Calibri')

# ============================================================
# SLIDE 9: REVENUE OPPORTUNITIES
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_footer(slide)
add_text_box(slide, Inches(0.5), Inches(0.4), Inches(9), Inches(0.8),
             "Revenue Streams (Ranked by Profitability)", font_size=36, bold=True, color=NAVY, font_name='Cambria')

rev_headers = ["Rank", "Stream", "Model", "Margin", "Effort", "Notes"]
rev_rows = [
    ["1", "Trainer SaaS (B2B2C)", "$50-100/mo per trainer", "85%", "High", "Core moat; network effects"],
    ["2", "Consumer Pro Sub", "$15-20/mo", "80%", "Medium", "Direct; high churn risk"],
    ["3", "Enterprise/Wellness", "$5-10 PEPM", "75%", "High", "Employers/insurers; long sales cycle"],
    ["4", "White-Label for Gyms", "$500-2k/mo per location", "70%", "High", "Gym chains want branded app"],
    ["5", "Affiliate/Equipment", "5-10% commission", "95%", "Low", "Link to Rogue, Titan, Amazon"],
    ["6", "Premium Exercise Library", "$5/mo add-on", "90%", "Medium", "Video demos, progressions, mobility"],
    ["7", "API Access", "$0.01/analysis", "60%", "High", "Other apps embed form check"],
    ["8", "Data/Analytics (Anon)", "License to researchers", "50%", "Very High", "Ethical/legal minefield"],
    ["9", "Certification/CEU", "$100-300/course", "85%", "Medium", "Trainers need CEUs; you have platform"],
    ["10", "Marketplace (Trainer Finder)", "15-20% take rate", "70%", "Very High", "Chicken-egg; need liquidity first"]
]

table_data = [rev_headers] + rev_rows
rows = len(table_data)
cols = len(rev_headers)

table_shape = slide.shapes.add_table(rows, cols, Inches(0.3), Inches(1.1), Inches(9.4), Inches(4.2))
table = table_shape.table

col_widths = [Inches(0.4), Inches(1.5), Inches(1.4), Inches(0.7), Inches(0.7), Inches(3.7)]
for i, w in enumerate(col_widths):
    table.columns[i].width = w

for row_idx, row_data in enumerate(table_data):
    for col_idx, cell_text in enumerate(row_data):
        cell = table.cell(row_idx, col_idx)
        cell.text = cell_text
        for paragraph in cell.text_frame.paragraphs:
            paragraph.font.size = Pt(9.5)
            paragraph.font.name = 'Calibri'
            if row_idx == 0:
                paragraph.font.bold = True
                paragraph.font.color.rgb = WHITE
            else:
                paragraph.font.color.rgb = NAVY

for col_idx in range(cols):
    cell = table.cell(0, col_idx)
    cell.fill.solid()
    cell.fill.fore_color.rgb = NAVY

for row_idx in range(1, rows):
    for col_idx in range(cols):
        cell = table.cell(row_idx, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = WHITE if row_idx % 2 == 1 else LIGHT_PINK

# ============================================================
# SLIDE 10: FINANCIAL PROJECTIONS & ASSUMPTIONS
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_footer(slide)
add_text_box(slide, Inches(0.5), Inches(0.4), Inches(9), Inches(0.8),
             "Financial Projections & Key Assumptions", font_size=36, bold=True, color=NAVY, font_name='Cambria')

# Assumptions left
add_text_box(slide, Inches(0.5), Inches(1.3), Inches(4), Inches(0.4),
             "KEY ASSUMPTIONS", font_size=16, bold=True, color=CORAL, font_name='Cambria')
assumptions = [
    "Starting capital: $50k (founder savings)",
    "Team: 2 founders (eng + product) + 1 ML contractor",
    "Consumer churn: 8%/mo (industry avg); Trainer churn: 3%/mo",
    "CAC: Consumer $45 (content+referral); Trainer $200 (outbound)",
    "LTV: Consumer $180 (15mo @ $12); Trainer $1,800 (36mo @ $50)",
    "Gross margin: 80% (cloud + payment fees only)",
    "Trainer channel = lever (LTV 10x consumer)"
]
add_bullet_list(slide, Inches(0.5), Inches(1.7), Inches(4.5), Inches(2.5), assumptions,
                font_size=11, color=NAVY, font_name='Calibri', spacing=4)

# Projections right
add_text_box(slide, Inches(5.5), Inches(1.3), Inches(4), Inches(0.4),
             "PROJECTIONS", font_size=16, bold=True, color=CORAL, font_name='Cambria')

proj_data = [
    ["Metric", "Value"],
    ["MVP Cost (3 mo)", "$30k"],
    ["Monthly OpEx (Yr 1)", "$8k"],
    ["Break-Even", "Month 14"],
    ["Year 1 Revenue", "$120k"],
    ["Year 3 Revenue", "$1.2M"],
    ["Year 5 Revenue", "$6.5M"],
    ["EBITDA Margin (Yr 5)", "35%"],
    ["", ""],
    ["Sensitivity: Trainer channel fails -> Yr 5 = $2.1M"]
]

rows = len(proj_data)
cols = 2
table_shape = slide.shapes.add_table(rows, cols, Inches(5.5), Inches(1.7), Inches(4), Inches(3.5))
table = table_shape.table
table.columns[0].width = Inches(2.2)
table.columns[1].width = Inches(1.8)

for row_idx, row_data in enumerate(proj_data):
    for col_idx, cell_text in enumerate(row_data):
        cell = table.cell(row_idx, col_idx)
        cell.text = cell_text
        for paragraph in cell.text_frame.paragraphs:
            paragraph.font.size = Pt(12)
            paragraph.font.name = 'Calibri'
            if row_idx == 0:
                paragraph.font.bold = True
                paragraph.font.color.rgb = WHITE
            else:
                paragraph.font.color.rgb = NAVY

for col_idx in range(cols):
    cell = table.cell(0, col_idx)
    cell.fill.solid()
    cell.fill.fore_color.rgb = NAVY

for row_idx in range(1, rows):
    for col_idx in range(cols):
        cell = table.cell(row_idx, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = WHITE if row_idx % 2 == 1 else LIGHT_PINK

# ============================================================
# SLIDE 11: GO-TO-MARKET STRATEGY
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_footer(slide)
add_text_box(slide, Inches(0.5), Inches(0.4), Inches(9), Inches(0.8),
             "Go-to-Market Strategy (Limited Budget)", font_size=36, bold=True, color=NAVY, font_name='Cambria')

gtm_phases = [
    ("FIRST 100 USERS", "Friends, fitness subreddits, Discord, Twitter",
     "Product Hunt launch\nForm Check Friday Twitter threads\nFree 30-day for feedback\nDiscord community for form checks", "$0"),
    ("FIRST 1,000 USERS", "Organic search, micro-influencers, trainer referrals",
     "SEO: squat form check app, AI personal trainer free\n20 micro-influencers (10-50k) -> free lifetime\nTrainer beta: 10 trainers free 6mo + rev share\nReddit: r/fitness, r/homegym weekly posts", "$2k"),
    ("FIRST 10,000 USERS", "Content + referral flywheel + paid test",
     "YouTube Shorts/TikTok daily: Is your squat killing knees?\nReferral: 1 free month per referral (both sides)\nTrainer affiliate: $20 per referred trainer\nTest Meta/Google ads at $30 CAC target\nAppSumo/LTD launch for cash + users", "$15k")
]

for i, (phase, target, tactics, budget) in enumerate(gtm_phases):
    y = Inches(1.3 + i * 1.35)
    add_text_box(slide, Inches(0.5), y, Inches(2), Inches(0.35),
                 phase, font_size=15, bold=True, color=CORAL, font_name='Cambria')
    add_text_box(slide, Inches(0.5), Inches(y.inches + 0.35), Inches(3), Inches(0.3),
                 f"Target: {target}", font_size=11, color=NAVY, font_name='Calibri')
    add_text_box(slide, Inches(3.5), Inches(y.inches + 0.35), Inches(2), Inches(0.3),
                 f"Budget: {budget}", font_size=11, bold=True, color=DEEP_BLUE, font_name='Calibri')
    add_text_box(slide, Inches(0.5), Inches(y.inches + 0.65), Inches(5.5), Inches(0.6),
                 tactics, font_size=10, color=NAVY, font_name='Calibri')

# Organic tactics on right
add_text_box(slide, Inches(6.5), Inches(1.3), Inches(3), Inches(0.4),
             "ORGANIC GROWTH TACTICS", font_size=15, bold=True, color=CORAL, font_name='Cambria')
organic = [
    "Form Fix of the Day email (daily, 2-min read)",
    "Public leaderboards (anonymized) for reps/holds",
    "Exportable Form Report Card PDF for social sharing",
    "Trainer content: How I scaled to 100 clients with GYMSENSE",
    "Trainer referral program: $20 per trainer",
    "SEO content clusters: exercise form guides"
]
add_bullet_list(slide, Inches(6.5), Inches(1.7), Inches(3), Inches(2), organic,
                font_size=11, color=NAVY, font_name='Calibri', spacing=4)

# ============================================================
# SLIDE 12: MOAT ANALYSIS
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_footer(slide)
add_text_box(slide, Inches(0.5), Inches(0.4), Inches(9), Inches(0.8),
             "Competitive Moat Analysis", font_size=36, bold=True, color=NAVY, font_name='Cambria')

moat_headers = ["Moat Type", "Current (B2C)", "With Trainer Platform", "Verdict"]
moat_rows = [
    ["Network Effects", "None", "STRONG (trainer<->client<->data)", "BUILD THIS"],
    ["Brand", "Zero", "Medium (trainer influencers)", "Long-term"],
    ["Data Advantage", "None", "STRONG (labeled reps + outcomes)", "Core asset"],
    ["AI Advantage", "None (MediaPipe open)", "Medium (fine-tuned on pro data)", "Defensible"],
    ["Switching Costs", "Zero", "HIGH (trainer's roster, billing, programs)", "KEY MOAT"],
    ["Community", "None", "Medium (trainer-led groups)", "Buildable"],
    ["Economies of Scale", "Low", "Medium (cloud costs drop)", "Minor"],
    ["Distribution", "None", "STRONG (trainer = distribution)", "CRITICAL"],
    ["Technology", "Low (commodity CV)", "Medium (real-time multi-person)", "Patentable?"],
    ["IP", "None", "2-3 patents possible", "File early"]
]

table_data = [moat_headers] + moat_rows
rows = len(table_data)
cols = len(moat_headers)

table_shape = slide.shapes.add_table(rows, cols, Inches(0.3), Inches(1.1), Inches(9.4), Inches(4.2))
table = table_shape.table

col_widths = [Inches(1.5), Inches(2), Inches(3.5), Inches(1.4)]
for i, w in enumerate(col_widths):
    table.columns[i].width = w

for row_idx, row_data in enumerate(table_data):
    for col_idx, cell_text in enumerate(row_data):
        cell = table.cell(row_idx, col_idx)
        cell.text = cell_text
        for paragraph in cell.text_frame.paragraphs:
            paragraph.font.size = Pt(10)
            paragraph.font.name = 'Calibri'
            if row_idx == 0:
                paragraph.font.bold = True
                paragraph.font.color.rgb = WHITE
            else:
                paragraph.font.color.rgb = NAVY

for col_idx in range(cols):
    cell = table.cell(0, col_idx)
    cell.fill.solid()
    cell.fill.fore_color.rgb = NAVY

for row_idx in range(1, rows):
    for col_idx in range(cols):
        cell = table.cell(row_idx, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = WHITE if row_idx % 2 == 1 else LIGHT_PINK

add_text_box(slide, Inches(0.5), Inches(5.0), Inches(9), Inches(0.4),
             "Bottom Line: Without trainer platform = ZERO MOAT. With it = 3 STRONG MOATS (network, switching, distribution).",
             font_size=13, bold=True, color=CORAL, alignment=PP_ALIGN.CENTER, font_name='Calibri')

# ============================================================
# SLIDE 13: TOP 10 RISKS & MITIGATIONS
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_footer(slide)
add_text_box(slide, Inches(0.5), Inches(0.4), Inches(9), Inches(0.8),
             "Top 10 Risks & Mitigations", font_size=36, bold=True, color=NAVY, font_name='Cambria')

risk_headers = ["#", "Risk", "Likelihood", "Impact", "Mitigation"]
risk_rows = [
    ["1", "Trainer adoption fails - don't trust AI or won't pay", "High", "Fatal", "10 pilot trainers free; build features they request; revenue share"],
    ["2", "MediaPipe accuracy insufficient - false positives frustrate", "Med", "High", "Confidence threshold UI; user corrections; collect labels for fine-tuning"],
    ["3", "Apple/Google launch native form check (Vision/ML Kit)", "Med", "High", "Differentiate on trainer workflow, not just detection; move fast"],
    ["4", "Camera permission friction kills conversion", "High", "Med", "Progressive onboarding; try without camera mode; PWA install"],
    ["5", "Consumer churn >10%/mo (industry norm)", "High", "Med", "Trainer accountability reduces churn; gamification; contracts"],
    ["6", "Unit economics don't work (CAC > LTV)", "Med", "High", "Focus on trainer channel (LTV $1,800 vs $180); organic only"],
    ["7", "Privacy backlash - app watches me exercise", "Low", "High", "Local processing option; clear policy; no video storage default"],
    ["8", "Competitor copies trainer platform (Tempo, Caliber)", "Med", "High", "Speed; exclusive trainer contracts; data flywheel"],
    ["9", "Injury liability - user hurts self following bad AI advice", "Low", "Fatal", "Disclaimers; not medical advice; insurance; confidence gating"],
    ["10", "Founder burnout / cofounder conflict", "Med", "Fatal", "Vesting; therapy; advisor board; clear decision rights"]
]

table_data = [risk_headers] + risk_rows
rows = len(table_data)
cols = len(risk_headers)

table_shape = slide.shapes.add_table(rows, cols, Inches(0.3), Inches(1.0), Inches(9.4), Inches(4.4))
table = table_shape.table

col_widths = [Inches(0.3), Inches(2.2), Inches(0.7), Inches(0.6), Inches(4.6)]
for i, w in enumerate(col_widths):
    table.columns[i].width = w

for row_idx, row_data in enumerate(table_data):
    for col_idx, cell_text in enumerate(row_data):
        cell = table.cell(row_idx, col_idx)
        cell.text = cell_text
        for paragraph in cell.text_frame.paragraphs:
            paragraph.font.size = Pt(9)
            paragraph.font.name = 'Calibri'
            if row_idx == 0:
                paragraph.font.bold = True
                paragraph.font.color.rgb = WHITE
            else:
                paragraph.font.color.rgb = NAVY

for col_idx in range(cols):
    cell = table.cell(0, col_idx)
    cell.fill.solid()
    cell.fill.fore_color.rgb = NAVY

for row_idx in range(1, rows):
    for col_idx in range(cols):
        cell = table.cell(row_idx, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = WHITE if row_idx % 2 == 1 else LIGHT_PINK

# ============================================================
# SLIDE 14: VC PERSPECTIVE
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_footer(slide)
add_text_box(slide, Inches(0.5), Inches(0.4), Inches(9), Inches(0.8),
             "VC Perspective (Sequoia / Accel / YC / a16z)", font_size=36, bold=True, color=NAVY, font_name='Cambria')

add_text_box(slide, Inches(0.5), Inches(1.3), Inches(9), Inches(0.5),
             "WOULD WE INVEST TODAY?  \u2192  NO", font_size=24, bold=True, color=CORAL, alignment=PP_ALIGN.CENTER, font_name='Cambria')

red_flags = [
    ("No Distribution Strategy", "Build it and they will come fails in fitness. CAC will be $80+, LTV $150."),
    ("No Moat", "MediaPipe is free. Any dev can clone in 2 weeks. Zero switching costs."),
    ("TAM Inflation", "$140B digital fitness != your market. SAM ~$50M without trainer channel."),
    ("Team Gap", "No fitness domain expert. No trainer relationships. No GTM experience."),
    ("Zero Traction", "0 users, 0 revenue, 0 pilots. Just code.")
]

for i, (flag, detail) in enumerate(red_flags):
    y = Inches(2.0 + i * 0.6)
    add_text_box(slide, Inches(0.5), y, Inches(2.5), Inches(0.35),
                 f"RED FLAG: {flag}", font_size=15, bold=True, color=CORAL, font_name='Cambria')
    add_text_box(slide, Inches(3), y, Inches(6.5), Inches(0.35),
                 detail, font_size=12, color=NAVY, font_name='Calibri')

add_text_box(slide, Inches(0.5), Inches(5.0), Inches(9), Inches(0.4),
             "WHAT NEEDS TO CHANGE BEFORE INVESTING:", font_size=16, bold=True, color=CORAL, font_name='Cambria')
changes = [
    "10 pilot trainers using it with 50+ paying clients, 3-month retention data",
    "Trainer dashboard MVP (client mgmt, program builder, video review, billing)",
    "Pre-seed metrics: $10k MRR, 5% weekly growth, <5% trainer churn",
    "Domain cofounder (ex-trainer or gym owner)"
]
add_bullet_list(slide, Inches(0.5), Inches(5.4), Inches(9), Inches(1.5), changes,
                font_size=12, color=NAVY, font_name='Calibri', spacing=4)

# ============================================================
# SLIDE 15: PRE-SEED VALUATION
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_footer(slide)
add_text_box(slide, Inches(0.5), Inches(0.4), Inches(9), Inches(0.8),
             "Pre-Seed Valuation Range", font_size=36, bold=True, color=NAVY, font_name='Cambria')

add_text_box(slide, Inches(0.5), Inches(1.5), Inches(9), Inches(0.4),
             "WITH TRAINER TRACTION (above metrics achieved):", font_size=18, bold=True, color=CORAL, font_name='Cambria')
add_text_box(slide, Inches(0.5), Inches(2.0), Inches(9), Inches(0.5),
             "$4M - $7M cap on $500k - $750k raise", font_size=28, bold=True, color=NAVY, alignment=PP_ALIGN.CENTER, font_name='Cambria')

add_text_box(slide, Inches(0.5), Inches(3.0), Inches(9), Inches(0.4),
             "WITHOUT TRAINER TRACTION (team + tech bet only):", font_size=18, bold=True, color=GOLD, font_name='Cambria')
add_text_box(slide, Inches(0.5), Inches(3.5), Inches(9), Inches(0.5),
             "$1.5M - $2.5M cap on $250k raise", font_size=28, bold=True, color=NAVY, alignment=PP_ALIGN.CENTER, font_name='Cambria')

add_text_box(slide, Inches(0.5), Inches(4.5), Inches(9), Inches(0.5),
             "Key Insight: The Trainer Platform pivot increases valuation 3-4x by creating defensible moats and 10x LTV.",
             font_size=14, bold=True, color=CORAL, alignment=PP_ALIGN.CENTER, font_name='Calibri')

# ============================================================
# SLIDE 16: FINAL VERDICT
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_footer(slide)
add_text_box(slide, Inches(0.5), Inches(0.4), Inches(9), Inches(0.8),
             "Final Verdict", font_size=36, bold=True, color=NAVY, font_name='Cambria')

verdict_metrics = [
    ("Overall Score", "42/100", CORAL),
    ("Prob. of Success (> $0)", "35%", GOLD),
    ("Prob. of $1M ARR", "18%", DEEP_BLUE),
    ("Prob. of $10M ARR", "4%", TEAL),
    ("Prob. of Unicorn", "0.3%", NAVY)
]

for i, (label, value, color) in enumerate(verdict_metrics):
    add_text_box(slide, Inches(0.5 + i * 1.85), Inches(1.5), Inches(1.6), Inches(0.8),
                 value, font_size=32, bold=True, color=color, alignment=PP_ALIGN.CENTER, font_name='Cambria')
    add_text_box(slide, Inches(0.5 + i * 1.85), Inches(2.3), Inches(1.6), Inches(0.5),
                 label, font_size=11, color=NAVY, alignment=PP_ALIGN.CENTER, font_name='Calibri')

add_text_box(slide, Inches(0.5), Inches(3.0), Inches(9), Inches(0.4),
             "Confidence Level: 80% (based on public comps, fitness app benchmarks, VC patterns)",
             font_size=13, color=MED_GRAY, alignment=PP_ALIGN.CENTER, font_name='Calibri')

# ============================================================
# SLIDE 17: THE 10X IMPROVEMENT (PIVOT)
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_footer(slide)
add_text_box(slide, Inches(0.5), Inches(0.4), Inches(9), Inches(0.8),
             "Single Biggest Improvement: 10x Impact", font_size=36, bold=True, color=NAVY, font_name='Cambria')

add_text_box(slide, Inches(0.5), Inches(1.4), Inches(9), Inches(0.7),
             "PIVOT: B2C AI Trainer App  \u2192  B2B2C Trainer Operating System with AI Form Analysis",
             font_size=20, bold=True, color=CORAL, alignment=PP_ALIGN.CENTER, font_name='Cambria', line_spacing=1.3)

pivot_compare = [
    ("CAC", "$45-80", "$200 (but LTV: $1,800)"),
    ("Monthly Churn", "8%", "3%"),
    ("Moat", "None", "Network effects + switching costs"),
    ("Competition", "Free (Nike, YouTube)", "Enabling paid pros (they pay you)"),
    ("Relationship", "1:1 user", "1:many (trainer brings clients)"),
    ("Price Ceiling", "$15/mo", "$50-100/mo per trainer + upsell"),
    ("Distribution", "None", "Trainers = distribution channel")
]

pivot_headers = ["Metric", "Current Path (B2C)", "Pivoted Path (B2B2C)"]
pivot_rows = [[p[0], p[1], p[2]] for p in pivot_compare]
table_data = [pivot_headers] + pivot_rows
rows = len(table_data)
cols = len(pivot_headers)

table_shape = slide.shapes.add_table(rows, cols, Inches(0.5), Inches(2.3), Inches(9), Inches(2.5))
table = table_shape.table

col_widths = [Inches(1.5), Inches(3.5), Inches(4)]
for i, w in enumerate(col_widths):
    table.columns[i].width = w

for row_idx, row_data in enumerate(table_data):
    for col_idx, cell_text in enumerate(row_data):
        cell = table.cell(row_idx, col_idx)
        cell.text = cell_text
        for paragraph in cell.text_frame.paragraphs:
            paragraph.font.size = Pt(12)
            paragraph.font.name = 'Calibri'
            if row_idx == 0:
                paragraph.font.bold = True
                paragraph.font.color.rgb = WHITE
            else:
                paragraph.font.color.rgb = NAVY

for col_idx in range(cols):
    cell = table.cell(0, col_idx)
    cell.fill.solid()
    cell.fill.fore_color.rgb = NAVY

for row_idx in range(1, rows):
    for col_idx in range(cols):
        cell = table.cell(row_idx, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = WHITE if row_idx % 2 == 1 else LIGHT_PINK

add_text_box(slide, Inches(0.5), Inches(4.9), Inches(9), Inches(0.4),
             "EXECUTION PLAN FOR PIVOT:", font_size=16, bold=True, color=CORAL, font_name='Cambria')
exec_plan = [
    "Week 1-2: Interview 20 trainers \u2192 What would make you pay $50/mo?",
    "Week 3-6: Build trainer dashboard (client list, session view, programs, billing)",
    "Week 7-10: Pilot with 5 trainers, 25 clients \u2192 measure time saved, retention, accuracy",
    "Week 11-12: Iterate \u2192 launch paid beta at $29/mo (grandfather price)",
    "Month 4: Raise pre-seed on TRACTION, not code"
]
add_bullet_list(slide, Inches(0.5), Inches(5.3), Inches(9), Inches(1.5), exec_plan,
                font_size=11, color=NAVY, font_name='Calibri', spacing=4)

# ============================================================
# SLIDE 18: CLOSING / CONTACT
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_background(slide, NAVY)
add_text_box(slide, Inches(1), Inches(1.5), Inches(8), Inches(1.5),
             "GYMSENSE", font_size=48, bold=True, color=WHITE,
             alignment=PP_ALIGN.CENTER, font_name='Cambria')
add_text_box(slide, Inches(1), Inches(3.2), Inches(8), Inches(1),
             "AI Form Coach \u2192 Trainer Operating System\n\nReady to build the platform that scales human expertise.\n\nLet's talk.",
             font_size=22, color=GOLD, alignment=PP_ALIGN.CENTER, font_name='Calibri', line_spacing=1.3)
add_text_box(slide, Inches(1), Inches(4.8), Inches(8), Inches(0.5),
             "Founder: [Your Name]  |  Email: [your@email.com]  |  GitHub: github.com/yourusername/gymsense",
             font_size=14, color=CORAL, alignment=PP_ALIGN.CENTER, font_name='Calibri')

# Update all slide numbers
for i, slide in enumerate(prs.slides):
    add_slide_number(slide, i + 1)

# Save
output_path = "/sessions/zealous-friendly-pasteur/mnt/GYMSENSE/GYMSENSE_Startup_Bihar_PitchDeck.pptx"
prs.save(output_path)
print(f"Pitch deck saved to: {output_path}")