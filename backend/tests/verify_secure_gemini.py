import os
import json
import httpx
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"
PROJECT_ROOT = Path("D:/AI-PPT-VALIDATOR")

def run_verification():
    print("=" * 70)
    print("SECURE GEMINI API CONFIGURATION — VERIFICATION SUITE")
    print("=" * 70)
    
    # 1. Verify Backend loads environment variable from .env
    print("\n--- 1. VERIFY ROOT .ENV LOADING ---")
    env_file = PROJECT_ROOT / ".env"
    assert env_file.exists(), "Root .env file does not exist!"
    print(f"✓ Root .env file exists at {env_file}")
    
    from backend.core.config import settings
    assert settings.GEMINI_API_KEY, "settings.GEMINI_API_KEY is empty!"
    print(f"✓ Backend successfully loaded GEMINI_API_KEY from .env (length: {len(settings.GEMINI_API_KEY)} chars, masked: {settings.GEMINI_API_KEY[:4]}...{settings.GEMINI_API_KEY[-4:]})")
    print(f"✓ Active model configured: {settings.GEMINI_MODEL}")

    # 2. Verify Settings API reports configured: true and never leaks the key
    print("\n--- 2. VERIFY SETTINGS API & SECURITY (NO KEY LEAK) ---")
    client = httpx.Client(timeout=60.0)
    settings_res = client.get(f"{BASE_URL}/api/settings/")
    assert settings_res.status_code == 200
    settings_data = settings_res.json()
    print("GET /api/settings/ response:", json.dumps(settings_data, indent=2))
    
    assert settings_data["gemini_configured"] is True, "gemini_configured must be True!"
    assert "GEMINI_API_KEY" not in settings_data, "SECURITY VIOLATION: GEMINI_API_KEY found in settings response!"
    assert settings.GEMINI_API_KEY not in json.dumps(settings_data), "SECURITY VIOLATION: Raw key string found in settings JSON!"
    print("✓ Security verified: API confirms gemini_configured=True without exposing the raw key.")

    # 3. Verify Real Gemini Connection Test via API
    print("\n--- 3. TEST REAL GEMINI API CONNECTIVITY CALL ---")
    conn_res = client.post(f"{BASE_URL}/api/settings/test-gemini", json={})
    assert conn_res.status_code == 200
    conn_data = conn_res.json()
    print("POST /api/settings/test-gemini response:", json.dumps(conn_data, indent=2))
    
    assert conn_data["connected"] is True, f"Connection test failed: {conn_data}"
    assert conn_data["model"] == settings.GEMINI_MODEL, f"Expected {settings.GEMINI_MODEL}, got {conn_data['model']}"
    assert "latency_ms" in conn_data, "Latency in ms should be reported!"
    assert settings.GEMINI_API_KEY not in json.dumps(conn_data), "SECURITY VIOLATION: Raw key found in connection response!"
    print(f"✓ Real Gemini connectivity verified! Model: {conn_data['model']} (Latency: {conn_data['latency_ms']}ms)")

    # 4. Verify Provider Can Generate Structured JSON Response
    print("\n--- 4. TEST STRUCTURED JSON GENERATION WITH GEMINI ---")
    from backend.ai.provider import ai_provider
    test_prompt = 'Analyze this presentation slide topic: "Edge AI Soil Telemetry". Return a JSON object with keys: "technical_depth" (float 1-10), "feasibility" (string), "recommendations" (list of 2 strings).'
    parsed, model_name, err = ai_provider.generate_json_response(test_prompt, "You are a presentation auditor. Respond in valid JSON only.")
    
    assert parsed is not None, f"JSON generation failed: {err}"
    assert "technical_depth" in parsed, f"Expected key 'technical_depth' in {parsed}"
    assert "Google Gemini" in model_name, f"Expected model name with Gemini, got {model_name}"
    print(f"✓ Successfully generated structured JSON response using {model_name}:")
    print(json.dumps(parsed, indent=2))

    # 5. Verify .env is in .gitignore
    print("\n--- 5. VERIFY .GITIGNORE PROTECTION ---")
    gitignore_file = PROJECT_ROOT / ".gitignore"
    assert gitignore_file.exists(), ".gitignore does not exist!"
    with open(gitignore_file, "r", encoding="utf-8") as f:
        git_content = f.read()
    assert ".env" in git_content, ".env must be ignored in .gitignore!"
    print("✓ .gitignore verified: contains '.env' pattern.")

    # 6. Verify Diagnostics Endpoint
    print("\n--- 6. VERIFY SYSTEM DIAGNOSTICS ENDPOINT ---")
    diag_res = client.get(f"{BASE_URL}/api/settings/diagnostics")
    assert diag_res.status_code == 200
    diag_data = diag_res.json()
    print("GET /api/settings/diagnostics response:", json.dumps(diag_data, indent=2))
    assert diag_data["ai_engine"]["gemini_configured"] is True
    assert settings.GEMINI_API_KEY not in json.dumps(diag_data), "SECURITY VIOLATION: Raw key found in diagnostics!"
    print("✓ System diagnostics endpoint verified safely.")

    # 7. Verify Offline Heuristic Evaluation Still Works
    print("\n--- 7. VERIFY OFFLINE HEURISTIC EVALUATION STILL FUNCTIONS ---")
    from backend.rubrics.definitions import BUILTIN_RUBRICS
    from backend.schemas.presentation import SlideContent
    from backend.ai.evaluator import evaluate_presentation
    
    dummy_slides = [
        SlideContent(slide_number=1, title="Test Slide", raw_text="Testing offline evaluation fallback without network.")
    ]
    offline_eval = evaluate_presentation("test-pres-offline", dummy_slides, BUILTIN_RUBRICS["sih"], preferred_mode="offline_heuristic")
    assert offline_eval.ai_mode_applied == "Offline heuristic evaluation"
    assert offline_eval.overall_score > 0
    print(f"✓ Offline fallback mode verified successfully: Mode applied = '{offline_eval.ai_mode_applied}' (Score: {offline_eval.overall_score})")

    print("\n" + "=" * 70)
    print("ALL 7 VERIFICATIONS PASSED WITH ZERO SECURITY OR INTEGRITY FAILURES!")
    print("=" * 70)

if __name__ == "__main__":
    run_verification()

