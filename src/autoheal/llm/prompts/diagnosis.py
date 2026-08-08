"""Prompt templates for error diagnosis."""

SYSTEM_PROMPT = (
    "You are an expert software debugger and root cause analyst. "
    "You analyze errors in any programming language and determine the exact root cause. "
    "You always respond in valid JSON format. "
    "You are precise, thorough, and honest about your confidence level."
)

DIAGNOSIS_PROMPT = """Analyze the following error and determine the root cause.

## Error Details
- **Type:** {error_type}
- **Message:** {error_message}
- **File:** {file_path}
- **Line:** {line_number}

## Stack Trace
```
{stack_trace}
```

## Source Code (around error)
```{language}
{code_context}
```

## Project Info
- **Language:** {project_language}
- **Framework:** {project_framework}
- **Dependencies:** {dependencies}

## Environment
- **OS:** {os_name} {os_version}
- **Runtime:** {runtime_version}
- **CPU:** {cpu_percent}%
- **Memory:** {memory_percent}%

## Instructions
1. Identify the ROOT CAUSE (not just the symptom)
2. Classify the error category
3. Rate your confidence (0.0 to 1.0) — be honest
4. Suggest the best fix strategy
5. Provide a brief, actionable explanation

## Response Format (STRICT JSON — no markdown, no extra text)
{{
    "root_cause": "One-line root cause description",
    "category": "runtime|config|dependency|resource|logic|network|permission|syntax",
    "confidence": 0.0,
    "fix_strategy": "restart|config_patch|code_patch|dependency_fix|rollback|escalate",
    "explanation": "2-3 sentence explanation of why this error occurred and how to fix it",
    "suggested_fix": "Brief description of the specific fix to apply"
}}"""

MANUAL_DIAGNOSIS_PROMPT = """Analyze the following error description and determine the likely root cause.

## Error Description
{error_description}

## Instructions
1. Identify the most likely ROOT CAUSE
2. Classify the error category
3. Rate your confidence (0.0 to 1.0)
4. Suggest the best fix strategy

## Response Format (STRICT JSON)
{{
    "root_cause": "One-line root cause description",
    "category": "runtime|config|dependency|resource|logic|network|permission|syntax",
    "confidence": 0.0,
    "fix_strategy": "restart|config_patch|code_patch|dependency_fix|rollback|escalate",
    "explanation": "2-3 sentence explanation",
    "suggested_fix": "Brief fix description"
}}"""
