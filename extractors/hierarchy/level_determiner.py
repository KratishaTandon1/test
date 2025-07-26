"""
Heading level determination module
Determines heading levels using multiple signals beyond font size
"""

import re
from typing import List, Dict, Any

class LevelDeterminer:
    """Determines heading levels using multiple signals"""
    
    def __init__(self, config: Dict):
        self.config = config
    
    def build_hierarchy(self, candidates: List[Dict]) -> List[Dict[str, Any]]:
        """Build proper heading hierarchy using multiple signals"""
        if not candidates:
            return []
        
        # Sort by page, then by y-position
        candidates.sort(key=lambda x: (x['page'], x['bbox'][1] if x['bbox'] else 0))
        
        # Analyze multiple factors for heading level determination
        structured = []
        for candidate in candidates:
            level = self._determine_heading_level(candidate, candidates)
            
            structured.append({
                "level": level,
                "text": candidate['text'],
                "page": candidate['page'] - 1  # Convert to 0-based for consistency
            })
        
        return structured
    
    def _determine_heading_level(self, candidate: Dict, all_candidates: List[Dict]) -> str:
        """Determine heading level using multiple signals beyond font size"""
        text = candidate['text']
        size = candidate['size']
        bold = candidate.get('bold', False)
        
        # Factor 1: Structural patterns (most reliable)
        structural_level = self._get_structural_level(text)
        if structural_level:
            return structural_level
        
        # Factor 2: Content-based patterns
        content_level = self._get_content_based_level(text)
        if content_level:
            return content_level
        
        # Factor 3: Position and context analysis
        position_level = self._get_position_based_level(candidate)
        if position_level:
            return position_level
        
        # Factor 4: Combined scoring approach
        return self._get_score_based_level(candidate, all_candidates)
    
    def _get_structural_level(self, text: str) -> str:
        """Get level based on structural patterns like numbering"""
        # Check for numbered section patterns
        if re.match(r'^\d+\.\s+[A-Z]', text):  # "1. Introduction"
            return "H1"
        elif re.match(r'^\d+\.\d+\s+[A-Z]', text):  # "1.1 Overview"
            return "H2"
        elif re.match(r'^\d+\.\d+\.\d+\s+[A-Z]', text):  # "1.1.1 Details"
            return "H3"
        
        # Check for lettered sections
        if re.match(r'^[A-Z]\.\s+[A-Z]', text):  # "A. Section"
            return "H2"
        
        # Check for roman numerals
        if re.match(r'^[IVX]+\.\s+[A-Z]', text):  # "I. Introduction"
            return "H1"
        
        return ""
    
    def _get_content_based_level(self, text: str) -> str:
        """Get level based on content keywords"""
        text_lower = text.lower()
        
        # Document structure keywords suggest main sections
        main_section_keywords = [
            'introduction', 'overview', 'background', 'conclusion', 'summary',
            'methodology', 'results', 'discussion', 'references', 'appendix'
        ]
        
        if any(keyword in text_lower for keyword in main_section_keywords):
            return "H1"
        
        # Table of contents, revision history are typically H2
        toc_keywords = ['table of contents', 'contents', 'revision history', 'references']
        if any(keyword in text_lower for keyword in toc_keywords):
            return "H2"
        
        return ""
    
    def _get_position_based_level(self, candidate: Dict) -> str:
        """Get level based on position in document"""
        # Very early headings in document are likely major sections
        if candidate['page'] <= 2 and len(candidate['text']) < 50:
            return "H1"
        
        return ""
    
    def _get_score_based_level(self, candidate: Dict, all_candidates: List[Dict]) -> str:
        """Get level using combined scoring approach"""
        text = candidate['text']
        size = candidate['size']
        bold = candidate.get('bold', False)
        
        # Font analysis (as backup, not primary)
        font_sizes = [c['size'] for c in all_candidates]
        unique_sizes = sorted(set(font_sizes), reverse=True)
        
        # Combined scoring approach
        score = 0
        
        # Size contribution (reduced weight)
        if size in unique_sizes[:1]:
            score += 3
        elif size in unique_sizes[1:2]:
            score += 2
        elif size in unique_sizes[2:3]:
            score += 1
        
        # Bold contribution
        if bold:
            score += 2
        
        # Length contribution (shorter = more likely to be heading)
        if len(text) < 20:
            score += 2
        elif len(text) < 40:
            score += 1
        
        # Position contribution (earlier = more likely major section)
        if candidate['page'] <= 3:
            score += 1
        
        # Capitalization pattern
        if text.istitle() or (len(text.split()) <= 3 and text.isupper()):
            score += 1
        
        # Convert score to level
        if score >= 6:
            return "H1"
        elif score >= 4:
            return "H2"
        else:
            return "H3"
