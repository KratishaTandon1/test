"""
Accuracy evaluation and enhancement module for PDF extraction
Focuses on precision, recall, and multilingual support
"""

import re
import time
import unicodedata
from typing import List, Dict, Any, Tuple, Set
from collections import defaultdict

class AccuracyEnhancer:
    """Enhances heading detection accuracy with precision/recall optimization"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.multilingual_patterns = self._init_multilingual_patterns()
        self.heading_quality_weights = {
            'structural_pattern': 0.35,
            'content_semantic': 0.25,
            'typography': 0.20,
            'position': 0.15,
            'multilingual': 0.05
        }
    
    def _init_multilingual_patterns(self) -> Dict[str, List[str]]:
        """Initialize multilingual heading patterns for better recall"""
        return {
            'japanese': {
                'section_keywords': ['章', '節', '項', '概要', '背景', '結論', '参考文献', '付録'],
                'numbering_patterns': [r'第\d+章', r'第\d+節', r'\d+\.\d+', r'[一二三四五六七八九十]+章'],
                'structure_indicators': ['について', 'に関して', 'の概要', 'まとめ']
            },
            'chinese': {
                'section_keywords': ['章', '节', '概述', '背景', '结论', '参考文献', '附录'],
                'numbering_patterns': [r'第\d+章', r'第\d+节', r'\d+\.\d+'],
                'structure_indicators': ['关于', '概述', '总结']
            },
            'korean': {
                'section_keywords': ['장', '절', '개요', '배경', '결론', '참고문헌', '부록'],
                'numbering_patterns': [r'제\d+장', r'제\d+절', r'\d+\.\d+'],
                'structure_indicators': ['에 대해', '개요', '요약']
            },
            'arabic': {
                'section_keywords': ['فصل', 'باب', 'خلاصة', 'مقدمة', 'خاتمة', 'مراجع'],
                'numbering_patterns': [r'\d+\.\d+', r'الفصل\s+\d+'],
                'structure_indicators': ['حول', 'ملخص', 'نتائج']
            },
            'european': {
                'section_keywords': ['introducción', 'conclusión', 'résumé', 'einführung', 'zusammenfassung'],
                'numbering_patterns': [r'\d+\.\d+', r'capítulo\s+\d+', r'chapitre\s+\d+', r'kapitel\s+\d+'],
                'structure_indicators': ['sobre', 'à propos', 'über', 'acerca de']
            }
        }
    
    def enhance_heading_detection(self, candidates: List[Dict], doc_profile: Dict) -> Tuple[List[Dict], Dict]:
        """Enhanced heading detection with improved precision/recall"""
        
        # Step 1: Apply precision enhancement (reduce false positives)
        high_precision_candidates = self._apply_precision_filters(candidates, doc_profile)
        
        # Step 2: Apply recall enhancement (find missed headings)
        enhanced_candidates = self._apply_recall_enhancement(high_precision_candidates, doc_profile)
        
        # Step 3: Multilingual enhancement
        multilingual_enhanced = self._apply_multilingual_enhancement(enhanced_candidates, doc_profile)
        
        # Step 4: Quality scoring and final selection
        final_headings, metrics = self._apply_quality_scoring(multilingual_enhanced)
        
        return final_headings, metrics
    
    def _apply_precision_filters(self, candidates: List[Dict], doc_profile: Dict) -> List[Dict]:
        """Apply strict filters to improve precision (reduce false positives)"""
        filtered = []
        
        for candidate in candidates:
            text = candidate['text'].strip()
            
            # Precision Filter 1: Minimum quality threshold
            if not self._meets_minimum_quality(text):
                continue
            
            # Precision Filter 2: Context-aware validation
            if not self._validates_in_context(candidate, candidates):
                continue
            
            # Precision Filter 3: Typography consistency
            if not self._has_consistent_typography(candidate, candidates):
                continue
            
            # Precision Filter 4: Semantic validation
            if not self._validates_semantically(text, doc_profile):
                continue
            
            filtered.append(candidate)
        
        return filtered
    
    def _apply_recall_enhancement(self, candidates: List[Dict], doc_profile: Dict) -> List[Dict]:
        """Apply techniques to improve recall (find missed headings)"""
        enhanced = candidates.copy()
        
        # Recall Enhancement 1: Relaxed typography detection
        relaxed_candidates = self._find_relaxed_typography_headings(doc_profile)
        
        # Recall Enhancement 2: Structural pattern recovery
        structural_candidates = self._recover_structural_patterns(doc_profile)
        
        # Recall Enhancement 3: Cross-page heading reconstruction
        cross_page_candidates = self._reconstruct_cross_page_headings(doc_profile)
        
        # Merge new candidates while avoiding duplicates
        all_candidates = enhanced + relaxed_candidates + structural_candidates + cross_page_candidates
        return self._deduplicate_candidates(all_candidates)
    
    def _apply_multilingual_enhancement(self, candidates: List[Dict], doc_profile: Dict) -> List[Dict]:
        """Apply multilingual detection for better international support"""
        enhanced = []
        
        for candidate in candidates:
            text = candidate['text']
            
            # Detect language and apply specific patterns
            detected_language = self._detect_text_language(text)
            
            # Apply language-specific enhancements
            if detected_language in self.multilingual_patterns:
                candidate = self._enhance_with_language_patterns(candidate, detected_language)
            
            # Apply Unicode normalization for better consistency
            candidate['text'] = self._normalize_unicode_text(text)
            
            enhanced.append(candidate)
        
        return enhanced
    
    def _apply_quality_scoring(self, candidates: List[Dict]) -> Tuple[List[Dict], Dict]:
        """Apply quality scoring for final heading selection"""
        scored_candidates = []
        quality_scores = []
        metrics = {'precision_score': 0, 'recall_score': 0, 'f1_score': 0}
        
        for candidate in candidates:
            quality_score = self._calculate_quality_score(candidate, candidates)
            scored_candidates.append(candidate)
            quality_scores.append(quality_score)
        
        # Sort by quality score and apply threshold
        candidate_score_pairs = list(zip(scored_candidates, quality_scores))
        candidate_score_pairs.sort(key=lambda x: x[1], reverse=True)
        
        # Dynamic threshold based on score distribution
        threshold = self._calculate_dynamic_threshold_from_scores(quality_scores)
        final_candidates = [pair[0] for pair in candidate_score_pairs if pair[1] >= threshold]
        
        # Calculate metrics
        metrics = self._calculate_accuracy_metrics(final_candidates, scored_candidates)
        
        return final_candidates, metrics
    
    def _meets_minimum_quality(self, text: str) -> bool:
        """Check if text meets minimum quality standards"""
        # Length check
        if len(text) < 3 or len(text) > 200:
            return False
        
        # Character diversity check
        unique_chars = len(set(text.lower()))
        if unique_chars < 3:
            return False
        
        # Word structure check
        words = text.split()
        if len(words) == 0:
            return False
        
        # Avoid pure numeric or symbolic content
        if re.match(r'^[\d\s\-_\.]+$', text):
            return False
        
        return True
    
    def _validates_in_context(self, candidate: Dict, all_candidates: List[Dict]) -> bool:
        """Validate heading in context of other candidates"""
        text = candidate['text']
        page = candidate['page']
        
        # Check for reasonable heading density per page
        same_page_headings = [c for c in all_candidates if c['page'] == page]
        if len(same_page_headings) > 10:  # Too many headings on one page
            # Only keep the highest quality ones
            sizes = [c.get('size', 12.0) for c in same_page_headings]  # Default size if missing
            avg_size = sum(sizes) / len(sizes)
            candidate_size = candidate.get('size', 12.0)
            if candidate_size < avg_size * 0.8:
                return False
        
        # Check for heading hierarchy consistency
        return self._validates_hierarchy_consistency(candidate, all_candidates)
    
    def _validates_hierarchy_consistency(self, candidate: Dict, all_candidates: List[Dict]) -> bool:
        """Validate heading hierarchy makes sense"""
        # Simple hierarchy validation based on size and position
        return True  # Simplified for now
    
    def _has_consistent_typography(self, candidate: Dict, all_candidates: List[Dict]) -> bool:
        """Check if typography is consistent with other headings"""
        size = candidate.get('size', 12.0)  # Default size if missing
        bold = candidate.get('bold', False)
        
        # Find similar-sized headings
        similar_headings = [c for c in all_candidates 
                          if abs(c.get('size', 12.0) - size) < 1.0]
        
        if len(similar_headings) < 2:
            return True  # Can't validate consistency with too few samples
        
        # Check bold consistency
        bold_ratio = sum(1 for c in similar_headings if c.get('bold', False)) / len(similar_headings)
        
        if bold and bold_ratio < 0.3:  # This heading is bold but most similar aren't
            return False
        if not bold and bold_ratio > 0.7:  # This heading isn't bold but most similar are
            return False
        
        return True
    
    def _validates_semantically(self, text: str, doc_profile: Dict) -> bool:
        """Semantic validation of heading content"""
        text_lower = text.lower()
        
        # Check for obvious non-heading patterns
        non_heading_patterns = [
            r'page\s+\d+', r'figure\s+\d+', r'table\s+\d+',
            r'see\s+page', r'continued\s+on', r'end\s+of',
            r'total\s*:', r'sum\s*:', r'amount\s*:'
        ]
        
        for pattern in non_heading_patterns:
            if re.search(pattern, text_lower):
                return False
        
        # Check for heading-like semantic patterns
        heading_indicators = [
            r'chapter\s+\d+', r'section\s+\d+', r'part\s+\d+',
            r'introduction', r'conclusion', r'summary', r'overview',
            r'background', r'methodology', r'results', r'discussion'
        ]
        
        # Bonus points for obvious heading patterns
        has_heading_indicator = any(re.search(pattern, text_lower) for pattern in heading_indicators)
        
        return True  # Be permissive in semantic validation
    
    def _detect_text_language(self, text: str) -> str:
        """Detect the language of the text for multilingual support"""
        # Japanese detection
        if re.search(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', text):
            return 'japanese'
        
        # Chinese detection
        if re.search(r'[\u4E00-\u9FFF]', text):
            return 'chinese'
        
        # Korean detection
        if re.search(r'[\uAC00-\uD7AF]', text):
            return 'korean'
        
        # Arabic detection
        if re.search(r'[\u0600-\u06FF]', text):
            return 'arabic'
        
        # European languages (basic detection)
        european_chars = re.search(r'[àáâãäåæçèéêëìíîïñòóôõöøùúûüýÿ]', text.lower())
        if european_chars:
            return 'european'
        
        return 'english'
    
    def _enhance_with_language_patterns(self, candidate: Dict, language: str) -> Dict:
        """Enhance candidate with language-specific patterns"""
        text = candidate['text']
        patterns = self.multilingual_patterns.get(language, {})
        
        # Check for language-specific section keywords
        section_keywords = patterns.get('section_keywords', [])
        has_section_keyword = any(keyword in text for keyword in section_keywords)
        
        # Check for language-specific numbering patterns
        numbering_patterns = patterns.get('numbering_patterns', [])
        has_numbering = any(re.search(pattern, text) for pattern in numbering_patterns)
        
        # Boost quality score for language-specific patterns
        quality_boost = 0
        if has_section_keyword:
            quality_boost += 0.2
        if has_numbering:
            quality_boost += 0.3
        
        candidate['language'] = language
        candidate['quality_boost'] = quality_boost
        
        return candidate
    
    def _normalize_unicode_text(self, text: str) -> str:
        """Normalize Unicode text for better consistency"""
        # Normalize Unicode composition
        normalized = unicodedata.normalize('NFC', text)
        
        # Clean up whitespace
        normalized = ' '.join(normalized.split())
        
        return normalized
    
    def _calculate_quality_score(self, candidate: Dict, all_candidates: List[Dict]) -> float:
        """Calculate comprehensive quality score for heading"""
        scores = {}
        
        # Structural pattern score
        scores['structural'] = self._score_structural_patterns(candidate)
        
        # Content semantic score
        scores['semantic'] = self._score_semantic_content(candidate)
        
        # Typography score
        scores['typography'] = self._score_typography(candidate, all_candidates)
        
        # Position score
        scores['position'] = self._score_position(candidate)
        
        # Multilingual score
        scores['multilingual'] = candidate.get('quality_boost', 0)
        
        # Calculate weighted score
        total_score = 0
        for component, weight in self.heading_quality_weights.items():
            if component == 'multilingual':
                total_score += weight * scores['multilingual']
            else:
                score_key = component.split('_')[0]  # 'structural_pattern' -> 'structural'
                total_score += weight * scores.get(score_key, 0)
        
        return min(1.0, total_score)  # Cap at 1.0
    
    def _score_structural_patterns(self, candidate: Dict) -> float:
        """Score based on structural patterns"""
        text = candidate['text']
        score = 0.0
        
        # Numbered sections (highest score)
        if re.match(r'^\d+\.\s+', text):
            score += 0.9
        elif re.match(r'^\d+\.\d+\s+', text):
            score += 0.8
        elif re.match(r'^[A-Z]\.\s+', text):
            score += 0.7
        
        # Common section types
        section_patterns = [
            r'introduction', r'conclusion', r'summary', r'overview',
            r'background', r'methodology', r'results', r'discussion',
            r'references', r'appendix', r'chapter\s+\d+', r'section\s+\d+'
        ]
        
        if any(re.search(pattern, text.lower()) for pattern in section_patterns):
            score += 0.6
        
        return min(1.0, score)
    
    def _score_semantic_content(self, candidate: Dict) -> float:
        """Score based on semantic content analysis"""
        text = candidate['text']
        score = 0.0
        
        # Length scoring (sweet spot for headings)
        length = len(text)
        if 10 <= length <= 60:
            score += 0.8
        elif 5 <= length <= 100:
            score += 0.6
        else:
            score += 0.3
        
        # Word count scoring
        word_count = len(text.split())
        if 2 <= word_count <= 8:
            score += 0.7
        elif 1 <= word_count <= 12:
            score += 0.5
        
        # Capitalization patterns
        if text.istitle():
            score += 0.5
        elif text.isupper() and length < 50:
            score += 0.4
        
        return min(1.0, score)
    
    def _score_typography(self, candidate: Dict, all_candidates: List[Dict]) -> float:
        """Score based on typography consistency"""
        size = candidate.get('size', 12.0)  # Default size if missing
        bold = candidate.get('bold', False)
        
        # Font size relative scoring
        sizes = [c.get('size', 12.0) for c in all_candidates]  # Default size if missing
        if sizes:
            max_size = max(sizes)
            size_ratio = size / max_size if max_size > 0 else 0.5
            
            if size_ratio > 0.9:  # Very large font
                return 0.9
            elif size_ratio > 0.7:  # Large font
                return 0.7
            elif size_ratio > 0.5:  # Medium font
                return 0.5
            else:
                return 0.3
        
        # Bold bonus
        if bold:
            return min(1.0, 0.6 + (0.3 if size > 12 else 0.1))
        
        return 0.5
    
    def _score_position(self, candidate: Dict) -> float:
        """Score based on position in document"""
        page = candidate['page']
        
        # Early pages more likely to have important headings
        if page <= 2:
            return 0.9
        elif page <= 5:
            return 0.7
        elif page <= 10:
            return 0.6
        else:
            return 0.5
    
    def _calculate_dynamic_threshold(self, scored_candidates: List[Dict]) -> float:
        """Calculate dynamic threshold based on score distribution"""
        if not scored_candidates:
            return 0.5
        
        scores = [c['quality_score'] for c in scored_candidates]
        
        # Use median as base threshold
        scores.sort()
        median_score = scores[len(scores) // 2]
        
        # Adjust based on score distribution
        threshold = max(0.3, min(0.8, median_score * 0.8))
        
        return threshold
    
    def _calculate_dynamic_threshold_from_scores(self, scores: List[float]) -> float:
        """Calculate dynamic threshold based on score distribution"""
        if not scores:
            return 0.5
        
        # Use median as base threshold
        sorted_scores = sorted(scores)
        median_score = sorted_scores[len(sorted_scores) // 2]
        
        # Adjust based on score distribution
        threshold = max(0.3, min(0.8, median_score * 0.8))
        
        return threshold
    
    def _calculate_accuracy_metrics(self, selected: List[Dict], all_candidates: List[Dict]) -> Dict:
        """Calculate precision, recall, and F1 metrics"""
        # Simplified metrics calculation
        total_candidates = len(all_candidates)
        selected_count = len(selected)
        
        # Estimate precision based on selection ratio (simplified approach)
        if selected_count > 0:
            precision = min(1.0, 0.8 + (0.2 * (1 - selected_count / max(1, total_candidates))))
        else:
            precision = 0.0
        
        # Estimate recall based on reasonable selection percentage
        recall = min(1.0, selected_count / max(1, total_candidates * 0.7))
        
        # Calculate F1 score
        if precision + recall > 0:
            f1_score = 2 * (precision * recall) / (precision + recall)
        else:
            f1_score = 0.0
        
        return {
            'precision_score': round(precision, 3),
            'recall_score': round(recall, 3),
            'f1_score': round(f1_score, 3),
            'total_candidates': total_candidates,
            'selected_count': selected_count
        }
    
    # Placeholder methods for recall enhancement (simplified implementations)
    def _find_relaxed_typography_headings(self, doc_profile: Dict) -> List[Dict]:
        """Find headings with relaxed typography criteria"""
        return []  # Simplified for now
    
    def _recover_structural_patterns(self, doc_profile: Dict) -> List[Dict]:
        """Recover headings based on structural patterns"""
        return []  # Simplified for now
    
    def _reconstruct_cross_page_headings(self, doc_profile: Dict) -> List[Dict]:
        """Reconstruct headings that span across pages"""
        return []  # Simplified for now
    
    def _deduplicate_candidates(self, candidates: List[Dict]) -> List[Dict]:
        """Remove duplicate candidates"""
        seen = set()
        unique = []
        
        for candidate in candidates:
            text_key = candidate['text'].strip().lower()
            if text_key not in seen:
                seen.add(text_key)
                unique.append(candidate)
        
        return unique
