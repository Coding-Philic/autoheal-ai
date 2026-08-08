"""Prompt templates for patch generation."""

SYSTEM_PROMPT = (
    "You are an expert software engineer specializing in bug fixes. "
    "You generate minimal, targeted code patches that fix the specific error "
    "without changing unrelated code. You always respond in valid JSON format. "
    "You never introduce new bugs."
)

PATCH_GEN_PROMPT = """Generate a minimal code patch to fix the following error.

## Error
- **Type:** {error_type}
- **Message:** {error_message}
- **Root Cause:** {root_cause}

## File to Patch
- **Path:** {file_path}
- **Language:** {language}

## Current File Content
```{language}
{file_content}
```

## Error Location
- **Line:** {line_number}
- **Error Context:** {error_context}

## Diagnosis
{explanation}

## Instructions
1. Generate the MINIMAL patch to fix this specific error
2. Do NOT change unrelated code
3. The patch should be a drop-in replacement for the current file
4. Include a brief description of what the patch does

## Response Format (STRICT JSON)
{{
    "patched_content": "Complete file content with the fix applied",
    "description": "Brief description of what was changed and why",
    "lines_changed": [42, 43],
    "risk_level": "low|medium|high"
}}"""

DEPENDENCY_FIX_PROMPT = """The following error is caused by a missing or incompatible dependency.

## Error
- **Type:** {error_type}
- **Message:** {error_message}

## Project
- **Language:** {language}
- **Package Manager:** {package_manager}
- **Current Dependencies:** {dependencies}

## Instructions
Determine the exact command to fix this dependency issue.

## Response Format (STRICT JSON)
{{
    "command": "pip install missing-package==1.0.0",
    "description": "Install missing package X which provides module Y",
    "confidence": 0.0
}}"""
