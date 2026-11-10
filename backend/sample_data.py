import uuid
import os
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from backend.core.config import settings

def create_sample_sih_pptx(output_path: Path) -> Path:
    """Generate a realistic SIH project presentation for testing."""
    prs = Presentation()
    
    # Slide 1: Title
    slide_layout = prs.slide_layouts[0]
    slide1 = prs.slides.add_slide(slide_layout)
    title1 = slide1.shapes.title
    subtitle1 = slide1.placeholders[1]
    title1.text = "AgriSense: IoT & AI-Powered Smart Micro-Irrigation"
    subtitle1.text = "Smart India Hackathon 2024 • Problem Statement: SIH1429 (Ministry of Agriculture)\nTeam: AgriTech Innovators"
    
    # Slide 2: Problem Statement
    slide2 = prs.slides.add_slide(prs.slide_layouts[1])
    slide2.shapes.title.text = "Problem Statement & Ground Reality"
    tf2 = slide2.placeholders[1].text_frame
    tf2.text = "Key Challenges Identified in Rural Farming:"
    p = tf2.add_paragraph()
    p.text = "• Inefficient flood irrigation leads to 45% ground water wastage in semi-arid zones."
    p = tf2.add_paragraph()
    p.text = "• Lack of affordable real-time soil moisture and salinity telemetry for smallholder farmers."
    p = tf2.add_paragraph()
    p.text = "• Erratic rural electricity causes delayed or over-irrigation resulting in root rot."
    p = tf2.add_paragraph()
    p.text = "• Over 80% of current commercial automated valves cost upwards of ₹40,000, which is prohibitive."
    
    # Slide 3: Proposed Solution
    slide3 = prs.slides.add_slide(prs.slide_layouts[1])
    slide3.shapes.title.text = "Proposed Solution: AgriSense Ecosystem"
    tf3 = slide3.placeholders[1].text_frame
    tf3.text = "Comprehensive Edge-to-Cloud Precision Irrigation Platform:"
    p = tf3.add_paragraph()
    p.text = "• Sub-₹3,000 solar-powered LoRaWAN sensor node measuring soil NPK, moisture & ambient temperature."
    p = tf3.add_paragraph()
    p.text = "• Edge AI predictive irrigation scheduling algorithm trained on ICAR crop evaporation models."
    p = tf3.add_paragraph()
    p.text = "• Automated pulse solenoid valve controllers with cellular NB-IoT uplink."
    p = tf3.add_paragraph()
    p.text = "• Multilingual WhatsApp bot & vernacular voice IVR alerts for non-smartphone users."
    
    # Slide 4: System Architecture
    slide4 = prs.slides.add_slide(prs.slide_layouts[1])
    slide4.shapes.title.text = "System Architecture & Hardware Workflow"
    tf4 = slide4.placeholders[1].text_frame
    tf4.text = "Modular 4-Tier Scalable System Design:"
    p = tf4.add_paragraph()
    p.text = "• Sensing Tier: ESP32-S3 microcontroller with capacitive soil sensors (300m range via LoRa 868MHz)."
    p = tf4.add_paragraph()
    p.text = "• Gateway & Ingestion: Raspberry Pi Compute Module 4 with Mosquitto MQTT broker."
    p = tf4.add_paragraph()
    p.text = "• Cloud Processing: FastAPI microservices on AWS EC2, TimescaleDB for time-series sensor telemetry."
    p = tf4.add_paragraph()
    p.text = "• User Interfaces: Next.js progressive web app with offline caching and Twilio SMS notification fallback."
    
    # Slide 5: Tech Stack
    slide5 = prs.slides.add_slide(prs.slide_layouts[1])
    slide5.shapes.title.text = "Technology Stack & Tooling Justification"
    tf5 = slide5.placeholders[1].text_frame
    tf5.text = "Carefully Selected for Rural Resilience and Low Latency:"
    p = tf5.add_paragraph()
    p.text = "• Hardware Firmware: FreeRTOS on ESP32 with deep-sleep power consumption (<15uA)."
    p = tf5.add_paragraph()
    p.text = "• Backend & Telemetry: Python FastAPI (asynchronous ASGI), MQTT with TLS 1.3 encryption."
    p = tf5.add_paragraph()
    p.text = "• Database: TimescaleDB for hyper-table compression of 100k daily telemetry events."
    p = tf5.add_paragraph()
    p.text = "• Machine Learning: LightGBM regressor for evapotranspiration forecast, latency <25ms."
    
    # Slide 6: Results & Prototype Verification
    slide6 = prs.slides.add_slide(prs.slide_layouts[1])
    slide6.shapes.title.text = "Prototype Verification & Field Test Results"
    tf6 = slide6.placeholders[1].text_frame
    tf6.text = "Empirical Results from 30-Day Pilot in Nashik Tomato Farm:"
    p = tf6.add_paragraph()
    p.text = "• Measured 38.4% reduction in overall irrigation water consumption vs traditional flood methods."
    p = tf6.add_paragraph()
    p.text = "• Zero sensor packet loss observed across 1.2km LoRa line-of-sight test."
    p = tf6.add_paragraph()
    p.text = "• Solar battery endurance lasted 72 hours under continuous overcast weather."
    p = tf6.add_paragraph()
    p.text = "• 14% crop yield improvement recorded through optimal moisture maintenance (between 60-70% field capacity)."
    
    # Slide 7: Scalability & Team
    slide7 = prs.slides.add_slide(prs.slide_layouts[1])
    slide7.shapes.title.text = "Deployment Feasibility, Business Model & Team"
    tf7 = slide7.placeholders[1].text_frame
    tf7.text = "Commercialization Strategy & Team Roles:"
    p = tf7.add_paragraph()
    p.text = "• Unit Manufacturing Cost: ₹2,850 per node; B2G subsidy tie-up via PM-KUSUM scheme."
    p = tf7.add_paragraph()
    p.text = "• Team Lead: Embedded Firmware & Hardware PCB Design (4th Year ECE)."
    p = tf7.add_paragraph()
    p.text = "• AI / Cloud Engineer: FastAPI & ML Pipeline Optimization (4th Year CSE)."
    p = tf7.add_paragraph()
    p.text = "• Future Roadmap: Satellite NDVI data fusion and drone spray integration."
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(output_path))
    return output_path

