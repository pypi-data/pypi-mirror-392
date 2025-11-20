"""
nnl.core - fixed JSON-capable NNL parser and serializer

Public API:
- parse_nnl(text: str) -> dict
- dump_nnl(obj: Any) -> str
"""
from typing import Any, Tuple, List, Dict
import re
import json

_ws_re = re.compile(r'^[ \t]*')


def _indent_level(line: str) -> int:
    lead = _ws_re.match(line).group(0)
    # treat a tab as 4 spaces
    return lead.count(' ') + lead.count('\t') * 4


def _unquote(s: str) -> str:
    s = s.strip()
    if not s:
        return s
    if (s[0] == s[-1]) and s[0] in ('"', "'"):
        try:
            if s[0] == "'":
                # convert single-quoted to double-quoted for json.loads
                inner = s[1:-1].replace('"', '\\"')
                return json.loads('"' + inner + '"')
            return json.loads(s)
        except Exception:
            return s[1:-1]
    return s


def _parse_scalar(token: str) -> Any:
    t = token.strip()
    if not t:
        return ""
    low = t.lower()
    if low == 'true':
        return True
    if low == 'false':
        return False
    if low in ('null', 'none'):
        return None
    # integer
    if re.fullmatch(r'[+-]?\d+', t):
        try:
            return int(t)
        except Exception:
            pass
    # float / scientific
    if re.fullmatch(r'[+-]?\d*\.\d+([eE][+-]?\d+)?', t) or re.fullmatch(r'[+-]?\d+[eE][+-]?\d+', t):
        try:
            return float(t)
        except Exception:
            pass
    return _unquote(t)


# Public API
def parse_nnl(text: str) -> Dict[str, Any]:
    """
    Parse NNL text into a Python dict (top-level object).
    """
    lines = text.splitlines()
    parsed, _ = _parse_block(lines, 0, 0)
    return parsed


# Core parser: returns (object, next_index)
def _parse_block(lines: List[str], start: int, base_indent: int) -> Tuple[Dict[str, Any], int]:
    obj: Dict[str, Any] = {}
    i = start
    n = len(lines)

    while i < n:
        raw = lines[i]
        # skip blank lines
        if not raw.strip():
            i += 1
            continue

        indent = _indent_level(raw)
        # if this line is less-indented, it belongs to outer block
        if indent < base_indent:
            break

        line = raw.strip()

        # 1) object block: key contains:
        if line.endswith('contains:'):
            key = line[:-len('contains:')].strip()
            # parse nested block: expect lines with greater indent
            nested, consumed = _parse_block(lines, i + 1, indent + 1)
            obj[key] = nested
            i = consumed
            continue

        # 2) block list: key are:
        m_are_colon = re.match(r'^(.+?)\s+are:\s*$', line)
        if m_are_colon:
            key = m_are_colon.group(1).strip()
            items: List[Any] = []
            j = i + 1
            while j < n:
                raw2 = lines[j]
                if not raw2.strip():
                    j += 1
                    continue
                indent2 = _indent_level(raw2)
                # stop when same or lesser indent (belongs to outer)
                if indent2 <= indent:
                    break
                sub = raw2.strip()
                # list item prefixed with '-'
                if sub.startswith('-'):
                    remainder = sub[1:].strip()
                    # case: "- contains:" empty remainder -> nested block under this item
                    if remainder == '':
                        # parse nested block for this list item (item block starts at next line)
                        nested_item, consumed2 = _parse_block(lines, j + 1, indent2 + 1)
                        items.append(nested_item)
                        j = consumed2
                        continue
                    # case: "- contains:" with remainder like "contains:"
                    if remainder.endswith('contains:'):
                        # build a fake "contains:" line for the nested object
                        fake_line = ' ' * indent2 + remainder
                        original = lines[j]
                        lines[j] = fake_line

                        # parse the nested block starting after this line
                        nested_dict, consumed2 = _parse_block(lines, j + 1, indent2 + 1)

                        # restore original line
                        lines[j] = original

                        # append ONLY the nested object (not {"contains":{}})
                        items.append(nested_dict)
                        j = consumed2
                        continue

                    # remainder might be inline scalars: possibly comma-separated
                    rem = remainder.rstrip(',').rstrip('.').strip()
                    if not rem:
                        j += 1
                        continue
                    # If comma-separated: this is a nested list (e.g. "- 1, 2, 3.")
                    if ',' in rem:
                        parts = [p.strip() for p in rem.split(',') if p.strip()]
                        nested_list = [_parse_list_item_token(p) for p in parts]
                        items.append(nested_list)
                    else:
                        # single scalar item
                        items.append(_parse_list_item_token(rem))
                    j += 1
                    continue
                else:
                    # indented non '-' lines: accept simple scalar lines (like "python," or "python")
                    token = sub.rstrip(',').rstrip('.').strip()
                    if token:
                        if ',' in token:
                            parts = [p.strip() for p in token.split(',') if p.strip()]
                            for p in parts:
                                items.append(_parse_list_item_token(p))
                        else:
                            items.append(_parse_list_item_token(token))
                    j += 1
            obj[key] = items
            i = j
            continue

        # 3) inline statements:
        core = line[:-1].strip() if line.endswith('.') else line

        # "key is value"
        m_is = re.match(r'^(.+?)\s+is\s+(.+)$', core)
        if m_is:
            key = m_is.group(1).strip()
            val_raw = m_is.group(2).strip()
            obj[key] = _parse_list_or_scalar(val_raw)
            i += 1
            continue

        # "key are a, b, c" inline
        m_are = re.match(r'^(.+?)\s+are\s+(.+)$', core)
        if m_are:
            key = m_are.group(1).strip()
            vals_raw = m_are.group(2).strip()
            # prefer comma separation; if no commas, split on whitespace (single-word items)
            if ',' in vals_raw:
                parts = [p.strip() for p in vals_raw.split(',') if p.strip()]
            else:
                parts = [p.strip() for p in vals_raw.split() if p.strip()]
            items = [_parse_list_or_scalar(p) for p in parts]
            obj[key] = items
            i += 1
            continue

        # fallback: "key value" (last token is value)
        parts = core.split()
        if len(parts) >= 2:
            key = ' '.join(parts[:-1])
            val = _parse_list_or_scalar(parts[-1])
            obj[key] = val
        else:
            # single word flag -> True
            obj[core] = True
        i += 1

    return obj, i


def _parse_list_item_token(token: str) -> Any:
    return _parse_list_or_scalar(token)


def _parse_list_or_scalar(raw: str) -> Any:
    return _parse_scalar(raw)


# Serializer
def dump_nnl(obj: Any, indent: int = 0) -> str:
    pad = '  ' * indent
    if isinstance(obj, dict):
        parts: List[str] = []
        for k, v in obj.items():
            if isinstance(v, dict):
                parts.append(f"{pad}{k} contains:")
                parts.append(dump_nnl(v, indent + 1))
            elif isinstance(v, list):
                # inline simple scalar lists
                if all(not isinstance(x, (dict, list)) for x in v) and len(v) <= 5:
                    items = ', '.join(_format_scalar(x) for x in v)
                    parts.append(f"{pad}{k} are {items}.")
                else:
                    parts.append(f"{pad}{k} are:")
                    for item in v:
                        if isinstance(item, dict):
                            parts.append(f"{pad}  - contains:")
                            parts.append(dump_nnl(item, indent + 3))
                        elif isinstance(item, list):
                            if all(not isinstance(x, (dict, list)) for x in item) and len(item) <= 5:
                                parts.append(f"{pad}  - " + ', '.join(_format_scalar(x) for x in item) + ".")
                            else:
                                parts.append(f"{pad}  -")
                                parts.append(dump_nnl(item, indent + 3))
                        else:
                            parts.append(f"{pad}  - {_format_scalar(item)}.")
            else:
                parts.append(f"{pad}{k} is {_format_scalar(v)}.")
        return "\n".join(parts)
    elif isinstance(obj, list):
        parts: List[str] = []
        for item in obj:
            if isinstance(item, dict):
                parts.append(f"{pad}- contains:")
                parts.append(dump_nnl(item, indent + 1))
            elif isinstance(item, list):
                if all(not isinstance(x, (dict, list)) for x in item) and len(item) <= 5:
                    parts.append(f"{pad}- " + ', '.join(_format_scalar(x) for x in item) + ".")
                else:
                    parts.append(f"{pad}-")
                    parts.append(dump_nnl(item, indent + 1))
            else:
                parts.append(f"{pad}- {_format_scalar(item)}.")
        return "\n".join(parts)
    else:
        return pad + _format_scalar(obj)


def _format_scalar(v: Any) -> str:
    if v is None:
        return 'null'
    if isinstance(v, bool):
        return 'true' if v else 'false'
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, str):
        # quote if contains whitespace or special punctuation
        if re.search(r'\s', v) or v == '' or re.search(r'[,:(){}\[\]]', v):
            return json.dumps(v)
        return v
    return json.dumps(v)
