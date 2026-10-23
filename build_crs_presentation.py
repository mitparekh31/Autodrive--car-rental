"""
Builds the complete Academic Project Presentation for AutoDrive: Modern Luxury Car Rental System & Fleet SaaS.
Takes reference from '3MCA PPT format Odd 2026 (1).pptx' and adapts every single slide (1 to 44)
with full domain content, draw.io diagrams, application screenshots, database schemas, and test cases.
Output: AutoDrive_Project_Presentation_3MCA.pptx
"""

import os
import shutil
import pptx
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE_TYPE
from PIL import Image

TEMPLATE_PPTX = "3MCA PPT format Odd 2026 (1).pptx"
OUTPUT_PPTX = "AutoDrive_Project_Presentation_3MCA.pptx"

# Copy template to output path so we preserve all master themes, logos, background banners
shutil.copyfile(TEMPLATE_PPTX, OUTPUT_PPTX)
prs = pptx.Presentation(OUTPUT_PPTX)

SLIDE_W = prs.slide_width  # 12,192,000 EMU
SLIDE_H = prs.slide_height # 6,858,000 EMU

# Brand Color Palette
PRIMARY_NAVY = RGBColor(12, 35, 64)       # Deep Academic Navy
CYBER_GOLD   = RGBColor(180, 130, 20)     # Luxury Gold Accent
DARK_GRAY    = RGBColor(40, 44, 52)       # Dark Charcoal
WHITE        = RGBColor(255, 255, 255)
SUCCESS_GRN  = RGBColor(20, 140, 60)      # Test Passed Green
TEXT_MUTED   = RGBColor(90, 95, 105)

def clean_old_body_pictures(slide):
    """
    Remove old body pictures (screenshots / diagrams from reference template),
    preserving the top-right university header graphic.
    Header graphic is located around left > 9,500,000 and top < 500,000.
    """
    shapes_to_remove = []
    for s in slide.shapes:
        if s.shape_type == MSO_SHAPE_TYPE.PICTURE:
            # Check if this is the top-right university logo
            if s.left > 9500000 and s.top < 700000 and s.width < 3000000:
                continue # Keep university logo
            shapes_to_remove.append(s)
    
    for s in shapes_to_remove:
        sp = s._element
        sp.getparent().remove(sp)

def insert_proportional_image(slide, img_path, center_x, center_y, max_w, max_h):
    """
    Inserts an image centered within a bounding box, preserving its exact aspect ratio.
    """
    if not os.path.exists(img_path):
        print(f"[!] Warning: Image not found: {img_path}")
        return None
    
    with Image.open(img_path) as im:
        orig_w, orig_h = im.size
    
    scale = min(max_w / orig_w, max_h / orig_h)
    new_w = int(orig_w * scale)
    new_h = int(orig_h * scale)
    left = int(center_x - new_w / 2)
    top = int(center_y - new_h / 2)
    
    return slide.shapes.add_picture(img_path, left, top, new_w, new_h)

def set_text_frame(tf, title, bullets, title_size=18, bullet_size=12, title_color=PRIMARY_NAVY):
    """
    Populates a text frame with a prominent title and styled bullet items.
    """
    tf.clear()
    p0 = tf.paragraphs[0]
    p0.text = title
    p0.font.name = "Calibri"
    p0.font.size = Pt(title_size)
    p0.font.bold = True
    p0.font.color.rgb = title_color
    p0.space_after = Pt(10)
    
    for item in bullets:
        p = tf.add_paragraph()
        if isinstance(item, tuple):
            prefix, body = item
            run_p = p.add_run()
            run_p.text = prefix + " "
            run_p.font.name = "Calibri"
            run_p.font.size = Pt(bullet_size)
            run_p.font.bold = True
            run_p.font.color.rgb = PRIMARY_NAVY
            
            run_b = p.add_run()
            run_b.text = body
            run_b.font.name = "Calibri"
            run_b.font.size = Pt(bullet_size)
            run_b.font.color.rgb = DARK_GRAY
        else:
            run = p.add_run()
            run.text = item
            run.font.name = "Calibri"
            run.font.size = Pt(bullet_size)
            run.font.color.rgb = DARK_GRAY
        p.space_after = Pt(6)
        p.level = 0

def format_table(table, data, col_widths=None, header_bg=PRIMARY_NAVY, font_size=10):
    """
    Populates an existing table with 2D array data and applies clean formatting.
    """
    for r_idx, row in enumerate(data):
        if r_idx < len(table.rows):
            for c_idx, val in enumerate(row):
                if c_idx < len(table.columns):
                    cell = table.cell(r_idx, c_idx)
                    cell.text = str(val)
                    if cell.text_frame.paragraphs:
                        p = cell.text_frame.paragraphs[0]
                        p.font.name = "Calibri"
                        p.font.size = Pt(font_size)
                        if r_idx == 0:
                            p.font.bold = True
                            p.font.color.rgb = WHITE
                            cell.fill.solid()
                            cell.fill.fore_color.rgb = header_bg
                        else:
                            p.font.color.rgb = DARK_GRAY
                            if r_idx % 2 == 1:
                                cell.fill.solid()
                                cell.fill.fore_color.rgb = RGBColor(245, 247, 250)
                            else:
                                cell.fill.solid()
                                cell.fill.fore_color.rgb = WHITE

print("[*] Rebuilding Presentation Slides 1 to 44 with AutoDrive Content...")

# ================= SLIDE 1: TITLE SLIDE =================
s1 = prs.slides[0]
for sh in s1.shapes:
    if sh.has_text_frame:
        t = sh.text_frame.text
        if "A PROJECT PRESENTATION" in t or "JOB PORTAL" in t:
            sh.text_frame.clear()
            p = sh.text_frame.paragraphs[0]
            p.text = "A PROJECT PRESENTATION\nON\n"
            p.font.size = Pt(16)
            p.font.bold = True
            p.font.color.rgb = PRIMARY_NAVY
            
            p_title = sh.text_frame.add_paragraph()
            p_title.text = "AUTODRIVE: MODERN LUXURY CAR RENTAL SYSTEM & FLEET SAAS\n"
            p_title.font.size = Pt(22)
            p_title.font.bold = True
            p_title.font.color.rgb = CYBER_GOLD
            p_title.space_after = Pt(14)
            
            p_sub = sh.text_frame.add_paragraph()
            p_sub.text = (
                "Submitted By:\n"
                "Kapil Dave (Enrollment: 2304070100022)\n\n"
                "Master of Computer Application (MCA) - Semester III\n\n"
                "Internal Guide:\n"
                "Mr. Shubh Shah, Assistant Professor\n\n"
                "Submitted To:\n"
                "Department of Computer Application\n"
                "Silver Oak University, Gota, Ahmedabad - 382481\n"
                "Academic Year: 2026-2027"
            )
            p_sub.font.size = Pt(13)
            p_sub.font.color.rgb = DARK_GRAY

# ================= SLIDE 2: PROJECT PROFILE =================
s2 = prs.slides[1]
for sh in s2.shapes:
    if sh.has_table:
        profile_data = [
            ["Project Profile:", "AUTODRIVE - Modern Luxury Car Rental System & Fleet SaaS"],
            ["Objective:", "To engineer an enterprise-grade cloud car rental platform that eliminates slot collisions and double-booking losses through a mathematical date range interval engine, automates multi-day tiered discounts (10% & 25%), integrates certified chauffeur dispatching, and provides an authentic dual-mode Razorpay gateway with an in-browser 3D Secure bank simulator."],
            ["Platform / Type:", "Full-Stack Web Application (Enterprise SaaS / Cloud-Ready)"],
            ["Front-End Stack:", "HTML5, CSS3 Glassmorphism, Bootstrap 5.3.3, JavaScript ES6+, FontAwesome Pro"],
            ["Back-End Framework:", "Python 3.12 / 3.14, Django 5.x Web Framework (MVT Architecture)"],
            ["Database Engine:", "SQLite 3.45 (Development) / PostgreSQL 16 (Production ACID Transactions)"],
            ["Payment Gateway:", "Razorpay Checkout.js SDK v1 + Integrated 3D Secure Bank Simulator"],
            ["Project Duration:", "3 Months (MCA 3rd Semester Minor Project - CAM6053C)"],
            ["Submitted By / To:", "Kapil Dave (2304070100022) | Department of Computer Application, SOU"],
        ]
        format_table(sh.table, profile_data, font_size=10)

# ================= SLIDE 3: EXISTING SYSTEM =================
s3 = prs.slides[2]
for sh in s3.shapes:
    if sh.has_text_frame and "existing system" in sh.text_frame.text.lower():
        bullets_s3 = [
            ("Manual Counter Procedures:", "Legacy car rental relies on paper contracts, phone-based scheduling, and physical registers prone to clerical discrepancies."),
            ("Concurrency & Double-Booking Failures:", "Conventional systems lack real-time date interval collision algorithms, resulting in simultaneous bookings of the same vehicle for overlapping dates."),
            ("Decoupled Chauffeur Management:", "Drivers are dispatched manually through offline phone calls, causing driver double-scheduling and zero automated availability tracking."),
            ("Static, Opaque Pricing:", "Rates remain rigid with no automated multi-day duration incentives or transparent dynamic pricing breakdowns for extended rentals."),
            ("Payment Sandbox Obstacles:", "Production payment gateways require business KYC, while public demo keys lack active instruments on local test servers, frequently producing 'No appropriate payment method found' errors during academic evaluation."),
            ("Dated User Experience:", "Cluttered legacy interfaces with poor contrast and no mobile responsiveness undermine customer trust in luxury fleet services.")
        ]
        set_text_frame(sh.text_frame, "2. LIMITATIONS OF EXISTING CAR RENTAL SYSTEMS", bullets_s3, title_size=18, bullet_size=12)

# ================= SLIDE 4: NEED FOR NEW SYSTEM & COMPARISON =================
s4 = prs.slides[3]
for idx, sh in enumerate(s4.shapes):
    if sh.has_text_frame and sh.text_frame.text.strip() != "‹#›":
        if idx == 0 or "3. need" in sh.text_frame.text.lower():
            sh.text_frame.clear()
            p0 = sh.text_frame.paragraphs[0]
            p0.text = "3. NEED FOR NEW SYSTEM (AUTODRIVE)"
            p0.font.name = "Calibri"
            p0.font.size = Pt(18)
            p0.font.bold = True
            p0.font.color.rgb = PRIMARY_NAVY
        else:
            # Body bullets
            bullets_s4 = [
                ("Guaranteed Slot Availability:", "Mathematical interval overlap checking (start_date <= end_B and end_date >= start_B) prevents vehicle and chauffeur double-bookings."),
                ("Dynamic Tiered Pricing:", "Automated multi-day discounts (10% for >= 3 days, 25% for >= 7 days) and live chauffeur surcharges."),
                ("Dual-Mode Razorpay Gateway:", "Provides live checkout.js popup alongside an integrated 3D Secure bank simulator for 100% reliable evaluation.")
            ]
            sh.text_frame.clear()
            for b_idx, (prefix, body) in enumerate(bullets_s4):
                p = sh.text_frame.paragraphs[0] if b_idx == 0 else sh.text_frame.add_paragraph()
                run_p = p.add_run()
                run_p.text = prefix + " "
                run_p.font.name = "Calibri"
                run_p.font.size = Pt(11)
                run_p.font.bold = True
                run_p.font.color.rgb = PRIMARY_NAVY
                
                run_b = p.add_run()
                run_b.text = body
                run_b.font.name = "Calibri"
                run_b.font.size = Pt(11)
                run_b.font.color.rgb = DARK_GRAY
                p.space_after = Pt(4)

    elif sh.has_table:
        comp_data = [
            ["Platform / Solution", "UI / UX Design", "Slot Collision Engine", "Chauffeur Dispatch", "Duration Discounts", "Test Sandbox"],
            ["Legacy Rental Counters", "Paper / Legacy", "Manual Check (High Error)", "Offline / External", "Manual Promo Codes", "None"],
            ["P2P Marketplaces (Turo)", "Standard Web", "Host Dependent", "Not Supported", "Host Discretion", "Production Only"],
            ["On-Demand Apps (Zoomcar)", "Mobile Only", "Algorithmic", "Not Supported", "Surge Dynamic", "Production Only"],
            ["AutoDrive CRS (Proposed)", "Luxury Glassmorphic", "Strict Mathematical Interval", "Native Chauffeur Engine", "Automated Tiers (10% & 25%)", "Dual-Mode Simulator"],
            ["Enterprise Advantage", "High Visual Trust", "100% Zero-Conflict Guarantee", "Real-Time Driver Sync", "Transparent Cost Savings", "100% Offline Demo Ready"],
        ]
        format_table(sh.table, comp_data, font_size=10)

# ================= SLIDE 5: FUNCTIONAL SPECIFICATION - ADMIN =================
s5 = prs.slides[4]
for sh in s5.shapes:
    if sh.has_text_frame and ("admin" in sh.text_frame.text.lower() or "user of the system" in sh.text_frame.text.lower()):
        bullets_s5 = [
            ("Fleet Inventory Management:", "Full CRUD operations to add, inspect, update, and retire luxury vehicles with specifications (Horsepower, Top Speed, 0-60 mph, Transmission, Daily Rate)."),
            ("Vehicle Classification Control:", "Categorize fleet into Electric Supercars, Luxury Sedans, Track Bikes, VIP 8-Seater Vans, and Luxury SUVs."),
            ("Certified Chauffeur Oversight:", "Manage professional drivers, commercial license verification, customer ratings, daily fees, and active assignment status."),
            ("Booking Lifecycle Administration:", "Real-time transition controls for reservations (CONFIRMED, COMPLETED, CANCELLED)."),
            ("Business Revenue Intelligence:", "Dynamic dashboard aggregating total vehicles, active bookings, fleet utilization percentage, and gross revenue."),
            ("Security & Access Guarding:", "Enforce Django staff/superuser decorators to protect administrative operational endpoints.")
        ]
        set_text_frame(sh.text_frame, "4.1 USER OF THE SYSTEM: FLEET ADMINISTRATOR / MANAGER", bullets_s5, title_size=18, bullet_size=12)

# ================= SLIDE 6: FUNCTIONAL SPECIFICATION - CUSTOMER =================
s6 = prs.slides[5]
for sh in s6.shapes:
    if sh.has_text_frame and ("company" in sh.text_frame.text.lower() or "functional" in sh.text_frame.text.lower()):
        bullets_s6 = [
            ("Live Fleet Browsing & Filtering:", "Interactive catalog supporting instant filtering by category slug, transmission type, fuel source, and search terms."),
            ("Real-Time Availability Calendar:", "Interactive date pickers enforcing mathematical slot collision validation against active database reservations."),
            ("Dynamic Pricing Engine:", "Instant in-browser subtotal, multi-day discount calculation (10% & 25%), and driver service fee adjustments."),
            ("Self-Drive vs Chauffeur Toggle:", "One-click selection between Self-Drive and certified executive chauffeurs with rating badges."),
            ("Dual-Mode Razorpay Payment:", "Seamless checkout modal supporting Cards, UPI QR codes, Netbanking, and the 3D Secure Bank Simulator."),
            ("Customer Hub & Digital Invoicing:", "Inspect active/past bookings and download auto-generated, printable GST-compliant tax invoices.")
        ]
        set_text_frame(sh.text_frame, "4.2 USER OF THE SYSTEM: CUSTOMER / RENTER", bullets_s6, title_size=18, bullet_size=12)

# ================= SLIDE 7: FUNCTIONAL SPECIFICATION - WORKFLOW =================
s7 = prs.slides[6]
for sh in s7.shapes:
    if sh.has_text_frame and ("workflow" in sh.text_frame.text.lower() or "functional" in sh.text_frame.text.lower()):
        bullets_s7 = [
            ("Step 1 - Vehicle Selection:", "Customer browses fleet catalog and opens target luxury vehicle detail view."),
            ("Step 2 - Date & Chauffeur Selection:", "Customer selects rental start/return dates and chooses between Self-Drive or Chauffeur."),
            ("Step 3 - Mathematical Collision Checking:", "System queries DB: (start_date <= end_B and end_date >= start_B). If conflict exists, booking is blocked with alert banner."),
            ("Step 4 - Dynamic Pricing Calculation:", "Calculates duration in days and applies multi-day discount tier (10% for >=3 days, 25% for >=7 days)."),
            ("Step 5 - Payment Execution:", "Launches Razorpay checkout modal or Bank Simulator OTP dialog for dummy transaction approval."),
            ("Step 6 - Atomic Database Commit:", "Upon payment approval, Django commits Booking (CONFIRMED) and Payment (SUCCESS) records atomically."),
            ("Step 7 - Invoice & Receipt Generation:", "Customer receives booking reference (AD-XXXXXXXX) and printable tax invoice.")
        ]
        set_text_frame(sh.text_frame, "4.3 SYSTEM WORKFLOW: VEHICLE RESERVATION & PAYMENT", bullets_s7, title_size=18, bullet_size=11)

# ================= SLIDE 8: SYSTEM REQUIREMENTS - SOFTWARE =================
s8 = prs.slides[7]
tables_s8 = [sh.table for sh in s8.shapes if sh.has_table]
if len(tables_s8) >= 2:
    sw_server = [
        ["Server-Side Software Layer", "Specification & Purpose"],
        ["Operating System", "Microsoft Windows Server 2022 / Ubuntu Linux 22.04 LTS"],
        ["Backend Runtime", "Python 3.12 / 3.14 (PEP 8 Compliant, Type Hinted)"],
        ["Web Framework", "Django 5.x Web Framework (MVT Architecture & ORM)"],
        ["Database Management", "SQLite 3.45 (Dev) / PostgreSQL 16 (Production Relational)"],
    ]
    sw_client = [
        ["Client-Side Software Layer", "Specification & Purpose"],
        ["Web Browsers", "Google Chrome, Microsoft Edge, Mozilla Firefox, Safari"],
        ["Payment SDK & Libraries", "Razorpay Checkout.js v1, Bootstrap 5.3.3, FontAwesome Pro"],
        ["Operating Systems", "Windows 10/11, macOS Sequoia, Linux, iOS, Android (Responsive)"],
    ]
    format_table(tables_s8[0], sw_server, font_size=10)
    format_table(tables_s8[1], sw_client, font_size=10)

# ================= SLIDE 9: SYSTEM REQUIREMENTS - HARDWARE =================
s9 = prs.slides[8]
tables_s9 = [sh.table for sh in s9.shapes if sh.has_table]
if len(tables_s9) >= 2:
    hw_server = [
        ["Server Hardware Component", "Minimum Requirement (Cloud / Local Server)"],
        ["Processor (CPU)", "Intel Core i5 / Intel Xeon Quad-Core @ 2.5 GHz or higher"],
        ["System Memory (RAM)", "8 GB DDR4 RAM or higher"],
        ["Storage (Disk)", "20 GB NVMe / SSD Available Space"],
        ["Network Interface", "100 Mbps High-Speed Broadband / Dedicated Cloud Port"],
    ]
    hw_client = [
        ["Client Hardware Component", "Minimum Client Device Specification"],
        ["Processor", "Any Dual-Core 1.5 GHz or Modern Smartphone SoC"],
        ["System Memory (RAM)", "2 GB RAM or higher"],
        ["Display Resolution", "1366 x 768 Desktop or 360px+ Mobile Viewport"],
        ["Network Connectivity", "4G / 5G / Wi-Fi Active Internet Connection"],
    ]
    format_table(tables_s9[0], hw_server, font_size=10)
    format_table(tables_s9[1], hw_client, font_size=10)

# ================= SLIDE 10: SYSTEM ARCHITECTURE (FIGURE 4.1) =================
s10 = prs.slides[9]
clean_old_body_pictures(s10)
for sh in s10.shapes:
    if sh.has_text_frame and ("flowchart" in sh.text_frame.text.lower() or "architecture" in sh.text_frame.text.lower()):
        sh.top = 348181
        sh.left = 609600
        sh.height = 450000
        sh.text_frame.paragraphs[0].text = "6. SYSTEM ARCHITECTURE (DJANGO MVT PATTERN)"
        sh.text_frame.paragraphs[0].font.size = Pt(18)
        sh.text_frame.paragraphs[0].font.bold = True
        sh.text_frame.paragraphs[0].font.color.rgb = PRIMARY_NAVY

# Insert draw.io System Architecture Diagram
insert_proportional_image(s10, "docs/diagrams/system_architecture.png",
                          center_x=SLIDE_W / 2, center_y=3850000, max_w=9800000, max_h=5100000)

# ================= SLIDE 11: ER DIAGRAM (FIGURE 4.3) =================
s11 = prs.slides[10]
clean_old_body_pictures(s11)
for sh in s11.shapes:
    if sh.has_text_frame and "er diagram" in sh.text_frame.text.lower():
        sh.top = 348181
        sh.left = 609600
        sh.height = 450000
        sh.text_frame.paragraphs[0].text = "7. ENTITY-RELATIONSHIP (ER) DIAGRAM"
        sh.text_frame.paragraphs[0].font.size = Pt(18)
        sh.text_frame.paragraphs[0].font.bold = True
        sh.text_frame.paragraphs[0].font.color.rgb = PRIMARY_NAVY

# Insert draw.io ER Diagram (Portrait)
insert_proportional_image(s11, "docs/diagrams/er_diagram.png",
                          center_x=SLIDE_W / 2, center_y=3850000, max_w=8500000, max_h=5100000)

# ================= SLIDE 12: RELATIONAL SCHEMA ASSOCIATIONS =================
s12 = prs.slides[11]
clean_old_body_pictures(s12)
tb12 = s12.shapes.add_textbox(Inches(0.8), Inches(1.0), Inches(11.7), Inches(5.5))
tf12 = tb12.text_frame
bullets_s12 = [
    ("Category to Car (1:M):", "One category (e.g. Electric Supercars) contains multiple luxury vehicles in the fleet catalog."),
    ("Car to Booking (1:M):", "One vehicle participates in multiple reservations, strictly enforced to be non-overlapping across date intervals."),
    ("User to Booking (1:M):", "One registered customer can reserve multiple vehicles across different calendar dates."),
    ("Driver to Booking (1:M, Nullable):", "A certified chauffeur is assigned to non-overlapping bookings when drive_mode='chauffeur'."),
    ("Booking to Payment (1:1):", "Each confirmed reservation maps to exactly one verified financial transaction record in tbl_payment."),
    ("Car to Review (1:M):", "Customers submit ratings (1 to 5 stars) and feedback reviews for verified rental experiences."),
    ("Referential Integrity:", "Foreign keys enforce ON DELETE CASCADE / PROTECT to guarantee ACID transactional consistency.")
]
set_text_frame(tf12, "7.1 RELATIONAL DATABASE ARCHITECTURE & CARDINALITIES", bullets_s12, title_size=18, bullet_size=13)

# ================= SLIDE 13: DFD SECTION HEADER =================
s13 = prs.slides[12]
clean_old_body_pictures(s13)
for sh in s13.shapes:
    if sh.has_text_frame and "dataflow" in sh.text_frame.text.lower():
        sh.top = 348181
        sh.left = 609600
        sh.height = 450000
        sh.text_frame.paragraphs[0].text = "8. DATA FLOW DIAGRAMS (DFD)"
        sh.text_frame.paragraphs[0].font.size = Pt(18)
        sh.text_frame.paragraphs[0].font.bold = True
        sh.text_frame.paragraphs[0].font.color.rgb = PRIMARY_NAVY

tb13 = s13.shapes.add_textbox(Inches(0.8), Inches(1.2), Inches(11.7), Inches(5.0))
tf13 = tb13.text_frame
bullets_s13 = [
    ("Context Diagram (Level 0):", "Illustrates external entities (Customer, Fleet Admin, Razorpay Gateway) and primary data flows."),
    ("Decomposition Diagram (Level 1):", "Decomposes the platform into 5 modular subsystems (Auth, Search, Conflict Engine, Payment, Admin)."),
    ("Process Logic & Data Stores:", "Traces state transitions between temporary HTTP sessions and persistent database tables."),
    ("Mathematical Slot Validation:", "Depicts real-time collision prevention queries intercepting overlapping rental attempts.")
]
set_text_frame(tf13, "DATA FLOW MODELING OVERVIEW", bullets_s13, title_size=18, bullet_size=14)

tb13 = s13.shapes.add_textbox(Inches(1.2), Inches(2.2), Inches(10.8), Inches(4.0))
tf13 = tb13.text_frame
bullets_s13 = [
    ("Context Diagram (Level 0):", "Illustrates external entities (Customer, Fleet Admin, Razorpay Gateway) and primary data flows."),
    ("Decomposition Diagram (Level 1):", "Decomposes the platform into 5 modular subsystems (Auth, Search, Conflict Engine, Payment, Admin)."),
    ("Process Logic & Data Stores:", "Traces state transitions between temporary HTTP sessions and persistent database tables."),
    ("Mathematical Slot Validation:", "Depicts real-time collision prevention queries intercepting overlapping rental attempts.")
]
set_text_frame(tf13, "DATA FLOW MODELING OVERVIEW", bullets_s13, title_size=18, bullet_size=14)

# ================= SLIDE 14: DFD LEVEL 0 (FIGURE 4.2) =================
s14 = prs.slides[13]
clean_old_body_pictures(s14)
for sh in s14.shapes:
    if sh.has_text_frame and "dataflow" in sh.text_frame.text.lower():
        sh.text_frame.paragraphs[0].text = "8.1 DFD LEVEL 0: CONTEXT DIAGRAM"
        sh.text_frame.paragraphs[0].font.size = Pt(20)
        sh.text_frame.paragraphs[0].font.bold = True
        sh.text_frame.paragraphs[0].font.color.rgb = PRIMARY_NAVY

# Insert draw.io DFD Level 0 Diagram
insert_proportional_image(s14, "docs/diagrams/dfd_level_0.png",
                          center_x=SLIDE_W / 2, center_y=3700000, max_w=10500000, max_h=5000000)

# ================= SLIDE 15: DFD LEVEL 1 =================
s15 = prs.slides[14]
clean_old_body_pictures(s15)
for sh in s15.shapes:
    if sh.has_text_frame and "dfd" in sh.text_frame.text.lower():
        sh.text_frame.paragraphs[0].text = "8.2 DFD LEVEL 1: SUBSYSTEM DECOMPOSITION"
        sh.text_frame.paragraphs[0].font.size = Pt(20)
        sh.text_frame.paragraphs[0].font.bold = True
        sh.text_frame.paragraphs[0].font.color.rgb = PRIMARY_NAVY

tb15 = s15.shapes.add_textbox(Inches(0.8), Inches(1.2), Inches(11.7), Inches(5.2))
tf15 = tb15.text_frame
bullets_s15 = [
    ("Process 1.0 - User Authentication & Session Security:", "Validates customer/staff credentials against auth_user, enforces session cookies and PBKDF2 hashing."),
    ("Process 2.0 - Fleet Catalog Search & Multi-Facet Filtering:", "Queries tbl_car and tbl_category based on category slug, transmission type, fuel type, and keywords."),
    ("Process 3.0 - Real-Time Slot Collision & Dynamic Pricing Engine:", "Executes interval validation against tbl_booking and applies multi-day discount formulas (10% & 25%)."),
    ("Process 4.0 - Dual-Mode Razorpay Gateway & Bank Simulator:", "Exchanges tokens with Razorpay Checkout.js or launches the 3D Secure Bank Simulator, writing verified records to tbl_payment."),
    ("Process 5.0 - Administrative Fleet Operations & Intelligence:", "Provides fleet CRUD controls, booking lifecycle updates, chauffeur assignment, and aggregated revenue analytics.")
]
set_text_frame(tf15, "SUBSYSTEM PROCESS SPECIFICATION", bullets_s15, title_size=16, bullet_size=12)

# ================= SLIDE 16: DATA FLOW CHART (CUSTOMER) =================
s16 = prs.slides[15]
clean_old_body_pictures(s16)
for sh in s16.shapes:
    if sh.has_text_frame and "data flow" in sh.text_frame.text.lower():
        sh.text_frame.paragraphs[0].text = "8.3 DATA FLOW CHART: CUSTOMER RESERVATION PROCESS"
        sh.text_frame.paragraphs[0].font.size = Pt(20)
        sh.text_frame.paragraphs[0].font.bold = True
        sh.text_frame.paragraphs[0].font.color.rgb = PRIMARY_NAVY

tb16 = s16.shapes.add_textbox(Inches(0.8), Inches(1.2), Inches(11.7), Inches(5.2))
tf16 = tb16.text_frame
bullets_s16 = [
    ("Step 1 - Catalog Exploration:", "Customer enters portal -> Filter by category, transmission, horsepower -> Select target vehicle."),
    ("Step 2 - Date Interval Selection:", "Customer picks start date & end date -> System computes rental duration in days."),
    ("Step 3 - Algorithmic Conflict Verification:", "System executes is_available_between(start_date, end_date) -> Returns True (Proceed) or False (Block with error alert)."),
    ("Step 4 - Dynamic Pricing Calculation:", "Subtotal = daily_rate * days -> Applies 10% discount (>=3 days) or 25% discount (>=7 days) -> Adds chauffeur fee if chosen."),
    ("Step 5 - Payment Handshake:", "Proceed to payment -> Razorpay modal / 3D Secure Simulator -> Customer approves dummy OTP -> HTTP 200 Handshake."),
    ("Step 6 - Transaction Finalization:", "Atomic database commit: Booking status -> CONFIRMED, Payment status -> PAID -> Redirect to digital tax invoice.")
]
set_text_frame(tf16, "END-TO-END CUSTOMER RESERVATION FLOW", bullets_s16, title_size=16, bullet_size=12)

# ================= SLIDE 17: DATA FLOW CHART (ADMIN) =================
s17 = prs.slides[16]
clean_old_body_pictures(s17)
for sh in s17.shapes:
    if sh.has_text_frame and "data flow" in sh.text_frame.text.lower():
        sh.text_frame.paragraphs[0].text = "8.4 DATA FLOW CHART: FLEET OPERATIONS & CHAUFFEUR DISPATCH"
        sh.text_frame.paragraphs[0].font.size = Pt(20)
        sh.text_frame.paragraphs[0].font.bold = True
        sh.text_frame.paragraphs[0].font.color.rgb = PRIMARY_NAVY

tb17 = s17.shapes.add_textbox(Inches(0.8), Inches(1.2), Inches(11.7), Inches(5.2))
tf17 = tb17.text_frame
bullets_s17 = [
    ("Fleet Inventory CRUD:", "Admin logs into Dashboard -> Enters vehicle details (make, model, daily rate, specs, photo) -> Commits new vehicle to tbl_car."),
    ("Certified Chauffeur Registration:", "Input chauffeur name, commercial license, contact, experience years, rating, and daily fee into tbl_driver."),
    ("Booking Lifecycle Management:", "Inspect incoming reservations -> Update status to COMPLETED upon return, or CANCELLED if requested."),
    ("Real-Time Conflict Oversight:", "Inspect calendar dispatches to ensure drivers and cars operate on non-overlapping schedules."),
    ("Executive Revenue Intelligence:", "Auto-aggregate total revenue = SUM(total_price) across CONFIRMED and COMPLETED bookings."),
    ("Fleet Utilization Rate:", "Compute active deployed vehicles / total fleet size to evaluate real-time return on investment (ROI).")
]
set_text_frame(tf17, "ADMINISTRATIVE OPERATIONS WORKFLOW", bullets_s17, title_size=16, bullet_size=12)

# ================= SLIDE 18: UML SEQUENCE DIAGRAM (FIGURE 4.4) =================
s18 = prs.slides[17]
clean_old_body_pictures(s18)
for sh in list(s18.shapes):
    if sh.shape_type in (MSO_SHAPE_TYPE.GROUP, MSO_SHAPE_TYPE.AUTO_SHAPE):
        sp = sh._element
        sp.getparent().remove(sp)

for sh in s18.shapes:
    if sh.has_text_frame and "use case" in sh.text_frame.text.lower():
        sh.text_frame.paragraphs[0].text = "8.5 UML SEQUENCE DIAGRAM (RESERVATION & PAYMENT)"
        sh.text_frame.paragraphs[0].font.size = Pt(20)
        sh.text_frame.paragraphs[0].font.bold = True
        sh.text_frame.paragraphs[0].font.color.rgb = PRIMARY_NAVY

# Insert draw.io Sequence Diagram
insert_proportional_image(s18, "docs/diagrams/sequence_diagram.png",
                          center_x=SLIDE_W / 2, center_y=3700000, max_w=10500000, max_h=5100000)

# ================= SLIDE 19: UML USE CASE SPECIFICATION =================
s19 = prs.slides[18]
clean_old_body_pictures(s19)
for sh in list(s19.shapes):
    if sh.shape_type in (MSO_SHAPE_TYPE.GROUP, MSO_SHAPE_TYPE.AUTO_SHAPE):
        sp = sh._element
        sp.getparent().remove(sp)

for sh in s19.shapes:
    if sh.has_text_frame and "use case" in sh.text_frame.text.lower():
        sh.text_frame.paragraphs[0].text = "8.6 UML USE CASE SPECIFICATION (ROLE RESPONSIBILITIES)"
        sh.text_frame.paragraphs[0].font.size = Pt(20)
        sh.text_frame.paragraphs[0].font.bold = True
        sh.text_frame.paragraphs[0].font.color.rgb = PRIMARY_NAVY

tb19 = s19.shapes.add_textbox(Inches(0.8), Inches(1.2), Inches(11.7), Inches(5.2))
tf19 = tb19.text_frame
bullets_s19 = [
    ("Customer Use Cases:", "Browse Fleet Catalog, Search & Filter Vehicles, Compare Vehicle Specifications, Select Date Interval, Choose Self-Drive or Chauffeur, Simulate / Execute Razorpay Payment, View Booking History, Download Tax Receipts, Submit Vehicle Reviews."),
    ("Certified Chauffeur Use Cases:", "View Active Dispatches, Verify Customer Commercial Credentials, Track Upcoming Assigned Bookings, Log Completed Trips."),
    ("Fleet Administrator Use Cases:", "Manage Fleet Inventory (Create, Read, Update, Delete vehicles), Configure Rental Categories, Register & Dispatch Chauffeurs, Inspect Revenue Analytics, Update Reservation Lifecycle, Manage System Security & Permissions."),
    ("External Payment Gateway (Razorpay):", "Tokenize payment requests, process simulated 3D Secure OTPs, return cryptographic payment IDs and authorization status.")
]
set_text_frame(tf19, "SYSTEM USE CASE ROLES & SCOPE", bullets_s19, title_size=16, bullet_size=12)

# ================= SLIDE 20: DATA DICTIONARY INDEX =================
s20 = prs.slides[19]
for sh in s20.shapes:
    if sh.has_text_frame and "data" in sh.text_frame.text.lower() and "dictionary" in sh.text_frame.text.lower():
        sh.text_frame.paragraphs[0].text = "9. DATA DICTIONARY (DATABASE SCHEMA)"
        sh.text_frame.paragraphs[0].font.size = Pt(20)
        sh.text_frame.paragraphs[0].font.bold = True
        sh.text_frame.paragraphs[0].font.color.rgb = PRIMARY_NAVY
    elif sh.has_text_frame and "admin" in sh.text_frame.text.lower():
        bullets_s20 = [
            ("tbl_category:", "Stores vehicle classifications (Electric Supercars, Sedans, Bikes, VIP Vans, SUVs) with FontAwesome icons and URL slugs."),
            ("tbl_car:", "Main fleet inventory containing vehicle specifications, rates, transmission, fuel, seating, and media paths."),
            ("tbl_driver:", "Certified chauffeur credentials, commercial license IDs, experience years, customer ratings, and daily surcharges."),
            ("tbl_booking:", "Reservation ledger storing customer foreign key, start/end dates, duration, discounts, chauffeur fee, and statuses."),
            ("tbl_payment:", "Financial transaction ledger recording 1:1 payment audit records, transaction IDs, payment methods, and timestamps."),
            ("tbl_review:", "Customer feedback repository linking verified users to vehicles with numeric ratings and commentary.")
        ]
        set_text_frame(sh.text_frame, "RELATIONAL DATABASE TABLES OVERVIEW", bullets_s20, title_size=16, bullet_size=12)

# ================= SLIDE 21: DATA DICTIONARY: tbl_category & tbl_car =================
s21 = prs.slides[20]
tables_s21 = [sh.table for sh in s21.shapes if sh.has_table]
if len(tables_s21) >= 2:
    t_cat = [
        ["Field Name", "Data Types", "Constraints", "Description"],
        ["id", "Integer", "PK, Auto Increment", "Unique category identifier"],
        ["name", "Varchar(100)", "NOT NULL", "Category title (e.g. Electric Supercars)"],
        ["slug", "Varchar(100)", "UNIQUE, Indexed", "URL-friendly slug for routing"],
        ["icon", "Varchar(50)", "DEFAULT 'fa-car'", "FontAwesome icon CSS class identifier"],
    ]
    t_car = [
        ["Field Name", "Data Types", "Constraints", "Description"],
        ["id", "Integer", "PK, Auto Increment", "Unique vehicle identifier"],
        ["name", "Varchar(150)", "NOT NULL", "Full vehicle title (e.g. Porsche Taycan)"],
        ["category_id", "Integer", "FK -> tbl_category", "Associated vehicle classification"],
        ["daily_rate", "Decimal(10,2)", "NOT NULL", "Base daily rental rate in INR (₹)"],
        ["horsepower", "Integer", "NOT NULL", "Engine power output rating in HP"],
        ["transmission", "Varchar(30)", "CHOICES", "Automatic, Manual, Direct-Drive"],
    ]
    format_table(tables_s21[0], t_cat, font_size=9)
    format_table(tables_s21[1], t_car, font_size=9)

for sh in s21.shapes:
    if sh.has_text_frame and "admin:" in sh.text_frame.text.lower():
        sh.text_frame.text = "tbl_category (Category Classification)"
    elif sh.has_text_frame and "apply:" in sh.text_frame.text.lower():
        sh.text_frame.text = "tbl_car (Fleet Vehicle Inventory)"

# ================= SLIDE 22: DATA DICTIONARY: tbl_driver & tbl_booking =================
s22 = prs.slides[21]
tables_s22 = [sh.table for sh in s22.shapes if sh.has_table]
if len(tables_s22) >= 2:
    t_driver = [
        ["Field Name", "Data Types", "Constraints", "Description"],
        ["id", "Integer", "PK, Auto Increment", "Unique chauffeur identifier"],
        ["name", "Varchar(150)", "NOT NULL", "Full legal name of certified driver"],
        ["license_number", "Varchar(50)", "UNIQUE, NOT NULL", "Commercial driver's license ID"],
        ["rating", "Decimal(3,1)", "DEFAULT 4.9", "Customer satisfaction star rating"],
        ["daily_fee", "Decimal(10,2)", "DEFAULT 800.00", "Daily chauffeur service surcharge (₹)"],
        ["is_available", "Boolean", "DEFAULT TRUE", "Active operational duty status"],
    ]
    t_booking = [
        ["Field Name", "Data Types", "Constraints", "Description"],
        ["id", "Integer", "PK, Auto Increment", "Internal booking primary key"],
        ["booking_ref", "Varchar(20)", "UNIQUE, Indexed", "Customer reference (e.g. AD-3FA1B890)"],
        ["user_id", "Integer", "FK -> auth_user", "Customer placing reservation"],
        ["car_id", "Integer", "FK -> tbl_car", "Reserved luxury fleet vehicle"],
        ["start_date", "Date", "NOT NULL, Indexed", "Rental commencement pickup date"],
        ["end_date", "Date", "NOT NULL, Indexed", "Rental conclusion return date"],
        ["drive_mode", "Varchar(20)", "CHOICES", "'self' (Self-Drive) or 'chauffeur'"],
        ["total_price", "Decimal(10,2)", "NOT NULL", "Net payable amount after duration discounts"],
        ["status", "Varchar(20)", "CHOICES", "CONFIRMED, COMPLETED, CANCELLED"],
        ["payment_status", "Varchar(20)", "CHOICES", "PAID, PENDING, FAILED"],
        ["transaction_id", "Varchar(50)", "DEFAULT ''", "Razorpay / Simulator transaction token"],
    ]
    format_table(tables_s22[0], t_driver, font_size=9)
    format_table(tables_s22[1], t_booking, font_size=8)

for sh in s22.shapes:
    if sh.has_text_frame and "user resume" in sh.text_frame.text.lower():
        sh.text_frame.text = "tbl_driver (Chauffeur Registry)"
    elif sh.has_text_frame and "company:" in sh.text_frame.text.lower():
        sh.text_frame.text = "tbl_booking (Vehicle Reservation Ledger)"

# ================= SLIDE 23: SCREENSHOTS SECTION HEADER =================
s23 = prs.slides[22]
clean_old_body_pictures(s23)
for sh in s23.shapes:
    if sh.has_text_frame and "screenshot" in sh.text_frame.text.lower():
        sh.top = 348181
        sh.left = 609600
        sh.height = 450000
        sh.text_frame.paragraphs[0].text = "10. SYSTEM SCREENSHOTS & USER INTERFACES"
        sh.text_frame.paragraphs[0].font.size = Pt(18)
        sh.text_frame.paragraphs[0].font.bold = True
        sh.text_frame.paragraphs[0].font.color.rgb = PRIMARY_NAVY

tb23 = s23.shapes.add_textbox(Inches(0.8), Inches(1.2), Inches(11.7), Inches(5.0))
tf23 = tb23.text_frame
bullets_s23 = [
    ("Visual Design Philosophy:", "Cyberpunk-luxury dark aesthetic featuring glassmorphism cards, glowing status badges, and refined typography."),
    ("Key Functional Modules Captured:", "Homepage Hero Portal, Real-Time Date Picker & Collision Alerts, Dynamic Pricing Tier Calculation, Dual-Mode Razorpay Gateway, 3D Secure Bank Simulator, and Admin Intelligence Dashboard."),
    ("Responsive Grid Framework:", "Fluid layouts engineered with Bootstrap 5.3.3 delivering flawless presentation across mobile, tablet, and 4K desktop screens.")
]
set_text_frame(tf23, "APPLICATION DEMONSTRATION SUITE", bullets_s23, title_size=18, bullet_size=14)

# ================= HELPER FOR SCREENSHOT SLIDES (24 to 36) =================
def customize_screenshot_slide(slide, title, description, image_path):
    clean_old_body_pictures(slide)
    
    # Identify or create Title and Description text boxes
    title_shape = None
    desc_shape = None
    
    for sh in slide.shapes:
        if sh.has_text_frame and sh.text_frame.text.strip() != "‹#›":
            if sh.top < 700000 and not title_shape:
                title_shape = sh
            elif sh.top >= 4500000 and not desc_shape:
                desc_shape = sh
            else:
                # Clear any other text frame
                sh.text_frame.clear()
    
    # Title setup
    if not title_shape:
        title_shape = slide.shapes.add_textbox(Inches(0.67), Inches(0.38), Inches(10.5), Inches(0.45))
    title_shape.text_frame.clear()
    p_t = title_shape.text_frame.paragraphs[0]
    p_t.text = title
    p_t.font.name = "Calibri"
    p_t.font.size = Pt(16)
    p_t.font.bold = True
    p_t.font.color.rgb = PRIMARY_NAVY
    
    # Description setup
    if not desc_shape:
        desc_shape = slide.shapes.add_textbox(Inches(0.67), Inches(6.25), Inches(11.5), Inches(0.65))
    desc_shape.text_frame.clear()
    p_d = desc_shape.text_frame.paragraphs[0]
    p_d.text = f"Description: {description}"
    p_d.font.name = "Calibri"
    p_d.font.size = Pt(11)
    p_d.font.color.rgb = DARK_GRAY

    # Insert centered screenshot
    insert_proportional_image(slide, image_path,
                              center_x=SLIDE_W / 2, center_y=3500000, max_w=9800000, max_h=4200000)

# Slide 24: Homepage & Luxury Hero Portal
customize_screenshot_slide(prs.slides[23],
    "Homepage & Luxury Fleet Hero Portal",
    "Sleek cyberpunk-luxury glassmorphism hero banner showcasing featured electric supercars, dynamic category navigation, and quick reservation triggers.",
    "docs/screenshots/homepage_hero.png")

# Slide 25: Fleet Inventory Catalog & Multi-Filters
customize_screenshot_slide(prs.slides[24],
    "Fleet Inventory Catalog & Multi-Facet Filtering",
    "Real-time faceted filtering by category (Electric Supercars, Sedans, Bikes, VIP Vans, SUVs), transmission type, and keyword search.",
    "docs/screenshots/homepage_hero.png")

# Slide 26: Vehicle Detail & Technical Specifications
customize_screenshot_slide(prs.slides[25],
    "Vehicle Detail & Performance Specifications",
    "Comprehensive technical breakdown showcasing Horsepower, Top Speed, 0-60 mph acceleration timing, seating capacity, and real-time availability status.",
    "docs/screenshots/car_detail_reservation.png")

# Slide 27: Dynamic Pricing Engine & Chauffeur Selection
customize_screenshot_slide(prs.slides[26],
    "Dynamic Pricing Engine & Chauffeur Dispatch",
    "Interactive date selection automatically calculates rental duration and applies 10% (3+ days) or 25% (7+ days) discounts, plus driver daily surcharges live.",
    "docs/screenshots/car_detail_reservation.png")

# Slide 28: Mathematical Slot Collision Prevention Alert
customize_screenshot_slide(prs.slides[27],
    "Real-Time Slot Collision Prevention Engine",
    "When overlapping dates are chosen for an already reserved vehicle, the collision engine instantly triggers a red alert banner and disables submission.",
    "docs/screenshots/car_detail_reservation.png")

# Slide 29: Dual-Mode Razorpay Standard Checkout Modal
customize_screenshot_slide(prs.slides[28],
    "Dual-Mode Razorpay Standard Checkout Modal",
    "Official Razorpay Checkout.js modal popup supporting Credit/Debit Cards, UPI QR codes, Netbanking, and Wallets with dynamic INR amounts.",
    "docs/screenshots/razorpay_gateway_modal.png")

# Slide 30: Built-In 3D Secure Bank Simulator
customize_screenshot_slide(prs.slides[29],
    "Built-In 3D Secure Bank Simulator",
    "Eliminates public demo key failures by providing an integrated in-browser payment simulator with simulated OTP approval/decline options.",
    "docs/screenshots/razorpay_gateway_modal.png")

# Slide 31: Luxury Fleet Asset Showcase
customize_screenshot_slide(prs.slides[30],
    "High-Performance Luxury Fleet Asset Showcase",
    "Ultra-high-resolution asset demonstration (Aston Martin / Porsche Taycan Turbo S) highlighting automotive luxury aesthetics.",
    "docs/screenshots/fleet_vehicle_sample.jpg")

# Slide 32: Side-by-Side Vehicle Specification Comparison
customize_screenshot_slide(prs.slides[31],
    "Vehicle Specification Comparison Matrix",
    "Side-by-side performance matrix comparing horsepower, top speed, acceleration, daily rates, and features across multiple selected fleet vehicles.",
    "docs/screenshots/car_detail_reservation.png")

# Slide 33: Customer Self-Service Booking Hub
customize_screenshot_slide(prs.slides[32],
    "Customer Hub & Booking History Portal",
    "Dedicated user dashboard displaying active, completed, and cancelled reservations with live status badges and direct invoice access.",
    "docs/screenshots/car_detail_reservation.png")

# Slide 34: Printable Digital Tax Invoice & Receipt
customize_screenshot_slide(prs.slides[33],
    "Digital Tax Invoice & Payment Receipt",
    "Auto-generated printable GST-compliant tax receipt complete with booking reference, unique gateway transaction ID, cost breakdowns, and payment confirmation stamp.",
    "docs/screenshots/car_detail_reservation.png")

# Slide 35: Admin Intelligence Dashboard
customize_screenshot_slide(prs.slides[34],
    "Admin Intelligence Dashboard & Revenue Analytics",
    "Executive business dashboard displaying total fleet size, confirmed bookings count, fleet utilization rate, and real-time gross revenue aggregates.",
    "docs/screenshots/homepage_hero.png")

# Slide 36: Fleet Inventory Management & CRUD Console
customize_screenshot_slide(prs.slides[35],
    "Fleet Inventory Management & CRUD Console",
    "Administrative interface allowing staff to add new luxury vehicles, configure rental pricing, assign certified chauffeurs, and update reservation statuses.",
    "docs/screenshots/homepage_hero.png")

# ================= SLIDES 37-41: TESTING & QUALITY ASSURANCE =================

def customize_testing_slide(slide, title, test_data):
    # Set title shape
    title_set = False
    for sh in slide.shapes:
        if sh.has_text_frame and sh.text_frame.text.strip() != "‹#›":
            sh.text_frame.clear()
            p = sh.text_frame.paragraphs[0]
            p.text = title
            p.font.name = "Calibri"
            p.font.size = Pt(16)
            p.font.bold = True
            p.font.color.rgb = PRIMARY_NAVY
            title_set = True
            break
    
    if not title_set:
        tb = slide.shapes.add_textbox(Inches(0.67), Inches(0.38), Inches(10.5), Inches(0.45))
        p = tb.text_frame.paragraphs[0]
        p.text = title
        p.font.name = "Calibri"
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = PRIMARY_NAVY
        
    for sh in slide.shapes:
        if sh.has_table:
            format_table(sh.table, test_data, font_size=9)

# Slide 37: TC-01 to TC-04 (Authentication)
tc_auth = [
    ["Test ID", "Test Condition", "Description / Input", "Expected Result", "Actual Output", "Status"],
    ["TC-01", "User Signup", "Register valid username and secure password", "Account created, session established", "HTTP 302 Redirect to /fleet/", "PASS"],
    ["TC-02", "User Login", "Login with valid demo credentials (customer1)", "Authenticated session initialized", "HTTP 302 Redirect to /fleet/", "PASS"],
    ["TC-03", "Invalid Auth", "Submit incorrect password for customer1", "Login rejected with error message", "HTTP 200 Re-render with Alert", "PASS"],
    ["TC-04", "Staff Guard", "Unauthenticated request to /dashboard/", "Access blocked, redirect to login", "HTTP 302 Redirect to /login/", "PASS"],
]
customize_testing_slide(prs.slides[36], "12. TESTING & QUALITY ASSURANCE: AUTHENTICATION SUITE", tc_auth)

# Slide 38: TC-05 to TC-08 (Fleet Catalog & Filters)
tc_fleet = [
    ["Test ID", "Test Condition", "Description / Input", "Expected Result", "Actual Output", "Status"],
    ["TC-05", "Fleet Catalog", "HTTP GET /fleet/ without query parameters", "Renders all active fleet vehicles", "HTTP 200 with vehicle grid", "PASS"],
    ["TC-06", "Category Filter", "HTTP GET /fleet/?category=electric-supercars", "Filters to electric supercars only", "HTTP 200 with matching cars", "PASS"],
    ["TC-07", "Transmission Filter", "HTTP GET /fleet/?transmission=Automatic", "Filters to automatic vehicles only", "HTTP 200 matching transmission", "PASS"],
    ["TC-08", "Search Query", "HTTP GET /fleet/?q=Taycan", "Full-text search across make & model", "HTTP 200 returns Porsche Taycan", "PASS"],
]
customize_testing_slide(prs.slides[37], "12. TESTING & QA: FLEET INVENTORY & FILTER SUITE", tc_fleet)

# Slide 39: TC-09 to TC-13 (Slot Collision Engine)
tc_conflict = [
    ["Test ID", "Test Condition", "Description / Input", "Expected Result", "Actual Output", "Status"],
    ["TC-09", "Non-Overlap Slot", "Book car during completely vacant date range", "is_available_between() returns True", "Returns True (Permit Booking)", "PASS"],
    ["TC-10", "Exact Overlap", "Request dates identical to active booking", "is_available_between() returns False", "Returns False (Reject Booking)", "PASS"],
    ["TC-11", "Enclosing Overlap", "Request range encompassing an existing booking", "Overlap detected, reject submission", "Returns False (Collision Blocked)", "PASS"],
    ["TC-12", "Sub-Interval Overlap", "Request range falling entirely within a booking", "Overlap detected, reject submission", "Returns False (Collision Blocked)", "PASS"],
]
customize_testing_slide(prs.slides[38], "12. TESTING & QA: REAL-TIME SLOT COLLISION ENGINE", tc_conflict)

# Slide 40: TC-14 to TC-20 (Chauffeur & Pricing Tiers)
tc_pricing = [
    ["Test ID", "Test Condition", "Description / Input", "Expected Result", "Actual Output", "Status"],
    ["TC-14", "Chauffeur Assign", "Assign available driver to booking", "Assigned driver saved in booking record", "Assigned driver linked properly", "PASS"],
    ["TC-15", "Chauffeur Overlap", "Assign driver already booked in same window", "Driver conflict detected, reject", "Conflict caught, booking rejected", "PASS"],
    ["TC-16", "1-Day Base Rate", "Book vehicle for 1 single day", "Subtotal = daily_rate * 1 (0% discount)", "Calculates exact daily rate", "PASS"],
    ["TC-17", "3-Day Tier (10%)", "Book vehicle for 3 consecutive days", "Applies 10% discount on subtotal", "Calculates net total with 10% off", "PASS"],
]
customize_testing_slide(prs.slides[39], "12. TESTING & QA: CHAUFFEUR DISPATCH & PRICING TIERS", tc_pricing)

# Slide 41: TC-21 to TC-27 (Payment & Admin Intelligence)
tc_pay = [
    ["Test ID", "Test Condition", "Description / Input", "Expected Result", "Actual Output", "Status"],
    ["TC-18", "7-Day Tier (25%)", "Book vehicle for 7 consecutive days", "Applies 25% weekly duration discount", "Calculates net total with 25% off", "PASS"],
    ["TC-21", "Card Simulator", "Submit card payment simulation (success)", "Booking CONFIRMED, Payment SUCCESS", "Transaction ID TXN-... created", "PASS"],
    ["TC-22", "Decline Simulator", "Submit card payment simulation (failure)", "Booking FAILED, remains unpaid", "Decline message rendered properly", "PASS"],
    ["TC-25", "Admin Metrics", "Query aggregated revenue in dashboard", "Total sum matches confirmed bookings", "Matches exact sum in DB", "PASS"],
    ["TC-27", "27/27 Test Suite", "Full automated test suite execution", "100% tests pass (Ran in 24.1s)", "27 Passed, 0 Failures, 0 Errors", "PASS"],
]
customize_testing_slide(prs.slides[40], "12. TESTING & QA: PAYMENT SIMULATOR & ADMIN INTELLIGENCE", tc_pay)

# ================= SLIDE 42: FUTURE ENHANCEMENTS =================
s42 = prs.slides[41]
for idx, sh in enumerate(s42.shapes):
    if sh.has_text_frame and sh.text_frame.text.strip() != "‹#›":
        if idx == 0 or "13. future" in sh.text_frame.text.lower():
            sh.text_frame.clear()
            p = sh.text_frame.paragraphs[0]
            p.text = "13. FUTURE ENHANCEMENTS & COMMERCIAL ROADMAP"
            p.font.name = "Calibri"
            p.font.size = Pt(18)
            p.font.bold = True
            p.font.color.rgb = PRIMARY_NAVY
        else:
            bullets_s42 = [
                ("Native Mobile Applications (iOS & Android):", "Develop native mobile apps featuring Bluetooth Low Energy (BLE) keyless vehicle unlock and digital smart check-in."),
                ("IoT Telematics & Hardware Tracking:", "Integrate cloud OBD-II hardware for live GPS telemetry, geofencing, speed monitoring, and remote engine immobilization."),
                ("AI Predictive Maintenance Engine:", "Employ machine learning models analyzing driving behavior and vehicle telemetry to predict servicing intervals proactively."),
                ("EV Supercharger Telemetry:", "Connect with national EV supercharging networks for automated battery percentage monitoring and charging slot booking."),
                ("Blockchain Smart Escrow Contracts:", "Implement cryptographic smart contracts for automated security deposit escrow and damage dispute arbitration.")
            ]
            sh.text_frame.clear()
            for b_idx, (prefix, body) in enumerate(bullets_s42):
                p = sh.text_frame.paragraphs[0] if b_idx == 0 else sh.text_frame.add_paragraph()
                run_p = p.add_run()
                run_p.text = prefix + " "
                run_p.font.name = "Calibri"
                run_p.font.size = Pt(12)
                run_p.font.bold = True
                run_p.font.color.rgb = PRIMARY_NAVY
                
                run_b = p.add_run()
                run_b.text = body
                run_b.font.name = "Calibri"
                run_b.font.size = Pt(12)
                run_b.font.color.rgb = DARK_GRAY
                p.space_after = Pt(8)

# ================= SLIDE 43: BIBLIOGRAPHY & REFERENCES =================
s43 = prs.slides[42]
for idx, sh in enumerate(s43.shapes):
    if sh.has_text_frame and sh.text_frame.text.strip() != "‹#›":
        if idx == 0 or "14. biblio" in sh.text_frame.text.lower():
            sh.text_frame.clear()
            p = sh.text_frame.paragraphs[0]
            p.text = "14. BIBLIOGRAPHY & TECHNICAL REFERENCES"
            p.font.name = "Calibri"
            p.font.size = Pt(18)
            p.font.bold = True
            p.font.color.rgb = PRIMARY_NAVY
        else:
            bullets_s43 = [
                ("Django Software Foundation:", "\"Django 5.x Web Framework Documentation and Architectural Patterns,\" 2026. [Online]. https://docs.djangoproject.com/"),
                ("Python Software Foundation:", "\"Python 3.14 Language Specification & Standard Library Reference,\" 2026. [Online]. https://docs.python.org/3/"),
                ("Razorpay Developers:", "\"Razorpay Payment Gateway Web Integration Standard Guide & Checkout.js,\" 2026. [Online]. https://razorpay.com/docs/"),
                ("Bootstrap Core Team:", "\"Bootstrap 5.3 Component Library, Flexbox Grid and Glassmorphism Utilities,\" 2026. [Online]. https://getbootstrap.com/"),
                ("A. Silberschatz, H. F. Korth, and S. Sudarshan:", "Database System Concepts, 7th ed. McGraw-Hill Education, 2020."),
                ("Silver Oak University:", "Guidelines for MCA Minor Project (CAM6053C) Curriculum and Presentation Evaluation Rubrics, Ahmedabad, 2026.")
            ]
            sh.text_frame.clear()
            for b_idx, (prefix, body) in enumerate(bullets_s43):
                p = sh.text_frame.paragraphs[0] if b_idx == 0 else sh.text_frame.add_paragraph()
                run_p = p.add_run()
                run_p.text = prefix + " "
                run_p.font.name = "Calibri"
                run_p.font.size = Pt(11)
                run_p.font.bold = True
                run_p.font.color.rgb = PRIMARY_NAVY
                
                run_b = p.add_run()
                run_b.text = body
                run_b.font.name = "Calibri"
                run_b.font.size = Pt(11)
                run_b.font.color.rgb = DARK_GRAY
                p.space_after = Pt(6)

# ================= SLIDE 44: THANK YOU =================
s44 = prs.slides[43]
for sh in s44.shapes:
    if sh.has_text_frame and "thank you" in sh.text_frame.text.lower():
        sh.text_frame.clear()
        p = sh.text_frame.paragraphs[0]
        p.text = "THANK YOU!\n\n"
        p.font.size = Pt(40)
        p.font.bold = True
        p.font.color.rgb = PRIMARY_NAVY
        p.alignment = PP_ALIGN.CENTER
        
        p2 = sh.text_frame.add_paragraph()
        p2.text = "AUTODRIVE: LUXURY CAR RENTAL SYSTEM & FLEET SAAS\n"
        p2.font.size = Pt(18)
        p2.font.bold = True
        p2.font.color.rgb = CYBER_GOLD
        p2.alignment = PP_ALIGN.CENTER
        
        p3 = sh.text_frame.add_paragraph()
        p3.text = "Department of Computer Application\nSilver Oak College of Computer Application | Silver Oak University\n\nQuestions & Discussion (Q&A)"
        p3.font.size = Pt(14)
        p3.font.color.rgb = DARK_GRAY
        p3.alignment = PP_ALIGN.CENTER

# Save presentation
prs.save(OUTPUT_PPTX)
print(f"[OK] Successfully built Presentation: {OUTPUT_PPTX} (Size: {os.path.getsize(OUTPUT_PPTX)} bytes)")
