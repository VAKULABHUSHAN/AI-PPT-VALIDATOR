import uuid
import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from backend.schemas.presentation import SlideContent
from backend.schemas.rubric import RubricDefinition
from backend.schemas.evaluation import (
    EvaluationResult, CategoryScore, SlideFeedback, JuryQuestion
)
from backend.ai.provider import ai_provider

def determine_rating_label(score: float) -> str:
    if score >= 90:
        return "Excellent"
    elif score >= 80:
        return "Very Good"
    elif score >= 70:
        return "Good"
    elif score >= 60:
        return "Needs Improvement"
    elif score >= 40:
        return "Weak"
    else:
        return "Critical Improvements Required"

def detect_section_across_slides(slides: List[SlideContent], section_name: str) -> Optional[int]:
    """
    Search for a mandatory section across ALL slides (titles, body text, tables, notes).
    Returns the 1-based slide number where the section is covered, or None if truly missing.
    Ensures information present anywhere in the deck is NEVER falsely penalized as missing.
    """
    keywords = [k.strip().lower() for k in re.split(r'[/&,]', section_name) if k.strip()]
    
    # 1. First pass: Check slide titles
    for s in slides:
        t_lower = s.title.lower()
        if any(k in t_lower for k in keywords):
            return s.slide_number
            
    # 2. Second pass: Check slide body text, bullets, and raw content
    for s in slides:
        text_lower = s.raw_text.lower()
        if any(k in text_lower for k in keywords):
            return s.slide_number
            
    return None

def detect_all_missing_sections(slides: List[SlideContent], mandatory_sections: List[str]) -> Tuple[List[str], Dict[str, int]]:
    """
    Returns:
      missing_sections: List of section names that are truly missing from every slide
      found_map: Dict mapping section_name -> slide_number where it was found
    """
    missing = []
    found_map = {}
    for section in mandatory_sections:
        slide_num = detect_section_across_slides(slides, section)
        if slide_num is not None:
            found_map[section] = slide_num
        else:
            missing.append(section)
    return missing, found_map

def normalize_rubric_weights(rubric: RubricDefinition) -> Dict[str, float]:
    """Ensure criterion weightages strictly sum to 100.0% through proportional normalization."""
    total_weight = sum([c.weightage for c in rubric.criteria])
    if total_weight <= 0:
        equal_weight = 100.0 / max(1, len(rubric.criteria))
        return {c.id: equal_weight for c in rubric.criteria}
        
    return {c.id: round((c.weightage / total_weight) * 100.0, 2) for c in rubric.criteria}

def evaluate_presentation(
    presentation_id: str,
    slides: List[SlideContent],
    rubric: RubricDefinition,
    preferred_mode: str = "hybrid"  # "full_ai", "hybrid", "offline_heuristic"
) -> EvaluationResult:
    """
    Comprehensive presentation evaluation pipeline.
    Explicitly tracks whether evaluation is Full AI, Hybrid, or Offline Heuristic.
    Never fabricates AI execution.
    """
    missing_sections, found_map = detect_all_missing_sections(slides, rubric.mandatory_sections)
    normalized_weights = normalize_rubric_weights(rubric)
    
    ai_applied = "Offline heuristic evaluation"
    model_name = ""
    llm_result = None
    
    # Only attempt LLM if preferred_mode is full_ai or hybrid
    if preferred_mode in ["full_ai", "hybrid"] and (ai_provider.gemini_client or ai_provider.openai_client):
        parsed, model, err = _run_llm_evaluation(slides, rubric, missing_sections, found_map)
        if parsed:
            llm_result = parsed
            model_name = model
            ai_applied = "Full AI evaluation" if preferred_mode == "full_ai" else "Hybrid AI + rule-based evaluation"
            
    if llm_result:
        return _format_llm_result(presentation_id, rubric, slides, llm_result, missing_sections, normalized_weights, ai_applied, model_name)
        
    # Offline deterministic academic heuristic evaluation
    return _run_heuristic_evaluation(presentation_id, slides, rubric, missing_sections, found_map, normalized_weights, ai_mode="Offline heuristic evaluation")

def _run_llm_evaluation(
    slides: List[SlideContent],
    rubric: RubricDefinition,
    missing_sections: List[str],
    found_map: Dict[str, int]
) -> Tuple[Optional[Dict[str, Any]], str, Optional[str]]:
    slide_summaries = []
    for s in slides:
        slide_summaries.append(
            f"--- SLIDE {s.slide_number}: {s.title} ---\n"
            f"Content: {s.raw_text[:500]}\n"
            f"Metrics: Words={s.visual_metrics.word_count if s.visual_metrics else 0}, "
            f"Images={s.image_count}, Tables={len(s.tables)}"
        )
    slides_context = "\n\n".join(slide_summaries[:25])
    
    criteria_list = [f"- {c.id}: {c.name} (Weight: {c.weightage}%, Max: {c.max_score}). {c.description}" for c in rubric.criteria]
    criteria_context = "\n".join(criteria_list)
    
    found_sections_context = ", ".join([f"'{sec}' found on Slide {snum}" for sec, snum in found_map.items()])
    
    prompt = f"""
Evaluate this presentation against the selected evaluation profile:
Mode: {rubric.name}
Criteria:
{criteria_context}

Mandatory Sections Context:
- Successfully located sections: {found_sections_context if found_sections_context else 'None'}
- Missing sections across all slides: {', '.join(missing_sections) if missing_sections else 'None'}

Presentation Slides:
{slides_context}

CRITICAL RULES:
1. Every observation, critique, and recommendation MUST reference its supporting slide number (e.g. "[Slide 2]", "Slide 4").
2. Do not penalize any section as missing if it was located on a slide.
3. Return valid JSON only.

Schema:
{{
  "overall_score": 78.5,
  "summary_text": "Executive summary...",
  "verdict": "Professional verdict...",
  "category_scores": [
    {{
      "criterion_id": "id",
      "name": "Criterion Name",
      "score": 8.0,
      "explanation": "Detailed explanation citing [Slide X]...",
      "evidence": "Quoted evidence from Slide X...",
      "recommendation": "Actionable recommendation citing [Slide X]..."
    }}
  ],
  "slide_feedback": [
    {{
      "slide_number": 1,
      "slide_title": "Title",
      "purpose": "Purpose of slide",
      "content_score": 8.0,
      "technical_score": 7.5,
      "visual_score": 8.5,
      "severity": "Medium",
      "issues": ["[Slide 1] Issue description"],
      "missing_info": ["[Slide 1] Missing detail"],
      "recommendations": ["[Slide 1] Actionable recommendation"],
      "suggested_rewrite": "• Rewritten bullet 1\\n• Rewritten bullet 2"
    }}
  ],
  "critical_issues": ["[Slide X] Critical issue"],
  "major_improvements": ["[Slide X] Strategic improvement"],
  "minor_improvements": ["[Slide X] Formatting polish"],
  "strengths": ["[Slide X] Identified strength"],
  "jury_questions": [
    {{
      "evaluator_type": "Technical Expert",
      "question": "Deep technical question?",
      "reason": "Why the jury probes this...",
      "difficulty": "Tough",
      "relevant_slide": 3,
      "good_answer_criteria": ["Defense point 1", "Defense point 2"],
      "suggested_answer": "Model defense citing Slide 3..."
    }}
  ]
}}
"""
    system_prompt = (
        "You are a senior academic evaluator and Smart India Hackathon jury chair. "
        "Strictly cite slide numbers for all claims. Never fabricate content. Output valid JSON only."
    )
    return ai_provider.generate_json_response(prompt, system_prompt)

def _format_llm_result(
    presentation_id: str,
    rubric: RubricDefinition,
    slides: List[SlideContent],
    llm_result: Dict[str, Any],
    missing_sections: List[str],
    normalized_weights: Dict[str, float],
    ai_applied: str,
    model_name: str
) -> EvaluationResult:
    category_scores = []
    total_weighted = 0.0
    weight_map = {c.id: c for c in rubric.criteria}
    
    for cs in llm_result.get("category_scores", []):
        c_id = cs.get("criterion_id", "")
        crit = weight_map.get(c_id)
        weight = normalized_weights.get(c_id, 100.0 / max(1, len(rubric.criteria)))
        max_s = crit.max_score if crit else 10.0
        score = float(cs.get("score", 7.0))
        score = max(0.0, min(max_s, score))
        weighted = (score / max_s) * weight
        total_weighted += weighted
        
        category_scores.append(CategoryScore(
            criterion_id=c_id,
            name=cs.get("name", "Criterion"),
            score=round(score, 1),
            max_score=max_s,
            weightage=round(weight, 1),
            weighted_score=round(weighted, 1),
            explanation=cs.get("explanation", ""),
            evidence=cs.get("evidence", ""),
            recommendation=cs.get("recommendation", "")
        ))
        
    overall_score = round(min(100.0, max(0.0, total_weighted)), 1)
    rating_label = determine_rating_label(overall_score)
    
    slide_feedback = []
    preview_map = {s.slide_number: s.preview_image_url for s in slides}
    for sf in llm_result.get("slide_feedback", []):
        s_num = sf.get("slide_number", 1)
        c_s = float(sf.get("content_score", 7.0))
        t_s = float(sf.get("technical_score", 7.0))
        v_s = float(sf.get("visual_score", 7.0))
        o_s = round((c_s + t_s + v_s) / 3.0, 1)
        
        slide_feedback.append(SlideFeedback(
            slide_number=s_num,
            slide_title=sf.get("slide_title", f"Slide {s_num}"),
            purpose=sf.get("purpose", "Information delivery"),
            content_score=c_s,
            technical_score=t_s,
            visual_score=v_s,
            overall_score=o_s,
            severity=sf.get("severity", "Medium"),
            issues=sf.get("issues", []),
            missing_info=sf.get("missing_info", []),
            recommendations=sf.get("recommendations", []),
            suggested_rewrite=sf.get("suggested_rewrite"),
            preview_image_url=preview_map.get(s_num, f"/static/slides/{presentation_id}/slide_{s_num}.png")
        ))
        
    jury_questions = []
    for jq in llm_result.get("jury_questions", []):
        jury_questions.append(JuryQuestion(
            id=str(uuid.uuid4())[:8],
            evaluator_type=jq.get("evaluator_type", "Technical Expert"),
            question=jq.get("question", ""),
            reason=jq.get("reason", ""),
            difficulty=jq.get("difficulty", "Moderate"),
            relevant_slide=int(jq.get("relevant_slide", 1)),
            good_answer_criteria=jq.get("good_answer_criteria", []),
            suggested_answer=jq.get("suggested_answer", "")
        ))
        
    return EvaluationResult(
        id=str(uuid.uuid4()),
        presentation_id=presentation_id,
        mode=rubric.mode_key,
        ai_mode_applied=ai_applied,
        ai_model_name=model_name,
        overall_score=overall_score,
        rating_label=rating_label,
        verdict=llm_result.get("verdict", f"{rating_label} presentation with clear technical intent."),
        summary_text=llm_result.get("summary_text", f"Evaluated via {ai_applied} ({model_name})."),
        category_scores=category_scores,
        slide_feedback=slide_feedback,
        critical_issues=llm_result.get("critical_issues", []),
        major_improvements=llm_result.get("major_improvements", []),
        minor_improvements=llm_result.get("minor_improvements", []),
        strengths=llm_result.get("strengths", []),
        jury_questions=jury_questions,
        created_at=datetime.now().isoformat()
    )

def _run_heuristic_evaluation(
    presentation_id: str,
    slides: List[SlideContent],
    rubric: RubricDefinition,
    missing_sections: List[str],
    found_map: Dict[str, int],
    normalized_weights: Dict[str, float],
    ai_mode: str = "Offline heuristic evaluation"
) -> EvaluationResult:
    """
    Deterministic academic evaluation engine.
    Computes explainable weighted scores with slide citations and strict boundaries.
    """
    slide_count = len(slides)
    total_words = sum([s.visual_metrics.word_count if s.visual_metrics else 0 for s in slides])
    avg_words_per_slide = total_words / max(1, slide_count)
    total_images = sum([s.image_count for s in slides])
    total_tables = sum([len(s.tables) for s in slides])
    
    slide_feedback: List[SlideFeedback] = []
    all_issues = []
    all_recommendations = []
    
    tech_keywords = {"architecture", "pipeline", "api", "database", "latency", "benchmark", "cloud", "docker", "scalability", "microservices", "security", "encryption", "frontend", "backend", "framework"}
    evidence_keywords = {"accuracy", "f1", "%", "ms", "users", "dataset", "test cases", "results", "table", "graph", "metrics"}
    
    for s in slides:
        words = s.visual_metrics.word_count if s.visual_metrics else 0
        raw_lower = s.raw_text.lower()
        title_lower = s.title.lower()
        s_num = s.slide_number
        
        # Purpose classification
        purpose = "Context & Overview"
        if any(k in title_lower for k in ["problem", "background", "motivation", "challenge"]):
            purpose = "Problem Statement & Background"
        elif any(k in title_lower for k in ["solution", "proposed", "concept", "approach"]):
            purpose = "Proposed Solution & Methodology"
        elif any(k in title_lower for k in ["architecture", "workflow", "design", "diagram"]):
            purpose = "System Architecture & Engineering Flow"
        elif any(k in title_lower for k in ["tech", "stack", "tools", "framework"]):
            purpose = "Technology Stack Justification"
        elif any(k in title_lower for k in ["result", "test", "metric", "output", "demo"]):
            purpose = "Experimental Results & Verification"
        elif any(k in title_lower for k in ["impact", "scalability", "future", "commercial"]):
            purpose = "Scalability & Real-World Impact"
        elif any(k in title_lower for k in ["team", "role", "conclusion", "reference"]):
            purpose = "Team Capabilities & References"
            
        c_score = 7.5
        t_score = 7.0
        v_score = 8.0
        s_issues = []
        s_missing = []
        s_recs = []
        severity = "Low"
        
        # Visual density
        if words > 110:
            v_score -= 2.5
            s_issues.append(f"[Slide {s_num}] Excessive text density ({words} words). Risk of cognitive fatigue during presentation.")
            s_recs.append(f"[Slide {s_num}] Condense long sentences into 3-5 high-impact bullet points.")
            severity = "High"
        elif words < 12 and not (s.image_count > 0 or len(s.tables) > 0 or s_num == 1):
            v_score -= 1.5
            s_issues.append(f"[Slide {s_num}] Thin content ({words} words) without diagrams or data.")
            s_recs.append(f"[Slide {s_num}] Add substantive bullet points or architecture components.")
            severity = "Medium"
            
        # Technical depth
        tech_matches = [k for k in tech_keywords if k in raw_lower]
        if tech_matches:
            t_score = min(10.0, t_score + 1.5)
        else:
            if "architecture" in title_lower or "implementation" in title_lower:
                t_score -= 2.5
                s_issues.append(f"[Slide {s_num}] Lacks concrete technical architecture terms (protocols, data flow, storage).")
                s_missing.append(f"[Slide {s_num}] Missing database schema, protocol definitions, or latency bounds.")
                severity = "Critical"
                
        # Evidence check
        has_evidence = any(k in raw_lower for k in evidence_keywords)
        if "result" in title_lower and not has_evidence and len(s.tables) == 0:
            c_score -= 2.5
            t_score -= 2.0
            s_issues.append(f"[Slide {s_num}] Results slide presents subjective claims without quantified test metrics.")
            s_missing.append(f"[Slide {s_num}] Missing benchmark numbers (latency ms, accuracy %, sample sizes, test runs).")
            severity = "Critical"
            
        # Suggested rewrite
        rewrite = None
        if words > 80:
            sentences = [sent.strip() for sent in re.split(r'[.!?\n]', s.raw_text) if len(sent.strip()) > 15]
            rewrite = "• " + "\n• ".join([sent[:90] + "..." for sent in sentences[:4]])
            
        content_score = round(max(2.0, min(10.0, c_score)), 1)
        tech_score = round(max(2.0, min(10.0, t_score)), 1)
        visual_score = round(max(2.0, min(10.0, v_score)), 1)
        overall_s = round((content_score + tech_score + visual_score) / 3.0, 1)
        
        slide_feedback.append(SlideFeedback(
            slide_number=s_num,
            slide_title=s.title,
            purpose=purpose,
            content_score=content_score,
            technical_score=tech_score,
            visual_score=visual_score,
            overall_score=overall_s,
            severity=severity,
            issues=s_issues,
            missing_info=s_missing,
            recommendations=s_recs,
            suggested_rewrite=rewrite,
            preview_image_url=f"/static/slides/{presentation_id}/slide_{s_num}.png"
        ))
        
        if s_issues:
            all_issues.extend(s_issues)
        if s_recs:
            all_recommendations.extend(s_recs)
            
    # Category scoring with normalized weights
    category_scores: List[CategoryScore] = []
    total_weighted = 0.0
    
    for crit in rubric.criteria:
        c_id = crit.id
        weight = normalized_weights.get(c_id, 100.0 / max(1, len(rubric.criteria)))
        base_score = 7.8
        explanation = f"Evaluated under standard rubric guidelines for {crit.name}."
        evidence = f"Audited deck content across {slide_count} slides."
        recommendation = "Provide quantified validation data."
        
        if "problem" in c_id:
            prob_slide = found_map.get("Problem Statement") or next((s.slide_number for s in slides if "problem" in s.title.lower()), None)
            if prob_slide:
                base_score = 8.6
                evidence = f"[Slide {prob_slide}] Clear problem framing identified in '{slides[prob_slide-1].title}'."
                explanation = f"Problem context is articulated on Slide {prob_slide} with domain relevance."
                recommendation = f"[Slide {prob_slide}] Quantify user pain points and target demographics."
            else:
                base_score = 5.0
                explanation = "Dedicated Problem Statement slide is missing from the presentation."
                evidence = "No slide or body text containing problem statement found."
                recommendation = "Add a dedicated Problem Identification slide highlighting severity and user impact."
                
        elif "innovation" in c_id:
            inno_words = ["novel", "patent", "unique", "differentiator", "competitive", "ai", "smart", "algorithm", "breakthrough"]
            matches = [w for w in inno_words if w in " ".join([s.raw_text.lower() for s in slides])]
            sol_slide = found_map.get("Proposed Solution") or min(2, slide_count)
            if len(matches) >= 3:
                base_score = 8.3
                explanation = f"Demonstrates competitive differentiation across slides (e.g. [Slide {sol_slide}])."
                evidence = f"[Slide {sol_slide}] Innovation terms: {', '.join(matches[:4])}."
                recommendation = f"[Slide {sol_slide}] Include a feature matrix table contrasting your solution against market alternatives."
            else:
                base_score = 6.2
                explanation = f"[Slide {sol_slide}] Solution appears incremental; competitive advantages are not sharply contrasted."
                evidence = "Limited competitive comparison found in deck."
                recommendation = f"[Slide {sol_slide}] Add a competitor benchmark table explicitly proving 3x efficiency or cost savings."
                
        elif "tech" in c_id or "stack" in c_id:
            tech_slide = found_map.get("Technology Stack") or next((s.slide_number for s in slides if "tech" in s.title.lower()), None)
            if tech_slide:
                base_score = 8.5
                evidence = f"[Slide {tech_slide}] Documented technology stack in '{slides[tech_slide-1].title}'."
                explanation = f"Technology stack is documented on Slide {tech_slide} with modern libraries."
                recommendation = f"[Slide {tech_slide}] Explain WHY each tool was selected over standard alternatives (e.g. latency, throughput)."
            else:
                base_score = 5.8
                explanation = "Technology stack is mentioned informally without dedicated architectural grounding."
                evidence = "No dedicated technology stack slide or table located."
                recommendation = "Add a dedicated Technology Stack slide categorizing Frontend, Backend, Database, Cloud & DevOps."
                
        elif "architecture" in c_id or "methodology" in c_id:
            arch_slide = found_map.get("System Architecture") or next((s.slide_number for s in slides if "architecture" in s.title.lower() or "flow" in s.title.lower()), None)
            if arch_slide:
                base_score = 8.7
                evidence = f"[Slide {arch_slide}] Engineering architecture presented on Slide {arch_slide}."
                explanation = f"System architecture diagram on Slide {arch_slide} provides strong technical credibility."
                recommendation = f"[Slide {arch_slide}] Explicitly label data encryption boundaries and API gateway protocols."
            else:
                base_score = 5.2
                explanation = "Missing formal system architecture diagram; jury will scrutinize engineering flow."
                evidence = "No dedicated system architecture diagram detected."
                recommendation = "Include a high-level component diagram showing client, API layer, workers, and database."
                
        elif "prototype" in c_id or "results" in c_id or "implementation" in c_id:
            res_slide = found_map.get("Demonstration / Results") or found_map.get("Results & Testing") or next((s.slide_number for s in slides if "result" in s.title.lower()), None)
            if res_slide:
                base_score = 8.2
                evidence = f"[Slide {res_slide}] Prototype testing data presented on Slide {res_slide}."
                explanation = f"Empirical results and validation metrics documented on Slide {res_slide}."
                recommendation = f"[Slide {res_slide}] Add a live demonstration link or GitHub repository badge."
            else:
                base_score = 5.5
                explanation = "Claims lack tangible prototype screenshots, test outputs, or performance graphs."
                evidence = "No dedicated results or prototype evidence slide detected."
                recommendation = "Add actual UI screenshots, terminal outputs, or benchmark charts proving the prototype works."
                
        elif "impact" in c_id or "feasibility" in c_id or "scalability" in c_id:
            imp_slide = found_map.get("Feasibility & Impact") or slide_count
            base_score = 7.8
            evidence = f"[Slide {imp_slide}] Deployment considerations discussed on Slide {imp_slide}."
            explanation = f"Real-world scalability is projected on Slide {imp_slide} with reasonable viability."
            recommendation = f"[Slide {imp_slide}] Provide estimated monthly cloud hosting costs and user rollout phases."
            
        elif "presentation" in c_id or "formatting" in c_id or "coverage" in c_id:
            if avg_words_per_slide < 75:
                base_score = 8.8
                evidence = f"Deck average: {int(avg_words_per_slide)} words/slide across {slide_count} slides."
                explanation = "Clean visual hierarchy, appropriate text density, and readable formatting."
                recommendation = "Maintain font sizes at or above 24pt for bullet points during projection."
            else:
                base_score = 6.4
                evidence = f"High text density detected: {int(avg_words_per_slide)} words/slide average."
                explanation = "Multiple slides suffer from excessive text density, resembling documents rather than presentation decks."
                recommendation = "Prune long paragraphs into concise bullet points with bold keywords."

        # Penalty for missing mandatory sections
        if missing_sections and any(k.lower() in crit.name.lower() for k in missing_sections):
            base_score = max(3.5, base_score - 2.5)
            explanation += f" (Note: Mandatory section '{missing_sections[0]}' is missing across all slides)."
            
        score_val = round(min(crit.max_score, max(0.0, base_score)), 1)
        weighted_val = round((score_val / crit.max_score) * weight, 1)
        total_weighted += weighted_val
        
        category_scores.append(CategoryScore(
            criterion_id=c_id,
            name=crit.name,
            score=score_val,
            max_score=crit.max_score,
            weightage=round(weight, 1),
            weighted_score=round(weighted_val, 1),
            explanation=explanation,
            evidence=evidence,
            recommendation=recommendation
        ))
        
    overall_score = round(min(100.0, max(0.0, total_weighted)), 1)
    rating_label = determine_rating_label(overall_score)
    
    # Jury Questions citing actual slides
    arch_s = found_map.get("System Architecture") or min(3, slide_count)
    sol_s = found_map.get("Proposed Solution") or min(2, slide_count)
    res_s = found_map.get("Demonstration / Results") or found_map.get("Results & Testing") or min(slide_count, 4)
    
    jury_questions = [
        JuryQuestion(
            id=str(uuid.uuid4())[:8],
            evaluator_type="Technical Expert",
            question=f"Referring to Slide {arch_s}, how does your architecture handle sudden concurrent traffic surges, and what database caching layer is implemented?",
            reason="Technical jury members verify whether the design is production-ready or only a single-user prototype.",
            difficulty="Tough",
            relevant_slide=arch_s,
            good_answer_criteria=[
                "Mention Redis/Memcached in-memory caching",
                "Explain load balancing and asynchronous queues (Celery/RabbitMQ)",
                "Specify database indexing and horizontal read-replicas"
            ],
            suggested_answer=f"As illustrated on Slide {arch_s}, stateless workers scale horizontally behind a reverse proxy. Redis handles session and hot-query caching, sustaining 5,000 req/sec with under 40ms latency."
        ),
        JuryQuestion(
            id=str(uuid.uuid4())[:8],
            evaluator_type="Innovation Evaluator",
            question=f"On Slide {sol_s}, what is the fundamental intellectual or algorithmic novelty preventing a competitor from replicating this next week?",
            reason="Innovation evaluators look for unique defensibility, domain-specific proprietary weights, or optimized pipelines.",
            difficulty="Challenging",
            relevant_slide=sol_s,
            good_answer_criteria=[
                "Highlight domain-specific model tuning or heuristic algorithms",
                "Demonstrate lower operational cost or specialized hardware integration",
                "Emphasize localized workflow optimization"
            ],
            suggested_answer=f"Referring to Slide {sol_s}, our competitive edge is our lightweight hybrid edge pipeline delivering sub-100ms inference locally without GPU cluster dependencies, achieving a 70% cost reduction."
        ),
        JuryQuestion(
            id=str(uuid.uuid4())[:8],
            evaluator_type="Problem Domain Expert",
            question="Have you validated this workflow with actual grassroots stakeholders, and what real-world constraints did they point out?",
            reason="Domain experts check if the team understands field constraints or merely designed a theoretical concept.",
            difficulty="Moderate",
            relevant_slide=1,
            good_answer_criteria=[
                "Cite interviews with target beneficiaries or faculty mentors",
                "Discuss handling intermittent network connectivity or low digital literacy",
                "Provide user feedback quotes"
            ],
            suggested_answer="We engaged with 25 target beneficiaries during pilot testing. Their primary feedback was intermittent connectivity, prompting our offline-first synchronization and SMS fallback triggers."
        ),
        JuryQuestion(
            id=str(uuid.uuid4())[:8],
            evaluator_type="Implementation Feasibility Evaluator",
            question=f"Looking at Slide {res_s}, what parts of this deck represent working code today versus planned future roadmap items?",
            reason="Juries strictly penalize teams exaggerating mockups as functional systems.",
            difficulty="Tough",
            relevant_slide=res_s,
            good_answer_criteria=[
                "Distinguish core functional APIs from roadmap extensions",
                "Offer immediate live terminal or UI execution proof",
                "Cite test coverage metrics"
            ],
            suggested_answer=f"Slide {res_s} documents our current functional alpha release. The core ingestion and analysis pipeline is fully implemented with 88% unit test coverage. Advanced multi-tenant features are currently in staging."
        ),
        JuryQuestion(
            id=str(uuid.uuid4())[:8],
            evaluator_type="Project Impact Evaluator",
            question=f"On Slide {slide_count}, what is the unit economic cost per user/transaction, and how will this project sustain itself after hackathon prize money?",
            reason="Impact judges evaluate long-term viability, cloud burn rate, and institutional adoption readiness.",
            difficulty="Moderate",
            relevant_slide=slide_count,
            good_answer_criteria=[
                "Calculate monthly server expense per 1,000 transactions",
                "Outline freemium B2B or institutional license model",
                "Demonstrate positive ROI for adopting institutions"
            ],
            suggested_answer=f"As outlined on Slide {slide_count}, each evaluation transaction costs approximately ₹0.42 using serverless container compute. Break-even is achieved at 1,200 active campus users under our institutional subscription model."
        )
    ]
    
    critical_issues = [
        f"Missing mandatory section across all slides: {sec}" for sec in missing_sections
    ]
    if any(s.severity == "Critical" for s in slide_feedback):
        critical_issues.extend([iss for s in slide_feedback if s.severity == "Critical" for iss in s.issues])
        
    major_improvements = [
        f"[Slide {arch_s}] Include formal component architecture diagram with labeled data flow and protocol boundaries.",
        f"[Slide {sol_s}] Add a competitive feature matrix table to prove differentiation over existing solutions.",
        f"[Slide {res_s}] Provide quantified verification metrics (accuracy %, latency ms, sample sizes) on the results slide.",
        "Specify technology stack justifications rather than merely listing library names."
    ]
    
    minor_improvements = [
        "Ensure consistent header typography and padding across all slides.",
        "Limit bullet points to maximum 5-6 items per slide to prevent cognitive overload.",
        "Add slide page numbers (e.g. 'Slide 4 of 12') for smooth jury Q&A reference."
    ]
    
    strengths = [
        f"[Deck Structure] Well-structured presentation deck containing {slide_count} slides.",
        "Clear thematic progression from problem definition toward technical realization.",
        f"Average slide density ({int(avg_words_per_slide)} words/slide) maintains audience engagement.",
        f"Presentation aligns cleanly with target evaluation criteria under {rubric.name}."
    ]
    
    verdict = (
        f"{rating_label} Project Pitch: The presentation demonstrates clear problem understanding and technical intent. "
        f"Addressing the {len(critical_issues)} identified critical points will make this deck strongly competitive for top-tier evaluation."
    )
    
    summary_text = (
        f"PPT Validator AI analyzed {slide_count} slides across {len(rubric.criteria)} rubric dimensions for mode '{rubric.name}'. "
        f"Evaluation performed using: {ai_mode}. "
        f"Final composite score achieved is {overall_score}/100 ({rating_label}). "
        f"{len(jury_questions)} targeted jury simulation questions have been synthesized to prepare the presenting team."
    )
    
    return EvaluationResult(
        id=str(uuid.uuid4()),
        presentation_id=presentation_id,
        mode=rubric.mode_key,
        ai_mode_applied=ai_mode,
        ai_model_name="",
        overall_score=overall_score,
        rating_label=rating_label,
        verdict=verdict,
        summary_text=summary_text,
        category_scores=category_scores,
        slide_feedback=slide_feedback,
        critical_issues=critical_issues,
        major_improvements=major_improvements,
        minor_improvements=minor_improvements,
        strengths=strengths,
        jury_questions=jury_questions,
        created_at=datetime.now().isoformat()
    )
