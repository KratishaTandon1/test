"""
LayoutLMv3 Configuration Examples
Optimized settings for different use cases
"""

# High Accuracy Configuration (slower but more accurate)
HIGH_ACCURACY_CONFIG = {
    'layoutlmv3': {
        'enabled': True,
        'model_name': 'microsoft/layoutlmv3-base',
        'confidence_thresholds': {
            'title': 0.9,      # Very high confidence for titles
            'h1': 0.8,         # High confidence for H1
            'h2': 0.7,         # Good confidence for H2
            'h3': 0.6          # Moderate confidence for H3
        },
        'max_pages_analyze': 5,  # Analyze more pages
        'quality_boost_factor': 0.4,  # Higher boost
        'use_gpu': True,
        'lazy_loading': True
    },
    'accuracy': {
        'enable_quality_scoring': True,
        'quality_weights': {
            'font_size': 0.15,      # Reduced weight on font size
            'font_style': 0.15,     # Reduced weight on font style
            'position': 0.15,       # Reduced weight on position
            'text_features': 0.15,  # Reduced weight on text features
            'context': 0.20,        # Moderate weight on context
            'layoutlmv3': 0.30      # High weight on LayoutLMv3 predictions
        },
        'min_quality_threshold': 0.6,
        'enable_clustering': True,
        'clustering_features': 14  # Use all features
    }
}

# Balanced Configuration (good balance of speed and accuracy)
BALANCED_CONFIG = {
    'layoutlmv3': {
        'enabled': True,
        'model_name': 'microsoft/layoutlmv3-base',
        'confidence_thresholds': {
            'title': 0.8,
            'h1': 0.7,
            'h2': 0.6,
            'h3': 0.5
        },
        'max_pages_analyze': 3,  # Default
        'quality_boost_factor': 0.3,
        'use_gpu': True,
        'lazy_loading': True
    },
    'accuracy': {
        'quality_weights': {
            'font_size': 0.20,
            'font_style': 0.20,
            'position': 0.20,
            'text_features': 0.15,
            'context': 0.15,
            'layoutlmv3': 0.25      # Moderate weight
        },
        'min_quality_threshold': 0.5
    }
}

# Fast Configuration (prioritize speed, basic LayoutLMv3)
FAST_CONFIG = {
    'layoutlmv3': {
        'enabled': True,
        'model_name': 'microsoft/layoutlmv3-base',
        'confidence_thresholds': {
            'title': 0.7,
            'h1': 0.6,
            'h2': 0.5,
            'h3': 0.4
        },
        'max_pages_analyze': 1,  # Only first page
        'quality_boost_factor': 0.2,
        'use_gpu': True,
        'lazy_loading': True
    },
    'accuracy': {
        'quality_weights': {
            'font_size': 0.25,
            'font_style': 0.25,
            'position': 0.25,
            'text_features': 0.15,
            'context': 0.05,
            'layoutlmv3': 0.15      # Lower weight for speed
        }
    },
    'performance': {
        'time_limit': 2.0,  # Stricter time limit
        'memory_limit': 150  # Lower memory limit
    }
}

# CPU-Only Configuration (no GPU required)
CPU_ONLY_CONFIG = {
    'layoutlmv3': {
        'enabled': True,
        'model_name': 'microsoft/layoutlmv3-base',
        'confidence_thresholds': {
            'title': 0.8,
            'h1': 0.7,
            'h2': 0.6,
            'h3': 0.5
        },
        'max_pages_analyze': 2,  # Reduced for CPU
        'quality_boost_factor': 0.3,
        'use_gpu': False,  # Force CPU usage
        'lazy_loading': True
    }
}

# Multilingual Configuration (enhanced for non-English documents)
MULTILINGUAL_CONFIG = {
    'layoutlmv3': {
        'enabled': True,
        'model_name': 'microsoft/layoutlmv3-base',  # Supports multilingual
        'confidence_thresholds': {
            'title': 0.75,  # Slightly lower for multilingual
            'h1': 0.65,
            'h2': 0.55,
            'h3': 0.45
        },
        'max_pages_analyze': 3,
        'quality_boost_factor': 0.35,  # Higher boost for multilingual
        'use_gpu': True,
        'lazy_loading': True
    },
    'filtering': {
        'multilingual_support': True,
        'unicode_normalization': True,
        'language_detection': True
    }
}

# Research/Academic Configuration (highest accuracy for research papers)
ACADEMIC_CONFIG = {
    'layoutlmv3': {
        'enabled': True,
        'model_name': 'microsoft/layoutlmv3-base',
        'confidence_thresholds': {
            'title': 0.95,  # Very high for academic titles
            'h1': 0.85,     # High for section headers
            'h2': 0.75,     # High for subsections
            'h3': 0.65      # Good for sub-subsections
        },
        'max_pages_analyze': 10,  # Analyze many pages
        'quality_boost_factor': 0.5,  # Maximum boost
        'use_gpu': True,
        'lazy_loading': True
    },
    'document_types': {
        'academic': {
            'indicators': ['abstract', 'introduction', 'methodology', 'results', 'conclusion'],
            'min_indicators': 1,
            'section_numbering': True,
            'reference_aware': True
        }
    }
}

def get_config_for_use_case(use_case: str):
    """Get optimized configuration for specific use case"""
    configs = {
        'high_accuracy': HIGH_ACCURACY_CONFIG,
        'balanced': BALANCED_CONFIG,
        'fast': FAST_CONFIG,
        'cpu_only': CPU_ONLY_CONFIG,
        'multilingual': MULTILINGUAL_CONFIG,
        'academic': ACADEMIC_CONFIG
    }
    
    return configs.get(use_case, BALANCED_CONFIG)

def print_config_recommendations():
    """Print configuration recommendations"""
    print("🔧 LayoutLMv3 Configuration Recommendations:")
    print("=" * 50)
    print("📊 High Accuracy:    Best quality, slower processing")
    print("⚖️  Balanced:        Good quality-speed balance")
    print("🚀 Fast:            Quick processing, basic quality")
    print("💻 CPU Only:        No GPU required")
    print("🌍 Multilingual:    Enhanced non-English support")
    print("🎓 Academic:        Optimized for research papers")
    print("\nUsage: extractor = ModularPDFExtractor(config=get_config_for_use_case('balanced'))")

if __name__ == "__main__":
    print_config_recommendations()
