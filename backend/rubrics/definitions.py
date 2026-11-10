from typing import Dict, List
from backend.schemas.rubric import RubricDefinition, Criterion

BUILTIN_RUBRICS: Dict[str, RubricDefinition] = {
    "sih": RubricDefinition(
        id="rubric-sih",
        name="Smart India Hackathon (SIH) Project Validator",
        description="Comprehensive evaluation tailored for SIH Grand Finale jury criteria, focusing on problem clarity, technical feasibility, architecture, prototype readiness, and real-world impact.",
        is_builtin=True,
        mode_key="sih",
        criteria=[
            Criterion(
                id="sih_problem",
                name="Problem Identification & Clarity",
                description="Clarity in defining the root cause, background context, target beneficiaries, and alignment with the official problem statement.",
                weightage=10.0,
                max_score=10.0
            ),
            Criterion(
                id="sih_innovation",
                name="Innovation & Uniqueness",
                description="Novelty of the solution, competitive differentiation compared to existing alternatives, and intellectual property/uniqueness.",
                weightage=15.0,
                max_score=10.0
            ),
            Criterion(
                id="sih_tech_feasibility",
                name="Technical Feasibility & Tech Stack",
                description="Justification of technology stack choices (languages, frameworks, hardware/cloud), algorithmic feasibility, and practical viability.",
                weightage=15.0,
                max_score=10.0
            ),
            Criterion(
                id="sih_architecture",
                name="System Architecture & Flow",
                description="Clarity of system design, component diagrams, data flow pipelines, security considerations, and modular integration.",
                weightage=15.0,
                max_score=10.0
            ),
            Criterion(
                id="sih_prototype",
                name="Prototype Readiness & Implementation Evidence",
                description="Demonstrated progress, actual working prototype proof (screenshots, metrics, demo links, output tables), rather than theoretical promises.",
                weightage=15.0,
                max_score=10.0
            ),
            Criterion(
                id="sih_impact",
                name="Scalability & Real-World Impact",
                description="Practical deployment potential, user adoption model, commercial or social viability, cost-efficiency, and measurable public benefit.",
                weightage=15.0,
                max_score=10.0
            ),
            Criterion(
                id="sih_presentation",
                name="Presentation Quality & Structure",
                description="Visual cleanliness, readability, concise bullet points, slide navigation flow, and professional pitch aesthetics.",
                weightage=15.0,
                max_score=10.0
            )
        ],
        mandatory_sections=[
            "Problem Statement",
            "Proposed Solution",
            "System Architecture",
            "Technology Stack",
            "Feasibility & Impact",
            "Demonstration / Results",
            "Team & Future Scope"
        ],
        min_passing_score=65.0
    ),
    
    "academic": RubricDefinition(
        id="rubric-academic",
        name="Academic Project Validator (Mini / Major / Seminar)",
        description="Standard university academic evaluation rubric verifying abstract, literature survey, methodology, system design, testing evidence, and IEEE/academic references.",
        is_builtin=True,
        mode_key="academic",
        criteria=[
            Criterion(
                id="acad_abstract",
                name="Abstract & Problem Definition",
                description="Precision of the abstract, research motivation, well-articulated problem definition, and project objectives.",
                weightage=15.0,
                max_score=10.0
            ),
            Criterion(
                id="acad_lit_survey",
                name="Literature Survey & Existing Systems",
                description="Critical comparative review of prior work, existing system limitations, and identified project gap.",
                weightage=15.0,
                max_score=10.0
            ),
            Criterion(
                id="acad_methodology",
                name="System Architecture & Methodology",
                description="Engineering methodology, UML/DFD/flow diagrams, algorithm pseudocode, and technical workflows.",
                weightage=20.0,
                max_score=10.0
            ),
            Criterion(
                id="acad_implementation",
                name="Implementation & Technology Stack",
                description="Code structure, tools, database schema, APIs, and evidence of authentic module development.",
                weightage=15.0,
                max_score=10.0
            ),
            Criterion(
                id="acad_results",
                name="Results, Testing & Verification",
                description="Verification methodology, test cases, performance benchmark graphs, output tables, and error analysis.",
                weightage=20.0,
                max_score=10.0
            ),
            Criterion(
                id="acad_references",
                name="Conclusion, Future Scope & References",
                description="Cohesive summary, tangible future enhancements, and properly formatted academic/IEEE citations.",
                weightage=15.0,
                max_score=10.0
            )
        ],
        mandatory_sections=[
            "Abstract / Introduction",
            "Literature Survey",
            "Objectives",
            "System Architecture",
            "Implementation",
            "Results & Testing",
            "Conclusion & References"
        ],
        min_passing_score=60.0
    ),
    
    "project_review": RubricDefinition(
        id="rubric-project-review",
        name="Project Review Validator (Milestone / Sprints)",
        description="Evaluates periodic project review milestone decks, cross-referencing claimed progress percentage against tangible delivered artifacts and risk mitigation.",
        is_builtin=True,
        mode_key="project_review",
        criteria=[
            Criterion(
                id="rev_progress",
                name="Claimed Progress vs Demonstrated Evidence",
                description="Consistency between stated completion percentages and actual visible screens, unit test outputs, or database milestones.",
                weightage=25.0,
                max_score=10.0
            ),
            Criterion(
                id="rev_modules",
                name="Module Development & Functional Deliverables",
                description="Detailing completed deliverables, in-progress tasks, and clear separation of concerns across modules.",
                weightage=20.0,
                max_score=10.0
            ),
            Criterion(
                id="rev_decisions",
                name="Technical Decisions & Architecture Integrity",
                description="Soundness of architectural choices, trade-offs made during development, and refactoring decisions.",
                weightage=20.0,
                max_score=10.0
            ),
            Criterion(
                id="rev_risks",
                name="Known Bottlenecks & Risk Mitigation",
                description="Transparency regarding technical blockers, security/performance bottlenecks, and counter-strategies.",
                weightage=15.0,
                max_score=10.0
            ),
            Criterion(
                id="rev_roadmap",
                name="Next Phase Sprint Planning",
                description="Actionable milestones, sprint allocation, testing targets, and realistic deadline projections.",
                weightage=20.0,
                max_score=10.0
            )
        ],
        mandatory_sections=[
            "Project Scope",
            "Sprint / Milestone Progress",
            "Demonstrated Features",
            "Challenges & Limitations",
            "Next Phase Roadmap"
        ],
        min_passing_score=60.0
    ),
    
    "subject": RubricDefinition(
        id="rubric-subject",
        name="Subject Presentation / Academic Seminar Validator",
        description="Assesses pedagogical flow, technical correctness, conceptual depth, diagram clarity, and instructional examples.",
        is_builtin=True,
        mode_key="subject",
        criteria=[
            Criterion(
                id="subj_coverage",
                name="Topic Coverage & Conceptual Depth",
                description="Comprehensive coverage of subject fundamentals, clear explanations, and appropriate academic depth.",
                weightage=25.0,
                max_score=10.0
            ),
            Criterion(
                id="subj_accuracy",
                name="Technical Correctness & Terminology",
                description="Accurate usage of industry terms, formulas, verified facts, and avoidance of misleading oversimplifications.",
                weightage=25.0,
                max_score=10.0
            ),
            Criterion(
                id="subj_pedagogy",
                name="Logical Flow & Pedagogical Clarity",
                description="Sequential progression from simple principles to advanced nuances with effective storytelling.",
                weightage=20.0,
                max_score=10.0
            ),
            Criterion(
                id="subj_visuals",
                name="Visual Aids, Diagrams & Examples",
                description="Use of illustrative diagrams, real-world case studies, and clear code/data examples instead of plain text.",
                weightage=15.0,
                max_score=10.0
            ),
            Criterion(
                id="subj_references",
                name="Summary, Key Takeaways & Bibliography",
                description="Concise synthesis of core takeaways, Q&A readiness, and authoritative textbook/paper references.",
                weightage=15.0,
                max_score=10.0
            )
        ],
        mandatory_sections=[
            "Topic Overview",
            "Core Concepts",
            "Practical Examples / Architecture",
            "Summary & Takeaways",
            "References"
        ],
        min_passing_score=60.0
    ),
    
    "research": RubricDefinition(
        id="rubric-research",
        name="Research Paper Presentation Validator",
        description="Scrutinizes scientific rigor, literature gap definition, mathematical/experimental formulation, statistical validity, and reproducible results.",
        is_builtin=True,
        mode_key="research",
        criteria=[
            Criterion(
                id="res_gap",
                name="Research Gap & Problem Motivation",
                description="Explicit identification of current state-of-the-art shortcomings and well-scoped research hypothesis.",
                weightage=20.0,
                max_score=10.0
            ),
            Criterion(
                id="res_methodology",
                name="Scientific Methodology & Design",
                description="Mathematical formulation, experimental setup, algorithmic design, and baseline comparison models.",
                weightage=25.0,
                max_score=10.0
            ),
            Criterion(
                id="res_evidence",
                name="Empirical Evidence & Statistical Analysis",
                description="Rigorous evaluation metrics (F1, precision, ablation study, p-values, latency benchmarks) with confidence bounds.",
                weightage=25.0,
                max_score=10.0
            ),
            Criterion(
                id="res_critique",
                name="Discussion, Limitations & Threat to Validity",
                description="Intellectual honesty regarding edge-case failures, computational bounds, and dataset constraints.",
                weightage=15.0,
                max_score=10.0
            ),
            Criterion(
                id="res_citations",
                name="Academic Citations & Publication Readiness",
                description="Citation accuracy, conformance to scholarly presentation standards, and author affiliations.",
                weightage=15.0,
                max_score=10.0
            )
        ],
        mandatory_sections=[
            "Introduction & Motivation",
            "Related Work & Gap",
            "Proposed Methodology",
            "Experimental Evaluation & Results",
            "Discussion & Limitations",
            "References"
        ],
        min_passing_score=65.0
    )
}

def get_rubric_for_mode(mode_key: str) -> RubricDefinition:
    return BUILTIN_RUBRICS.get(mode_key, BUILTIN_RUBRICS["sih"])

