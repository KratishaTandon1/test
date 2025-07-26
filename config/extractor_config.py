"""
Complete working configuration for PDF extractor
Includes all required keys to prevent errors
"""

class ExtractorConfig:
    """Configuration management for PDF extraction components"""
    
    @staticmethod
    def get_default_config():
        """Get complete default configuration for the extractor"""
        return {
            'extraction': {
                'min_confidence': 0.5,
                'max_workers': 6,  # Optimized for 8 CPU system (leave 2 for system)
                'clustering': {
                    'min_clusters': 2,
                    'max_clusters': 5,
                    'cluster_ratio': 3,
                    'random_state': 42,
                    'n_init': 10
                },
                'font_thresholds': {
                    'min_heading_size': 11.0,
                    'large_font_threshold': 14.0,
                    'small_font_threshold': 9.0,
                    'title_font_threshold': 20,
                    'max_caps_length': 30
                },
                'distance_thresholds': {
                    'line_spacing': 1.5,
                    'paragraph_spacing': 2.0,
                    'section_spacing': 3.0,
                    'font_size_tolerance': 2.0,
                    'grouping_distance': 30,
                    'large_font_tolerance': 3.0,
                    'large_font_distance': 40
                },
                'text_limits': {
                    'min_text_length': 3,
                    'max_text_length': 200,
                    'min_word_count': 1,
                    'max_word_count': 20,
                    'min_word_avg_length': 2,
                    'max_form_heading': 50,
                    'max_academic_heading': 150,  # Add missing config key
                    'max_simple_heading': 100,
                    'max_complex_heading': 150
                }
            },
            'accuracy': {
                'enable_quality_scoring': True,
                'quality_weights': {
                    'font_size': 0.25,
                    'font_style': 0.25,
                    'position': 0.20,
                    'text_features': 0.15,
                    'context': 0.15
                },
                'min_quality_threshold': 0.4,
                'enable_clustering': True,
                'clustering_features': 10
            },
            'performance': {
                'time_limit': 3.0,
                'memory_limit': 200,
                'monitor_enabled': True,
                'log_detailed_metrics': True
            },
            'document_types': {
                'business': {
                    'indicators': ['memo', 'report', 'proposal', 'minutes'],
                    'min_indicators': 1,
                    'avoid_fields': ['name:', 'date:', 'signature:', 'employee']
                },
                'form': {
                    'indicators': ['application', 'form', 'template', 'document', 'submission'],
                    'min_indicators': 1,
                    'title_keywords': ['application', 'document', 'form', 'template', 'submission'],
                    'avoid_keywords': ['microsoft', 'word', '.doc', 'file', '.pdf'],
                    'avoid_fields': ['name:', 'date:', 'signature:', 'employee']
                },
                'academic': {
                    'indicators': ['syllabus', 'curriculum', 'course', 'university', 'college', 'academic'],
                    'min_indicators': 1,
                    'max_dots': 3
                },
                'technical': {
                    'indicators': ['technical', 'specification', 'manual', 'guide', 'documentation'],
                    'min_indicators': 1,
                    'max_parentheses': 3
                },
                'simple': {
                    'max_underscores': 2,
                    'avoid_patterns': ['copyright', '©', 'all rights reserved']
                }
            },
            'filtering': {
                'noise_patterns': [
                    r'^[\s\-_\.]+$',
                    r'^\d+$',
                    r'^[^\w\s]*$',
                    r'^(page|p\.)\s*\d+',
                    r'^\s*\d+\s*/\s*\d+\s*$'
                ],
                'avoid_general': [
                    'copyright', 'all rights reserved', '©', 'confidential',
                    'draft', 'preliminary', 'internal use'
                ],
                'avoid_metadata': [
                    'filename', 'author', 'created', 'modified',
                    'subject', 'keywords', 'producer'
                ],
                'min_unique_chars': 3,
                'max_space_ratio': 0.7
            },
            # LayoutLMv3 multimodal enhancement settings
            'layoutlmv3': {
                'enabled': True,
                'model_name': 'microsoft/layoutlmv3-base',
                'confidence_thresholds': {
                    'title': 0.8,
                    'h1': 0.7,
                    'h2': 0.6,
                    'h3': 0.5
                },
                'max_pages_analyze': 3,
                'quality_boost_factor': 0.3,
                'use_gpu': True,
                'lazy_loading': True
            }
        }
    
    @staticmethod
    def merge_configs(default_config, custom_config):
        """Recursively merge custom config with default config"""
        if not custom_config:
            return default_config
            
        merged = default_config.copy()
        
        for key, value in custom_config.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = ExtractorConfig.merge_configs(merged[key], value)
            else:
                merged[key] = value
        
        return merged
    
    @staticmethod
    def create_config(custom_config=None):
        """Create a configuration by merging custom with defaults"""
        default = ExtractorConfig.get_default_config()
        return ExtractorConfig.merge_configs(default, custom_config)
