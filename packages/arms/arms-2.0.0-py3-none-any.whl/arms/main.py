import base64
import os
import re
import sys
import zipfile
from fnmatch import fnmatch
from pathlib import Path
from typing import List

from lesscli import add_argument, run

from arms.utils.wordstyle import replace_all, replace_dict


def format_single_file(file_path: str, file_content: bytes):
    # Try to decode as UTF-8 text; if fails or contains NUL, treat as binary
    try:
        text_content = file_content.decode('utf-8')
        if '\x00' in text_content:
            raise ValueError('NUL in text -> binary')
        # Text path: keep existing logic
        max_backticks = 3
        for line in text_content.splitlines():
            line = line.rstrip()
            if re.match(r'^`+', line) and max_backticks <= len(line):
                max_backticks = len(line) + 1
        line_break = '`' * max_backticks
        return f'**{file_path}**:\n{line_break}\n{text_content}\n{line_break}\n\n'
    except (UnicodeDecodeError, ValueError):
        # Binary path: encode with base64 and mark fence with language
        b64 = base64.b64encode(file_content).decode('ascii')
        return f'**{file_path}**:\n```base64\n{b64}\n```\n\n'


def _parse_markdown_archive(md_text: str):
    lines = md_text.splitlines()
    i = 0
    n = len(lines)
    header_re = re.compile(r'^\*\*(.+?)\*\*:\s*$')
    while i < n:
        m = header_re.match(lines[i])
        if not m:
            i += 1
            continue
        rel_path = m.group(1)
        i += 1
        if i >= n:
            break
        opener = lines[i]
        # Binary block: ```base64 ... ```
        if opener.strip() == '```base64':
            i += 1
            b64_lines = []
            while i < n and not lines[i].strip().startswith('```'):
                b64_lines.append(lines[i])
                i += 1
            # consume closing fence if present
            if i < n and lines[i].strip().startswith('```'):
                i += 1
            # skip trailing blanks between sections
            while i < n and lines[i] == '':
                i += 1
            content = base64.b64decode('\n'.join(b64_lines)) if b64_lines else b''
            yield rel_path, content
            continue
        # Text block: line of >=3 backticks, same count closes
        m_tick = re.match(r'^`{3,}\s*$', opener)
        if not m_tick:
            # Unexpected line; skip
            i += 1
            continue
        fence = opener.strip()
        i += 1
        text_lines = []
        while i < n and lines[i].strip() != fence:
            text_lines.append(lines[i])
            i += 1
        # consume closing fence if present
        if i < n and lines[i].strip() == fence:
            i += 1
        # skip trailing blanks between sections
        while i < n and lines[i] == '':
            i += 1
        yield rel_path, ('\n'.join(text_lines)).encode('utf-8')


def _create_archive(input_file: str, file_name: str, locked: str, rules: List[str]):
    """Create markdown archive from a zip file."""
    if not input_file:
        print('Error: --input (-i) .zip file is required for create.', file=sys.stderr)
        sys.exit(2)
    if not os.path.isfile(input_file):
        print(f'Error: input zip not found: {input_file}', file=sys.stderr)
        sys.exit(2)

    # Build lock patterns
    lock_patterns = [p.strip() for p in (locked or '').split(',') if p.strip()]

    # Build replacement dict from rules (rules are new:old)
    repl_map = {}
    for token in (rules or []):
        if ':' not in token:
            continue
        new_word, old_word = token.split(':', 1)
        new_word, old_word = new_word.strip(), old_word.strip()
        if new_word and old_word:
            repl_map.update(replace_dict(old_word, new_word))

    # Process zip file
    parts = []
    with zipfile.ZipFile(input_file, 'r') as zf:
        names = sorted([
            zi.filename for zi in zf.infolist()
            if not (zi.is_dir() if hasattr(zi, 'is_dir') else zi.filename.endswith('/'))
        ])
        for name in names:
            data = zf.read(name)
            snippet = format_single_file(name, data)
            base = name.rsplit('/', 1)[-1]
            is_locked = any(fnmatch(name, pat) or fnmatch(base, pat) for pat in lock_patterns)
            if not is_locked and repl_map:
                snippet = replace_all(snippet, repl_map)
            parts.append(snippet)

    # Write output
    output_text = ''.join(parts)
    if file_name:
        Path(os.path.dirname(file_name) or '.').mkdir(parents=True, exist_ok=True)
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(output_text)
    else:
        sys.stdout.write(output_text)


def _extract_archive(file_name: str, output_dir: str, overwrite: bool):
    """Extract files from markdown archive."""
    # Read markdown archive
    if file_name:
        with open(file_name, 'r', encoding='utf-8') as f:
            md_text = f.read()
    else:
        md_text = sys.stdin.read()

    # Validate output directory
    out_dir = output_dir or '.'
    if output_dir and not os.path.isdir(out_dir):
        print(f'Error: output directory not found: {out_dir}', file=sys.stderr)
        sys.exit(2)

    # Extract files
    for rel_path, content in _parse_markdown_archive(md_text):
        dest_path = os.path.join(out_dir, rel_path)

        # Handle existing files
        if not overwrite and os.path.exists(dest_path):
            dest_path = f"{dest_path}.patch"

        Path(os.path.dirname(dest_path) or '.').mkdir(parents=True, exist_ok=True)
        with open(dest_path, 'wb') as f:
            f.write(content)


@add_argument('--create', short='c', help='Create markdown archive from a .zip (-i).', type=bool, default=False, required=False)
@add_argument('--extract', short='x', help='Extract files from a markdown archive.', type=bool, default=False, required=False)
@add_argument('--input', short='i', help='Input .zip when using -c/--create.', type=str, default='', required=False, dest='input_file')
@add_argument('--output', short='o', help='Output directory for -x/--extract (must exist).', type=str, default='', required=False, dest='output_dir')
@add_argument('--file', short='f', help='Read/write the markdown archive file (default: STDIO).', type=str, default='', required=False, dest='file_name')
@add_argument('--locked', short='l', help='Comma-separated filenames/patterns to lock (skip replacements when creating).', type=str, default='', required=False)
@add_argument('--overwrite', help='Overwrite existing files during extraction (default: add .patch suffix to duplicates).', type=bool, default=False, required=False)
@add_argument('rules', help='Replacement rule(s) as "new:old". Pass multiple values separated by space. Uses full-style replacement.', type=str, nargs='*')
def entrypoint(create: bool, extract: bool, input_file: str, output_dir: str, file_name: str, locked: str, overwrite: bool, rules: List[str]):
    if create and extract:
        print('Error: cannot use --create and --extract together.', file=sys.stderr)
        sys.exit(2)
    if not create and not extract:
        print('Error: must specify either --create (-c) or --extract (-x).', file=sys.stderr)
        sys.exit(2)

    if create:
        _create_archive(input_file, file_name, locked, rules)
    else:
        _extract_archive(file_name, output_dir, overwrite)


def main():
    run(entrypoint)
