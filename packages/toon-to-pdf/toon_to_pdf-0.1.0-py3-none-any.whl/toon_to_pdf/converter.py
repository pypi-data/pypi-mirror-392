"""
Core conversion logic for TOON to PDF.

This module implements the three-step process:
1. Parse TOON input into a dictionary
2. Transform (if needed) to match pdfme format
3. Generate PDF using pdfme
"""

import importlib
from pathlib import Path
from typing import Union, Any

# Note: TOON parser is built-in, no external dependency needed
# pdfme import is lazy (only when actually generating PDF)


def generate_from_toon(toon_input: str, output_path: Union[str, Path]) -> None:
    """
    Generate a PDF file from TOON format input.

    This function performs a three-step process:
    1. Parse: Convert TOON string to Python dictionary
    2. Transform: Ensure the dictionary matches pdfme's expected format
    3. Generate: Create PDF file using pdfme

    Args:
        toon_input: TOON format string describing the PDF structure
        output_path: Path where the generated PDF file will be saved

    Raises:
        ImportError: If required dependencies (python-toon or pdfme) are not installed
        ValueError: If the TOON input cannot be parsed or is invalid
        IOError: If the output file cannot be written

    Example:
        >>> toon_content = '''
        ... (
        ...   schemas: [
        ...     (
        ...       content: ( type: "text", text: "Hello World" )
        ...       position: ( x: 50, y: 50 )
        ...     )
        ...   ]
        ...   basePdf: "blank"
        ... )
        ... '''
        >>> generate_from_toon(toon_content, "output.pdf")
    """
    # Step 1: Parse TOON input into a dictionary
    try:
        pdf_data = _parse_toon(toon_input)
    except Exception as e:
        raise ValueError(f"Failed to parse TOON input: {str(e)}") from e

    # Step 2: Transform (if needed)
    # Currently, we assume the TOON schema matches pdfme's format directly
    # Future enhancements can add transformation logic here for convenience features
    transformed_data = _transform_to_pdfme_format(pdf_data)

    # Step 3: Generate PDF using pdfme
    pdf_cls = _load_pdf_class()

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        pdf = pdf_cls(
            page_size=_resolve_page_size(transformed_data.get("basePdf")),
            margin=0,
        )
        _render_pdf_document(pdf, transformed_data, output_path)
    except Exception as e:
        raise IOError(f"Failed to generate PDF file: {str(e)}") from e


def generate_from_toon_file(toon_file_path: Union[str, Path], output_path: Union[str, Path]) -> None:
    """
    Generate a PDF file from a TOON format file.

    Convenience function that reads a TOON file and generates a PDF.

    Args:
        toon_file_path: Path to the input TOON file
        output_path: Path where the generated PDF file will be saved

    Raises:
        FileNotFoundError: If the TOON file does not exist
        ValueError: If the TOON input cannot be parsed or is invalid
        IOError: If the output file cannot be written

    Example:
        >>> generate_from_toon_file("document.toon", "document.pdf")
    """
    toon_file_path = Path(toon_file_path)
    if not toon_file_path.exists():
        raise FileNotFoundError(f"TOON file not found: {toon_file_path}")

    with open(toon_file_path, "r", encoding="utf-8") as f:
        toon_content = f.read()

    generate_from_toon(toon_content, output_path)


def _transform_to_pdfme_format(data: dict) -> dict:
    """
    Transform parsed TOON data to match pdfme's expected format.

    This function ensures the data structure matches what pdfme expects.
    Currently, it performs basic validation and normalization.
    Future versions may add more sophisticated transformations.

    Args:
        data: Dictionary parsed from TOON input

    Returns:
        Dictionary in pdfme-compatible format
    """
    # Basic validation: ensure required keys exist
    if not isinstance(data, dict):
        raise ValueError("TOON input must parse to a dictionary")

    # Ensure 'schemas' key exists (required by pdfme)
    if "schemas" not in data:
        # If schemas is missing, try to create a default structure
        # This allows for more flexible TOON input
        data["schemas"] = []

    # Ensure 'basePdf' has a default if not specified
    if "basePdf" not in data:
        data["basePdf"] = "blank"

    # Validate schema structure
    if not isinstance(data["schemas"], list):
        raise ValueError("'schemas' must be a list")

    # Normalize schema entries
    for i, schema in enumerate(data["schemas"]):
        if not isinstance(schema, dict):
            raise ValueError(f"Schema at index {i} must be a dictionary")
        
        # Ensure required schema fields
        if "content" not in schema:
            raise ValueError(f"Schema at index {i} must have a 'content' field")
        
        if "position" not in schema:
            # Provide default position if missing
            schema["position"] = {"x": 0, "y": 0}

    return data


def _load_pdf_class():
    """Import pdfme's PDF class lazily so tests can stub it."""
    try:
        pdf_module = importlib.import_module("pdfme")
    except ImportError as exc:
        raise ImportError(
            "pdfme is required. Install it with: pip install pdfme"
        ) from exc
    try:
        return getattr(pdf_module, "PDF")
    except AttributeError as exc:
        raise ImportError(
            "Installed pdfme package does not expose PDF class"
        ) from exc


def _render_pdf_document(pdf: Any, data: dict, output_path: Path) -> None:
    """
    Render the normalized TOON data into a PDF file using pdfme.
    """
    schemas = data.get("schemas", [])
    if not isinstance(schemas, list):
        raise ValueError("'schemas' must be a list")

    if not pdf.pages:
        pdf.add_page()

    for index, schema in enumerate(schemas):
        _render_schema(pdf, schema, index)

    with open(output_path, "wb") as pdf_file:
        pdf.output(pdf_file)


def _render_schema(pdf: Any, schema: dict, schema_index: int) -> None:
    """Render a single schema entry."""
    if not isinstance(schema, dict):
        raise ValueError(f"Schema at index {schema_index} must be a dictionary")

    content = schema.get("content")
    if not isinstance(content, dict):
        raise ValueError(f"Schema at index {schema_index} must include a content dictionary")

    content_type = (content.get("type") or "text").lower()
    position = _normalize_position(schema.get("position"))

    if content_type == "text":
        _render_text_schema(pdf, content, position, schema_index)
    else:
        raise ValueError(f"Unsupported schema content type '{content_type}' at index {schema_index}")


def _render_text_schema(pdf: Any, content: dict, position: dict, schema_index: int) -> None:
    """Render a text schema by placing text at the specified coordinates."""
    text_value = content.get("text")
    if text_value is None:
        raise ValueError(f"Text schema at index {schema_index} must include a 'text' field")

    style = _build_text_style(content)
    paragraph: dict[str, Any] = {".": str(text_value)}
    if style:
        paragraph["style"] = style

    width = max(pdf.page.width - position["x"] - pdf.page.margin_right, 1)
    height = max(pdf.page.height - position["y"] - pdf.page.margin_bottom, 1)

    pdf._text(
        paragraph,
        x=position["x"],
        y=position["y"],
        width=width,
        height=height,
        move="none",
    )


def _build_text_style(content: dict) -> dict:
    """Map TOON text style attributes to pdfme shorthand style keys."""
    style: dict[str, Any] = {}

    font_size = content.get("fontSize")
    if font_size is not None:
        style["s"] = float(font_size)

    font_family = content.get("font") or content.get("fontFamily")
    if font_family:
        style["f"] = str(font_family)

    if content.get("bold"):
        style["b"] = True
    if content.get("italic"):
        style["i"] = True

    color = content.get("color")
    if color is not None:
        style["c"] = _parse_color(color)

    line_height = content.get("lineHeight")
    if line_height is not None:
        style["line_height"] = float(line_height)

    align_value = content.get("textAlign") or content.get("align")
    if align_value:
        style["text_align"] = _normalize_alignment(align_value)

    return style


def _normalize_alignment(value: str) -> str:
    """Convert human-friendly alignment names to pdfme shorthand."""
    mapping = {
        "left": "l",
        "l": "l",
        "center": "c",
        "c": "c",
        "right": "r",
        "r": "r",
        "justify": "j",
        "j": "j",
    }
    return mapping.get(value.lower(), "l")


def _normalize_position(position: Any) -> dict:
    """Ensure schemas always provide numeric x/y coordinates."""
    if not isinstance(position, dict):
        return {"x": 0.0, "y": 0.0}

    try:
        x = float(position.get("x", 0))
        y = float(position.get("y", 0))
    except (TypeError, ValueError) as exc:
        raise ValueError("Position coordinates must be numeric") from exc

    if x < 0 or y < 0:
        raise ValueError("Position coordinates must be non-negative")

    return {"x": x, "y": y}


def _parse_color(color_value: Any) -> Any:
    """Convert TOON color values into pdfme-compatible values."""
    if isinstance(color_value, (int, float)):
        return float(color_value)

    if isinstance(color_value, (list, tuple)):
        return tuple(color_value)

    if isinstance(color_value, str):
        color_value = color_value.strip()
        if color_value.startswith("#"):
            hex_value = color_value[1:]
            if len(hex_value) == 3:
                hex_value = "".join(ch * 2 for ch in hex_value)
            if len(hex_value) == 6:
                r = int(hex_value[0:2], 16) / 255
                g = int(hex_value[2:4], 16) / 255
                b = int(hex_value[4:6], 16) / 255
                return (r, g, b)
        return color_value

    return color_value


def _resolve_page_size(base_pdf: Any) -> Any:
    """Determine the pdfme page_size argument from the TOON basePdf field."""
    if isinstance(base_pdf, (tuple, list)) and len(base_pdf) == 2:
        return tuple(base_pdf)

    if isinstance(base_pdf, str):
        alias = base_pdf.lower()
        if alias == "blank":
            return "letter"
        if alias in {"letter", "a4", "legal"}:
            return alias

    return "letter"


def _parse_toon(toon_input: str) -> dict:
    """
    Parse TOON format string into a Python dictionary.
    
    TOON format is a simplified syntax similar to S-expressions:
    - Parentheses () for grouping
    - Key-value pairs: key: value
    - Lists: [ item1, item2 ]
    - Strings: "text" or text (without quotes for simple identifiers)
    - Numbers: 123, 45.67
    - Booleans: true, false
    
    Args:
        toon_input: TOON format string
        
    Returns:
        Dictionary representation of the TOON structure
    """
    # Remove comments and normalize whitespace
    toon_input = _clean_toon_input(toon_input)
    
    # Parse the TOON structure using a token-based approach
    tokens = _tokenize(toon_input)
    result, _ = _parse_tokens(tokens, 0)
    return result


def _clean_toon_input(text: str) -> str:
    """Remove comments and normalize whitespace, respecting quoted strings."""
    processed_lines = []
    for raw_line in text.split("\n"):
        line_chars: list[str] = []
        in_string = False
        escape_next = False
        for ch in raw_line:
            if in_string:
                line_chars.append(ch)
                if escape_next:
                    escape_next = False
                    continue
                if ch == "\\":
                    escape_next = True
                elif ch == '"':
                    in_string = False
                continue

            if ch == '"':
                in_string = True
                line_chars.append(ch)
            elif ch == "#":
                break
            else:
                line_chars.append(ch)
        processed_lines.append("".join(line_chars))
    return "\n".join(processed_lines)


def _tokenize(text: str) -> list:
    """Tokenize TOON input into a list of tokens."""
    tokens = []
    i = 0
    text = text.strip()
    
    while i < len(text):
        # Skip whitespace
        if text[i] in ' \t\n\r':
            i += 1
            continue
        
        # Special characters
        if text[i] in '()[]:,':
            tokens.append(text[i])
            i += 1
            continue
        
        # String
        if text[i] == '"':
            start = i
            i += 1
            while i < len(text):
                if text[i] == '"' and text[i-1] != '\\':
                    break
                i += 1
            if i >= len(text):
                raise ValueError("Unclosed string")
            value = text[start+1:i]
            value = value.replace('\\"', '"').replace('\\n', '\n').replace('\\t', '\t')
            tokens.append(('STRING', value))
            i += 1
            continue
        
        # Number
        if text[i].isdigit() or (text[i] == '-' and i + 1 < len(text) and text[i+1].isdigit()):
            start = i
            if text[i] == '-':
                i += 1
            while i < len(text) and (text[i].isdigit() or text[i] == '.'):
                i += 1
            num_str = text[start:i]
            if '.' in num_str:
                tokens.append(('NUMBER', float(num_str)))
            else:
                tokens.append(('NUMBER', int(num_str)))
            continue
        
        # Boolean or identifier
        start = i
        while i < len(text) and text[i] not in ' \t\n\r()[]:,':
            i += 1
        word = text[start:i]
        if word == 'true':
            tokens.append(('BOOLEAN', True))
        elif word == 'false':
            tokens.append(('BOOLEAN', False))
        else:
            tokens.append(('IDENTIFIER', word))
    
    return tokens


def _parse_tokens(tokens: list, pos: int) -> tuple[Any, int]:
    """Parse tokens starting at position pos."""
    if pos >= len(tokens):
        raise ValueError("Unexpected end of input")
    
    token = tokens[pos]
    
    # Parse object
    if token == '(':
        return _parse_object_tokens(tokens, pos)
    
    # Parse list
    if token == '[':
        return _parse_list_tokens(tokens, pos)
    
    # Parse value
    if isinstance(token, tuple):
        if token[0] == 'STRING':
            return token[1], pos + 1
        if token[0] == 'NUMBER':
            return token[1], pos + 1
        if token[0] == 'BOOLEAN':
            return token[1], pos + 1
        if token[0] == 'IDENTIFIER':
            return token[1], pos + 1
    
    raise ValueError(f"Unexpected token: {token}")


def _parse_object_tokens(tokens: list, pos: int) -> tuple[dict, int]:
    """Parse an object from tokens: ( key: value ... )"""
    if tokens[pos] != '(':
        raise ValueError("Expected '('")
    
    pos += 1
    result = {}
    
    while pos < len(tokens) and tokens[pos] != ')':
        # Skip commas (they're optional separators between key-value pairs)
        if tokens[pos] == ',':
            pos += 1
            continue
        
        # Parse key
        if not isinstance(tokens[pos], tuple) or tokens[pos][0] not in ('IDENTIFIER', 'STRING'):
            raise ValueError(f"Expected key, got {tokens[pos]}")
        key = tokens[pos][1]
        pos += 1
        
        # Expect colon
        if pos >= len(tokens) or tokens[pos] != ':':
            raise ValueError(f"Expected ':' after key '{key}'")
        pos += 1
        
        # Parse value
        value, pos = _parse_tokens(tokens, pos)
        result[key] = value
    
    if pos >= len(tokens) or tokens[pos] != ')':
        raise ValueError("Expected ')' to close object")
    
    return result, pos + 1


def _parse_list_tokens(tokens: list, pos: int) -> tuple[list, int]:
    """Parse a list from tokens: [ value ... ]"""
    if tokens[pos] != '[':
        raise ValueError("Expected '['")
    
    pos += 1
    result = []
    
    while pos < len(tokens) and tokens[pos] != ']':
        # Parse value
        value, pos = _parse_tokens(tokens, pos)
        result.append(value)
        
        # Skip comma if present
        if pos < len(tokens) and tokens[pos] == ',':
            pos += 1
    
    if pos >= len(tokens) or tokens[pos] != ']':
        raise ValueError("Expected ']' to close list")
    
    return result, pos + 1

