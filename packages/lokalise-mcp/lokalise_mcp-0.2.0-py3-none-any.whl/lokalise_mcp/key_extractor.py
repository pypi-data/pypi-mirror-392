"""Extract translation keys from source code."""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict


@dataclass
class TranslationKey:
    """Represents an extracted translation key."""
    key_name: str
    default_text: Optional[str] = None
    parameters: List[str] = field(default_factory=list)
    context: str = ""
    file_path: str = ""
    line_number: int = 0


class KeyExtractor:
    """Extract translation keys from source code using regex and AST."""

    def __init__(
        self,
        translation_functions: List[str] = None,
        default_param: str = "_",
        context_lines: int = 3
    ):
        self.translation_functions = translation_functions or ["t", "translate"]
        self.default_param = default_param
        self.context_lines = context_lines

        # Build regex patterns
        self._build_patterns()

    def _build_patterns(self):
        """Build regex patterns for detecting translation calls."""
        func_pattern = "|".join(re.escape(f) for f in self.translation_functions)

        # Pattern 1: With default value - t('key', { _: 'default' })
        self.pattern_with_default = re.compile(
            rf"(?:{func_pattern})\s*\(\s*['\"]([^'\"]+)['\"]\s*,\s*\{{\s*[^}}]*{self.default_param}\s*:\s*['\"]([^'\"]+)['\"]",
            re.MULTILINE | re.DOTALL
        )

        # Pattern 2: Simple - t('key')
        self.pattern_simple = re.compile(
            rf"(?:{func_pattern})\s*\(\s*['\"]([^'\"]+)['\"]\s*\)",
            re.MULTILINE
        )

        # Pattern 3: Parameters - extract variable names like {count}
        self.param_pattern = re.compile(r"%\{(\w+)\}")

    def extract_from_code(self, code: str, file_path: str = "") -> List[TranslationKey]:
        """Extract translation keys from code string."""
        keys = []
        seen_keys = set()

        lines = code.split('\n')

        # First pass: keys with defaults (priority)
        for match in self.pattern_with_default.finditer(code):
            key_name = match.group(1)
            default_text = match.group(2)

            if key_name in seen_keys:
                continue
            seen_keys.add(key_name)

            # Extract parameters from default text
            params = self.param_pattern.findall(default_text)

            # Get line number and context
            line_num = code[:match.start()].count('\n') + 1
            context = self._extract_context(lines, line_num)

            keys.append(TranslationKey(
                key_name=key_name,
                default_text=default_text,
                parameters=params,
                context=context,
                file_path=file_path,
                line_number=line_num
            ))

        # Second pass: simple keys without defaults
        for match in self.pattern_simple.finditer(code):
            key_name = match.group(1)

            if key_name in seen_keys:
                continue
            seen_keys.add(key_name)

            line_num = code[:match.start()].count('\n') + 1
            context = self._extract_context(lines, line_num)

            keys.append(TranslationKey(
                key_name=key_name,
                default_text=None,
                parameters=[],
                context=context,
                file_path=file_path,
                line_number=line_num
            ))

        return keys

    def _extract_context(self, lines: List[str], line_num: int) -> str:
        """Extract surrounding lines for context."""
        start = max(0, line_num - self.context_lines - 1)
        end = min(len(lines), line_num + self.context_lines)

        context_lines = lines[start:end]
        return '\n'.join(context_lines)

    def extract_from_file(self, file_path: Path) -> List[TranslationKey]:
        """Extract translation keys from a file."""
        code = file_path.read_text(encoding='utf-8')
        return self.extract_from_code(code, file_path=str(file_path))
