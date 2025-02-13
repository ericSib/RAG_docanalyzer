"""
Anomaly detection module for identifying potential issues in document content and structure.
"""
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import spacy
from textblob import TextBlob
import re
from loguru import logger
from dataclasses import dataclass
from enum import Enum

class AnomalyType(Enum):
    CONTENT_QUALITY = "content_quality"
    STRUCTURAL = "structural"
    SEMANTIC = "semantic"
    STATISTICAL = "statistical"
    FORMATTING = "formatting"

@dataclass
class Anomaly:
    type: AnomalyType
    description: str
    severity: float  # 0.0 to 1.0
    location: Dict[str, Any]  # Contains location information (e.g., chunk_id, line_number, etc.)
    context: Optional[str] = None
    suggested_action: Optional[str] = None

class AnomalyDetector:
    def __init__(self):
        """Initialize the anomaly detector with required models and configurations."""
        self.nlp = spacy.load("en_core_web_sm")
        self.scaler = StandardScaler()
        self.isolation_forest = IsolationForest(
            contamination=0.1,
            random_state=42
        )
        
    def detect_anomalies(self, document_content: str, chunks: List[Dict]) -> List[Anomaly]:
        """
        Detect various types of anomalies in the document content and chunks.
        
        Args:
            document_content: The full document content
            chunks: List of document chunks with their metadata
            
        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        # Content quality anomalies
        anomalies.extend(self._detect_content_quality_anomalies(document_content, chunks))
        
        # Structural anomalies
        anomalies.extend(self._detect_structural_anomalies(chunks))
        
        # Semantic anomalies
        anomalies.extend(self._detect_semantic_anomalies(chunks))
        
        # Statistical anomalies
        anomalies.extend(self._detect_statistical_anomalies(chunks))
        
        # Formatting anomalies
        anomalies.extend(self._detect_formatting_anomalies(document_content, chunks))
        
        return anomalies
    
    def _detect_content_quality_anomalies(
        self, content: str, chunks: List[Dict]
    ) -> List[Anomaly]:
        """Detect anomalies related to content quality."""
        anomalies = []
        
        # Analyze each chunk for content quality issues
        for i, chunk in enumerate(chunks):
            chunk_content = chunk['content']
            
            # Check for empty or very short chunks
            if len(chunk_content.strip()) < 50:
                anomalies.append(Anomaly(
                    type=AnomalyType.CONTENT_QUALITY,
                    description="Unusually short content chunk",
                    severity=0.7,
                    location={"chunk_id": i},
                    suggested_action="Review chunk size configuration or content splitting logic"
                ))
            
            # Check for repetitive content
            if self._is_content_repetitive(chunk_content):
                anomalies.append(Anomaly(
                    type=AnomalyType.CONTENT_QUALITY,
                    description="Repetitive content detected",
                    severity=0.6,
                    location={"chunk_id": i},
                    context=chunk_content[:100] + "..."
                ))
            
            # Check for gibberish or low-quality content
            quality_score = self._assess_content_quality(chunk_content)
            if quality_score < 0.5:
                anomalies.append(Anomaly(
                    type=AnomalyType.CONTENT_QUALITY,
                    description="Low quality or potentially corrupted content",
                    severity=0.8,
                    location={"chunk_id": i},
                    context=chunk_content[:100] + "..."
                ))
        
        return anomalies
    
    def _detect_structural_anomalies(self, chunks: List[Dict]) -> List[Anomaly]:
        """Detect anomalies in document structure."""
        anomalies = []
        
        # Analyze chunk transitions
        for i in range(len(chunks) - 1):
            current_chunk = chunks[i]
            next_chunk = chunks[i + 1]
            
            # Check for abrupt topic changes
            if self._is_topic_break(current_chunk['content'], next_chunk['content']):
                anomalies.append(Anomaly(
                    type=AnomalyType.STRUCTURAL,
                    description="Abrupt topic change between chunks",
                    severity=0.5,
                    location={"chunk_id": i, "next_chunk_id": i + 1}
                ))
            
            # Check for broken sentences at chunk boundaries
            if self._has_broken_sentence_boundary(current_chunk['content'], next_chunk['content']):
                anomalies.append(Anomaly(
                    type=AnomalyType.STRUCTURAL,
                    description="Sentence broken at chunk boundary",
                    severity=0.6,
                    location={"chunk_id": i, "next_chunk_id": i + 1},
                    suggested_action="Adjust chunk boundaries to respect sentence boundaries"
                ))
        
        return anomalies
    
    def _detect_semantic_anomalies(self, chunks: List[Dict]) -> List[Anomaly]:
        """Detect semantic anomalies in content."""
        anomalies = []
        
        for i, chunk in enumerate(chunks):
            content = chunk['content']
            doc = self.nlp(content)
            
            # Check for semantic consistency
            blob = TextBlob(content)
            
            # Detect sentiment inconsistencies
            sentiment_scores = [sentence.sentiment.polarity for sentence in blob.sentences]
            if len(sentiment_scores) > 1:
                sentiment_std = np.std(sentiment_scores)
                if sentiment_std > 0.5:  # High sentiment variance
                    anomalies.append(Anomaly(
                        type=AnomalyType.SEMANTIC,
                        description="High sentiment variance within chunk",
                        severity=0.4,
                        location={"chunk_id": i}
                    ))
            
            # Check for contextual inconsistencies
            if self._has_contextual_inconsistency(doc):
                anomalies.append(Anomaly(
                    type=AnomalyType.SEMANTIC,
                    description="Potential contextual inconsistency detected",
                    severity=0.7,
                    location={"chunk_id": i},
                    context=content[:100] + "..."
                ))
        
        return anomalies
    
    def _detect_statistical_anomalies(self, chunks: List[Dict]) -> List[Anomaly]:
        """Detect statistical anomalies using isolation forest."""
        anomalies = []
        
        # Extract numerical features from chunks
        features = []
        for chunk in chunks:
            features.append(self._extract_chunk_features(chunk))
        
        if not features:
            return anomalies
        
        # Prepare features for anomaly detection
        X = np.array(features)
        X_scaled = self.scaler.fit_transform(X)
        
        # Detect anomalies using Isolation Forest
        predictions = self.isolation_forest.fit_predict(X_scaled)
        
        # Process anomalies
        for i, pred in enumerate(predictions):
            if pred == -1:  # Anomaly detected
                anomalies.append(Anomaly(
                    type=AnomalyType.STATISTICAL,
                    description="Statistical outlier detected in chunk",
                    severity=0.6,
                    location={"chunk_id": i},
                    context=f"Unusual statistical properties in chunk content"
                ))
        
        return anomalies
    
    def _detect_formatting_anomalies(
        self, content: str, chunks: List[Dict]
    ) -> List[Anomaly]:
        """Detect formatting and style anomalies."""
        anomalies = []
        
        for i, chunk in enumerate(chunks):
            chunk_content = chunk['content']
            
            # Check for inconsistent spacing
            if self._has_inconsistent_spacing(chunk_content):
                anomalies.append(Anomaly(
                    type=AnomalyType.FORMATTING,
                    description="Inconsistent spacing detected",
                    severity=0.3,
                    location={"chunk_id": i},
                    suggested_action="Normalize spacing in content"
                ))
            
            # Check for unusual character sequences
            unusual_chars = self._find_unusual_characters(chunk_content)
            if unusual_chars:
                anomalies.append(Anomaly(
                    type=AnomalyType.FORMATTING,
                    description="Unusual character sequences detected",
                    severity=0.5,
                    location={"chunk_id": i},
                    context=f"Characters: {unusual_chars}"
                ))
            
            # Check for inconsistent line endings
            if self._has_inconsistent_line_endings(chunk_content):
                anomalies.append(Anomaly(
                    type=AnomalyType.FORMATTING,
                    description="Inconsistent line endings",
                    severity=0.4,
                    location={"chunk_id": i},
                    suggested_action="Normalize line endings"
                ))
        
        return anomalies
    
    def _is_content_repetitive(self, content: str) -> bool:
        """Check if content contains repetitive patterns."""
        # Convert to lowercase and split into words
        words = content.lower().split()
        if len(words) < 10:
            return False
            
        # Check for repeated word sequences
        for i in range(len(words) - 3):
            sequence = " ".join(words[i:i+3])
            if content.lower().count(sequence) > 2:
                return True
                
        return False
    
    def _assess_content_quality(self, content: str) -> float:
        """Assess the overall quality of content."""
        try:
            # Basic quality checks
            if not content.strip():
                return 0.0
                
            # Check for coherent sentences
            blob = TextBlob(content)
            if not blob.sentences:
                return 0.2
                
            # Calculate quality metrics
            words = content.split()
            unique_words = len(set(words))
            total_words = len(words)
            
            if total_words == 0:
                return 0.0
                
            # Vocabulary richness
            vocabulary_richness = unique_words / total_words
            
            # Sentence structure quality
            doc = self.nlp(content)
            has_verbs = any(token.pos_ == "VERB" for token in doc)
            has_nouns = any(token.pos_ == "NOUN" for token in doc)
            
            # Combine metrics
            quality_score = (
                vocabulary_richness * 0.4 +
                (1.0 if has_verbs else 0.0) * 0.3 +
                (1.0 if has_nouns else 0.0) * 0.3
            )
            
            return min(1.0, max(0.0, quality_score))
            
        except Exception as e:
            logger.error(f"Error assessing content quality: {str(e)}")
            return 0.0
    
    def _is_topic_break(self, content1: str, content2: str) -> bool:
        """Detect if there's an abrupt topic change between contents."""
        try:
            doc1 = self.nlp(content1)
            doc2 = self.nlp(content2)
            
            # Compare document similarities
            similarity = doc1.similarity(doc2)
            return similarity < 0.3  # Threshold for topic break
            
        except Exception as e:
            logger.error(f"Error detecting topic break: {str(e)}")
            return False
    
    def _has_broken_sentence_boundary(self, content1: str, content2: str) -> bool:
        """Check if there's a broken sentence at the boundary."""
        # Check if first content ends with sentence terminator
        if not re.search(r'[.!?]\s*$', content1):
            # Check if next content starts with lowercase letter
            if re.match(r'^\s*[a-z]', content2):
                return True
        return False
    
    def _has_contextual_inconsistency(self, doc: spacy.tokens.Doc) -> bool:
        """Detect contextual inconsistencies in content."""
        try:
            # Check for conflicting named entities
            entity_groups = {}
            for ent in doc.ents:
                if ent.label_ not in entity_groups:
                    entity_groups[ent.label_] = set()
                entity_groups[ent.label_].add(ent.text.lower())
                
            # Check for multiple different locations or dates in same context
            for label in ['DATE', 'GPE', 'LOC']:
                if label in entity_groups and len(entity_groups[label]) > 2:
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"Error checking contextual inconsistency: {str(e)}")
            return False
    
    def _extract_chunk_features(self, chunk: Dict) -> List[float]:
        """Extract numerical features from a chunk for statistical analysis."""
        content = chunk['content']
        doc = self.nlp(content)
        
        return [
            len(content),  # Content length
            len(content.split()),  # Word count
            len(set(content.lower().split())),  # Unique word count
            len(list(doc.sents)),  # Sentence count
            sum(1 for _ in doc.ents),  # Named entity count
            sum(1 for token in doc if token.is_stop),  # Stop word count
            sum(1 for token in doc if token.pos_ == "VERB"),  # Verb count
            sum(1 for token in doc if token.pos_ == "NOUN"),  # Noun count
        ]
    
    def _has_inconsistent_spacing(self, content: str) -> bool:
        """Check for inconsistent spacing patterns."""
        # Check for multiple consecutive spaces
        if re.search(r' {2,}', content):
            return True
            
        # Check for inconsistent spacing around punctuation
        if re.search(r'\s+[.,!?]|[.,!?]\s+[.,!?]', content):
            return True
            
        return False
    
    def _find_unusual_characters(self, content: str) -> str:
        """Find unusual or potentially problematic characters."""
        unusual_chars = []
        
        # Check for non-printing characters
        for char in content:
            if ord(char) < 32 and char not in '\n\t\r':
                unusual_chars.append(f"\\x{ord(char):02x}")
                
        # Check for Unicode control characters
        control_chars = re.findall(r'[\x00-\x1F\x7F-\x9F]', content)
        unusual_chars.extend(control_chars)
        
        return "".join(set(unusual_chars))
    
    def _has_inconsistent_line_endings(self, content: str) -> bool:
        """Check for mixed line endings."""
        endings = re.findall(r'\r\n|\r|\n', content)
        return len(set(endings)) > 1
        
    def get_anomaly_summary(self, anomalies: List[Anomaly]) -> Dict[str, Any]:
        """
        Generate a summary of detected anomalies.
        
        Args:
            anomalies: List of detected anomalies
            
        Returns:
            Dictionary containing anomaly statistics and highlights
        """
        summary = {
            "total_anomalies": len(anomalies),
            "by_type": {},
            "by_severity": {
                "high": [],
                "medium": [],
                "low": []
            },
            "critical_issues": []
        }
        
        # Group anomalies by type
        for anomaly in anomalies:
            # Count by type
            if anomaly.type.value not in summary["by_type"]:
                summary["by_type"][anomaly.type.value] = 0
            summary["by_type"][anomaly.type.value] += 1
            
            # Group by severity
            if anomaly.severity >= 0.7:
                summary["by_severity"]["high"].append(anomaly)
                if anomaly.severity >= 0.8:
                    summary["critical_issues"].append(anomaly)
            elif anomaly.severity >= 0.4:
                summary["by_severity"]["medium"].append(anomaly)
            else:
                summary["by_severity"]["low"].append(anomaly)
        
        return summary
