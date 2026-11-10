import time
import json
import os
from pathlib import Path
import httpx

BASE_URL = "http://127.0.0.1:8000"
DECKS_DIR = Path("D:/AI-PPT-VALIDATOR/test_decks")

def run_backend_audit():
    client = httpx.Client(timeout=45.0)
    print("=" * 70)
    print("PPT VALIDATOR AI — COMPREHENSIVE BACKEND AUDIT SUITE")
    print("=" * 70)
    
    # 1. System Diagnostics & Conversion Pipeline
    print("\n--- 1. SYSTEM & CONVERSION PIPELINE DIAGNOSTICS ---")
    diag_resp = client.get(f"{BASE_URL}/api/settings/diagnostics")
    assert diag_resp.status_code == 200, f"Diagnostics failed: {diag_resp.text}"
    diag = diag_resp.json()
    print("Conversion Pipeline Status:", json.dumps(diag["conversion_pipeline"], indent=2))
    print("AI Engine Diagnostics:", json.dumps(diag["ai_engine"], indent=2))

    # 2. AI Connectivity Independent Tests
    print("\n--- 2. INDEPENDENT AI CONNECTIVITY TESTS ---")
    gemini_test = client.post(f"{BASE_URL}/api/settings/test-gemini", json={})
    print(f"Gemini Test Status [{gemini_test.status_code}]:", gemini_test.json())
    
    openai_test = client.post(f"{BASE_URL}/api/settings/test-openai", json={})
    print(f"OpenAI Test Status [{openai_test.status_code}]:", openai_test.json())

    # 3. Process All 5 Synthetic Test Presentations
    print("\n--- 3. TESTING ALL 5 SYNTHETIC PRESENTATIONS THROUGH FULL PIPELINE ---")
    
    test_cases = [
        ("1_HighQuality_SIH_SmartHealthcare.pptx", "sih", "High-Quality SIH"),
        ("2_PoorQuality_SIH_GenericApp.pptx", "sih", "Poor-Quality SIH (Deliberate Flaws)"),
        ("3_Academic_AutonomousRobotics.pdf", "academic", "Academic Project"),
        ("4_ProjectReview_Milestone3.pptx", "project_review", "Project Milestone Review"),
        ("5_SubjectSeminar_QuantumComputing.pdf", "subject", "Subject Seminar"),
    ]
    
    evaluated_decks = {}
    
    for filename, mode, label in test_cases:
        deck_path = DECKS_DIR / filename
        assert deck_path.exists(), f"Deck file not found: {deck_path}"
        
        print(f"\n>> Uploading: {filename} (Mode: {mode.upper()} | {label})...")
        ext = deck_path.suffix.lower()
        mime = "application/pdf" if ext == ".pdf" else "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        
        with open(deck_path, "rb") as f:
            upload_res = client.post(
                f"{BASE_URL}/api/upload",
                files={"file": (filename, f, mime)},
                data={"mode": mode, "evaluation_mode_type": "offline_heuristic"}
            )
            
        assert upload_res.status_code == 200, f"Upload failed for {filename}: {upload_res.text}"
        pres_id = upload_res.json()["presentation_id"]
        print(f"   Assigned Presentation ID: {pres_id}")
        
        # Poll status
        completed = False
        for _ in range(25):
            st = client.get(f"{BASE_URL}/api/status/{pres_id}").json()
            if st["status"] == "completed":
                completed = True
                print(f"   Pipeline completed: Stage {st['progress_stage']}/7 ({st['slide_count']} slides)")
                break
            elif st["status"] == "failed":
                raise RuntimeError(f"Pipeline failed for {filename}: {st.get('error_message')}")
            time.sleep(1)
            
        assert completed, f"Pipeline timed out for {filename}"
        
        # Fetch evaluation result
        ev = client.get(f"{BASE_URL}/api/evaluations/{pres_id}").json()
        print(f"   Score: {ev['overall_score']}/100 [{ev['rating_label']}] | AI Mode: {ev['ai_mode_applied']}")
        print(f"   Verdict: {ev['verdict'][:110]}...")
        print(f"   Critical issues found: {len(ev['critical_issues'])}")
        print(f"   Slide feedback items: {len(ev['slide_feedback'])}")
        print(f"   Jury questions synthesized: {len(ev['jury_questions'])}")
        
        # Verify slide preview images exist and respond with HTTP 200
        first_slide_img = client.get(f"{BASE_URL}/static/slides/{pres_id}/slide_1.png")
        assert first_slide_img.status_code == 200, f"Slide 1 PNG preview failed for {pres_id}"
        
        # Verify downloadable PDF and JSON reports
        pdf_res = client.get(f"{BASE_URL}/api/reports/{pres_id}/pdf")
        assert pdf_res.status_code == 200, f"PDF report failed for {pres_id}"
        json_res = client.get(f"{BASE_URL}/api/reports/{pres_id}/json")
        assert json_res.status_code == 200, f"JSON report failed for {pres_id}"
        
        evaluated_decks[filename] = ev

    # 4. Scoring Engine Validation & Sanity Assertions
    print("\n--- 4. SCORING ENGINE SANITY & BOUNDARY VALIDATION ---")
    sih_high = evaluated_decks["1_HighQuality_SIH_SmartHealthcare.pptx"]
    sih_poor = evaluated_decks["2_PoorQuality_SIH_GenericApp.pptx"]
    
    print(f"High-Quality SIH Score: {sih_high['overall_score']}")
    print(f"Poor-Quality SIH Score: {sih_poor['overall_score']}")
    
    assert sih_high["overall_score"] > sih_poor["overall_score"], (
        f"Scoring failure: High-quality deck ({sih_high['overall_score']}) should score higher than poor-quality deck ({sih_poor['overall_score']})"
    )
    assert sih_poor["overall_score"] < 70, f"Poor deck score should be < 70, got {sih_poor['overall_score']}"
    assert len(sih_poor["critical_issues"]) >= 2, "Poor deck should have triggered at least 2 critical issues"
    print("✓ High-Quality vs Poor-Quality scoring separation verified successfully!")
    print(f"✓ Poor deck triggered {len(sih_poor['critical_issues'])} critical flags:")
    for c in sih_poor["critical_issues"][:3]:
        print(f"    - {c}")

    # 5. API Endpoints Completeness Verification
    print("\n--- 5. API ENDPOINTS COMPLETENESS VERIFICATION ---")
    sample_id = evaluated_decks["1_HighQuality_SIH_SmartHealthcare.pptx"]["presentation_id"]
    
    # 5.1 Slides API
    slides_res = client.get(f"{BASE_URL}/api/slides/{sample_id}")
    assert slides_res.status_code == 200
    print("✓ GET /api/slides/{id} -> OK")
    
    # 5.2 Jury API
    jury_res = client.get(f"{BASE_URL}/api/jury/{sample_id}")
    assert jury_res.status_code == 200
    print("✓ GET /api/jury/{id} -> OK")
    
    # 5.3 Jury Evaluate Answer API
    defense_res = client.post(f"{BASE_URL}/api/jury/evaluate-answer", json={
        "presentation_id": sample_id,
        "question_id": "test_q",
        "question_text": "How do you handle audio latency?",
        "evaluator_type": "Technical Expert",
        "user_answer": "We use STM32 FreeRTOS deterministic audio buffer and ONNX runtime int8 quantization."
    })
    assert defense_res.status_code == 200
    print("✓ POST /api/jury/evaluate-answer -> OK, Verdict:", defense_res.json()["verdict"])
    
    # 5.4 Assistant Chat API
    chat_res = client.post(f"{BASE_URL}/api/assistant/chat", json={
        "presentation_id": sample_id,
        "message": "What is the weakest part of my presentation?"
    })
    assert chat_res.status_code == 200
    print("✓ POST /api/assistant/chat -> OK, Cited slides:", chat_res.json()["cited_slides"])
    
    # 5.5 Assistant History API
    hist_res = client.get(f"{BASE_URL}/api/assistant/{sample_id}/history")
    assert hist_res.status_code == 200
    print("✓ GET /api/assistant/{id}/history -> OK, Message count:", len(hist_res.json()))
    
    # 5.6 Rubrics CRUD API
    rubrics_res = client.get(f"{BASE_URL}/api/rubrics/")
    assert rubrics_res.status_code == 200
    print("✓ GET /api/rubrics/ -> OK, Rubric count:", len(rubrics_res.json()))
    
    create_rubric_res = client.post(f"{BASE_URL}/api/rubrics/", json={
        "name": "Audit Test Rubric",
        "description": "Temporary rubric for testing",
        "criteria": [
            {"id": "c1", "name": "Technical Depth", "description": "Depth test", "weightage": 50.0, "max_score": 10.0},
            {"id": "c2", "name": "Presentation", "description": "Visual test", "weightage": 50.0, "max_score": 10.0}
        ],
        "mandatory_sections": ["Problem Statement", "Architecture"],
        "min_passing_score": 60.0
    })
    assert create_rubric_res.status_code == 200
    custom_rubric_id = create_rubric_res.json()["id"]
    print(f"✓ POST /api/rubrics/ -> Created custom rubric {custom_rubric_id}")
    
    del_rubric_res = client.delete(f"{BASE_URL}/api/rubrics/{custom_rubric_id}")
    assert del_rubric_res.status_code == 200
    print(f"✓ DELETE /api/rubrics/{custom_rubric_id} -> Successfully deleted")
    
    # 5.7 Analytics & Dashboard API
    dash_res = client.get(f"{BASE_URL}/api/analytics/dashboard")
    assert dash_res.status_code == 200
    print("✓ GET /api/analytics/dashboard -> OK, Total presentations:", dash_res.json()["total_analyzed"])
    
    pres_list_res = client.get(f"{BASE_URL}/api/analytics/presentations")
    assert pres_list_res.status_code == 200
    print("✓ GET /api/analytics/presentations -> OK, Count:", len(pres_list_res.json()))

    # 5.8 Re-evaluate API
    re_eval_res = client.post(f"{BASE_URL}/api/evaluations/re-evaluate/{sample_id}?mode=academic")
    assert re_eval_res.status_code == 200
    print(f"✓ POST /api/evaluations/re-evaluate/{sample_id} -> Mode switched to Academic, Score: {re_eval_res.json()['overall_score']}")

    print("\n" + "=" * 70)
    print("ALL BACKEND AUDIT CHECKS PASSED WITH ZERO FAILURES!")
    print("=" * 70)

if __name__ == "__main__":
    run_backend_audit()

