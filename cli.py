#!/usr/bin/env python3
"""
Command Line Interface for PDF Extractor
Simple way to process PDFs from command line
"""

import argparse
import sys
import os
import json
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        description="Extract structure from PDF documents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process single file
  python cli.py document.pdf

  # Process with high accuracy
  python cli.py document.pdf --config high_accuracy

  # Process multiple files
  python cli.py file1.pdf file2.pdf --output results/

  # Batch process directory
  python cli.py input/*.pdf --output batch_results/

  # Show detailed output
  python cli.py document.pdf --verbose
        """
    )
    
    parser.add_argument('files', nargs='+', help='PDF file(s) to process')
    parser.add_argument('-o', '--output', default='output', 
                       help='Output directory (default: output)')
    parser.add_argument('-c', '--config', 
                       choices=['balanced', 'high_accuracy', 'fast', 'cpu_only', 'multilingual', 'academic'],
                       default='balanced',
                       help='Configuration preset (default: balanced)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Show detailed output')
    parser.add_argument('--no-accuracy', action='store_true',
                       help='Disable accuracy enhancement')
    parser.add_argument('--no-performance', action='store_true',
                       help='Disable performance monitoring')
    
    args = parser.parse_args()
    
    try:
        # Import and setup
        from pdf_extractor_modular import ModularPDFExtractor
        from config.layoutlmv3_configs import get_config_for_use_case
        
        # Get configuration
        config = get_config_for_use_case(args.config)
        if args.verbose:
            print(f"📋 Using configuration: {args.config}")
        
        # Initialize extractor
        extractor = ModularPDFExtractor(
            config=config,
            enable_accuracy_enhancement=not args.no_accuracy,
            enable_performance_monitoring=not args.no_performance
        )
        
        if args.verbose:
            print(f"🚀 Extractor initialized")
            print(f"   LayoutLMv3: {'✅' if extractor.layoutlmv3_enhancer else '❌'}")
            print(f"   Accuracy enhancer: {'✅' if extractor.accuracy_enhancer else '❌'}")
            print(f"   Performance monitor: {'✅' if extractor.performance_monitor else '❌'}")
        
        # Create output directory
        os.makedirs(args.output, exist_ok=True)
        
        # Process files
        processed = 0
        total_files = len(args.files)
        
        for pdf_file in args.files:
            if not os.path.exists(pdf_file):
                print(f"❌ File not found: {pdf_file}")
                continue
                
            try:
                if args.verbose:
                    print(f"📄 Processing: {pdf_file}")
                
                # Extract structure
                result = extractor.extract_structure(pdf_file)
                
                # Generate output filename
                base_name = Path(pdf_file).stem
                output_file = os.path.join(args.output, f"{base_name}.json")
                
                # Save result
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                
                processed += 1
                
                # Show results
                title = result.get('title', 'No title')
                headings = len(result.get('outline', []))
                
                if args.verbose:
                    print(f"   ✅ Title: {title}")
                    print(f"   📑 Headings: {headings}")
                    print(f"   💾 Saved: {output_file}")
                    
                    # Show performance metrics if available
                    if 'performance_metrics' in result:
                        perf = result['performance_metrics']
                        print(f"   ⚡ Time: {perf.get('processing_time', 0):.3f}s")
                        print(f"   💾 Memory: {perf.get('memory_usage', 0):.1f}MB")
                    
                    # Show accuracy metrics if available
                    if 'accuracy_metrics' in result:
                        acc = result['accuracy_metrics']
                        print(f"   🎯 F1-Score: {acc.get('f1_score', 0):.3f}")
                else:
                    print(f"✅ {pdf_file} → {output_file} (title: {title[:30]}{'...' if len(title) > 30 else ''}, {headings} headings)")
                
            except Exception as e:
                print(f"❌ Error processing {pdf_file}: {e}")
        
        # Summary
        print(f"\n📊 Summary: {processed}/{total_files} files processed successfully")
        if processed > 0:
            print(f"📁 Results saved in: {args.output}/")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Try: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
