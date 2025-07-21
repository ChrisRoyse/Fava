"""
AI-Powered Security Analytics and Anomaly Detection for Fava PQC.

This module provides advanced security analytics using machine learning to detect
anomalies, threats, and suspicious patterns in cryptographic operations and system behavior.
"""

import json
import logging
import time
import numpy as np
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Callable
from datetime import datetime, timezone, timedelta
from enum import Enum
import threading
import uuid
from pathlib import Path
import pickle
import hashlib
from collections import deque, defaultdict
import statistics
import math

from .dependency_manager import DependencyManager, enterprise_feature
from .monitoring import get_audit_logger, get_metrics_collector

logger = logging.getLogger(__name__)


class AnomalyType(Enum):
    """Types of security anomalies."""
    CRYPTO_OPERATION_ANOMALY = "crypto_operation_anomaly"
    ACCESS_PATTERN_ANOMALY = "access_pattern_anomaly"
    PERFORMANCE_ANOMALY = "performance_anomaly"
    BEHAVIORAL_ANOMALY = "behavioral_anomaly"
    NETWORK_ANOMALY = "network_anomaly"
    AUTHENTICATION_ANOMALY = "authentication_anomaly"
    KEY_USAGE_ANOMALY = "key_usage_anomaly"
    TIMING_ANOMALY = "timing_anomaly"


class ThreatLevel(Enum):
    """Threat severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ModelType(Enum):
    """Types of ML models for different analysis."""
    ISOLATION_FOREST = "isolation_forest"
    ONE_CLASS_SVM = "one_class_svm"
    AUTOENCODER = "autoencoder"
    STATISTICAL_BASELINE = "statistical_baseline"
    LSTM_SEQUENCE = "lstm_sequence"
    CLUSTERING = "clustering"


@dataclass
class SecurityEvent:
    """A security event for analysis."""
    event_id: str
    timestamp: float
    event_type: str
    source: str
    features: Dict[str, Any]
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None


@dataclass
class AnomalyDetection:
    """Result of anomaly detection analysis."""
    detection_id: str
    timestamp: float
    anomaly_type: AnomalyType
    threat_level: ThreatLevel
    confidence_score: float  # 0.0 to 1.0
    event_ids: List[str]
    description: str
    features_analyzed: List[str]
    baseline_deviation: Dict[str, float]
    recommended_actions: List[str] = field(default_factory=list)
    related_detections: List[str] = field(default_factory=list)
    false_positive_probability: float = 0.0


@dataclass
class ModelMetrics:
    """Metrics for ML model performance."""
    model_id: str
    model_type: ModelType
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    false_positive_rate: float
    training_samples: int
    last_updated: float
    feature_importance: Dict[str, float] = field(default_factory=dict)


class FeatureExtractor:
    """Extract features from security events for ML analysis."""
    
    def __init__(self):
        self.feature_history = defaultdict(deque)
        self.max_history_size = 10000
    
    def extract_crypto_features(self, event: SecurityEvent) -> Dict[str, float]:
        """Extract features from cryptographic operations."""
        features = {}
        
        try:
            # Basic timing features
            if 'duration' in event.features:
                features['operation_duration'] = float(event.features['duration'])
            
            # Key size and algorithm features
            if 'algorithm' in event.features:
                algorithm = event.features['algorithm']
                features['algorithm_kyber'] = 1.0 if 'kyber' in algorithm.lower() else 0.0
                features['algorithm_dilithium'] = 1.0 if 'dilithium' in algorithm.lower() else 0.0
                features['algorithm_sphincs'] = 1.0 if 'sphincs' in algorithm.lower() else 0.0
            
            # Operation type features
            if 'operation' in event.features:
                operation = event.features['operation']
                features['op_keygen'] = 1.0 if 'keygen' in operation.lower() else 0.0
                features['op_encrypt'] = 1.0 if 'encrypt' in operation.lower() else 0.0
                features['op_sign'] = 1.0 if 'sign' in operation.lower() else 0.0
                features['op_verify'] = 1.0 if 'verify' in operation.lower() else 0.0
            
            # Success/failure patterns
            if 'outcome' in event.features:
                features['success'] = 1.0 if event.features['outcome'] == 'success' else 0.0
            
            # Memory and CPU usage if available
            if 'memory_usage' in event.features:
                features['memory_usage'] = float(event.features['memory_usage'])
            
            if 'cpu_usage' in event.features:
                features['cpu_usage'] = float(event.features['cpu_usage'])
            
            # Time-based features
            dt = datetime.fromtimestamp(event.timestamp)
            features['hour_of_day'] = float(dt.hour)
            features['day_of_week'] = float(dt.weekday())
            features['is_weekend'] = 1.0 if dt.weekday() >= 5 else 0.0
            features['is_business_hours'] = 1.0 if 9 <= dt.hour <= 17 else 0.0
            
            return features
            
        except Exception as e:
            logger.error(f"Failed to extract crypto features: {e}")
            return {}
    
    def extract_access_features(self, event: SecurityEvent) -> Dict[str, float]:
        """Extract features from access pattern events."""
        features = {}
        
        try:
            # User behavior features
            if event.user_id:
                user_history = self.feature_history[f"user_{event.user_id}"]
                if user_history:
                    recent_events = list(user_history)[-100:]  # Last 100 events
                    features['user_event_frequency'] = len(recent_events) / max(1, 
                        (event.timestamp - recent_events[0][0]) / 3600)  # events per hour
                else:
                    features['user_event_frequency'] = 0.0
                
                features['new_user'] = 1.0 if len(user_history) < 10 else 0.0
            
            # Session features
            if event.session_id:
                session_key = f"session_{event.session_id}"
                session_history = self.feature_history[session_key]
                features['session_length'] = len(session_history)
                features['new_session'] = 1.0 if len(session_history) == 0 else 0.0
            
            # IP address features
            if event.ip_address:
                ip_history = self.feature_history[f"ip_{event.ip_address}"]
                features['ip_reputation'] = min(1.0, len(ip_history) / 100.0)  # Normalized
                features['new_ip'] = 1.0 if len(ip_history) < 5 else 0.0
            
            # Resource access patterns
            if 'resource' in event.features:
                resource = event.features['resource']
                features['admin_resource'] = 1.0 if 'admin' in resource.lower() else 0.0
                features['crypto_resource'] = 1.0 if 'crypto' in resource.lower() else 0.0
                features['key_resource'] = 1.0 if 'key' in resource.lower() else 0.0
            
            # Authentication method features
            if 'auth_method' in event.features:
                auth_method = event.features['auth_method']
                features['mfa_auth'] = 1.0 if 'mfa' in auth_method.lower() else 0.0
                features['cert_auth'] = 1.0 if 'cert' in auth_method.lower() else 0.0
                features['password_auth'] = 1.0 if 'password' in auth_method.lower() else 0.0
            
            return features
            
        except Exception as e:
            logger.error(f"Failed to extract access features: {e}")
            return {}
    
    def extract_performance_features(self, event: SecurityEvent) -> Dict[str, float]:
        """Extract features from performance events."""
        features = {}
        
        try:
            # Response time features
            if 'response_time' in event.features:
                features['response_time'] = float(event.features['response_time'])
            
            # Throughput features
            if 'throughput' in event.features:
                features['throughput'] = float(event.features['throughput'])
            
            # Error rate features
            if 'error_rate' in event.features:
                features['error_rate'] = float(event.features['error_rate'])
            
            # Resource utilization
            if 'cpu_utilization' in event.features:
                features['cpu_utilization'] = float(event.features['cpu_utilization'])
            
            if 'memory_utilization' in event.features:
                features['memory_utilization'] = float(event.features['memory_utilization'])
            
            # System load features
            if 'system_load' in event.features:
                features['system_load'] = float(event.features['system_load'])
            
            return features
            
        except Exception as e:
            logger.error(f"Failed to extract performance features: {e}")
            return {}
    
    def update_feature_history(self, event: SecurityEvent, features: Dict[str, float]):
        """Update feature history for context-aware analysis."""
        try:
            timestamp = event.timestamp
            
            # Update user history
            if event.user_id:
                user_key = f"user_{event.user_id}"
                self.feature_history[user_key].append((timestamp, features))
                self._trim_history(user_key)
            
            # Update session history
            if event.session_id:
                session_key = f"session_{event.session_id}"
                self.feature_history[session_key].append((timestamp, features))
                self._trim_history(session_key)
            
            # Update IP history
            if event.ip_address:
                ip_key = f"ip_{event.ip_address}"
                self.feature_history[ip_key].append((timestamp, features))
                self._trim_history(ip_key)
                
        except Exception as e:
            logger.error(f"Failed to update feature history: {e}")
    
    def _trim_history(self, key: str):
        """Trim feature history to max size."""
        history = self.feature_history[key]
        while len(history) > self.max_history_size:
            history.popleft()


class StatisticalAnomalyDetector:
    """Statistical anomaly detection using baseline analysis."""
    
    def __init__(self):
        self.baselines = {}
        self.min_samples = 50
        self.z_score_threshold = 3.0
    
    def update_baseline(self, feature_name: str, value: float):
        """Update statistical baseline for a feature."""
        if feature_name not in self.baselines:
            self.baselines[feature_name] = {'values': deque(maxlen=1000), 'stats': {}}
        
        self.baselines[feature_name]['values'].append(value)
        self._recalculate_stats(feature_name)
    
    def detect_anomaly(self, features: Dict[str, float]) -> Dict[str, float]:
        """Detect anomalies using statistical analysis."""
        anomaly_scores = {}
        
        for feature_name, value in features.items():
            if feature_name in self.baselines:
                baseline = self.baselines[feature_name]
                if len(baseline['values']) >= self.min_samples:
                    stats = baseline['stats']
                    if stats['std'] > 0:
                        z_score = abs((value - stats['mean']) / stats['std'])
                        anomaly_scores[feature_name] = min(1.0, z_score / self.z_score_threshold)
                    else:
                        anomaly_scores[feature_name] = 0.0
                else:
                    anomaly_scores[feature_name] = 0.0  # Not enough data
            else:
                anomaly_scores[feature_name] = 0.5  # Unknown feature
        
        return anomaly_scores
    
    def _recalculate_stats(self, feature_name: str):
        """Recalculate statistics for a feature."""
        try:
            values = list(self.baselines[feature_name]['values'])
            if len(values) >= 2:
                self.baselines[feature_name]['stats'] = {
                    'mean': statistics.mean(values),
                    'std': statistics.stdev(values),
                    'median': statistics.median(values),
                    'min': min(values),
                    'max': max(values),
                    'count': len(values)
                }
            
        except Exception as e:
            logger.error(f"Failed to recalculate stats for {feature_name}: {e}")


class MachineLearningDetector:
    """Machine learning-based anomaly detection."""
    
    def __init__(self):
        self.dep_manager = DependencyManager()
        self.models = {}
        self.model_metrics = {}
        self.training_data = defaultdict(list)
    
    @enterprise_feature('scikit-learn', fallback_value=None)
    def train_isolation_forest(self, features_list: List[Dict[str, float]], 
                             model_id: str = 'default_isolation_forest') -> bool:
        """Train an Isolation Forest model for anomaly detection."""
        try:
            sklearn = self.dep_manager.get_module('sklearn')
            if not sklearn:
                logger.warning("scikit-learn not available, using fallback detection")
                return False
            
            from sklearn.ensemble import IsolationForest
            from sklearn.preprocessing import StandardScaler
            import pandas as pd
            
            if len(features_list) < 50:
                logger.warning("Insufficient training data for Isolation Forest")
                return False
            
            # Prepare data
            df = pd.DataFrame(features_list)
            df = df.fillna(0.0)  # Handle missing values
            
            # Standardize features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(df)
            
            # Train model
            model = IsolationForest(
                contamination=0.1,  # Expect 10% anomalies
                random_state=42,
                n_estimators=100
            )
            model.fit(X_scaled)
            
            # Store model and scaler
            self.models[model_id] = {
                'model': model,
                'scaler': scaler,
                'feature_names': list(df.columns),
                'model_type': ModelType.ISOLATION_FOREST,
                'trained_at': time.time()
            }
            
            logger.info(f"Trained Isolation Forest model '{model_id}' on {len(features_list)} samples")
            return True
            
        except Exception as e:
            logger.error(f"Failed to train Isolation Forest: {e}")
            return False
    
    @enterprise_feature('scikit-learn', fallback_value=None)
    def train_one_class_svm(self, features_list: List[Dict[str, float]], 
                           model_id: str = 'default_svm') -> bool:
        """Train a One-Class SVM for anomaly detection."""
        try:
            sklearn = self.dep_manager.get_module('sklearn')
            if not sklearn:
                return False
            
            from sklearn.svm import OneClassSVM
            from sklearn.preprocessing import StandardScaler
            import pandas as pd
            
            if len(features_list) < 30:
                logger.warning("Insufficient training data for One-Class SVM")
                return False
            
            # Prepare data
            df = pd.DataFrame(features_list)
            df = df.fillna(0.0)
            
            # Standardize features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(df)
            
            # Train model
            model = OneClassSVM(
                kernel='rbf',
                gamma='scale',
                nu=0.1  # Expected fraction of outliers
            )
            model.fit(X_scaled)
            
            # Store model and scaler
            self.models[model_id] = {
                'model': model,
                'scaler': scaler,
                'feature_names': list(df.columns),
                'model_type': ModelType.ONE_CLASS_SVM,
                'trained_at': time.time()
            }
            
            logger.info(f"Trained One-Class SVM model '{model_id}' on {len(features_list)} samples")
            return True
            
        except Exception as e:
            logger.error(f"Failed to train One-Class SVM: {e}")
            return False
    
    def predict_anomaly(self, features: Dict[str, float], model_id: str = 'default_isolation_forest') -> Tuple[float, bool]:
        """Predict anomaly score using trained model."""
        try:
            if model_id not in self.models:
                logger.warning(f"Model '{model_id}' not found")
                return 0.5, False  # Default moderate score
            
            model_info = self.models[model_id]
            model = model_info['model']
            scaler = model_info['scaler']
            feature_names = model_info['feature_names']
            
            # Prepare features
            feature_vector = []
            for name in feature_names:
                feature_vector.append(features.get(name, 0.0))
            
            # Scale features
            X_scaled = scaler.transform([feature_vector])
            
            # Make prediction
            if model_info['model_type'] == ModelType.ISOLATION_FOREST:
                # Isolation Forest returns -1 for anomalies, 1 for normal
                prediction = model.predict(X_scaled)[0]
                anomaly_score = model.decision_function(X_scaled)[0]
                
                # Convert to 0-1 score (higher = more anomalous)
                normalized_score = max(0.0, min(1.0, (0.5 - anomaly_score) * 2))
                is_anomaly = prediction == -1
                
            elif model_info['model_type'] == ModelType.ONE_CLASS_SVM:
                # One-Class SVM returns -1 for anomalies, 1 for normal
                prediction = model.predict(X_scaled)[0]
                anomaly_score = model.decision_function(X_scaled)[0]
                
                # Convert to 0-1 score
                normalized_score = max(0.0, min(1.0, (0.0 - anomaly_score) + 0.5))
                is_anomaly = prediction == -1
            
            else:
                normalized_score = 0.5
                is_anomaly = False
            
            return normalized_score, is_anomaly
            
        except Exception as e:
            logger.error(f"Failed to predict anomaly: {e}")
            return 0.5, False


class ThreatIntelligenceEngine:
    """Threat intelligence and pattern recognition engine."""
    
    def __init__(self):
        self.known_attack_patterns = {}
        self.threat_indicators = defaultdict(list)
        self.load_threat_patterns()
    
    def load_threat_patterns(self):
        """Load known attack patterns and threat indicators."""
        # Common PQC-specific attack patterns
        self.known_attack_patterns = {
            'side_channel_timing': {
                'description': 'Potential timing side-channel attack',
                'indicators': [
                    'repeated_similar_operations',
                    'precise_timing_measurements',
                    'unusual_operation_frequency'
                ],
                'severity': ThreatLevel.HIGH
            },
            'key_extraction_attempt': {
                'description': 'Potential key extraction attack',
                'indicators': [
                    'multiple_failed_authentications',
                    'systematic_key_access_patterns',
                    'unusual_crypto_operations'
                ],
                'severity': ThreatLevel.CRITICAL
            },
            'quantum_algorithm_probe': {
                'description': 'Potential quantum algorithm analysis',
                'indicators': [
                    'large_scale_crypto_operations',
                    'pattern_analysis_behavior',
                    'systematic_algorithm_testing'
                ],
                'severity': ThreatLevel.HIGH
            },
            'brute_force_attack': {
                'description': 'Brute force attack attempt',
                'indicators': [
                    'high_frequency_operations',
                    'systematic_parameter_variation',
                    'resource_exhaustion_patterns'
                ],
                'severity': ThreatLevel.MEDIUM
            }
        }
    
    def analyze_threat_indicators(self, events: List[SecurityEvent], 
                                detections: List[AnomalyDetection]) -> List[Dict[str, Any]]:
        """Analyze events and detections for threat patterns."""
        threats = []
        
        try:
            # Group events by time windows
            time_windows = self._group_events_by_time(events, window_size=300)  # 5-minute windows
            
            for window_events in time_windows:
                # Check for known attack patterns
                for pattern_name, pattern_info in self.known_attack_patterns.items():
                    threat_score = self._calculate_threat_score(
                        window_events, pattern_info['indicators']
                    )
                    
                    if threat_score > 0.6:  # Threshold for threat detection
                        threats.append({
                            'threat_id': str(uuid.uuid4()),
                            'pattern_name': pattern_name,
                            'description': pattern_info['description'],
                            'severity': pattern_info['severity'].value,
                            'confidence': threat_score,
                            'detected_at': time.time(),
                            'event_count': len(window_events),
                            'event_ids': [e.event_id for e in window_events],
                            'indicators_matched': self._get_matched_indicators(
                                window_events, pattern_info['indicators']
                            )
                        })
            
            # Correlate with anomaly detections
            for detection in detections:
                if detection.threat_level in [ThreatLevel.CRITICAL, ThreatLevel.HIGH]:
                    correlated_threats = self._correlate_with_patterns(detection)
                    threats.extend(correlated_threats)
            
            return threats
            
        except Exception as e:
            logger.error(f"Failed to analyze threat indicators: {e}")
            return []
    
    def _group_events_by_time(self, events: List[SecurityEvent], window_size: int) -> List[List[SecurityEvent]]:
        """Group events into time windows."""
        if not events:
            return []
        
        # Sort events by timestamp
        sorted_events = sorted(events, key=lambda e: e.timestamp)
        
        windows = []
        current_window = []
        window_start = sorted_events[0].timestamp
        
        for event in sorted_events:
            if event.timestamp - window_start <= window_size:
                current_window.append(event)
            else:
                if current_window:
                    windows.append(current_window)
                current_window = [event]
                window_start = event.timestamp
        
        if current_window:
            windows.append(current_window)
        
        return windows
    
    def _calculate_threat_score(self, events: List[SecurityEvent], indicators: List[str]) -> float:
        """Calculate threat score based on indicator presence."""
        if not events or not indicators:
            return 0.0
        
        matched_indicators = 0
        total_indicators = len(indicators)
        
        # Check for indicator patterns in events
        for indicator in indicators:
            if self._check_indicator_presence(events, indicator):
                matched_indicators += 1
        
        # Calculate weighted score
        base_score = matched_indicators / total_indicators
        
        # Apply modifiers based on event characteristics
        frequency_modifier = min(1.0, len(events) / 10.0)  # More events = higher risk
        time_modifier = self._calculate_time_concentration(events)
        
        final_score = base_score * (1 + frequency_modifier * 0.3 + time_modifier * 0.2)
        return min(1.0, final_score)
    
    def _check_indicator_presence(self, events: List[SecurityEvent], indicator: str) -> bool:
        """Check if a threat indicator is present in the events."""
        if indicator == 'repeated_similar_operations':
            # Check for repeated operations
            operations = [e.features.get('operation', '') for e in events]
            return len(set(operations)) < len(operations) * 0.5
        
        elif indicator == 'multiple_failed_authentications':
            # Check for authentication failures
            failures = sum(1 for e in events 
                         if e.event_type == 'authentication' and 
                         e.features.get('outcome') == 'failure')
            return failures > 3
        
        elif indicator == 'high_frequency_operations':
            # Check for high frequency patterns
            if len(events) > 1:
                time_span = events[-1].timestamp - events[0].timestamp
                frequency = len(events) / max(1, time_span / 60)  # operations per minute
                return frequency > 10
        
        elif indicator == 'unusual_operation_frequency':
            # Similar to high frequency but with pattern analysis
            return self._detect_unusual_frequency_patterns(events)
        
        elif indicator == 'systematic_key_access_patterns':
            # Check for systematic key access
            key_operations = [e for e in events if 'key' in e.event_type.lower()]
            return len(key_operations) > len(events) * 0.3
        
        return False
    
    def _detect_unusual_frequency_patterns(self, events: List[SecurityEvent]) -> bool:
        """Detect unusual frequency patterns in events."""
        if len(events) < 5:
            return False
        
        # Calculate inter-event intervals
        intervals = []
        for i in range(1, len(events)):
            interval = events[i].timestamp - events[i-1].timestamp
            intervals.append(interval)
        
        # Check for very regular patterns (possible automation)
        if len(set([round(interval, 1) for interval in intervals])) == 1:
            return True
        
        # Check for exponentially increasing/decreasing patterns
        try:
            avg_interval = statistics.mean(intervals)
            std_interval = statistics.stdev(intervals)
            return std_interval / avg_interval < 0.1  # Very consistent timing
        except:
            return False
    
    def _calculate_time_concentration(self, events: List[SecurityEvent]) -> float:
        """Calculate how concentrated events are in time."""
        if len(events) < 2:
            return 0.0
        
        time_span = events[-1].timestamp - events[0].timestamp
        if time_span == 0:
            return 1.0  # All events at same time
        
        # Higher concentration = higher risk
        return min(1.0, len(events) / (time_span / 60))  # events per minute normalized
    
    def _get_matched_indicators(self, events: List[SecurityEvent], indicators: List[str]) -> List[str]:
        """Get list of matched threat indicators."""
        matched = []
        for indicator in indicators:
            if self._check_indicator_presence(events, indicator):
                matched.append(indicator)
        return matched
    
    def _correlate_with_patterns(self, detection: AnomalyDetection) -> List[Dict[str, Any]]:
        """Correlate anomaly detection with known threat patterns."""
        correlated = []
        
        # Check if anomaly matches known patterns
        for pattern_name, pattern_info in self.known_attack_patterns.items():
            correlation_score = 0.0
            
            # Check anomaly type correlation
            if detection.anomaly_type == AnomalyType.CRYPTO_OPERATION_ANOMALY:
                if pattern_name in ['side_channel_timing', 'key_extraction_attempt']:
                    correlation_score += 0.4
            
            elif detection.anomaly_type == AnomalyType.ACCESS_PATTERN_ANOMALY:
                if pattern_name in ['key_extraction_attempt', 'brute_force_attack']:
                    correlation_score += 0.4
            
            elif detection.anomaly_type == AnomalyType.PERFORMANCE_ANOMALY:
                if pattern_name in ['quantum_algorithm_probe', 'brute_force_attack']:
                    correlation_score += 0.3
            
            # Add confidence score influence
            correlation_score += detection.confidence_score * 0.3
            
            if correlation_score > 0.5:
                correlated.append({
                    'threat_id': str(uuid.uuid4()),
                    'pattern_name': pattern_name,
                    'description': f"Correlated with {detection.anomaly_type.value}",
                    'severity': pattern_info['severity'].value,
                    'confidence': correlation_score,
                    'detected_at': time.time(),
                    'related_detection': detection.detection_id,
                    'correlation_type': 'anomaly_pattern_match'
                })
        
        return correlated


class AISecurityAnalyticsEngine:
    """Main AI-powered security analytics engine."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.dep_manager = DependencyManager()
        self.audit_logger = get_audit_logger()
        self.metrics = get_metrics_collector()
        
        # Initialize components
        self.feature_extractor = FeatureExtractor()
        self.statistical_detector = StatisticalAnomalyDetector()
        self.ml_detector = MachineLearningDetector()
        self.threat_intelligence = ThreatIntelligenceEngine()
        
        # Detection state
        self.recent_events = deque(maxlen=10000)
        self.recent_detections = deque(maxlen=1000)
        self.model_training_queue = []
        
        # Background processing
        self.processing_thread = threading.Thread(target=self._background_analysis_worker, daemon=True)
        self.is_running = True
        self.processing_thread.start()
        
        logger.info("AI Security Analytics Engine initialized")
    
    def analyze_event(self, event: SecurityEvent) -> List[AnomalyDetection]:
        """Analyze a single security event for anomalies."""
        detections = []
        
        try:
            # Extract features based on event type
            features = {}
            
            if 'crypto' in event.event_type.lower():
                features.update(self.feature_extractor.extract_crypto_features(event))
            
            if 'access' in event.event_type.lower() or 'auth' in event.event_type.lower():
                features.update(self.feature_extractor.extract_access_features(event))
            
            if 'performance' in event.event_type.lower():
                features.update(self.feature_extractor.extract_performance_features(event))
            
            if not features:
                logger.debug(f"No features extracted for event {event.event_id}")
                return detections
            
            # Update feature history
            self.feature_extractor.update_feature_history(event, features)
            
            # Statistical anomaly detection
            stat_anomaly_scores = self.statistical_detector.detect_anomaly(features)
            max_stat_score = max(stat_anomaly_scores.values()) if stat_anomaly_scores else 0.0
            
            if max_stat_score > 0.7:  # Statistical anomaly threshold
                detections.append(self._create_statistical_detection(
                    event, features, stat_anomaly_scores, max_stat_score
                ))
            
            # Machine learning anomaly detection
            if self.ml_detector.models:
                for model_id in self.ml_detector.models:
                    ml_score, is_anomaly = self.ml_detector.predict_anomaly(features, model_id)
                    
                    if is_anomaly and ml_score > 0.6:
                        detections.append(self._create_ml_detection(
                            event, features, ml_score, model_id
                        ))
            
            # Update statistical baselines
            for feature_name, value in features.items():
                self.statistical_detector.update_baseline(feature_name, value)
            
            # Store event for batch analysis
            self.recent_events.append(event)
            
            # Store detections
            for detection in detections:
                self.recent_detections.append(detection)
                
                # Log critical detections immediately
                if detection.threat_level in [ThreatLevel.CRITICAL, ThreatLevel.HIGH]:
                    self.audit_logger.log_event(
                        event_type="security_anomaly",
                        component="ai_security_analytics",
                        action="anomaly_detected",
                        outcome="alert",
                        details={
                            "detection_id": detection.detection_id,
                            "anomaly_type": detection.anomaly_type.value,
                            "threat_level": detection.threat_level.value,
                            "confidence": detection.confidence_score,
                            "event_id": event.event_id
                        },
                        severity="critical" if detection.threat_level == ThreatLevel.CRITICAL else "high"
                    )
            
            return detections
            
        except Exception as e:
            logger.error(f"Failed to analyze event {event.event_id}: {e}")
            return []
    
    def analyze_batch_events(self, events: List[SecurityEvent]) -> List[AnomalyDetection]:
        """Analyze a batch of events for complex patterns."""
        all_detections = []
        
        try:
            # Analyze individual events first
            for event in events:
                detections = self.analyze_event(event)
                all_detections.extend(detections)
            
            # Perform threat intelligence analysis
            threats = self.threat_intelligence.analyze_threat_indicators(events, all_detections)
            
            # Convert threats to detections
            for threat in threats:
                threat_detection = self._create_threat_detection(threat, events)
                all_detections.append(threat_detection)
            
            return all_detections
            
        except Exception as e:
            logger.error(f"Failed to analyze batch events: {e}")
            return all_detections
    
    def train_models(self, force_retrain: bool = False) -> Dict[str, bool]:
        """Train or retrain ML models."""
        results = {}
        
        try:
            # Collect training data from recent events
            training_features = []
            for event in list(self.recent_events)[-1000:]:  # Use last 1000 events
                features = {}
                
                if 'crypto' in event.event_type.lower():
                    features.update(self.feature_extractor.extract_crypto_features(event))
                
                if 'access' in event.event_type.lower():
                    features.update(self.feature_extractor.extract_access_features(event))
                
                if 'performance' in event.event_type.lower():
                    features.update(self.feature_extractor.extract_performance_features(event))
                
                if features:
                    training_features.append(features)
            
            if len(training_features) < 100:
                logger.warning("Insufficient training data for ML models")
                return {"error": "insufficient_data"}
            
            # Train Isolation Forest
            results['isolation_forest'] = self.ml_detector.train_isolation_forest(
                training_features, 'default_isolation_forest'
            )
            
            # Train One-Class SVM
            results['one_class_svm'] = self.ml_detector.train_one_class_svm(
                training_features, 'default_svm'
            )
            
            logger.info(f"Model training completed: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to train models: {e}")
            return {"error": str(e)}
    
    def get_analytics_dashboard(self) -> Dict[str, Any]:
        """Get analytics dashboard data."""
        try:
            # Recent detection statistics
            recent_detections_list = list(self.recent_detections)[-100:]
            
            detection_counts = defaultdict(int)
            threat_level_counts = defaultdict(int)
            
            for detection in recent_detections_list:
                detection_counts[detection.anomaly_type.value] += 1
                threat_level_counts[detection.threat_level.value] += 1
            
            # Model status
            model_status = {}
            for model_id, model_info in self.ml_detector.models.items():
                model_status[model_id] = {
                    'type': model_info['model_type'].value,
                    'trained_at': model_info['trained_at'],
                    'age_hours': (time.time() - model_info['trained_at']) / 3600
                }
            
            # Feature baseline status
            baseline_status = {}
            for feature_name, baseline in self.statistical_detector.baselines.items():
                baseline_status[feature_name] = {
                    'sample_count': len(baseline['values']),
                    'has_stats': 'stats' in baseline and len(baseline['stats']) > 0
                }
            
            return {
                'recent_events_count': len(self.recent_events),
                'recent_detections_count': len(recent_detections_list),
                'detection_types': dict(detection_counts),
                'threat_levels': dict(threat_level_counts),
                'models_trained': len(self.ml_detector.models),
                'model_status': model_status,
                'baseline_features': len(self.statistical_detector.baselines),
                'baseline_status': baseline_status,
                'threat_patterns': len(self.threat_intelligence.known_attack_patterns),
                'engine_uptime': time.time() - getattr(self, '_start_time', time.time()),
                'is_running': self.is_running
            }
            
        except Exception as e:
            logger.error(f"Failed to get analytics dashboard: {e}")
            return {"error": str(e)}
    
    def _create_statistical_detection(self, event: SecurityEvent, features: Dict[str, float], 
                                    anomaly_scores: Dict[str, float], max_score: float) -> AnomalyDetection:
        """Create anomaly detection from statistical analysis."""
        
        # Determine anomaly type based on event and features
        anomaly_type = self._determine_anomaly_type(event.event_type, features)
        
        # Determine threat level based on score
        if max_score >= 0.9:
            threat_level = ThreatLevel.CRITICAL
        elif max_score >= 0.8:
            threat_level = ThreatLevel.HIGH
        elif max_score >= 0.7:
            threat_level = ThreatLevel.MEDIUM
        else:
            threat_level = ThreatLevel.LOW
        
        # Generate description
        top_anomalous_features = sorted(
            anomaly_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:3]
        
        description = f"Statistical anomaly detected in {event.event_type}. " \
                     f"Top anomalous features: {', '.join([f[0] for f in top_anomalous_features])}"
        
        return AnomalyDetection(
            detection_id=str(uuid.uuid4()),
            timestamp=time.time(),
            anomaly_type=anomaly_type,
            threat_level=threat_level,
            confidence_score=max_score,
            event_ids=[event.event_id],
            description=description,
            features_analyzed=list(features.keys()),
            baseline_deviation=anomaly_scores,
            recommended_actions=self._get_recommended_actions(anomaly_type, threat_level)
        )
    
    def _create_ml_detection(self, event: SecurityEvent, features: Dict[str, float], 
                           ml_score: float, model_id: str) -> AnomalyDetection:
        """Create anomaly detection from ML analysis."""
        
        anomaly_type = self._determine_anomaly_type(event.event_type, features)
        
        # ML-based threat level
        if ml_score >= 0.9:
            threat_level = ThreatLevel.CRITICAL
        elif ml_score >= 0.8:
            threat_level = ThreatLevel.HIGH
        elif ml_score >= 0.6:
            threat_level = ThreatLevel.MEDIUM
        else:
            threat_level = ThreatLevel.LOW
        
        model_info = self.ml_detector.models.get(model_id, {})
        model_type = model_info.get('model_type', ModelType.ISOLATION_FOREST).value
        
        description = f"ML anomaly detected using {model_type} model. " \
                     f"Event type: {event.event_type}, Anomaly score: {ml_score:.3f}"
        
        return AnomalyDetection(
            detection_id=str(uuid.uuid4()),
            timestamp=time.time(),
            anomaly_type=anomaly_type,
            threat_level=threat_level,
            confidence_score=ml_score,
            event_ids=[event.event_id],
            description=description,
            features_analyzed=list(features.keys()),
            baseline_deviation={"ml_anomaly_score": ml_score},
            recommended_actions=self._get_recommended_actions(anomaly_type, threat_level)
        )
    
    def _create_threat_detection(self, threat: Dict[str, Any], events: List[SecurityEvent]) -> AnomalyDetection:
        """Create anomaly detection from threat intelligence."""
        
        # Map threat pattern to anomaly type
        pattern_name = threat['pattern_name']
        if 'timing' in pattern_name:
            anomaly_type = AnomalyType.TIMING_ANOMALY
        elif 'key' in pattern_name:
            anomaly_type = AnomalyType.KEY_USAGE_ANOMALY
        elif 'access' in pattern_name or 'auth' in pattern_name:
            anomaly_type = AnomalyType.ACCESS_PATTERN_ANOMALY
        else:
            anomaly_type = AnomalyType.BEHAVIORAL_ANOMALY
        
        # Convert threat severity to threat level
        severity_map = {
            'critical': ThreatLevel.CRITICAL,
            'high': ThreatLevel.HIGH,
            'medium': ThreatLevel.MEDIUM,
            'low': ThreatLevel.LOW
        }
        threat_level = severity_map.get(threat['severity'], ThreatLevel.MEDIUM)
        
        return AnomalyDetection(
            detection_id=threat['threat_id'],
            timestamp=threat['detected_at'],
            anomaly_type=anomaly_type,
            threat_level=threat_level,
            confidence_score=threat['confidence'],
            event_ids=threat.get('event_ids', []),
            description=f"Threat pattern detected: {threat['description']}",
            features_analyzed=threat.get('indicators_matched', []),
            baseline_deviation={"threat_confidence": threat['confidence']},
            recommended_actions=self._get_threat_recommended_actions(pattern_name),
            related_detections=[threat.get('related_detection', '')]
        )
    
    def _determine_anomaly_type(self, event_type: str, features: Dict[str, float]) -> AnomalyType:
        """Determine anomaly type based on event type and features."""
        event_lower = event_type.lower()
        
        if 'crypto' in event_lower or 'key' in event_lower:
            return AnomalyType.CRYPTO_OPERATION_ANOMALY
        elif 'access' in event_lower or 'auth' in event_lower:
            return AnomalyType.ACCESS_PATTERN_ANOMALY
        elif 'performance' in event_lower:
            return AnomalyType.PERFORMANCE_ANOMALY
        elif 'network' in event_lower:
            return AnomalyType.NETWORK_ANOMALY
        elif 'timing' in event_lower or 'duration' in features:
            return AnomalyType.TIMING_ANOMALY
        else:
            return AnomalyType.BEHAVIORAL_ANOMALY
    
    def _get_recommended_actions(self, anomaly_type: AnomalyType, threat_level: ThreatLevel) -> List[str]:
        """Get recommended actions based on anomaly type and threat level."""
        actions = []
        
        if threat_level in [ThreatLevel.CRITICAL, ThreatLevel.HIGH]:
            actions.append("Immediate investigation required")
            actions.append("Consider blocking suspicious IP/user")
        
        if anomaly_type == AnomalyType.CRYPTO_OPERATION_ANOMALY:
            actions.extend([
                "Review cryptographic operation logs",
                "Check for side-channel attack indicators",
                "Verify key integrity"
            ])
        
        elif anomaly_type == AnomalyType.ACCESS_PATTERN_ANOMALY:
            actions.extend([
                "Review access logs and user behavior",
                "Verify user authentication methods",
                "Check for credential compromise"
            ])
        
        elif anomaly_type == AnomalyType.PERFORMANCE_ANOMALY:
            actions.extend([
                "Monitor system resources",
                "Check for DoS attack indicators",
                "Review application performance"
            ])
        
        return actions
    
    def _get_threat_recommended_actions(self, pattern_name: str) -> List[str]:
        """Get recommended actions for specific threat patterns."""
        action_map = {
            'side_channel_timing': [
                "Implement timing attack countermeasures",
                "Review cryptographic implementations",
                "Monitor for repeated timing patterns"
            ],
            'key_extraction_attempt': [
                "Immediately rotate affected keys",
                "Investigate key access patterns",
                "Implement additional key protection"
            ],
            'quantum_algorithm_probe': [
                "Monitor for quantum-specific attack patterns",
                "Review post-quantum cryptography implementation",
                "Consider enhanced monitoring"
            ],
            'brute_force_attack': [
                "Implement rate limiting",
                "Block attacking IP addresses",
                "Review authentication mechanisms"
            ]
        }
        
        return action_map.get(pattern_name, ["Investigate security incident"])
    
    def _background_analysis_worker(self):
        """Background worker for periodic analysis tasks."""
        while self.is_running:
            try:
                # Periodic model retraining
                if len(self.recent_events) > 500:
                    current_time = time.time()
                    
                    # Check if models need retraining (every 24 hours)
                    needs_training = False
                    for model_id, model_info in self.ml_detector.models.items():
                        if current_time - model_info['trained_at'] > 86400:  # 24 hours
                            needs_training = True
                            break
                    
                    if needs_training or not self.ml_detector.models:
                        logger.info("Starting background model training")
                        self.train_models()
                
                # Clean old data
                current_time = time.time()
                cutoff_time = current_time - 7 * 24 * 3600  # 7 days
                
                # Clean old events
                while (self.recent_events and 
                       self.recent_events[0].timestamp < cutoff_time):
                    self.recent_events.popleft()
                
                # Clean old detections
                while (self.recent_detections and 
                       self.recent_detections[0].timestamp < cutoff_time):
                    self.recent_detections.popleft()
                
                # Sleep for 1 hour
                time.sleep(3600)
                
            except Exception as e:
                logger.error(f"Background analysis worker error: {e}")
                time.sleep(300)  # 5 minutes on error
    
    def shutdown(self):
        """Shutdown the analytics engine."""
        self.is_running = False
        if self.processing_thread.is_alive():
            self.processing_thread.join(timeout=10)
        
        logger.info("AI Security Analytics Engine shut down")


# Global analytics engine instance
_analytics_engine = None


def get_ai_security_engine(config: Optional[Dict[str, Any]] = None) -> AISecurityAnalyticsEngine:
    """Get global AI security analytics engine instance."""
    global _analytics_engine
    if _analytics_engine is None:
        _analytics_engine = AISecurityAnalyticsEngine(config)
    return _analytics_engine


def create_security_event(event_type: str, source: str, features: Dict[str, Any], **kwargs) -> SecurityEvent:
    """Helper function to create security events."""
    return SecurityEvent(
        event_id=str(uuid.uuid4()),
        timestamp=time.time(),
        event_type=event_type,
        source=source,
        features=features,
        **kwargs
    )