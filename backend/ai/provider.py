import os
import json
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
from PIL import Image

from backend.core.config import settings

logger = logging.getLogger(__name__)

def sanitize_error_message(err_str: str, key_to_mask: Optional[str] = None) -> str:
    """Ensure API keys and sensitive tokens are completely scrubbed from error messages."""
    sanitized = err_str
    if key_to_mask and len(key_to_mask) > 6:
        sanitized = sanitized.replace(key_to_mask, "[REDACTED_KEY]")
    if settings.GEMINI_API_KEY and len(settings.GEMINI_API_KEY) > 6:
        sanitized = sanitized.replace(settings.GEMINI_API_KEY, "[REDACTED_GEMINI_KEY]")
    if settings.OPENAI_API_KEY and len(settings.OPENAI_API_KEY) > 6:
        sanitized = sanitized.replace(settings.OPENAI_API_KEY, "[REDACTED_OPENAI_KEY]")
    return sanitized

class AIProvider:
    def __init__(self):
        self.gemini_client = None
        self.openai_client = None
        self._init_clients()

    def _init_clients(self):
        # Gemini Client using official google.genai Client
        if settings.GEMINI_API_KEY:
            try:
                from google import genai
                from google.genai import types
                http_options = types.HttpOptions(
                    timeout=25000,
                    retry_options=types.HttpRetryOptions(attempts=2)
                )
                self.gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY, http_options=http_options)
                logger.info(f"Google GenAI client initialized with model {settings.GEMINI_MODEL}.")
            except Exception as e:
                logger.warning(f"Could not initialize Gemini Client: {sanitize_error_message(str(e))}")
                self.gemini_client = None
        else:
            self.gemini_client = None
                
        # OpenAI Client
        if settings.OPENAI_API_KEY:
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, timeout=25.0)
                logger.info("OpenAI client initialized.")
            except Exception as e:
                logger.warning(f"Could not initialize OpenAI Client: {sanitize_error_message(str(e))}")
                self.openai_client = None
        else:
            self.openai_client = None

    def test_gemini_connectivity(self, test_api_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute an actual lightweight Gemini API verification request.
        Diagnoses: Invalid key, Quota exceeded, Network failure, Model availability.
        Never leaks the API key in the response or error text.
        """
        key_to_use = test_api_key or settings.GEMINI_API_KEY
        if not key_to_use:
            return {
                "status": "unconfigured",
                "provider": "google_gemini",
                "connected": False,
                "model": settings.GEMINI_MODEL,
                "message": "Gemini API key is not configured. Provide GEMINI_API_KEY in .env or via settings."
            }

        start_time = time.time()
        try:
            from google import genai
            from google.genai import types
            http_options = types.HttpOptions(
                timeout=20000,
                retry_options=types.HttpRetryOptions(attempts=2)
            )
            client = genai.Client(api_key=key_to_use, http_options=http_options)
            
            # Real lightweight ping to verify model availability and auth
            prompt = 'Respond with JSON only: {"ping": "pong", "service": "gemini"}'
            response = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt
            )
            elapsed_ms = int((time.time() - start_time) * 1000)
            
            text = (response.text or "").strip()
            if text.startswith("```json"):
                text = text[7:]
            elif text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
                
            parsed = {}
            try:
                parsed = json.loads(text.strip())
            except Exception:
                parsed = {"raw": text[:50]}
                
            return {
                "status": "connected",
                "provider": "google_gemini",
                "connected": True,
                "model": settings.GEMINI_MODEL,
                "latency_ms": elapsed_ms,
                "verified_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "message": f"Successfully authenticated and verified {settings.GEMINI_MODEL} ({elapsed_ms}ms)."
            }
        except Exception as e:
            raw_err = str(e)
            sanitized_err = sanitize_error_message(raw_err, key_to_use)
            logger.error(f"Gemini connectivity verification failed: {sanitized_err}")
            
            # Categorize error type
            error_category = "unknown_error"
            user_friendly_msg = sanitized_err
            
            lower_err = sanitized_err.lower()
            if "400" in lower_err or "401" in lower_err or "403" in lower_err or "api_key_invalid" in lower_err or "permission_denied" in lower_err or "unauthenticated" in lower_err:
                error_category = "authentication_failed"
                user_friendly_msg = "Invalid or unauthorized Gemini API key. Please check your credentials in Google AI Studio."
            elif "429" in lower_err or "resource_exhausted" in lower_err or "quota" in lower_err:
                error_category = "quota_exceeded"
                user_friendly_msg = "Gemini API quota or rate limit exceeded for this key."
            elif "timeout" in lower_err or "connection" in lower_err or "dns" in lower_err or "unreachable" in lower_err:
                error_category = "network_failure"
                user_friendly_msg = "Network failure or timeout contacting Google Gemini API endpoints."
            elif "404" in lower_err or "not_found" in lower_err:
                error_category = "model_not_found"
                user_friendly_msg = f"The requested model {settings.GEMINI_MODEL} was not found or is restricted for this API key tier."
                
            return {
                "status": "failed",
                "provider": "google_gemini",
                "connected": False,
                "model": settings.GEMINI_MODEL,
                "error_category": error_category,
                "error": user_friendly_msg,
                "message": user_friendly_msg
            }

    def test_openai_connectivity(self, test_api_key: Optional[str] = None) -> Dict[str, Any]:
        """Test OpenAI API authentication, connectivity, and JSON response."""
        key_to_use = test_api_key or settings.OPENAI_API_KEY
        if not key_to_use:
            return {
                "status": "unconfigured",
                "provider": "openai",
                "connected": False,
                "model": settings.OPENAI_MODEL,
                "message": "OpenAI API key is not configured."
            }

        start_time = time.time()
        try:
            from openai import OpenAI
            client = OpenAI(api_key=key_to_use, timeout=20.0)
            
            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Respond in JSON only."},
                    {"role": "user", "content": 'Respond with: {"ping": "pong"}'}
                ],
                response_format={"type": "json_object"}
            )
            elapsed_ms = int((time.time() - start_time) * 1000)
            
            return {
                "status": "connected",
                "provider": "openai",
                "connected": True,
                "model": settings.OPENAI_MODEL,
                "latency_ms": elapsed_ms,
                "message": f"Successfully connected to OpenAI {settings.OPENAI_MODEL} ({elapsed_ms}ms)."
            }
        except Exception as e:
            sanitized = sanitize_error_message(str(e), key_to_use)
            return {
                "status": "failed",
                "provider": "openai",
                "connected": False,
                "error": sanitized,
                "message": f"OpenAI API connection error: {sanitized}"
            }

    def generate_json_response(self, prompt: str, system_prompt: str = "") -> Tuple[Optional[Dict[str, Any]], str, Optional[str]]:
        """
        Attempt LLM generation using configured provider.
        Returns: (parsed_json, model_name_or_none, error_message_or_none)
        """
        # 1. Try Gemini
        if self.gemini_client:
            try:
                combined_prompt = f"{system_prompt}\n\nTask:\n{prompt}\n\nRespond with valid JSON only."
                response = self.gemini_client.models.generate_content(
                    model=settings.GEMINI_MODEL,
                    contents=combined_prompt,
                )
                text = (response.text or "").strip()
                if text.startswith("```json"):
                    text = text[7:]
                elif text.startswith("```"):
                    text = text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                parsed = json.loads(text.strip())
                return parsed, f"Google Gemini ({settings.GEMINI_MODEL})", None
            except Exception as e:
                sanitized = sanitize_error_message(str(e))
                logger.error(f"Gemini API error during JSON generation: {sanitized}")
                
        # 2. Try OpenAI
        if self.openai_client:
            try:
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": f"{prompt}\n\nRespond with valid JSON only."})
                response = self.openai_client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=messages,
                    response_format={"type": "json_object"}
                )
                text = response.choices[0].message.content
                parsed = json.loads(text.strip())
                return parsed, f"OpenAI ({settings.OPENAI_MODEL})", None
            except Exception as e:
                sanitized = sanitize_error_message(str(e))
                logger.error(f"OpenAI API error during JSON generation: {sanitized}")
                
        return None, "", "No active AI provider succeeded or API keys not provided."

    def generate_text_response(self, prompt: str, system_prompt: str = "") -> Tuple[Optional[str], str]:
        """Generate text for conversational assistant."""
        if self.gemini_client:
            try:
                full_prompt = f"{system_prompt}\n\nUser Question:\n{prompt}"
                response = self.gemini_client.models.generate_content(
                    model=settings.GEMINI_MODEL,
                    contents=full_prompt
                )
                return response.text.strip(), f"Google Gemini ({settings.GEMINI_MODEL})"
            except Exception as e:
                logger.error(f"Gemini text generation error: {sanitize_error_message(str(e))}")
                
        if self.openai_client:
            try:
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                response = self.openai_client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=messages
                )
                return response.choices[0].message.content.strip(), f"OpenAI ({settings.OPENAI_MODEL})"
            except Exception as e:
                logger.error(f"OpenAI text generation error: {sanitize_error_message(str(e))}")
                
        return None, ""

    def analyze_slide_image_multimodal(self, image_path: Path, slide_title: str) -> Optional[Dict[str, Any]]:
        """
        Multimodal visual analysis of a slide image using Gemini 3.8 Flash.
        Evaluates visual hierarchy, color contrast, typography, and chart clarity.
        """
        if not self.gemini_client or not image_path.exists():
            return None

        try:
            pil_image = Image.open(image_path)
            prompt = (
                f"You are a professional presentation design auditor. Analyze this slide image for title: '{slide_title}'.\n"
                "Evaluate:\n"
                "1. Text readability and font size appropriateness\n"
                "2. Layout balance, whitespace, and visual clutter\n"
                "3. Color contrast and visual hierarchy\n"
                "4. Diagram or chart clarity (if present)\n\n"
                "Respond in valid JSON only with keys:\n"
                "{\n"
                '  "visual_score": 8.5,\n'
                '  "visual_rating": "Excellent / Good / Needs Improvement / Overcrowded",\n'
                '  "visual_strengths": ["Clear font hierarchy"],\n'
                '  "visual_weaknesses": ["Low contrast on subtitle"],\n'
                '  "design_recommendation": "Increase line spacing"\n'
                "}"
            )
            response = self.gemini_client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=[pil_image, prompt]
            )
            text = (response.text or "").strip()
            if text.startswith("```json"):
                text = text[7:]
            elif text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            return json.loads(text.strip())
        except Exception as e:
            logger.warning(f"Multimodal slide analysis failed: {sanitize_error_message(str(e))}")
            return None

ai_provider = AIProvider()
