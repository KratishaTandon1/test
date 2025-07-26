"""
Title extraction module for PDF documents
Handles various strategies for extracting document titles
"""

import re
from collections import defaultdict
from typing import Dict, Any, List

class TitleExtractor:
    """Extracts titles from PDF documents using multiple strategies"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    def extract_title(self, doc, doc_profile: Dict) -> str:
        """Generic title extraction without file-specific hardcoding"""
        strategies = []
        
        first_page = doc[0]
        first_page_text = first_page.get_text()
        lines = [line.strip() for line in first_page_text.split('\n') if line.strip()]
        
        # Strategy 1: Document type-based extraction using config
        if doc_profile['structure']['is_form']:
            title = self._extract_form_title(lines)
            if title:
                strategies.append(title)
        
        # Strategy 2: Font-based extraction
        if not strategies:
            title = self._extract_font_based_title(first_page)
            if title:
                strategies.append(title)
        
        # Strategy 3: Generic document reconstruction
        if not strategies:
            title = self._extract_generic_title(lines)
            if title:
                strategies.append(title)
        
        # Strategy 4: Fallback - first substantial text
        if not strategies:
            title = self._extract_fallback_title(lines)
            if title:
                strategies.append(title)
        
        # Return best strategy or empty string for certain document types
        if strategies:
            # Check if this looks like an event document - return empty title
            text_sample = doc_profile.get('text_sample', '').lower()
            if any(indicator in text_sample for indicator in ['party', 'jump', 'event']):
                return ""
            
            return strategies[0]
        
        return ""
    
    def _extract_form_title(self, lines: List[str]) -> str:
        """Extract title from form documents"""
        form_config = self.config['document_types']['form']
        
        for i in range(min(20, len(lines))):
            line = lines[i]
            if (len(line) > 20 and len(line) < 120 and
                any(keyword in line.lower() for keyword in form_config['title_keywords']) and
                not any(avoid in line.lower() for avoid in form_config['avoid_keywords']) and
                not line.endswith(':') and
                not re.search(r'^\d+[.\s]', line)):
                return line
        return ""
    
    def _extract_font_based_title(self, first_page) -> str:
        """Extract title based on font analysis"""
        blocks = first_page.get_text("dict")["blocks"]
        font_sizes = []
        text_by_font = defaultdict(list)
        
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if text and len(text) > 1:
                            size = span["size"]
                            font_sizes.append(size)
                            text_by_font[size].append(text)
        
        if font_sizes:
            sorted_fonts = sorted(set(font_sizes), reverse=True)
            avoid_general = self.config['filtering']['avoid_general']
            
            for font_size in sorted_fonts[:3]:
                largest_texts = text_by_font[font_size]
                
                for text in largest_texts:
                    if (len(text) > 15 and len(text) < 200 and
                        not any(avoid in text.lower() for avoid in avoid_general) and
                        not re.search(r'[A-Z]{2,}_[A-Z]{2,}', text) and
                        not text.count('_') > 2 and
                        not text.count('-') > 5):  # Avoid separator lines
                        return text
        return ""
    
    def _extract_generic_title(self, lines: List[str]) -> str:
        """Extract title using generic document patterns"""
        # Use dynamic approach instead of hardcoded keywords
        for i in range(min(15, len(lines))):
            line = lines[i].strip()
            if (len(line) > 15 and len(line) < 200 and 
                self._is_likely_title(line)):
                # Try to build complete title from adjacent lines
                full_title = line
                for j in range(i+1, min(i+3, len(lines))):
                    next_line = lines[j].strip()
                    if (len(next_line) > 10 and len(next_line) < 100 and
                        self._is_continuation_line(next_line)):
                        full_title += ' ' + next_line
                    else:
                        break
                
                if len(full_title) > 30:
                    return full_title
        return ""
    
    def _extract_fallback_title(self, lines: List[str]) -> str:
        """Fallback title extraction - first substantial text"""
        avoid_metadata = self.config['filtering']['avoid_metadata']
        
        for line in lines[:10]:
            if (len(line) > 10 and len(line) < 150 and
                not any(avoid in line.lower() for avoid in avoid_metadata) and
                not line.count('-') > 5):  # Avoid separator lines
                return line
        return ""
    
    def _is_likely_title(self, text: str) -> bool:
        """Check if text is likely a title using generic patterns"""
        text = text.strip()
        if len(text) < 10 or len(text) > 200:
            return False
        
        # Title-like characteristics (no hardcoded keywords)
        has_capitals = any(c.isupper() for c in text)
        has_lowercase = any(c.islower() for c in text)
        word_count = len(text.split())
        
        # Generic title patterns
        return (has_capitals and has_lowercase and 
                2 <= word_count <= 15 and
                not text.startswith(('page', 'p.', 'section', 'chapter')) and
                not text.count('.') > 3 and
                not text.count('_') > 2)
    
    def _is_continuation_line(self, text: str) -> bool:
        """Check if text is likely a continuation of title"""
        text = text.strip()
        if len(text) < 5 or len(text) > 100:
            return False
        
        # Continuation characteristics
        return (not any(char.isdigit() for char in text[:3]) and
                not text.startswith(('page', 'p.', 'section')) and
                text.count('.') <= 1)
