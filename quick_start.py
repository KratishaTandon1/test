#!/usr/bin/env python3
"""
Quick Start Script - Copy and run this to test your PDF extractor
"""

def quick_demo():
    """Demonstrate the most common usage patterns"""
    
    print("🚀 PDF Extractor Quick Demo")
    print("=" * 40)
    
    # 1. Basic import and setup
    print("\n1️⃣ Basic Setup:")
    print("from pdf_extractor_modular import ModularPDFExtractor")
    print("extractor = ModularPDFExtractor()")
    
    try:
        from pdf_extractor_modular import ModularPDFExtractor
        extractor = ModularPDFExtractor()
        print("✅ Extractor initialized successfully!")
        
        # Check what's available
        has_layoutlmv3 = extractor.layoutlmv3_enhancer is not None
        print(f"   LayoutLMv3 available: {'✅' if has_layoutlmv3 else '❌'}")
        print(f"   Accuracy enhancer: {'✅' if extractor.accuracy_enhancer else '❌'}")
        print(f"   Performance monitor: {'✅' if extractor.performance_monitor else '❌'}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # 2. Single file processing
    print("\n2️⃣ Single File Processing:")
    print("result = extractor.extract_structure('input/file01.pdf')")
    
    try:
        result = extractor.extract_structure('input/file01.pdf')
        print(f"✅ File processed successfully!")
        print(f"   Title: '{result.get('title', 'No title')}'")
        print(f"   Headings found: {len(result.get('outline', []))}")
        
        if result.get('outline'):
            print("   First heading:")
            first = result['outline'][0]
            print(f"     Level: {first.get('level', 'Unknown')}")
            print(f"     Text: {first.get('text', 'No text')[:50]}...")
            print(f"     Quality: {first.get('quality_score', 0):.3f}")
            
    except Exception as e:
        print(f"❌ Error processing file: {e}")
    
    # 3. Configuration options
    print("\n3️⃣ Configuration Options:")
    print("from config.layoutlmv3_configs import get_config_for_use_case")
    
    try:
        from config.layoutlmv3_configs import get_config_for_use_case
        
        configs = ['balanced', 'high_accuracy', 'fast', 'multilingual']
        for config_name in configs:
            config = get_config_for_use_case(config_name)
            layoutlmv3_enabled = config.get('layoutlmv3', {}).get('enabled', False)
            print(f"   {config_name}: LayoutLMv3={'✅' if layoutlmv3_enabled else '❌'}")
            
    except Exception as e:
        print(f"❌ Error loading configs: {e}")
    
    # 4. Batch processing
    print("\n4️⃣ Batch Processing:")
    print("files = ['input/file01.pdf', 'input/file02.pdf']")
    print("successful, time, metrics = extractor.process_files(files, 'output/')")
    
    try:
        import glob
        pdf_files = glob.glob('input/*.pdf')[:2]  # Process first 2 files
        
        if pdf_files:
            successful, total_time, metrics = extractor.process_files(pdf_files, 'output/')
            print(f"✅ Batch processing completed!")
            print(f"   Files processed: {successful}/{len(pdf_files)}")
            print(f"   Total time: {total_time:.3f}s")
            print(f"   Average: {total_time/max(1,successful):.3f}s per file")
        else:
            print("❌ No PDF files found in input/ directory")
            
    except Exception as e:
        print(f"❌ Error in batch processing: {e}")
    
    # 5. Testing
    print("\n5️⃣ Testing Commands:")
    print("python examples/modular_examples.py    # Usage examples")
    
    print("\n🎯 Next Steps:")
    print("1. Add your PDF files to input/ directory")
    print("2. Run: python main_modular.py")
    print("3. Check output/ directory for JSON results")
    print("4. For best accuracy: pip install -r requirements-layoutlmv3.txt")

if __name__ == "__main__":
    quick_demo()
