import re
from typing import Optional, List, Tuple

from backend.src.models.candidate_profile import CandidateProfile

try:
    import morfeusz2
except ImportError:
    morfeusz2 = None


class CandidateExtractor:
    EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
    PHONE_RE = re.compile(r"(\+?\d(?:[ \t-]?\d){8,})")
    NAME_LINE_RE = re.compile(
        r"(imię\s+i\s+nazwisko|imię\s+nazwisko)\s*[:\-]\s*(.+)",
        re.IGNORECASE,
    )

    _morfeusz_instance = None

    @classmethod
    def _get_morfeusz(cls):
        if morfeusz2 is None:
            return None
        if cls._morfeusz_instance is None:
            cls._morfeusz_instance = morfeusz2.Morfeusz()
        return cls._morfeusz_instance

    def extract(self, text: str) -> CandidateProfile:
        lines = [l.strip() for l in text.splitlines() if l.strip()]

        name, surname = self._extract_name_surname(text, lines)

        email = self._find_first(self.EMAIL_RE, text)
        phone = self._find_first(self.PHONE_RE, text)

        return CandidateProfile(
            name=name,
            surname=surname,
            email=email,
            phone_number=phone,
            linkedin_profile=None,
            education=[],
            experience=[],
            skills=[],
        )

    def _extract_name_surname(self, text: str, lines: List[str]) -> Tuple[str, str]:
        name_from_label = self._extract_from_labeled_line(lines)
        if name_from_label:
            return name_from_label

        morf = self._get_morfeusz()
        if morf is not None and lines:
            name_from_morph = self._extract_with_morfeusz(morf, lines)
            if name_from_morph:
                return name_from_morph

        if lines:
            tokens = lines[0].split()
            if len(tokens) >= 2:
                return tokens[0], " ".join(tokens[1:])

        return "Nieznane", "Nieznane"

    def _extract_from_labeled_line(self, lines: List[str]) -> Optional[Tuple[str, str]]:
        for line in lines[:10]:
            m = self.NAME_LINE_RE.search(line)
            if not m:
                continue
            raw = m.group(2).strip()
            tokens = raw.split()
            if len(tokens) >= 2:
                return tokens[0], " ".join(tokens[1:])
        return None

    def _extract_with_morfeusz(
        self, morfeusz, lines: List[str]
    ) -> Optional[Tuple[str, str]]:
        candidate_text = "\n".join(lines[:10])
        analyses = morfeusz.analyse(candidate_text)

        tokens_raw: List[Tuple[str, List[str], List[str], int, int]] = []

        for start, end, analysis in analyses:
            orth, lemma, tag, labels, *rest = analysis
            tokens_raw.append((orth, [tag], labels or [], start, end))

        merged: List[Tuple[str, List[str], List[str]]] = []
        last_pos = None
        temp_orth = ""
        temp_tags: List[str] = []
        temp_labels: List[str] = []

        for orth, tags, labels, start, end in sorted(
            tokens_raw, key=lambda t: (t[3], t[4])
        ):
            pos = (start, end)
            if pos != last_pos:
                if last_pos is not None:
                    merged.append((temp_orth, temp_tags, temp_labels))
                temp_orth = orth
                temp_tags = list(tags)
                temp_labels = list(labels)
                last_pos = pos
            else:
                temp_tags.extend(tags)
                temp_labels.extend(labels)

        if last_pos is not None:
            merged.append((temp_orth, temp_tags, temp_labels))

        def has_label(labels: List[str], value: str) -> bool:
            return any(l.lower() == value for l in labels)

        def is_name_like(orth: str, tags: List[str]) -> bool:
            if not orth or not orth[0].isupper():
                return False
            return any("subst" in t and "nom" in t for t in tags)

        for i in range(len(merged) - 1):
            orth1, tags1, labels1 = merged[i]
            orth2, tags2, labels2 = merged[i + 1]

            if has_label(labels1, "imię") and has_label(labels2, "nazwisko"):
                return orth1, orth2

        for i in range(len(merged) - 1):
            orth1, tags1, labels1 = merged[i]
            orth2, tags2, labels2 = merged[i + 1]

            if is_name_like(orth1, tags1) and is_name_like(orth2, tags2):
                return orth1, orth2

        return None

    @staticmethod
    def _find_first(pattern: re.Pattern, text: str) -> Optional[str]:
        m = pattern.search(text)
        return m.group(0) if m else None
