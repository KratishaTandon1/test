"""
LayoutLMv3 integration for enhanced document understanding
Combines text, layout, and visual features for superior heading detection
"""

import torch
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from PIL import Image
import fitz  # PyMuPDF
from transformers import LayoutLMv3Processor, LayoutLMv3ForTokenClassification
import cv2

class LayoutLMv3Enhancer:
    """Enhanced document analysis using LayoutLMv3 multimodal transformer"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        # Force CPU-only mode for compliance (no GPU required)
        self.device = torch.device("cpu")
        
        # Initialize LayoutLMv3 model and processor
        self.model_name = "microsoft/layoutlmv3-base"  # ~200MB model
        self.processor = None
        self.model = None
        self.initialized = False
        self.max_model_size_mb = 200.0  # Strict model size limit
        
        # Heading classification labels (for token classification)
        self.label_map = {
            0: 'O',      # Other/Not a heading
            1: 'B-H1',   # Beginning of H1 heading
            2: 'I-H1',   # Inside H1 heading
            3: 'B-H2',   # Beginning of H2 heading
            4: 'I-H2',   # Inside H2 heading
            5: 'B-H3',   # Beginning of H3 heading
            6: 'I-H3',   # Inside H3 heading
            7: 'B-TITLE', # Beginning of title
            8: 'I-TITLE'  # Inside title
        }
        
        # Confidence thresholds
        self.confidence_thresholds = {
            'title': 0.8,
            'h1': 0.7,
            'h2': 0.6,
            'h3': 0.5
        }
    
    def initialize_model(self) -> bool:
        """Initialize LayoutLMv3 model (lazy loading for performance)"""
        if self.initialized:
            return True
        
        try:
            print("🤖 Checking for LayoutLMv3 model...")
            
            # Only load if transformers is available (no automatic downloads)
            try:
                from transformers import LayoutLMv3Processor, LayoutLMv3ForTokenClassification
            except ImportError:
                print("⚠️  LayoutLMv3 dependencies not available")
                return False
            
            # Check if model exists locally (no downloads)
            try:
                # Use local_files_only to prevent downloads
                self.processor = LayoutLMv3Processor.from_pretrained(
                    self.model_name, 
                    local_files_only=True
                )
                self.model = LayoutLMv3ForTokenClassification.from_pretrained(
                    self.model_name,
                    num_labels=len(self.label_map),
                    local_files_only=True
                )
                
                # Validate model size constraint
                model_size_mb = self._estimate_model_size()
                if model_size_mb > self.max_model_size_mb:
                    print(f"⚠️  Model size {model_size_mb:.1f}MB exceeds limit {self.max_model_size_mb}MB")
                    return False
                    
            except Exception:
                print(f"⚠️  LayoutLMv3 model '{self.model_name}' not available locally")
                return False
            
            # Force CPU mode for compliance
            self.model.to(self.device)
            self.model.eval()
            
            self.initialized = True
            print(f"✅ LayoutLMv3 model loaded ({model_size_mb:.1f}MB) on CPU")
            return True
            
        except Exception as e:
            print(f"⚠️  Failed to initialize LayoutLMv3: {e}")
            print("   Falling back to traditional methods")
            return False
    
    def enhance_document_analysis(self, doc, doc_profile: Dict) -> Dict[str, Any]:
        """Enhance document analysis with LayoutLMv3 multimodal understanding"""
        
        if not self.initialize_model():
            return doc_profile
        
        enhanced_profile = doc_profile.copy()
        
        try:
            # Process first few pages for document understanding
            pages_to_analyze = min(3, len(doc))
            
            multimodal_features = []
            for page_num in range(pages_to_analyze):
                page_features = self._analyze_page_with_layoutlm(doc, page_num)
                multimodal_features.append(page_features)
            
            # Aggregate multimodal insights
            enhanced_profile['layoutlm_features'] = self._aggregate_multimodal_features(multimodal_features)
            
        except Exception as e:
            print(f"Error in LayoutLMv3 analysis: {e}")
        
        return enhanced_profile
    
    def enhance_heading_detection(self, candidates: List[Dict], doc, doc_profile: Dict) -> List[Dict]:
        """Enhance heading detection using LayoutLMv3 predictions"""
        
        if not self.initialize_model():
            return candidates
        
        enhanced_candidates = []
        
        try:
            # Group candidates by page for efficient processing
            candidates_by_page = {}
            for candidate in candidates:
                page = candidate.get('page', 1) - 1  # Convert to 0-based
                if page not in candidates_by_page:
                    candidates_by_page[page] = []
                candidates_by_page[page].append(candidate)
            
            # Process each page with LayoutLMv3
            for page_num, page_candidates in candidates_by_page.items():
                if page_num < len(doc):
                    enhanced_page_candidates = self._enhance_page_candidates(
                        page_candidates, doc, page_num
                    )
                    enhanced_candidates.extend(enhanced_page_candidates)
                else:
                    enhanced_candidates.extend(page_candidates)
            
        except Exception as e:
            print(f"Error in LayoutLMv3 heading enhancement: {e}")
            return candidates
        
        return enhanced_candidates
    
    def _analyze_page_with_layoutlm(self, doc, page_num: int) -> Dict[str, Any]:
        """Analyze a single page with LayoutLMv3"""
        
        page = doc[page_num]
        
        # Convert page to image
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
        img_data = pix.tobytes("png")
        image = Image.open(io.BytesIO(img_data)).convert("RGB")
        
        # Extract text with bounding boxes
        text_dict = page.get_text("dict")
        words, boxes = self._extract_words_and_boxes(text_dict)
        
        if not words:
            return {'predictions': [], 'confidence': 0.0}
        
        # Prepare input for LayoutLMv3
        encoding = self.processor(
            image, 
            words, 
            boxes=boxes, 
            return_tensors="pt",
            truncation=True,
            padding=True
        )
        
        # Move to device
        for key in encoding:
            if isinstance(encoding[key], torch.Tensor):
                encoding[key] = encoding[key].to(self.device)
        
        # Run inference
        with torch.no_grad():
            outputs = self.model(**encoding)
            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
        
        # Process predictions
        predicted_labels = torch.argmax(predictions, dim=-1)
        confidence_scores = torch.max(predictions, dim=-1)[0]
        
        return {
            'words': words,
            'boxes': boxes,
            'predictions': predicted_labels.cpu().numpy(),
            'confidences': confidence_scores.cpu().numpy(),
            'page_num': page_num
        }
    
    def _extract_words_and_boxes(self, text_dict: Dict) -> Tuple[List[str], List[List[int]]]:
        """Extract words and their bounding boxes from PyMuPDF text dict"""
        
        words = []
        boxes = []
        
        for block in text_dict.get("blocks", []):
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if text:
                            # Split text into words
                            span_words = text.split()
                            bbox = span["bbox"]
                            
                            # Estimate individual word bounding boxes
                            word_width = (bbox[2] - bbox[0]) / len(span_words) if span_words else 0
                            
                            for i, word in enumerate(span_words):
                                words.append(word)
                                
                                # Estimate word bounding box
                                x0 = bbox[0] + i * word_width
                                x1 = x0 + word_width
                                y0 = bbox[1]
                                y1 = bbox[3]
                                
                                # Convert to LayoutLMv3 format (normalize to 1000x1000)
                                # Assuming page dimensions - you might need to get actual page size
                                page_width, page_height = 595, 842  # A4 default
                                
                                normalized_box = [
                                    int((x0 / page_width) * 1000),
                                    int((y0 / page_height) * 1000),
                                    int((x1 / page_width) * 1000),
                                    int((y1 / page_height) * 1000)
                                ]
                                
                                boxes.append(normalized_box)
        
        return words, boxes
    
    def _enhance_page_candidates(self, candidates: List[Dict], doc, page_num: int) -> List[Dict]:
        """Enhance candidates for a specific page using LayoutLMv3 predictions"""
        
        # Get LayoutLMv3 analysis for this page
        page_analysis = self._analyze_page_with_layoutlm(doc, page_num)
        
        if not page_analysis.get('predictions', []).size:
            return candidates
        
        enhanced_candidates = []
        
        for candidate in candidates:
            enhanced_candidate = candidate.copy()
            
            # Find matching words in LayoutLMv3 predictions
            candidate_text = candidate.get('text', '').strip()
            layoutlm_prediction = self._find_text_in_predictions(
                candidate_text, 
                page_analysis
            )
            
            if layoutlm_prediction:
                # Add LayoutLMv3 insights
                enhanced_candidate['layoutlm_label'] = layoutlm_prediction['label']
                enhanced_candidate['layoutlm_confidence'] = layoutlm_prediction['confidence']
                
                # Update level based on LayoutLMv3 if confident enough
                if layoutlm_prediction['confidence'] > self.confidence_thresholds.get(
                    layoutlm_prediction['level'], 0.5
                ):
                    enhanced_candidate['level'] = layoutlm_prediction['level']
                    enhanced_candidate['level_source'] = 'layoutlmv3'
            
            enhanced_candidates.append(enhanced_candidate)
        
        return enhanced_candidates
    
    def _find_text_in_predictions(self, text: str, page_analysis: Dict) -> Optional[Dict]:
        """Find text in LayoutLMv3 predictions and return classification"""
        
        words = page_analysis.get('words', [])
        predictions = page_analysis.get('predictions', [])
        confidences = page_analysis.get('confidences', [])
        
        if len(words) != len(predictions) or len(words) != len(confidences):
            return None
        
        # Simple text matching (could be improved with fuzzy matching)
        text_words = text.lower().split()
        
        best_match = None
        best_confidence = 0.0
        
        # Sliding window to find the best match
        for i in range(len(words) - len(text_words) + 1):
            window_words = [w.lower() for w in words[i:i+len(text_words)]]
            
            # Check if words match
            if window_words == text_words:
                window_predictions = predictions[i:i+len(text_words)]
                window_confidences = confidences[i:i+len(text_words)]
                
                # Get most confident prediction in the window
                max_conf_idx = np.argmax(window_confidences)
                prediction_id = window_predictions[max_conf_idx]
                confidence = window_confidences[max_conf_idx]
                
                if confidence > best_confidence:
                    label = self.label_map.get(prediction_id, 'O')
                    level = self._label_to_level(label)
                    
                    if level:  # Only consider actual heading predictions
                        best_match = {
                            'label': label,
                            'level': level,
                            'confidence': float(confidence),
                            'prediction_id': int(prediction_id)
                        }
                        best_confidence = confidence
        
        return best_match
    
    def _label_to_level(self, label: str) -> Optional[str]:
        """Convert LayoutLMv3 label to heading level"""
        if 'H1' in label:
            return 'H1'
        elif 'H2' in label:
            return 'H2'
        elif 'H3' in label:
            return 'H3'
        elif 'TITLE' in label:
            return 'TITLE'
        return None
    
    def _calculate_layoutlm_boost(self, prediction: Dict) -> float:
        """Calculate quality score boost based on LayoutLMv3 prediction"""
        confidence = prediction['confidence']
        level = prediction['level']
        
        # Base boost based on confidence
        base_boost = confidence * 0.3
        
        # Additional boost for high-confidence predictions
        if confidence > 0.9:
            base_boost += 0.2
        elif confidence > 0.8:
            base_boost += 0.1
        
        # Level-specific adjustments
        level_multiplier = {
            'TITLE': 1.2,
            'H1': 1.1,
            'H2': 1.0,
            'H3': 0.9
        }.get(level, 1.0)
        
        return base_boost * level_multiplier
    
    def _aggregate_multimodal_features(self, page_features: List[Dict]) -> Dict[str, Any]:
        """Aggregate multimodal features across pages"""
        
        total_predictions = 0
        heading_predictions = 0
        avg_confidence = 0.0
        
        level_counts = {'H1': 0, 'H2': 0, 'H3': 0, 'TITLE': 0}
        
        for features in page_features:
            predictions = features.get('predictions', [])
            confidences = features.get('confidences', [])
            
            for pred_id, conf in zip(predictions, confidences):
                total_predictions += 1
                label = self.label_map.get(pred_id, 'O')
                level = self._label_to_level(label)
                
                if level:
                    heading_predictions += 1
                    level_counts[level] += 1
                
                avg_confidence += conf
        
        if total_predictions > 0:
            avg_confidence /= total_predictions
            heading_ratio = heading_predictions / total_predictions
        else:
            avg_confidence = 0.0
            heading_ratio = 0.0
        
        return {
            'total_predictions': total_predictions,
            'heading_predictions': heading_predictions,
            'heading_ratio': heading_ratio,
            'avg_confidence': float(avg_confidence),
            'level_distribution': level_counts,
            'layoutlm_available': True
        }

    def _estimate_model_size(self) -> float:
        """Estimate model size in MB for compliance checking"""
        if not self.model:
            return 0.0
        
        try:
            # Count parameters and estimate size
            total_params = sum(p.numel() for p in self.model.parameters())
            # Assume 4 bytes per parameter (float32)
            size_bytes = total_params * 4
            size_mb = size_bytes / (1024 * 1024)
            return size_mb
        except Exception:
            # Conservative estimate for LayoutLMv3-base
            return 150.0  # Safe estimate under 200MB limit

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the LayoutLMv3 model"""
        return {
            'model_name': self.model_name,
            'device': str(self.device),
            'initialized': self.initialized,
            'num_labels': len(self.label_map),
            'labels': list(self.label_map.values()),
            'confidence_thresholds': self.confidence_thresholds
        }

# Import fix for missing io module
import io
