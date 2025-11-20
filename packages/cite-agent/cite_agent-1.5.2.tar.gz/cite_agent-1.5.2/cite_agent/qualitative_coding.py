"""
Qualitative Coding Suite - Theme Extraction, Coding, Inter-rater Reliability
============================================================================

Tools for qualitative research: coding transcripts, extracting themes,
organizing quotes, calculating inter-rater reliability (Cohen's kappa, etc.)

The "magical" feature professors need for interview/focus group analysis.
"""

import re
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from collections import defaultdict, Counter
import pandas as pd
import numpy as np


@dataclass
class Code:
    """A qualitative code applied to text"""
    name: str
    description: str
    color: Optional[str] = None  # For visualization
    parent_code: Optional[str] = None  # For hierarchical coding
    examples: List[str] = field(default_factory=list)


@dataclass
class CodedSegment:
    """A segment of text with applied codes"""
    text: str
    codes: List[str]
    source: str  # Document/transcript ID
    line_start: int
    line_end: int
    speaker: Optional[str] = None
    context: Optional[str] = None


class QualitativeCodingAssistant:
    """Assistant for qualitative data analysis"""

    def __init__(self):
        self.codebook: Dict[str, Code] = {}
        self.coded_segments: List[CodedSegment] = []
        self.documents: Dict[str, str] = {}  # doc_id -> full text

    def create_code(
        self,
        name: str,
        description: str,
        parent_code: Optional[str] = None,
        examples: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new code in the codebook

        Args:
            name: Code name (e.g., "uncertainty", "hope", "barrier")
            description: What this code represents
            parent_code: Parent code for hierarchical coding
            examples: Example quotes for this code

        Returns:
            Success status and code info
        """
        if name in self.codebook:
            return {"error": f"Code '{name}' already exists"}

        if parent_code and parent_code not in self.codebook:
            return {"error": f"Parent code '{parent_code}' not found"}

        self.codebook[name] = Code(
            name=name,
            description=description,
            parent_code=parent_code,
            examples=examples or []
        )

        return {
            "success": True,
            "code": name,
            "description": description,
            "parent": parent_code,
            "total_codes": len(self.codebook)
        }

    def load_transcript(
        self,
        doc_id: str,
        text: str,
        format_type: str = "plain"
    ) -> Dict[str, Any]:
        """
        Load a transcript or interview text

        Args:
            doc_id: Unique identifier for this document
            text: Full transcript text
            format_type: "plain", "interview" (with Speaker: format), or "focus_group"

        Returns:
            Document info and speaker extraction
        """
        self.documents[doc_id] = text

        # Extract speakers if interview format
        speakers = []
        if format_type in ["interview", "focus_group"]:
            speaker_pattern = r'^([A-Z][a-zA-Z\s]+):\s'
            speakers = list(set(re.findall(speaker_pattern, text, re.MULTILINE)))

        lines = text.split('\n')

        return {
            "success": True,
            "doc_id": doc_id,
            "lines": len(lines),
            "characters": len(text),
            "speakers": speakers if speakers else None,
            "format": format_type
        }

    def auto_extract_themes(
        self,
        doc_ids: Optional[List[str]] = None,
        min_frequency: int = 3
    ) -> Dict[str, Any]:
        """
        Automatically extract potential themes using keyword analysis

        Args:
            doc_ids: Which documents to analyze (None = all)
            min_frequency: Minimum times a phrase must appear

        Returns:
            Suggested themes with frequencies
        """
        if not doc_ids:
            doc_ids = list(self.documents.keys())

        # Combine all text
        all_text = "\n".join([self.documents[doc_id] for doc_id in doc_ids])

        # Extract n-grams (2-4 words)
        words = re.findall(r'\b[a-z]{3,}\b', all_text.lower())

        # Count bigrams and trigrams
        bigrams = [' '.join(words[i:i+2]) for i in range(len(words)-1)]
        trigrams = [' '.join(words[i:i+3]) for i in range(len(words)-2)]

        bigram_counts = Counter(bigrams)
        trigram_counts = Counter(trigrams)

        # Filter by frequency
        themes = {}

        for phrase, count in bigram_counts.most_common(50):
            if count >= min_frequency:
                # Skip common stopword phrases
                if not any(stop in phrase for stop in ['the ', ' the', ' and ', ' or ', ' to ', ' in ']):
                    themes[phrase] = {
                        "frequency": count,
                        "type": "bigram",
                        "suggested_code": phrase.replace(' ', '_')
                    }

        for phrase, count in trigram_counts.most_common(30):
            if count >= min_frequency:
                if not any(stop in phrase for stop in ['the ', ' the', ' and ', ' or ', ' to ', ' in ']):
                    themes[phrase] = {
                        "frequency": count,
                        "type": "trigram",
                        "suggested_code": phrase.replace(' ', '_')
                    }

        return {
            "success": True,
            "themes_found": len(themes),
            "themes": dict(sorted(themes.items(), key=lambda x: x[1]["frequency"], reverse=True)),
            "documents_analyzed": len(doc_ids)
        }

    def code_segment(
        self,
        doc_id: str,
        line_start: int,
        line_end: int,
        codes: List[str],
        speaker: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Apply codes to a segment of text

        Args:
            doc_id: Document identifier
            line_start: Starting line number (0-indexed)
            line_end: Ending line number (inclusive)
            codes: List of code names to apply
            speaker: Speaker name (if applicable)

        Returns:
            Success status and coded segment
        """
        if doc_id not in self.documents:
            return {"error": f"Document '{doc_id}' not found"}

        # Validate codes exist
        for code in codes:
            if code not in self.codebook:
                return {"error": f"Code '{code}' not in codebook. Create it first."}

        # Extract text segment
        lines = self.documents[doc_id].split('\n')
        if line_start < 0 or line_end >= len(lines):
            return {"error": f"Line range {line_start}-{line_end} out of bounds (doc has {len(lines)} lines)"}

        text = '\n'.join(lines[line_start:line_end+1])

        # Create coded segment
        segment = CodedSegment(
            text=text,
            codes=codes,
            source=doc_id,
            line_start=line_start,
            line_end=line_end,
            speaker=speaker
        )

        self.coded_segments.append(segment)

        return {
            "success": True,
            "segment_id": len(self.coded_segments) - 1,
            "text_preview": text[:100] + "..." if len(text) > 100 else text,
            "codes_applied": codes,
            "total_coded_segments": len(self.coded_segments)
        }

    def get_coded_excerpts(
        self,
        code: str,
        max_excerpts: int = 20
    ) -> Dict[str, Any]:
        """
        Retrieve all excerpts coded with a specific code

        Args:
            code: Code name to filter by
            max_excerpts: Maximum number of excerpts to return

        Returns:
            List of excerpts with this code
        """
        if code not in self.codebook:
            return {"error": f"Code '{code}' not found in codebook"}

        excerpts = []
        for segment in self.coded_segments:
            if code in segment.codes:
                excerpts.append({
                    "text": segment.text,
                    "source": segment.source,
                    "speaker": segment.speaker,
                    "line_range": f"{segment.line_start}-{segment.line_end}",
                    "all_codes": segment.codes
                })

        excerpts = excerpts[:max_excerpts]

        return {
            "success": True,
            "code": code,
            "description": self.codebook[code].description,
            "excerpts_found": len(excerpts),
            "excerpts": excerpts
        }

    def generate_code_frequency_matrix(self) -> Dict[str, Any]:
        """
        Generate frequency matrix of codes across documents

        Returns:
            Matrix showing code counts per document
        """
        if not self.coded_segments:
            return {"error": "No coded segments available"}

        # Build matrix
        doc_ids = sorted(set(s.source for s in self.coded_segments))
        code_names = sorted(self.codebook.keys())

        matrix = pd.DataFrame(0, index=doc_ids, columns=code_names)

        for segment in self.coded_segments:
            for code in segment.codes:
                if code in code_names:
                    matrix.loc[segment.source, code] += 1

        return {
            "success": True,
            "documents": len(doc_ids),
            "codes": len(code_names),
            "total_coded_segments": len(self.coded_segments),
            "matrix": matrix.to_dict(),
            "summary": {
                code: int(matrix[code].sum())
                for code in code_names
            }
        }

    def calculate_inter_rater_reliability(
        self,
        coder1_segments: List[CodedSegment],
        coder2_segments: List[CodedSegment],
        method: str = "cohen_kappa"
    ) -> Dict[str, Any]:
        """
        Calculate inter-rater reliability between two coders

        Args:
            coder1_segments: Coded segments from coder 1
            coder2_segments: Coded segments from coder 2
            method: "cohen_kappa", "percent_agreement", or "krippendorff_alpha"

        Returns:
            Reliability metrics
        """
        # Match segments (assume same doc + line range = same segment)
        def segment_key(seg):
            return (seg.source, seg.line_start, seg.line_end)

        coder1_map = {segment_key(s): set(s.codes) for s in coder1_segments}
        coder2_map = {segment_key(s): set(s.codes) for s in coder2_segments}

        # Find common segments
        common_keys = set(coder1_map.keys()) & set(coder2_map.keys())

        if not common_keys:
            return {"error": "No overlapping segments found between coders"}

        # Calculate percent agreement
        agreements = sum(
            1 for key in common_keys
            if coder1_map[key] == coder2_map[key]
        )
        percent_agreement = (agreements / len(common_keys)) * 100

        # Calculate Cohen's Kappa
        if method == "cohen_kappa":
            # Build agreement matrix for each code
            all_codes = sorted(set(
                code for codes in list(coder1_map.values()) + list(coder2_map.values())
                for code in codes
            ))

            kappa_scores = {}

            for code in all_codes:
                # Binary: did each coder use this code?
                coder1_used = [code in coder1_map.get(key, set()) for key in common_keys]
                coder2_used = [code in coder2_map.get(key, set()) for key in common_keys]

                # Calculate observed agreement
                observed = sum(c1 == c2 for c1, c2 in zip(coder1_used, coder2_used)) / len(common_keys)

                # Calculate expected agreement by chance
                p1_yes = sum(coder1_used) / len(common_keys)
                p2_yes = sum(coder2_used) / len(common_keys)
                expected = (p1_yes * p2_yes) + ((1-p1_yes) * (1-p2_yes))

                # Kappa formula
                if expected < 1.0:
                    kappa = (observed - expected) / (1 - expected)
                else:
                    kappa = 1.0

                kappa_scores[code] = round(kappa, 3)

            # Overall kappa (average)
            overall_kappa = sum(kappa_scores.values()) / len(kappa_scores) if kappa_scores else 0

            # Interpretation
            if overall_kappa < 0.20:
                interpretation = "slight agreement"
            elif overall_kappa < 0.40:
                interpretation = "fair agreement"
            elif overall_kappa < 0.60:
                interpretation = "moderate agreement"
            elif overall_kappa < 0.80:
                interpretation = "substantial agreement"
            else:
                interpretation = "almost perfect agreement"

            return {
                "success": True,
                "method": "Cohen's Kappa",
                "segments_compared": len(common_keys),
                "percent_agreement": round(percent_agreement, 2),
                "overall_kappa": round(overall_kappa, 3),
                "interpretation": interpretation,
                "kappa_by_code": kappa_scores,
                "codes_analyzed": len(all_codes)
            }

        else:  # Percent agreement only
            return {
                "success": True,
                "method": "Percent Agreement",
                "segments_compared": len(common_keys),
                "percent_agreement": round(percent_agreement, 2),
                "perfect_matches": agreements
            }

    def export_codebook(self, format_type: str = "markdown") -> Dict[str, Any]:
        """
        Export codebook in various formats

        Args:
            format_type: "markdown", "csv", or "json"

        Returns:
            Formatted codebook
        """
        if not self.codebook:
            return {"error": "Codebook is empty"}

        if format_type == "markdown":
            md = "# Codebook\n\n"
            for code_name, code in sorted(self.codebook.items()):
                md += f"## {code_name}\n"
                md += f"**Description:** {code.description}\n\n"
                if code.parent_code:
                    md += f"**Parent Code:** {code.parent_code}\n\n"
                if code.examples:
                    md += "**Examples:**\n"
                    for example in code.examples:
                        md += f"- \"{example}\"\n"
                    md += "\n"

            return {
                "success": True,
                "format": "markdown",
                "content": md
            }

        elif format_type == "csv":
            rows = []
            for code_name, code in self.codebook.items():
                rows.append({
                    "Code": code_name,
                    "Description": code.description,
                    "Parent": code.parent_code or "",
                    "Examples": " | ".join(code.examples) if code.examples else ""
                })

            df = pd.DataFrame(rows)

            return {
                "success": True,
                "format": "csv",
                "dataframe": df,
                "preview": df.to_dict('records')
            }

        elif format_type == "json":
            import json
            codebook_dict = {
                name: {
                    "description": code.description,
                    "parent": code.parent_code,
                    "examples": code.examples
                }
                for name, code in self.codebook.items()
            }

            return {
                "success": True,
                "format": "json",
                "content": json.dumps(codebook_dict, indent=2)
            }

        else:
            return {"error": f"Unknown format: {format_type}"}
