formula_labels = ["display_formula", "formula"]
image_labels = ["image"]
table_labels = ["table"]

FORMULA_PROMPT = """
You are a mathematical OCR system.

TASK:
Extract all mathematical expressions from the image crop.

RULES:
- Output ONLY valid JSON
- No explanation, no commentary
- Do not interpret meaning

FORMULA RULES:
- Convert all expressions into valid LaTeX
- Preserve exact structure (fractions, exponents, integrals, matrices, sums)
- Do not simplify expressions
- Do not normalize notation
- Ensure LaTeX is syntactically correct

IF MULTIPLE FORMULAS:
- Return them in a list

OUTPUT FORMAT:
{
  "type": "formula",
  "content": {
    "latex": ["..."]
  }
}

STRICT:
- Only valid LaTeX allowed"""

IMAGE_PROMPT = """
You are a visual document understanding system.

TASK:
Analyze the image and produce structured visual information.
Write it in french.

RULES:
- Output ONLY valid JSON
- No speculation beyond visible content
- Be precise and structured

EXTRACT:

1. OBJECTS:
- List all visible objects

2. TEXT:
- Extract all visible text exactly

3. LAYOUT:
- Describe spatial organization (top/bottom/left/right, grouping)

4. RELATIONSHIPS:
- Describe relationships between elements (e.g., "A points to B", "A contains B")
5  - DESCRIPTION:
- Optional overall description of the image content

IF GRAPH OR CHART:
- Identify axes, labels, units
- Describe trends (increase/decrease/constant)

"""
TABLE_PROMPT = """
You are a document table extraction system.

TASK:
Extract the table from the image crop and return ONLY valid JSON.

RULES:
- Output must be strictly valid JSON (no markdown, no explanation)
- Preserve full table structure exactly as seen
- Detect hierarchical headers if present
- Detect merged cells using rowspan and colspan
- Detect nested tables inside cells when present
- Do NOT flatten the structure
- Do NOT infer missing data

CELL RULES:
- All cells must be included
- Empty cells must be ""
- If a cell contains a nested table, represent it as a table object


STRICT REQUIREMENT:
- All rows must follow consistent structure
- Do not hallucinate columns or values
"""
