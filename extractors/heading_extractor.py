"""
Heading extraction module for PDF documents
Handles ML-based heading detection and hierarchy building
"""

import re
import numpy as np
from collections import defaultdict
from typing import List, Dict, Any, Set
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

class HeadingExtractor:
    """Extracts and structures headings from PDF documents"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.noise_patterns = set(self.config['filtering']['noise_patterns'])
    
    def extract_headings(self, doc, doc_profile: Dict) -> List[Dict[str, Any]]:
        """Extract headings with adaptive precision"""
        # Get candidates using ML clustering
        candidates = self._get_ml_heading_candidates(doc)
        
        # Apply document-specific filtering
        filtered_candidates = self._apply_filtering(candidates, doc_profile)
        
        # Structure hierarchy
        structured_headings = self._build_heading_hierarchy(filtered_candidates)
        
        return structured_headings
    
    def _get_ml_heading_candidates(self, doc) -> List[Dict[str, Any]]:
        """Use machine learning clustering to identify heading candidates"""
        all_texts = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("dict")["blocks"]
            
            # First pass: collect all line information
            lines_info = []
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        line_text = ""
                        max_size = 0
                        is_bold = False
                        bbox = None
                        
                        for span in line["spans"]:
                            text = span["text"].strip()
                            if text:
                                line_text += text + " "
                                max_size = max(max_size, span["size"])
                                if span["flags"] & 2**4:  # Bold flag
                                    is_bold = True
                                if bbox is None:
                                    bbox = span["bbox"]
                        
                        line_text = line_text.strip()
                        if line_text and len(line_text) > 3:
                            lines_info.append({
                                'text': line_text,
                                'size': max_size,
                                'bold': is_bold,
                                'bbox': bbox,
                                'y_pos': bbox[1] if bbox else 0
                            })
            
            # Second pass: group adjacent lines with similar properties
            if not lines_info:
                continue
                
            # Sort by Y position (top to bottom)
            lines_info.sort(key=lambda x: x['y_pos'])
            
            reconstructed_texts = self._reconstruct_text_blocks(lines_info, page_num)
            all_texts.extend(reconstructed_texts)
        
        if len(all_texts) < 5:
            return all_texts
        
        # Perform ML clustering
        return self._cluster_headings(all_texts)
    
    def _reconstruct_text_blocks(self, lines_info: List[Dict], page_num: int) -> List[Dict]:
        """Reconstruct fragmented text into complete blocks"""
        reconstructed_texts = []
        current_group = [lines_info[0]]
        
        for i in range(1, len(lines_info)):
            current_line = lines_info[i]
            prev_line = current_group[-1]
            
            # Use configurable thresholds for text reconstruction
            distance_config = self.config['extraction']['distance_thresholds']
            size_similar = abs(current_line['size'] - prev_line['size']) < distance_config['font_size_tolerance']
            y_distance = abs(current_line['y_pos'] - prev_line['y_pos'])
            close_vertically = y_distance < distance_config['grouping_distance']
            same_style = current_line['bold'] == prev_line['bold']
            
            # Special handling for large font fragments
            large_font_threshold = self.config['extraction']['font_thresholds']['title_font_threshold']
            if current_line['size'] > large_font_threshold and prev_line['size'] > large_font_threshold:
                size_similar = abs(current_line['size'] - prev_line['size']) < distance_config['large_font_tolerance']
                close_vertically = y_distance < distance_config['large_font_distance']
            
            if size_similar and close_vertically and same_style:
                current_group.append(current_line)
            else:
                # Process the current group
                if current_group:
                    combined_text = self._reconstruct_fragmented_text(current_group)
                    avg_size = sum(line['size'] for line in current_group) / len(current_group)
                    is_bold = current_group[0]['bold']
                    
                    if len(combined_text) > 5:
                        reconstructed_texts.append({
                            'text': combined_text,
                            'size': avg_size,
                            'bold': is_bold,
                            'page': page_num + 1,
                            'length': len(combined_text),
                            'bbox': current_group[0]['bbox']
                        })
                
                current_group = [current_line]
        
        # Don't forget the last group
        if current_group:
            combined_text = self._reconstruct_fragmented_text(current_group)
            avg_size = sum(line['size'] for line in current_group) / len(current_group)
            is_bold = current_group[0]['bold']
            
            if len(combined_text) > 5:
                reconstructed_texts.append({
                    'text': combined_text,
                    'size': avg_size,
                    'bold': is_bold,
                    'page': page_num + 1,
                    'length': len(combined_text),
                    'bbox': current_group[0]['bbox']
                })
        
        return reconstructed_texts
    
    def _cluster_headings(self, all_texts: List[Dict]) -> List[Dict]:
        """Cluster text using enhanced ML features"""
        # Create enhanced features for clustering
        features = []
        for text_info in all_texts:
            text = text_info['text']
            
            # Font and formatting features
            size_feature = text_info['size']
            bold_feature = int(text_info['bold'])
            length_feature = text_info['length']
            y_pos_feature = text_info['bbox'][1] if text_info['bbox'] else 0
            
            # Text pattern features
            has_numbers = int(bool(re.search(r'\d', text)))
            starts_with_number = int(bool(re.match(r'^\d+', text)))
            is_short = int(length_feature < 30)
            is_title_case = int(text.istitle())
            has_colon = int(':' in text)
            word_count = len(text.split())
            
            # Position features
            page_feature = text_info['page']
            is_early_page = int(page_feature <= 3)
            
            # Structural pattern features
            has_section_number = int(bool(re.search(r'^\d+\.', text)))
            has_subsection_number = int(bool(re.search(r'^\d+\.\d+', text)))
            
            features.append([
                size_feature, bold_feature, length_feature, y_pos_feature,
                has_numbers, starts_with_number, is_short, is_title_case,
                has_colon, word_count, page_feature, is_early_page,
                has_section_number, has_subsection_number
            ])
        
        # Perform clustering
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        clustering_config = self.config['extraction']['clustering']
        n_clusters = min(clustering_config['max_clusters'], len(all_texts) // clustering_config['cluster_ratio'])
        if n_clusters < clustering_config['min_clusters']:
            return all_texts
        
        kmeans = KMeans(
            n_clusters=n_clusters, 
            random_state=clustering_config['random_state'], 
            n_init=clustering_config['n_init']
        )
        clusters = kmeans.fit_predict(features_scaled)
        
        # Select heading candidates from clusters
        return self._select_heading_candidates(all_texts, clusters)
    
    def _select_heading_candidates(self, all_texts: List[Dict], clusters: np.ndarray) -> List[Dict]:
        """Select heading candidates from clustered text"""
        cluster_stats = defaultdict(list)
        for i, cluster in enumerate(clusters):
            cluster_stats[cluster].append(all_texts[i])
        
        heading_candidates = []
        
        for cluster_id, texts in cluster_stats.items():
            avg_size = np.mean([t['size'] for t in texts])
            avg_length = np.mean([t['length'] for t in texts])
            bold_ratio = np.mean([t['bold'] for t in texts])
            
            # Enhanced heuristics that don't rely solely on font size
            cluster_score = self._calculate_cluster_score(texts, avg_size, avg_length, bold_ratio)
            
            # Select clusters with high enough composite score
            if cluster_score >= 5:
                heading_candidates.extend(texts)
        
        return heading_candidates
    
    def _calculate_cluster_score(self, texts: List[Dict], avg_size: float, avg_length: float, bold_ratio: float) -> int:
        """Calculate composite score for cluster"""
        font_threshold = self.config['extraction']['font_thresholds']['min_heading_size']
        large_font_threshold = self.config['extraction']['font_thresholds']['large_font_threshold']
        max_length = self.config['extraction']['text_limits']['max_simple_heading']
        
        cluster_score = 0
        
        # Font size contribution (reduced weight)
        if avg_size > large_font_threshold:
            cluster_score += 3
        elif avg_size > font_threshold:
            cluster_score += 2
        
        # Length contribution (headings are typically shorter)
        if avg_length < 30:
            cluster_score += 3
        elif avg_length < max_length:
            cluster_score += 2
        
        # Bold formatting contribution
        if bold_ratio > 0.7:
            cluster_score += 3
        elif bold_ratio > 0.3:
            cluster_score += 2
        
        # Structural pattern analysis
        has_numbered_sections = any(re.search(r'^\d+\.', t['text']) for t in texts)
        has_section_keywords = any(
            any(keyword in t['text'].lower() for keyword in [
                'introduction', 'overview', 'conclusion', 'summary', 'background',
                'methodology', 'results', 'discussion', 'references'
            ]) for t in texts
        )
        
        if has_numbered_sections:
            cluster_score += 4
        if has_section_keywords:
            cluster_score += 3
        
        # Position-based scoring
        early_page_ratio = np.mean([1 if t['page'] <= 3 else 0 for t in texts])
        if early_page_ratio > 0.5:
            cluster_score += 2
        
        # Title case pattern
        title_case_ratio = np.mean([1 if t['text'].istitle() else 0 for t in texts])
        if title_case_ratio > 0.5:
            cluster_score += 2
        
        return cluster_score
    
    def _reconstruct_fragmented_text(self, text_group: List[Dict]) -> str:
        """Reconstruct fragmented text by intelligently combining fragments"""
        if not text_group:
            return ""
        
        texts = [item['text'] for item in text_group]
        combined = ' '.join(texts).strip()
        combined = ' '.join(combined.split())  # Normalize whitespace
        
        return combined
    
    def _apply_filtering(self, candidates: List[Dict], doc_profile: Dict) -> List[Dict]:
        """Apply filtering to remove noise and false positives"""
        # Import here to avoid circular imports
        try:
            from .filters.heading_filter import HeadingFilter
            filter_instance = HeadingFilter(self.config)
            return filter_instance.filter_candidates(candidates, doc_profile)
        except ImportError:
            # Fallback to basic filtering if module not available
            return candidates
    
    def _build_heading_hierarchy(self, candidates: List[Dict]) -> List[Dict[str, Any]]:
        """Build proper heading hierarchy using multiple signals"""
        # Import here to avoid circular imports
        try:
            from .hierarchy.level_determiner import LevelDeterminer
            level_determiner = LevelDeterminer(self.config)
            return level_determiner.build_hierarchy(candidates)
        except ImportError:
            # Fallback to basic hierarchy building
            if not candidates:
                return []
            
            # Sort by page, then by y-position
            candidates.sort(key=lambda x: (x['page'], x['bbox'][1] if x['bbox'] else 0))
            
            structured = []
            for candidate in candidates:
                structured.append({
                    "level": "H1",  # Default level
                    "text": candidate['text'],
                    "page": candidate['page'] - 1  # Convert to 0-based
                })
            
            return structured
