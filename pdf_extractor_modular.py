"""
Modular PDF Structure Extractor
Refactored for maximum reusability and maintainability
Enhanced with accuracy optimization and performance monitoring
"""

import fitz
import json
import time
from typing import List, Dict, Any, Tuple
from concurrent.futures import ThreadPoolExecutor

# Import modular components
from config.extractor_config import ExtractorConfig
from analyzers.document_analyzer import DocumentAnalyzer
from extractors.title_extractor import TitleExtractor
from extractors.heading_extractor import HeadingExtractor
from accuracy.accuracy_enhancer import AccuracyEnhancer
from performance.performance_monitor import PerformanceMonitor, SizeOptimizer

# Try to import LayoutLMv3 enhancer (optional dependency)
try:
    from enhancers.layoutlmv3_enhancer import LayoutLMv3Enhancer
    LAYOUTLMV3_AVAILABLE = True
except ImportError:
    LAYOUTLMV3_AVAILABLE = False
    print("⚠️  LayoutLMv3 not available. Install transformers and torch for enhanced accuracy.")

class ModularPDFExtractor:
    """Modular PDF extraction system with pluggable components"""
    
    def __init__(self, config=None, enable_accuracy_enhancement=True, enable_performance_monitoring=True):
        """Initialize with configuration and component modules"""
        # Setup configuration
        self.config = ExtractorConfig.create_config(config)
        
        # Optimize config for performance if needed
        if enable_performance_monitoring:
            self.config = SizeOptimizer.optimize_config_for_performance(self.config)
        
        # Initialize modular components
        self.document_analyzer = DocumentAnalyzer(self.config)
        self.title_extractor = TitleExtractor(self.config)
        self.heading_extractor = HeadingExtractor(self.config)
        
        # Enhanced components with strict performance constraints
        self.accuracy_enhancer = AccuracyEnhancer(self.config) if enable_accuracy_enhancement else None
        # Use strict constraints: 10s for 50-page PDF, 200MB max model
        self.performance_monitor = PerformanceMonitor(max_processing_time=10.0, max_memory_mb=200.0) if enable_performance_monitoring else None
        
        # Initialize LayoutLMv3 enhancer if available and enabled
        self.layoutlmv3_enhancer = None
        if (LAYOUTLMV3_AVAILABLE and 
            self.config.get('layoutlmv3', {}).get('enabled', True) and
            enable_accuracy_enhancement):
            self.layoutlmv3_enhancer = LayoutLMv3Enhancer(self.config)
    
    def extract_structure(self, pdf_path: str) -> Dict[str, Any]:
        """Extract document structure using modular approach with accuracy enhancement"""
        try:
            # Open PDF
            doc = fitz.open(pdf_path)
            
            # Analyze document characteristics
            doc_profile = self.document_analyzer.analyze_document(doc)
            
            # Enhance document analysis with LayoutLMv3 if available
            if self.layoutlmv3_enhancer:
                doc_profile = self.layoutlmv3_enhancer.enhance_document_analysis(doc, doc_profile)
            
            # Extract title using specialized extractor
            title = self.title_extractor.extract_title(doc, doc_profile)
            
            # Extract headings using ML-based extractor
            raw_headings = self.heading_extractor.extract_headings(doc, doc_profile)
            
            # Enhance headings with LayoutLMv3 multimodal analysis if available
            if self.layoutlmv3_enhancer:
                raw_headings = self.layoutlmv3_enhancer.enhance_heading_detection(
                    raw_headings, doc, doc_profile
                )
            
            # Apply accuracy enhancement if enabled
            if self.accuracy_enhancer:
                enhanced_headings, accuracy_metrics = self.accuracy_enhancer.enhance_heading_detection(
                    raw_headings, doc_profile
                )
                headings = enhanced_headings
            else:
                headings = raw_headings
                accuracy_metrics = {}
            
            doc.close()
            
            result = {
                "title": title,
                "outline": headings
            }
            
            # Add accuracy metrics if available
            if accuracy_metrics:
                result["_accuracy_metrics"] = accuracy_metrics
            
            return result
            
        except Exception as e:
            print(f"Error processing {pdf_path}: {str(e)}")
            return {"title": "", "outline": []}
    
    def process_files(self, input_paths: List[str], output_dir: str) -> Tuple[int, float, Dict]:
        """Process multiple PDF files using modular extraction with performance monitoring"""
        
        performance_data = {}
        
        # Start performance monitoring if enabled
        if self.performance_monitor:
            monitor_context = self.performance_monitor.monitor_extraction(len(input_paths))
            monitor_context.__enter__()
        else:
            monitor_context = None
        
        try:
            start_time = time.time()
            
            def process_single_file(pdf_path: str) -> bool:
                """Process a single PDF file"""
                try:
                    # Extract structure
                    result = self.extract_structure(pdf_path)
                    
                    # Generate output filename
                    import os
                    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
                    output_path = os.path.join(output_dir, f"{base_name}.json")
                    
                    # Remove internal metrics before saving
                    save_result = {k: v for k, v in result.items() if not k.startswith('_')}
                    
                    # Save results
                    with open(output_path, 'w', encoding='utf-8') as f:
                        json.dump(save_result, f, indent=2, ensure_ascii=False)
                    
                    return True
                    
                except Exception as e:
                    print(f"Error processing {pdf_path}: {str(e)}")
                    return False
            
            # Process files concurrently
            max_workers = self.config['extraction']['max_workers']
            successful_files = 0
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                results = list(executor.map(process_single_file, input_paths))
                successful_files = sum(results)
            
            total_time = time.time() - start_time
            
            # Collect performance data
            if self.performance_monitor and self.performance_monitor.metrics_history:
                latest_metrics = self.performance_monitor.metrics_history[-1]
                performance_data = {
                    'processing_time': latest_metrics.processing_time,
                    'memory_usage_mb': latest_metrics.memory_usage_mb,
                    'avg_time_per_file': latest_metrics.avg_time_per_file,
                    'compliance_status': {
                        'time_compliant': latest_metrics.processing_time <= 30.0,
                        'memory_compliant': latest_metrics.memory_usage_mb <= 512.0,
                        'speed_compliant': latest_metrics.avg_time_per_file <= 5.0
                    }
                }
            
            return successful_files, total_time, performance_data
            
        finally:
            # End performance monitoring
            if monitor_context:
                monitor_context.__exit__(None, None, None)
    
    def get_component_info(self) -> Dict[str, str]:
        """Get information about loaded components"""
        info = {
            "document_analyzer": type(self.document_analyzer).__name__,
            "title_extractor": type(self.title_extractor).__name__,
            "heading_extractor": type(self.heading_extractor).__name__,
            "config_version": "1.0.0"
        }
        
        if self.accuracy_enhancer:
            info["accuracy_enhancer"] = type(self.accuracy_enhancer).__name__
        
        if self.performance_monitor:
            info["performance_monitor"] = type(self.performance_monitor).__name__
        
        return info
    
    def run_performance_test(self, test_files: List[str]) -> Dict[str, Any]:
        """Run performance compliance test"""
        if not self.performance_monitor:
            return {"error": "Performance monitoring not enabled"}
        
        from performance.performance_monitor import ComplianceChecker
        
        checker = ComplianceChecker()
        results = checker.run_compliance_test(test_files)
        
        return results
    
    def print_performance_report(self):
        """Print performance report if monitoring is enabled"""
        if self.performance_monitor:
            self.performance_monitor.print_performance_report()
        else:
            print("Performance monitoring not enabled")

# Legacy compatibility wrapper
class UltimateExtractor(ModularPDFExtractor):
    """Legacy wrapper for backward compatibility"""
    
    def __init__(self, config=None):
        super().__init__(config)
    
    def extract_pdf_structure(self, pdf_path: str) -> Dict[str, Any]:
        """Legacy method name for backward compatibility"""
        return self.extract_structure(pdf_path)
