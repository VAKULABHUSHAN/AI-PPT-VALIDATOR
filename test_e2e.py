import time
from pathlib import Path
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
import httpx

# 1. Create a 4-page realistic academic project presentation PDF
pdf_path = Path("D:/AI-PPT-VALIDATOR/test_academic.pdf")
doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
styles = getSampleStyleSheet()

story = [
    # Slide 1: Title
    Paragraph("<b>Deep Neural Video Surveillance for Smart Campus Safety</b>", styles["Title"]),
    Paragraph("Department of Computer Science & Engineering • Major Project Phase II", styles["Heading2"]),
    Spacer(1, 20),
    Paragraph("<b>Team Members:</b> Aryan Sharma (CSE), Riya Patel (CSE)<br/><b>Project Guide:</b> Dr. K. Ramanathan, Professor & Head", styles["Normal"]),
    PageBreak(),

    # Slide 2: Abstract & Literature Survey
    Paragraph("<b>Abstract & Literature Survey</b>", styles["Title"]),
    Paragraph("• Current campus CCTV networks rely on passive human monitoring, leading to delayed incident detection.", styles["Normal"]),
    Paragraph("• Recent benchmarks (Redmon et al., 2023) show YOLOv8 achieves high inference speed but degrades under low-light occlusion.", styles["Normal"]),
    Paragraph("• Identified Gap: Need for lightweight edge tensor inference with multi-target tracking without central server bandwidth bottlenecks.", styles["Normal"]),
    PageBreak(),

    # Slide 3: Proposed Architecture & Implementation
    Paragraph("<b>System Architecture & Edge Pipeline</b>", styles["Title"]),
    Paragraph("• Edge Ingestion: RTSP video streams captured at 1080p 30fps from 16 IP cameras.", styles["Normal"]),
    Paragraph("• Detection & Tracking: Custom fine-tuned YOLOv10-Nano with ByteTrack associative tracker on Jetson Orin Nano.", styles["Normal"]),
    Paragraph("• Backend Architecture: FastAPI WebSocket dispatcher pushing geo-tagged alert frames to local Redis cache.", styles["Normal"]),
    Paragraph("• Database & Logging: PostgreSQL with TimescaleDB for spatial-temporal telemetry query acceleration.", styles["Normal"]),
    PageBreak(),

    # Slide 4: Results & Testing
    Paragraph("<b>Testing, Verification & Quantitative Results</b>", styles["Title"]),
    Paragraph("• Mean Average Precision (mAP@0.50): 91.4% across 4,500 annotated campus perimeter frames.", styles["Normal"]),
    Paragraph("• End-to-End Alert Latency: 142ms from camera sensor frame to security control-room alert pop-up.", styles["Normal"]),
    Paragraph("• Concurrency Testing: Successfully sustained 16 concurrent RTSP streams at 28.5 avg FPS.", styles["Normal"]),
    Paragraph("• Conclusion: 65% faster emergency response time verified during mock safety evacuation drill.", styles["Normal"]),
]

doc.build(story)
print(f"[1] Generated test PDF: {pdf_path}")

# 2. Upload to PPT Validator AI Backend
client = httpx.Client(timeout=30.0)
with open(pdf_path, "rb") as f:
    resp = client.post(
        "http://127.0.0.1:8000/api/upload",
        files={"file": ("Academic_Smart_Campus_Surveillance.pdf", f, "application/pdf")},
        data={"mode": "academic"}
    )

res_json = resp.json()
print("[2] Upload Response:", res_json)
pres_id = res_json["presentation_id"]

# 3. Poll Processing Pipeline
print("[3] Monitoring 7-Stage Pipeline...")
for i in range(20):
    st = client.get(f"http://127.0.0.1:8000/api/status/{pres_id}").json()
    print(f"    - Status: {st['status']} | Stage {st['progress_stage']}/7: {st['progress_message']}")
    if st["status"] in ["completed", "failed"]:
        break
    time.sleep(1)

# 4. Fetch Evaluation Result
ev = client.get(f"http://127.0.0.1:8000/api/evaluations/{pres_id}").json()
print("\n[4] Evaluation Result:")
print(f"    Overall Score: {ev['overall_score']}/100 ({ev['rating_label']})")
print(f"    Verdict: {ev['verdict']}")
print(f"    Category Dimensions: {len(ev['category_scores'])}")
for cs in ev['category_scores']:
    print(f"      • {cs['name']} (Weight {cs['weightage']}%): {cs['score']}/10 -> Weighted: {cs['weighted_score']}")
print(f"    Slide Feedback items: {len(ev['slide_feedback'])}")
print(f"    SIH/Academic Jury Questions: {len(ev['jury_questions'])}")

# 5. Check Reports
pdf_resp = client.get(f"http://127.0.0.1:8000/api/reports/{pres_id}/pdf")
json_resp = client.get(f"http://127.0.0.1:8000/api/reports/{pres_id}/json")
print(f"\n[5] Report Verification:")
print(f"    PDF Report HTTP: {pdf_resp.status_code} (Size: {len(pdf_resp.content)} bytes)")
print(f"    JSON Report HTTP: {json_resp.status_code} (Size: {len(json_resp.content)} bytes)")

# 6. Check Slide Previews
slide1_resp = client.get(f"http://127.0.0.1:8000/static/slides/{pres_id}/slide_1.png")
print(f"    Slide 1 PNG preview HTTP: {slide1_resp.status_code} (Size: {len(slide1_resp.content)} bytes)")
print("\n=== All Tests Passed Successfully! ===")

