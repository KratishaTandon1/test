"""
Document analysis module for PDF extra        
        # Document type detection
        text_lower = total_text.lower()
        
        # Business document detection
        business_config = self.config['document_types']['business']
        business_indicators = business_config['indicators']
        structure_indicators['is_business'] = sum(1 for indicator in business_indicators 
                                                if indicator in text_lower) >= business_config['min_indicators']
        
        # Form document detection
        form_config = self.config['document_types']['form']
        form_indicators = form_config['indicators']
        structure_indicators['is_form'] = sum(1 for indicator in form_indicators 
                                            if indicator in text_lower) >= form_config['min_indicators']
        
        # Academic document detection
        academic_config = self.config['document_types']['academic']
Handles document profiling and type detection
"""

import re
from collections import defaultdict
from typing import Dict, Any

class DocumentAnalyzer:
    """Analyzes PDF documents to determine type and characteristics"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    def analyze_document(self, doc) -> Dict[str, Any]:
        """Analyze document structure and content to create a profile"""
        structure_indicators = {}
        total_text = ""
        font_stats = defaultdict(int)
        
        # Quick scan of first few pages for analysis
        for page_num in range(min(3, len(doc))):
            page = doc[page_num]
            page_text = ""
            
            # Extract text and font information
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        line_text = ""
                        for span in line["spans"]:
                            text = span["text"].strip()
                            if text:
                                line_text += text + " "
                                font_key = f"{span['font']}_{span['size']:.1f}"
                                font_stats[font_key] += len(text)
                        
                        if line_text.strip():
                            page_text += line_text.strip() + "\n"
            
            total_text += page_text
        
        # Document type detection
        text_lower = total_text.lower()
        
        # Form detection
        form_config = self.config['document_types']['form']
        form_indicators = form_config['indicators']
        structure_indicators['is_form'] = sum(1 for indicator in form_indicators 
                                            if indicator in text_lower) >= form_config['min_indicators']
        
        # Academic detection
        academic_config = self.config['document_types']['academic']
        academic_indicators = academic_config['indicators']
        structure_indicators['is_academic'] = sum(1 for indicator in academic_indicators 
                                                if indicator in text_lower) >= academic_config['min_indicators']
        
        # Technical document detection
        tech_config = self.config['document_types']['technical']
        tech_indicators = tech_config['indicators']
        structure_indicators['is_technical'] = sum(1 for indicator in tech_indicators 
                                                 if indicator in text_lower) >= tech_config['min_indicators']
        
        # TOC detection
        structure_indicators['has_toc'] = any(phrase in text_lower for phrase in 
                                            ['table of contents', 'contents'])
        
        # Numbered sections detection
        structure_indicators['has_numbered_sections'] = bool(
            re.search(r'\b\d+\.\d+\s+[A-Z]', total_text)
        )
        
        structure_indicators['avg_text_per_page'] = len(total_text) / max(1, min(3, len(doc)))
        structure_indicators['font_variety'] = len(font_stats)
        
        return {
            'text_sample': total_text[:1000],
            'font_stats': dict(font_stats),
            'structure': structure_indicators,
            'page_count': len(doc)
        }
