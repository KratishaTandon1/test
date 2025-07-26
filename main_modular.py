"""
Main entry point for modular PDF extraction system
Demonstrates usage of the new modular architecture
"""

import os
import glob
from pdf_extractor_modular import ModularPDFExtractor

def main():
    """Main function demonstrating modular PDF extraction"""
    
    # Configuration for the extractor (can be customized)
    custom_config = {
        'extraction': {
            'max_workers': 3,
            'font_thresholds': {
                'min_heading_size': 10.0,  # Custom threshold
                'large_font_threshold': 14.0
            }
        }
    }
    
    # Initialize the modular extractor
    print("🚀 Initializing Modular PDF Extractor...")
    extractor = ModularPDFExtractor(config=custom_config)
    
    # Show component information
    components = extractor.get_component_info()
    print(f"📦 Loaded components:")
    for component, class_name in components.items():
        print(f"   • {component}: {class_name}")
    
    # Get PDF files to process
    input_directory = "input"
    input_pattern = os.path.join(input_directory, "*.pdf")
    output_directory = "output"
    
    pdf_files = glob.glob(input_pattern)
    if not pdf_files:
        print(f"❌ No PDF files found matching pattern: {input_pattern}")
        return
    
    # Ensure output directory exists
    os.makedirs(output_directory, exist_ok=True)
    
    print(f"📄 Found {len(pdf_files)} PDF files to process")
    print(f"🎯 Output directory: {output_directory}")
    
    # Process files using modular system
    successful_files, total_time, performance_report = extractor.process_files(pdf_files, output_directory)
    
    # Show results
    print(f"⚡ Processed {successful_files} files in {total_time:.3f}s")
    print(f"📊 Average: {total_time/max(1, successful_files):.3f}s per file")
    
    if successful_files == len(pdf_files):
        print("✅ All files processed successfully!")
    else:
        failed_files = len(pdf_files) - successful_files
        print(f"⚠️  {failed_files} files failed to process")

def demo_single_file():
    """Demonstrate single file processing with modular system"""
    
    print("🔍 Single File Processing Demo")
    print("=" * 40)
    
    # Initialize extractor
    extractor = ModularPDFExtractor()
    
    # Process a single file
    input_directory = "input"
    pdf_files = glob.glob(os.path.join(input_directory, "*.pdf"))
    if pdf_files:
        pdf_path = pdf_files[0]
        print(f"📄 Processing: {pdf_path}")
        
        result = extractor.extract_structure(pdf_path)
        
        print(f"📋 Title: {result['title']}")
        print(f"📑 Found {len(result['outline'])} headings:")
        
        for i, heading in enumerate(result['outline'][:5]):  # Show first 5
            print(f"   {i+1}. [{heading['level']}] {heading['text']} (page {heading['page']})")
        
        if len(result['outline']) > 5:
            print(f"   ... and {len(result['outline']) - 5} more headings")
    else:
        print("❌ No PDF files found for demo")

if __name__ == "__main__":
    print("🏗️  Modular PDF Extraction System")
    print("=" * 50)
    
    # Run main processing
    main()
    
    print("\n" + "=" * 50)
    
    # Run single file demo
    demo_single_file()
