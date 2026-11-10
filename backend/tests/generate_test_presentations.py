import os
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter

OUTPUT_DIR = Path("D:/AI-PPT-VALIDATOR/test_decks")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def generate_high_quality_sih() -> Path:
    """1. High-Quality SIH Presentation: Smart AI Healthcare Tele-Diagnostics."""
    path = OUTPUT_DIR / "1_HighQuality_SIH_SmartHealthcare.pptx"
    prs = Presentation()
    
    # Slide 1: Title
    s1 = prs.slides.add_slide(prs.slide_layouts[0])
    s1.shapes.title.text = "PulmoScan AI: Edge-Assisted Tele-Pulmonology"
    s1.placeholders[1].text = "Smart India Hackathon 2024 • Problem ID: SIH1502 (Ministry of Health)\nTeam: BioCode Innovators"
    
    # Slide 2: Problem Statement
    s2 = prs.slides.add_slide(prs.slide_layouts[1])
    s2.shapes.title.text = "Problem Statement: Rural Respiratory Crisis"
    tf = s2.placeholders[1].text_frame
    tf.text = "Identified Diagnostic Deficits in Primary Health Centers (PHCs):"
    tf.add_paragraph().text = "• Ratio of qualified pulmonologists in rural India is 1 per 240,000 residents."
    tf.add_paragraph().text = "• Average diagnostic delay for chronic obstructive pulmonary disease (COPD) is 4.8 months."
    tf.add_paragraph().text = "• 82% of rural PHCs lack spirometry calibration equipment due to prohibitive costs."
    tf.add_paragraph().text = "• Target Beneficiaries: 12 million rural patients across Tier-3/4 districts."
    
    # Slide 3: Proposed Solution
    s3 = prs.slides.add_slide(prs.slide_layouts[1])
    s3.shapes.title.text = "Proposed Solution: Sub-₹1,500 Acoustic Tele-Diagnostics"
    tf = s3.placeholders[1].text_frame
    tf.text = "Comprehensive Edge-to-Cloud Screening Pipeline:"
    tf.add_paragraph().text = "• Custom digital stethoscope attachment with active noise cancellation MEMS microphone."
    tf.add_paragraph().text = "• On-device quantized CNN model screening for wheezing and crackles in under 80ms."
    tf.add_paragraph().text = "• Automated triage report generation with ICD-10 diagnostic coding."
    tf.add_paragraph().text = "• Offline-first synchronization storing encrypted patient sound records locally."
    
    # Slide 4: System Architecture
    s4 = prs.slides.add_slide(prs.slide_layouts[1])
    s4.shapes.title.text = "System Architecture & Data Pipeline"
    tf = s4.placeholders[1].text_frame
    tf.text = "4-Tier End-to-End Modular Engineering Architecture:"
    tf.add_paragraph().text = "• Edge Sensing Layer: STM32 microcontroller sampling 24-bit 48kHz acoustic audio."
    tf.add_paragraph().text = "• Inference Engine: ONNX Runtime on Android with Int8 post-training quantization."
    tf.add_paragraph().text = "• Secure Cloud Gateway: FastAPI with mTLS authentication and AES-256 data encryption."
    tf.add_paragraph().text = "• Central Clinical Registry: FHIR compliant PostgreSQL with TimescaleDB for telemetry."
    
    # Slide 5: Tech Stack
    s5 = prs.slides.add_slide(prs.slide_layouts[1])
    s5.shapes.title.text = "Technology Stack Justification"
    tf = s5.placeholders[1].text_frame
    tf.text = "Carefully Selected for Medical Safety, Low Latency & Edge Deployability:"
    tf.add_paragraph().text = "• Firmware: FreeRTOS on STM32 for deterministic sampling without audio jitter."
    tf.add_paragraph().text = "• Deep Learning: MobileNetV3 acoustic backbone, 94.2% sensitivity on ICBHI dataset."
    tf.add_paragraph().text = "• Backend: Python FastAPI chosen for async non-blocking audio packet ingest."
    tf.add_paragraph().text = "• Database: PostgreSQL + TimescaleDB for longitudinal patient history tracking."
    
    # Slide 6: Results & Prototype Verification
    s6 = prs.slides.add_slide(prs.slide_layouts[1])
    s6.shapes.title.text = "Prototype Verification & Clinical Field Trial Results"
    tf = s6.placeholders[1].text_frame
    tf.text = "Empirical Validation Results from 120 Patients at District Hospital:"
    tf.add_paragraph().text = "• Overall Diagnostic Accuracy: 93.8% (AUC-ROC: 0.962) against gold-standard spirometry."
    tf.add_paragraph().text = "• End-to-End Classification Latency: 42ms on mid-tier smartphone."
    tf.add_paragraph().text = "• False Positive Rate: Limited to 3.2% across environmental ambient noise tests."
    tf.add_paragraph().text = "• Live GitHub Repository with 91% unit test coverage and functional API demo."
    
    # Slide 7: Scalability & Team
    s7 = prs.slides.add_slide(prs.slide_layouts[1])
    s7.shapes.title.text = "Scalability, Cost Economics & Team Capabilities"
    tf = s7.placeholders[1].text_frame
    tf.text = "Rollout Feasibility & Multidisciplinary Team:"
    tf.add_paragraph().text = "• Unit Manufacturing Cost: ₹1,240 per sensor head; 90% cheaper than commercial spirometers."
    tf.add_paragraph().text = "• Deployment Strategy: Integration with Ayushman Bharat Digital Mission (ABDM) sandbox."
    tf.add_paragraph().text = "• Team: Biomedical Hardware Lead (4th Year), Cloud/ML Architect (4th Year CSE)."
    tf.add_paragraph().text = "• Future Scope: Integration with pulse oximetry and pediatric wheeze classification."
    
    prs.save(str(path))
    return path

def generate_poor_quality_sih() -> Path:
    """2. Poor-Quality SIH Presentation: Deliberate critical flaws."""
    path = OUTPUT_DIR / "2_PoorQuality_SIH_GenericApp.pptx"
    prs = Presentation()
    
    # Slide 1: Title
    s1 = prs.slides.add_slide(prs.slide_layouts[0])
    s1.shapes.title.text = "Super App for Everyone"
    s1.placeholders[1].text = "A revolutionary multi-purpose solution for problems\nTeam Alpha"
    
    # Slide 2: Wall of text, missing clear problem definition
    s2 = prs.slides.add_slide(prs.slide_layouts[1])
    s2.shapes.title.text = "General Overview & Ideas"
    tf = s2.placeholders[1].text_frame
    # Excessive text density > 130 words
    tf.text = (
        "In our modern society there are many difficulties that people encounter on a daily basis. "
        "Technology has progressed very rapidly over the last several years with the introduction of smartphones, "
        "cloud computing, artificial intelligence, blockchain, and various machine learning paradigms that everyone uses. "
        "Our team decided that building an application that solves everything in a single dashboard would be a great hackathon project. "
        "Users can log in, click on buttons, view items, submit information, and receive responses very quickly. "
        "We believe this will be useful for many different people in both cities and rural villages because everyone likes simple solutions. "
        "Furthermore, we can add many additional features in the future whenever they are needed by the community."
    )
    
    # Slide 3: Vague solution without technical architecture
    s3 = prs.slides.add_slide(prs.slide_layouts[1])
    s3.shapes.title.text = "How Our Solution Works"
    tf = s3.placeholders[1].text_frame
    tf.text = "Our software will use modern technologies to provide high efficiency:"
    tf.add_paragraph().text = "• We will build a website and an application."
    tf.add_paragraph().text = "• It uses artificial intelligence to find answers."
    tf.add_paragraph().text = "• The backend is fast and reliable."
    tf.add_paragraph().text = "• Everything is stored securely in the cloud."
    
    # Slide 4: Subjective results with zero numbers
    s4 = prs.slides.add_slide(prs.slide_layouts[1])
    s4.shapes.title.text = "Results and Feedback"
    tf = s4.placeholders[1].text_frame
    tf.text = "We tested our application and got wonderful feedback:"
    tf.add_paragraph().text = "• The app runs very fast on our laptops."
    tf.add_paragraph().text = "• All our friends tested it and said it was very smooth."
    tf.add_paragraph().text = "• No bugs were observed during our casual demonstration."
    tf.add_paragraph().text = "• Conclusion: The system is ready to launch everywhere."
    
    prs.save(str(path))
    return path

def generate_academic_project_pdf() -> Path:
    """3. Academic Project Presentation PDF: Autonomous Robotics & SLAM."""
    path = OUTPUT_DIR / "3_Academic_AutonomousRobotics.pdf"
    doc = SimpleDocTemplate(str(path), pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    story = [
        # Slide 1: Title
        Paragraph("<b>Autonomous Ground Vehicle Navigation via Visual-LiDAR SLAM</b>", styles["Title"]),
        Paragraph("Department of Electronics & Communication Engineering • Final Year Major Project", styles["Heading2"]),
        Spacer(1, 20),
        Paragraph("<b>Students:</b> Siddharth Verma, Ananya Sen | <b>Supervisor:</b> Prof. M. Chandrasekhar", styles["Normal"]),
        PageBreak(),
        
        # Slide 2: Abstract & Literature Survey
        Paragraph("<b>Abstract & Literature Survey</b>", styles["Title"]),
        Paragraph("• <b>Abstract:</b> Investigates robust real-time localization in GPS-denied indoor warehouse environments using tightly-coupled visual-inertial odometry.", styles["Normal"]),
        Paragraph("• <b>Existing Systems:</b> Traditional 2D Gmapping suffers catastrophic drift in long corridors with low texture (Hornung et al., 2013).", styles["Normal"]),
        Paragraph("• <b>Literature Gap:</b> Failure of Kalman-filtered wheel odometry under wheel slip and dynamic lighting occlusions.", styles["Normal"]),
        Paragraph("• <b>Objectives:</b> Achieve sub-3cm localization accuracy and real-time octree map generation at >25 Hz.", styles["Normal"]),
        PageBreak(),
        
        # Slide 3: System Architecture & Methodology
        Paragraph("<b>System Architecture & Methodology</b>", styles["Title"]),
        Paragraph("• <b>Hardware Architecture:</b> 16-channel Livox Mid-360 LiDAR, Intel RealSense D435i depth camera, Jetson AGX Xavier.", styles["Normal"]),
        Paragraph("• <b>Sensor Fusion Pipeline:</b> Extended Kalman Filter (EKF) fusing 200Hz IMU pre-integration with LiDAR feature points.", styles["Normal"]),
        Paragraph("• <b>Loop Closure Detection:</b> BoW3 visual vocabulary with ICP geometric verification to eliminate cumulative drift.", styles["Normal"]),
        Paragraph("• <b>Path Planning:</b> A* global path search coupled with Timed-Elastic-Band (TEB) local obstacle avoidance.", styles["Normal"]),
        PageBreak(),
        
        # Slide 4: Implementation & Tech Stack
        Paragraph("<b>Implementation Details & Software Stack</b>", styles["Title"]),
        Paragraph("• <b>Operating Environment:</b> Ubuntu 22.04 LTS running ROS2 Humble with micro-ROS DDS communication layer.", styles["Normal"]),
        Paragraph("• <b>Compute Optimization:</b> Point cloud voxel downsampling accelerated using NVIDIA TensorRT and CUDA 12.", styles["Normal"]),
        Paragraph("• <b>Motor Control:</b> Differential drive PID velocity controller implemented on dual brushless DC hub motors.", styles["Normal"]),
        PageBreak(),
        
        # Slide 5: Experimental Results & Testing
        Paragraph("<b>Experimental Verification & Benchmark Results</b>", styles["Title"]),
        Paragraph("• <b>Trajectory Benchmark:</b> Absolute Trajectory Error (ATE) of 2.1cm over 350m warehouse test track.", styles["Normal"]),
        Paragraph("• <b>Compute Utilization:</b> Sustained 28.4 FPS SLAM update rate with 42% CPU and 65% GPU load.", styles["Normal"]),
        Paragraph("• <b>Obstacle Avoidance:</b> Dynamic obstacle deceleration latency measured at 38ms with zero collision events.", styles["Normal"]),
        Paragraph("• <b>Battery Endurance:</b> 4.2 hours continuous mapping on 24V 15Ah LiFePO4 battery pack.", styles["Normal"]),
        PageBreak(),
        
        # Slide 6: Conclusion & References
        Paragraph("<b>Conclusion, Future Scope & Academic References</b>", styles["Title"]),
        Paragraph("• <b>Conclusion:</b> Successfully implemented a drift-resilient multi-sensor SLAM system exceeding project benchmarks.", styles["Normal"]),
        Paragraph("• <b>Future Scope:</b> Semantic segmentation of static versus dynamic obstacles using YOLOv10-seg.", styles["Normal"]),
        Paragraph("• <b>[1]</b> Zhang et al., 'LOAM: Lidar Odometry and Mapping in Real-time', Robotics: Science and Systems, 2014.", styles["Normal"]),
        Paragraph("• <b>[2]</b> Mur-Artal et al., 'ORB-SLAM2: An Open-Source SLAM System', IEEE Trans. Robotics, 2017.", styles["Normal"]),
    ]
    doc.build(story)
    return path

def generate_project_review_pptx() -> Path:
    """4. Project Review Presentation: Sprint 3 Milestone Progress."""
    path = OUTPUT_DIR / "4_ProjectReview_Milestone3.pptx"
    prs = Presentation()
    
    # Slide 1: Title
    s1 = prs.slides.add_slide(prs.slide_layouts[0])
    s1.shapes.title.text = "OmniCommerce: Sprint 3 Milestone Review"
    s1.placeholders[1].text = "Quarterly Internal Engineering Review • Progress Audit\nTeam: Platform Architecture"
    
    # Slide 2: Scope & Milestone Progress
    s2 = prs.slides.add_slide(prs.slide_layouts[1])
    s2.shapes.title.text = "Sprint 3 Progress vs Claimed Deliverables"
    tf = s2.placeholders[1].text_frame
    tf.text = "Verified Deliverables Status (Target: 80% Sprint Completion):"
    tf.add_paragraph().text = "• Overall Sprint Completion: 82% verified by completed Jira epics and merged PRs."
    tf.add_paragraph().text = "• Inventory Synchronization Engine: 100% completed with real-time Redis Pub/Sub."
    tf.add_paragraph().text = "• Multi-Payment Gateway Integration: 85% completed (Stripe and Razorpay live in sandbox)."
    tf.add_paragraph().text = "• Fraud Detection Microservice: 60% completed (Rule engine active, ML classifier in training)."
    
    # Slide 3: Technical Decisions & Architecture
    s3 = prs.slides.add_slide(prs.slide_layouts[1])
    s3.shapes.title.text = "Technical Decisions & Architecture Trade-offs"
    tf = s3.placeholders[1].text_frame
    tf.text = "Core Architectural Evolutions in Sprint 3:"
    tf.add_paragraph().text = "• Decoupled checkout database using CQRS pattern to prevent locking during flash sales."
    tf.add_paragraph().text = "• Adopted gRPC for inter-service communication, reducing network serialization overhead by 45%."
    tf.add_paragraph().text = "• Replaced Elasticsearch indexing workers with Kafka streaming pipeline."
    
    # Slide 4: Limitations & Blockers
    s4 = prs.slides.add_slide(prs.slide_layouts[1])
    s4.shapes.title.text = "Identified Bottlenecks & Risk Mitigation"
    tf = s4.placeholders[1].text_frame
    tf.text = "Known Issues Under Active Mitigation:"
    tf.add_paragraph().text = "• High 99th-percentile latency (620ms) observed on search query autocomplete under 4,000 rps."
    tf.add_paragraph().text = "• Mitigation: Implementing tiered Redis read replicas with 60-second TTL hot-key cache."
    tf.add_paragraph().text = "• Third-party SMS OTP delivery failure rate at 4.2% in rural circles."
    
    # Slide 5: Roadmap
    s5 = prs.slides.add_slide(prs.slide_layouts[1])
    s5.shapes.title.text = "Sprint 4 Roadmap & Release Timeline"
    tf = s5.placeholders[1].text_frame
    tf.text = "Upcoming Milestone Commitments:"
    tf.add_paragraph().text = "• Finalize automated load testing with Locust targeting 10,000 peak concurrent checkouts."
    tf.add_paragraph().text = "• Complete SOC2 compliance and penetration security audit."
    tf.add_paragraph().text = "• User Acceptance Testing (UAT) sign-off scheduled for Dec 15."
    
    prs.save(str(path))
    return path

def generate_subject_seminar_pdf() -> Path:
    """5. Subject Seminar Presentation PDF: Quantum Computing & Algorithms."""
    path = OUTPUT_DIR / "5_SubjectSeminar_QuantumComputing.pdf"
    doc = SimpleDocTemplate(str(path), pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    story = [
        # Slide 1: Title
        Paragraph("<b>Introduction to Quantum Algorithms & Quantum Supremacy</b>", styles["Title"]),
        Paragraph("Department Seminar in Advanced Theoretical Computer Science", styles["Heading2"]),
        Spacer(1, 20),
        Paragraph("<b>Presenter:</b> Meera Krishnan, M.Tech CSE | <b>Faculty Evaluator:</b> Dr. S. Nambiar", styles["Normal"]),
        PageBreak(),
        
        # Slide 2: Core Concepts
        Paragraph("<b>Core Principles: Superposition & Entanglement</b>", styles["Title"]),
        Paragraph("• <b>Qubit Representation:</b> State vector |ψ⟩ = α|0⟩ + β|1⟩ where |α|² + |β|² = 1.", styles["Normal"]),
        Paragraph("• <b>Bloch Sphere:</b> Geometric representation of a single two-level quantum mechanical state.", styles["Normal"]),
        Paragraph("• <b>Quantum Entanglement:</b> Non-separable state |Φ+⟩ = 1/√2 (|00⟩ + |11⟩) providing instantaneous correlation.", styles["Normal"]),
        Paragraph("• <b>No-Cloning Theorem:</b> Fundamental impossibility of creating an identical copy of an unknown quantum state.", styles["Normal"]),
        PageBreak(),
        
        # Slide 3: Quantum Gates & Circuits
        Paragraph("<b>Quantum Circuit Architecture & Unitary Gates</b>", styles["Title"]),
        Paragraph("• <b>Single Qubit Operations:</b> Pauli-X (NOT), Pauli-Z (Phase Flip), and Hadamard (H) gate for superposition creation.", styles["Normal"]),
        Paragraph("• <b>Multi-Qubit Entanglement:</b> Controlled-NOT (CNOT) gate generating maximum entanglement.", styles["Normal"]),
        Paragraph("• <b>Reversibility:</b> All quantum logic gates correspond to unitary operators (U†U = I) preserving norm.", styles["Normal"]),
        PageBreak(),
        
        # Slide 4: Pedagogical Examples
        Paragraph("<b>Pedagogical Case Study: Grover's Search Algorithm</b>", styles["Title"]),
        Paragraph("• <b>Unsorted Database Search:</b> Classical search complexity requires O(N) evaluations.", styles["Normal"]),
        Paragraph("• <b>Quantum Speedup:</b> Grover's amplitude amplification achieves quadratic speedup in O(√N) oracle queries.", styles["Normal"]),
        Paragraph("• <b>Geometric Interpretation:</b> Alternating reflection between target state and orthogonal uniform superposition.", styles["Normal"]),
        Paragraph("• <b>Physical Implementation:</b> Superconducting transmon qubits (IBM Eagle 127-qubit) operating at 15 mK.", styles["Normal"]),
        PageBreak(),
        
        # Slide 5: Summary & References
        Paragraph("<b>Summary, Key Takeaways & Bibliography</b>", styles["Title"]),
        Paragraph("• <b>Summary:</b> Quantum algorithms offer super-polynomial speedups for specialized algebraic problems (Shor's factoring) and quadratic speedups for unstructured search.", styles["Normal"]),
        Paragraph("• <b>NISQ Challenges:</b> Decoherence time (T1/T2 < 100μs) requires Quantum Error Correction (surface codes).", styles["Normal"]),
        Paragraph("• <b>References:</b>", styles["Normal"]),
        Paragraph("• [1] Nielsen, M. A., & Chuang, I. L. (2010). 'Quantum Computation and Quantum Information', Cambridge Univ. Press.", styles["Normal"]),
        Paragraph("• [2] Preskill, J. (2018). 'Quantum Computing in the NISQ era and beyond', Quantum, 2, 79.", styles["Normal"]),
    ]
    doc.build(story)
    return path

if __name__ == "__main__":
    p1 = generate_high_quality_sih()
    p2 = generate_poor_quality_sih()
    p3 = generate_academic_project_pdf()
    p4 = generate_project_review_pptx()
    p5 = generate_subject_seminar_pdf()
    print("Generated 5 test presentation decks successfully:")
    print(f"  1. {p1.name}")
    print(f"  2. {p2.name}")
    print(f"  3. {p3.name}")
    print(f"  4. {p4.name}")
    print(f"  5. {p5.name}")

