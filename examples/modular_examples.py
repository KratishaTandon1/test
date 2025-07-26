"""
Examples demonstrating the modularity and reusability of the PDF extraction system
Shows how to customize and extend different components
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pdf_extractor_modular import ModularPDFExtractor
from config.extractor_config import ExtractorConfig

def example_custom_configuration():
    """Example 1: Using custom configuration"""
    print("Example 1: Custom Configuration")
    print("-" * 40)
    
    # Custom configuration for academic documents
    academic_config = {
        'document_types': {
            'academic': {
                'indicators': ['syllabus', 'curriculum', 'course', 'university', 'extension'],
                'min_indicators': 1,
                'max_dots': 5  # Allow more dots in academic headings
            }
        },
        'extraction': {
            'font_thresholds': {
                'min_heading_size': 9.0,  # Lower threshold for academic docs
                'large_font_threshold': 12.0
            },
            'text_limits': {
                'max_academic_heading': 200  # Longer academic headings
            }
        }
    }
    
    # Create extractor with custom config
    extractor = ModularPDFExtractor(config=academic_config)
    
    # Process files
    import glob
    pdf_files = glob.glob("input/*.pdf")
    if pdf_files:
        result = extractor.extract_structure(pdf_files[1])  # file02.pdf (academic)
        print(f"Title: {result['title']}")
        print(f"Headings found: {len(result['outline'])}")
        for heading in result['outline'][:3]:
            print(f"  • [{heading['level']}] {heading['text']}")
    
    print()

def example_component_swapping():
    """Example 2: Component modularity demonstration"""
    print("Example 2: Component Information")
    print("-" * 40)
    
    # Show how components can be inspected and potentially swapped
    extractor = ModularPDFExtractor()
    
    components = extractor.get_component_info()
    print("Loaded Components:")
    for name, class_name in components.items():
        print(f"  • {name}: {class_name}")
    
    # Show configuration structure
    print("\nConfiguration Structure:")
    config_keys = list(extractor.config.keys())
    for key in config_keys:
        subkeys = list(extractor.config[key].keys()) if isinstance(extractor.config[key], dict) else []
        print(f"  • {key}: {subkeys}")
    
    print()

def example_batch_processing():
    """Example 3: Efficient batch processing"""
    print("Example 3: Batch Processing with Custom Settings")
    print("-" * 40)
    
    # Configuration optimized for speed
    speed_config = {
        'extraction': {
            'max_workers': 4,  # More parallel processing
            'clustering': {
                'max_clusters': 3,  # Simpler clustering
                'n_init': 5  # Fewer initialization runs
            }
        }
    }
    
    extractor = ModularPDFExtractor(config=speed_config)
    
    import glob
    import os
    
    pdf_files = glob.glob("input/*.pdf")
    if pdf_files:
        print(f"Processing {len(pdf_files)} files with speed optimization...")
        
        successful, total_time = extractor.process_files(pdf_files, "output_speed")
        
        print(f"Processed {successful} files in {total_time:.3f}s")
        print(f"Speed: {total_time/max(1, successful):.3f}s per file")
    
    print()

def example_config_merging():
    """Example 4: Configuration merging demonstration"""
    print("Example 4: Configuration Merging")
    print("-" * 40)
    
    # Base configuration
    base_config = {
        'extraction': {
            'max_workers': 2,
            'font_thresholds': {
                'min_heading_size': 10.0
            }
        }
    }
    
    # Override configuration
    override_config = {
        'extraction': {
            'max_workers': 4,  # This will override
            'clustering': {     # This will be added
                'max_clusters': 6
            }
        },
        'new_section': {        # Completely new section
            'custom_setting': True
        }
    }
    
    # Merge configurations
    merged = ExtractorConfig.merge_configs(base_config, override_config)
    
    print("Original base config max_workers:", base_config['extraction']['max_workers'])
    print("Override config max_workers:", override_config['extraction']['max_workers'])
    print("Merged config max_workers:", merged['extraction']['max_workers'])
    print("Merged config has clustering:", 'clustering' in merged['extraction'])
    print("Merged config has new_section:", 'new_section' in merged)
    
    print()

def example_single_component_usage():
    """Example 5: Using individual components"""
    print("Example 5: Individual Component Usage")
    print("-" * 40)
    
    import fitz
    from analyzers.document_analyzer import DocumentAnalyzer
    from extractors.title_extractor import TitleExtractor
    
    # Use components individually
    config = ExtractorConfig.get_default_config()
    
    import glob
    pdf_files = glob.glob("input/*.pdf")
    if pdf_files:
        doc = fitz.open(pdf_files[0])
        
        # Use document analyzer independently
        analyzer = DocumentAnalyzer(config)
        doc_profile = analyzer.analyze_document(doc)
        
        print("Document Analysis:")
        print(f"  • Document type - Form: {doc_profile['structure']['is_form']}")
        print(f"  • Document type - Academic: {doc_profile['structure']['is_academic']}")
        print(f"  • Font variety: {doc_profile['structure']['font_variety']}")
        
        # Use title extractor independently
        title_extractor = TitleExtractor(config)
        title = title_extractor.extract_title(doc, doc_profile)
        print(f"  • Extracted title: '{title}'")
        
        doc.close()
    
    print()

def main():
    """Run all examples"""
    print("🔧 PDF Extraction System - Modularity Examples")
    print("=" * 60)
    print()
    
    # Run all examples
    example_custom_configuration()
    example_component_swapping()
    example_batch_processing()
    example_config_merging()
    example_single_component_usage()
    
    print("✅ All examples completed!")
    print("\nKey Benefits of Modular Design:")
    print("• Easy to customize configuration for different document types")
    print("• Components can be used independently or together")
    print("• Configuration merging allows flexible overrides")
    print("• Simple to extend with new extractors or analyzers")
    print("• Clear separation of concerns for maintainability")

if __name__ == "__main__":
    main()
