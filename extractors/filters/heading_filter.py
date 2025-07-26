"""
Heading filtering module for PDF extraction
Removes noise and false positives from heading candidates
"""

import re
from typing import List, Dict, Set

class HeadingFilter:
    """Filters heading candidates to remove noise and false positives"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.noise_patterns = set(self.config['filtering']['noise_patterns'])
    
    def filter_candidates(self, candidates: List[Dict], doc_profile: Dict) -> List[Dict]:
        """Apply filtering based on document analysis with improved accuracy"""
        if not candidates:
            return []
        
        filtered = []
        seen_texts = set()
        
        for candidate in candidates:
            text = candidate['text'].strip()
            text_lower = text.lower()
            
            # Skip if already seen (exact match)
            if text in seen_texts:
                continue
            
            # Enhanced noise detection
            if self._is_noise_text(text) or self._is_unlikely_heading(text):
                continue
            
            # Skip very short fragments (likely split text)
            if len(text) < 8:  # Increased from 5 to be more selective
                continue
            
            # Skip text that looks like fragments using configurable threshold
            words = text.split()
            min_word_length = self.config['extraction']['text_limits']['min_word_avg_length']
            if len(words) > 1:
                avg_word_length = sum(len(word) for word in words) / len(words)
                if avg_word_length < min_word_length:
                    continue
            
            # Enhanced document-specific filtering using configuration
            if not self._passes_document_filters(text, text_lower, doc_profile):
                continue
            
            # Enhanced quality checks
            if (self._has_good_heading_structure(text) and
                not self._is_repetitive_content(text, seen_texts) and
                self._is_likely_heading_content(text)):
                
                filtered.append(candidate)
                seen_texts.add(text)
        
        return filtered
    
    def _passes_document_filters(self, text: str, text_lower: str, doc_profile: Dict) -> bool:
        """Apply document-specific filtering rules"""
        text_limits = self.config['extraction']['text_limits']
        
        if doc_profile['structure']['is_form']:
            form_config = self.config['document_types']['form']
            if (len(text) < text_limits['min_text_length'] or 
                len(text) > text_limits['max_form_heading'] or
                ':' in text or 
                any(field in text_lower for field in form_config['avoid_fields'])):
                return False
        
        elif doc_profile['structure']['is_academic']:
            academic_config = self.config['document_types']['academic']
            if (len(text) < text_limits['min_text_length'] or 
                len(text) > text_limits['max_academic_heading'] or
                text.count('.') > academic_config['max_dots']):
                return False
        
        elif doc_profile['structure']['is_technical']:
            tech_config = self.config['document_types']['technical']
            if (len(text) < text_limits['min_text_length'] or 
                len(text) > text_limits['max_technical_heading'] or
                text.count('(') > tech_config['max_parentheses']):
                return False
        
        else:
            # Enhanced generic filtering for simple documents
            simple_config = self.config['document_types']['simple']
            if (len(text) < text_limits['min_text_length'] or 
                len(text) > text_limits['max_simple_heading'] or
                text.count('(') > 2 or
                text.count('_') > simple_config['max_underscores'] or
                any(pattern in text_lower for pattern in simple_config['avoid_patterns'])):
                return False
        
        return True
    
    def _is_noise_text(self, text: str) -> bool:
        """Check if text matches noise patterns"""
        text_clean = text.strip()
        
        for pattern in self.noise_patterns:
            if re.match(pattern, text_clean, re.IGNORECASE):
                return True
        
        # Generic noise checks based on configuration
        filter_config = self.config['filtering']
        if (len(text_clean) < filter_config['min_unique_chars'] or
            text_clean.count(' ') / max(1, len(text_clean)) > filter_config['max_space_ratio'] or
            len(set(text_clean)) < filter_config['min_unique_chars']):
            return True
        
        return False
    
    def _is_unlikely_heading(self, text: str) -> bool:
        """Enhanced check for text unlikely to be a heading"""
        text_clean = text.strip()
        text_lower = text_clean.lower()
        
        # Sentences starting with common sentence starters
        sentence_starters = [
            'those', 'these', 'this', 'that', 'when', 'where', 'while', 'during',
            'after', 'before', 'since', 'until', 'although', 'however', 'therefore',
            'moreover', 'furthermore', 'in addition', 'for example', 'such as'
        ]
        
        if any(text_lower.startswith(starter) for starter in sentence_starters):
            return True
        
        # Long sentences (likely body text)
        if len(text_clean) > 120 and '.' in text_clean:
            return True
        
        # Version/date patterns
        if re.search(r'\b(version|v\d+|\d{4}|\d+/\d+|\d+-\d+)\b', text_lower):
            return True
        
        # Page numbers and references
        if re.search(r'\bpage\s+\d+|\bp\.\s*\d+|\bpp\.\s*\d+', text_lower):
            return True
        
        # Legal/contract language patterns (generic detection)
        if (text_lower.count(' be ') > 1 or 
            text_lower.count(' shall ') > 0 or
            text_lower.count(' must ') > 0 or
            text_lower.count(' will ') > 1):
            return True
        
        # Multiple sentences (body text)
        if text_clean.count('.') > 1 and len(text_clean) > 50:
            return True
        
        return False
    
    def _has_good_heading_structure(self, text: str) -> bool:
        """Check if text has good heading structure"""
        # Should start with letter or number
        if not text[0].isalnum():
            return False
        
        # Should not be all caps unless short
        max_caps_length = self.config['extraction']['font_thresholds']['max_caps_length']
        if text.isupper() and len(text) > max_caps_length:
            return False
        
        # Should not end with punctuation except colon
        if text.endswith(('.', '!', '?')):
            return False
        
        return True
    
    def _is_repetitive_content(self, text: str, seen_texts: Set[str]) -> bool:
        """Check if content is repetitive or similar to already seen"""
        text_lower = text.lower()
        
        for seen in seen_texts:
            seen_lower = seen.lower()
            # If 80% similar, consider repetitive
            if (len(set(text_lower.split()) & set(seen_lower.split())) / 
                max(1, len(set(text_lower.split()) | set(seen_lower.split()))) > 0.8):
                return True
        
        return False
    
    def _is_likely_heading_content(self, text: str) -> bool:
        """Check if content is likely to be a heading based on semantic patterns"""
        text_lower = text.lower()
        
        # Common heading patterns
        heading_patterns = [
            r'^\d+\.?\s+[a-z]',  # Numbered sections
            r'^[a-z]+\s+(overview|introduction|summary|conclusion)',  # Section types
            r'^(overview|introduction|background|summary|conclusion|references)',  # Standard sections
            r'^chapter\s+\d+',  # Chapters
            r'^section\s+\d+',  # Sections
            r'^appendix\s+[a-z]',  # Appendices
        ]
        
        for pattern in heading_patterns:
            if re.search(pattern, text_lower):
                return True
        
        # Short, descriptive phrases (likely headings)
        words = text.split()
        if len(words) <= 6 and len(text) <= 80:
            # Check if it's descriptive rather than instructional
            if not any(word in text_lower for word in ['will', 'shall', 'must', 'should', 'can', 'may']):
                return True
        
        return False
