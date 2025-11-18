"""
Literature Synthesis AI - Extract Themes Across Papers, Find Gaps
==================================================================

Analyze multiple research papers to:
- Extract common themes and findings
- Identify contradictions/debates
- Find research gaps
- Create synthesis matrices

The "magical" part: Automatically synthesize dozens of papers.
"""

import re
from typing import Dict, Any, List, Optional, Tuple, Set
from collections import Counter, defaultdict
import pandas as pd


class LiteratureSynthesizer:
    """AI-powered literature synthesis for systematic reviews"""

    def __init__(self):
        self.papers: List[Dict[str, Any]] = []
        self.themes: Dict[str, List[str]] = defaultdict(list)  # theme -> paper_ids

    def add_paper(
        self,
        paper_id: str,
        title: str,
        abstract: str,
        year: int,
        authors: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None,
        findings: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a paper to the synthesis

        Args:
            paper_id: Unique identifier
            title: Paper title
            abstract: Abstract text
            year: Publication year
            authors: List of author names
            keywords: Author-provided keywords
            findings: Key findings/conclusion

        Returns:
            Success status
        """
        paper = {
            "id": paper_id,
            "title": title,
            "abstract": abstract,
            "year": year,
            "authors": authors or [],
            "keywords": keywords or [],
            "findings": findings or ""
        }

        self.papers.append(paper)

        return {
            "success": True,
            "paper_id": paper_id,
            "total_papers": len(self.papers)
        }

    def extract_common_themes(
        self,
        min_papers: int = 3,
        theme_length: int = 2
    ) -> Dict[str, Any]:
        """
        Extract common themes across papers using n-gram analysis

        Args:
            min_papers: Minimum number of papers mentioning a theme
            theme_length: Length of n-grams (2=bigrams, 3=trigrams)

        Returns:
            Themes with frequency and supporting papers
        """
        if len(self.papers) < 2:
            return {"error": "Need at least 2 papers for theme extraction"}

        # Combine all abstracts and findings
        all_text = []
        for paper in self.papers:
            text = f"{paper['abstract']} {paper['findings']}"
            all_text.append((paper['id'], text.lower()))

        # Extract n-grams
        theme_papers = defaultdict(set)  # theme -> set of paper_ids

        for paper_id, text in all_text:
            # Tokenize
            words = re.findall(r'\b[a-z]{3,}\b', text)

            # Generate n-grams
            for i in range(len(words) - theme_length + 1):
                ngram = ' '.join(words[i:i+theme_length])

                # Skip common phrases
                if self._is_meaningful_theme(ngram):
                    theme_papers[ngram].add(paper_id)

        # Filter by minimum papers
        common_themes = {
            theme: list(papers)
            for theme, papers in theme_papers.items()
            if len(papers) >= min_papers
        }

        # Sort by frequency
        sorted_themes = sorted(
            common_themes.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )

        return {
            "success": True,
            "themes_found": len(sorted_themes),
            "themes": {
                theme: {
                    "frequency": len(papers),
                    "papers": papers,
                    "coverage_pct": (len(papers) / len(self.papers)) * 100
                }
                for theme, papers in sorted_themes[:30]  # Top 30 themes
            }
        }

    def _is_meaningful_theme(self, phrase: str) -> bool:
        """Filter out common stopword phrases"""
        stopwords = [
            'the ', ' the', ' and ', ' or ', ' to ', ' in ', ' of ',
            ' for ', ' with ', ' on ', ' at ', ' by ', ' from ',
            'this study', 'our study', 'our findings', 'we found',
            'results show', 'data show', 'research shows'
        ]

        return not any(stop in phrase for stop in stopwords)

    def identify_research_gaps(self) -> Dict[str, Any]:
        """
        Identify potential research gaps based on:
        - Understudied topics
        - Missing methodologies
        - Contradictory findings

        Returns:
            List of potential research gaps
        """
        if len(self.papers) < 5:
            return {"error": "Need at least 5 papers to identify meaningful gaps"}

        gaps = []

        # Gap 1: Temporal gaps (under-researched time periods)
        years = [p['year'] for p in self.papers if p['year']]
        if years:
            year_counts = Counter(years)
            recent_years = [y for y in range(max(years) - 5, max(years) + 1)]
            understudied_years = [y for y in recent_years if year_counts.get(y, 0) < 2]

            if understudied_years:
                gaps.append({
                    "type": "temporal",
                    "description": f"Limited research in recent years: {understudied_years}",
                    "suggestion": f"Conduct updated research for {min(understudied_years)}-{max(understudied_years)}"
                })

        # Gap 2: Methodological gaps
        methods = defaultdict(int)
        method_keywords = ['qualitative', 'quantitative', 'mixed methods', 'experiment', 'survey', 'interview', 'case study', 'longitudinal']

        for paper in self.papers:
            text = f"{paper['abstract']} {paper['findings']}".lower()
            for method in method_keywords:
                if method in text:
                    methods[method] += 1

        total_papers = len(self.papers)
        underused_methods = [
            method for method, count in methods.items()
            if count < total_papers * 0.2  # Less than 20% of papers
        ]

        if underused_methods:
            gaps.append({
                "type": "methodological",
                "description": f"Underused methods: {', '.join(underused_methods)}",
                "suggestion": f"Consider {underused_methods[0]} approach to complement existing research"
            })

        # Gap 3: Theme coverage gaps (themes mentioned but not deeply studied)
        theme_analysis = self.extract_common_themes(min_papers=2, theme_length=2)
        if "themes" in theme_analysis:
            moderate_themes = [
                theme for theme, data in theme_analysis["themes"].items()
                if 20 < data["coverage_pct"] < 50
            ]

            if moderate_themes:
                gaps.append({
                    "type": "thematic",
                    "description": f"Emerging but understudied themes: {', '.join(moderate_themes[:5])}",
                    "suggestion": f"In-depth investigation of '{moderate_themes[0]}' could fill gap"
                })

        # Gap 4: Geographic/contextual gaps (if mentioned)
        contexts = defaultdict(int)
        context_keywords = ['united states', 'europe', 'asia', 'africa', 'developing', 'developed', 'rural', 'urban']

        for paper in self.papers:
            text = f"{paper['abstract']} {paper['findings']}".lower()
            for context in context_keywords:
                if context in text:
                    contexts[context] += 1

        if contexts:
            underrep_contexts = [
                ctx for ctx, count in contexts.items()
                if count < total_papers * 0.15
            ]

            if underrep_contexts:
                gaps.append({
                    "type": "contextual",
                    "description": f"Underrepresented contexts: {', '.join(underrep_contexts)}",
                    "suggestion": f"Replicate studies in {underrep_contexts[0]} context"
                })

        return {
            "success": True,
            "gaps_identified": len(gaps),
            "gaps": gaps
        }

    def create_synthesis_matrix(
        self,
        dimensions: List[str]
    ) -> Dict[str, Any]:
        """
        Create a synthesis matrix comparing papers across dimensions

        Args:
            dimensions: Aspects to compare (e.g., ["method", "sample_size", "findings"])

        Returns:
            Matrix comparing papers
        """
        if not self.papers:
            return {"error": "No papers loaded"}

        matrix_data = []

        for paper in self.papers:
            row = {
                "paper_id": paper["id"],
                "title": paper["title"][:50] + "..." if len(paper["title"]) > 50 else paper["title"],
                "year": paper["year"],
                "authors": paper["authors"][0] if paper["authors"] else "Unknown"
            }

            # Extract dimension values from abstract/findings
            text = f"{paper['abstract']} {paper['findings']}".lower()

            for dimension in dimensions:
                if dimension == "method":
                    row["method"] = self._extract_method(text)
                elif dimension == "sample_size":
                    row["sample_size"] = self._extract_sample_size(text)
                elif dimension == "findings":
                    row["findings"] = self._extract_key_finding(paper['findings'] or paper['abstract'])
                elif dimension == "population":
                    row["population"] = self._extract_population(text)
                else:
                    # Generic extraction
                    row[dimension] = "Not specified"

            matrix_data.append(row)

        df = pd.DataFrame(matrix_data)

        return {
            "success": True,
            "papers": len(matrix_data),
            "dimensions": dimensions,
            "matrix": df.to_dict('records'),
            "dataframe": df
        }

    def _extract_method(self, text: str) -> str:
        """Extract research method from text"""
        methods = {
            "experimental": ["experiment", "randomized", "rct", "controlled trial"],
            "survey": ["survey", "questionnaire"],
            "qualitative": ["interview", "focus group", "ethnography", "qualitative"],
            "longitudinal": ["longitudinal", "panel study", "repeated measures"],
            "case_study": ["case study"],
            "meta_analysis": ["meta-analysis", "systematic review"]
        }

        for method, keywords in methods.items():
            if any(kw in text for kw in keywords):
                return method

        return "Not specified"

    def _extract_sample_size(self, text: str) -> str:
        """Extract sample size from text"""
        # Look for patterns like "n=100", "N = 200", "sample of 150"
        patterns = [
            r'n\s*=\s*(\d+)',
            r'N\s*=\s*(\d+)',
            r'sample of (\d+)',
            r'(\d+) participants',
            r'(\d+) respondents'
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return f"n={match.group(1)}"

        return "Not specified"

    def _extract_key_finding(self, text: str) -> str:
        """Extract key finding from text"""
        # Look for conclusion/finding sentences
        sentences = text.split('.')

        # Prioritize sentences with finding keywords
        finding_keywords = ['found', 'showed', 'demonstrated', 'revealed', 'indicated', 'suggest']

        for sentence in sentences:
            if any(kw in sentence.lower() for kw in finding_keywords):
                return sentence.strip()[:150]

        # Fallback: return first sentence of findings
        return sentences[0].strip()[:150] if sentences else "Not available"

    def _extract_population(self, text: str) -> str:
        """Extract study population from text"""
        populations = {
            "students": ["student", "undergraduate", "college"],
            "adults": ["adult", "men and women"],
            "children": ["child", "adolescent", "youth"],
            "elderly": ["elderly", "older adult", "senior"],
            "patients": ["patient", "clinical"],
            "professionals": ["professional", "employee", "worker"]
        }

        for pop, keywords in populations.items():
            if any(kw in text for kw in keywords):
                return pop

        return "General population"

    def find_contradictory_findings(self) -> Dict[str, Any]:
        """
        Identify papers with contradictory findings on similar topics

        Returns:
            Potential contradictions/debates in the literature
        """
        if len(self.papers) < 3:
            return {"error": "Need at least 3 papers to detect contradictions"}

        # Keywords indicating contradictions
        positive_keywords = ['increase', 'improve', 'positive', 'benefit', 'enhance', 'effective']
        negative_keywords = ['decrease', 'reduce', 'negative', 'harm', 'ineffective', 'no effect']

        # Group papers by theme
        theme_analysis = self.extract_common_themes(min_papers=2, theme_length=2)

        contradictions = []

        if "themes" in theme_analysis:
            for theme, data in theme_analysis["themes"].items():
                if data["frequency"] < 2:
                    continue

                # Check if papers on this theme have opposite findings
                theme_papers = [p for p in self.papers if p["id"] in data["papers"]]

                positive_papers = []
                negative_papers = []

                for paper in theme_papers:
                    text = f"{paper['findings']} {paper['abstract']}".lower()

                    pos_count = sum(1 for kw in positive_keywords if kw in text)
                    neg_count = sum(1 for kw in negative_keywords if kw in text)

                    if pos_count > neg_count:
                        positive_papers.append(paper["id"])
                    elif neg_count > pos_count:
                        negative_papers.append(paper["id"])

                if positive_papers and negative_papers:
                    contradictions.append({
                        "theme": theme,
                        "positive_papers": positive_papers,
                        "negative_papers": negative_papers,
                        "description": f"Conflicting findings on '{theme}': {len(positive_papers)} positive vs {len(negative_papers)} negative"
                    })

        return {
            "success": True,
            "contradictions_found": len(contradictions),
            "contradictions": contradictions[:10]  # Top 10
        }
