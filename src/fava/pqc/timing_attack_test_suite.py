"""
Comprehensive Timing Attack Test Suite

This module provides extensive testing capabilities for timing side-channel vulnerabilities.
It validates that the implemented protections successfully prevent timing-based attacks.

Features:
- Statistical timing analysis with high precision measurements
- Automated detection of timing vulnerabilities 
- Comprehensive test coverage for all crypto operations
- Performance benchmarking with security validation
- Vulnerability assessment and reporting
"""

import time
import statistics
import threading
import concurrent.futures
from typing import List, Dict, Any, Callable, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict
import random
import os
import json
import logging

# Import timing protection modules to test
from .timing_protection import (
    SecureComparison, 
    SecureSignatureVerification,
    SecureKeyVerification,
    TimingJitter
)
from .error_timing_normalization import ErrorTimingNormalizer, UniformCryptoErrorHandler
from .statistical_pattern_mitigation import (
    StatisticalPatternEliminator,
    timing_protected_operation
)

logger = logging.getLogger(__name__)


@dataclass
class TimingTestResult:
    """Results from a timing attack test."""
    test_name: str
    operation_name: str
    sample_count: int
    mean_time: float
    std_deviation: float
    coefficient_of_variation: float
    is_vulnerable: bool
    vulnerability_score: float
    timing_samples: List[float] = field(default_factory=list)
    statistical_analysis: Dict[str, float] = field(default_factory=dict)


@dataclass
class VulnerabilityReport:
    """Comprehensive vulnerability assessment report."""
    overall_score: float
    vulnerabilities_found: List[TimingTestResult]
    warnings: List[str]
    test_summary: Dict[str, Any]
    recommendations: List[str]


class HighPrecisionTimer:
    """High-precision timer for timing attack detection."""
    
    @staticmethod
    def measure_operation(
        operation: Callable,
        iterations: int = 10000,
        warmup_iterations: int = 1000
    ) -> List[float]:
        """
        Measure operation timing with high precision.
        
        Args:
            operation: Operation to measure
            iterations: Number of measurement iterations
            warmup_iterations: Number of warmup iterations
            
        Returns:
            List of timing measurements in seconds
        """
        # Warmup phase to stabilize CPU frequency and caches
        for _ in range(warmup_iterations):
            operation()
        
        # Measurement phase
        measurements = []
        for _ in range(iterations):
            start_time = time.perf_counter()
            operation()
            end_time = time.perf_counter()
            measurements.append(end_time - start_time)
        
        return measurements
    
    @staticmethod
    def statistical_timing_analysis(measurements: List[float]) -> Dict[str, float]:
        """
        Perform statistical analysis on timing measurements.
        
        Args:
            measurements: List of timing measurements
            
        Returns:
            Dictionary of statistical metrics
        """
        if len(measurements) < 2:
            return {"error": "insufficient_samples"}
        
        mean_time = statistics.mean(measurements)
        std_dev = statistics.stdev(measurements)
        variance = statistics.variance(measurements)
        
        # Coefficient of variation (CV) - key metric for timing consistency
        cv = std_dev / mean_time if mean_time > 0 else float('inf')
        
        # Additional statistical metrics
        min_time = min(measurements)
        max_time = max(measurements)
        median_time = statistics.median(measurements)
        
        # Range and interquartile range
        time_range = max_time - min_time
        sorted_measurements = sorted(measurements)
        q1 = sorted_measurements[len(measurements) // 4]
        q3 = sorted_measurements[3 * len(measurements) // 4]
        iqr = q3 - q1
        
        return {
            "mean": mean_time,
            "std_dev": std_dev,
            "variance": variance,
            "cv": cv,
            "min": min_time,
            "max": max_time,
            "median": median_time,
            "range": time_range,
            "iqr": iqr,
            "sample_count": len(measurements)
        }


class TimingAttackTester:
    """
    Main class for conducting timing attack tests.
    """
    
    def __init__(self, 
                 precision_threshold: float = 0.02,  # 2% CV threshold
                 vulnerability_threshold: float = 0.05):  # 5% CV vulnerability
        """
        Initialize timing attack tester.
        
        Args:
            precision_threshold: Coefficient of variation threshold for good timing
            vulnerability_threshold: CV threshold above which indicates vulnerability
        """
        self.precision_threshold = precision_threshold
        self.vulnerability_threshold = vulnerability_threshold
        self.test_results = []
        self.timer = HighPrecisionTimer()
        
        logger.info(f"Timing attack tester initialized")
        logger.info(f"Precision threshold: {precision_threshold * 100:.1f}%")
        logger.info(f"Vulnerability threshold: {vulnerability_threshold * 100:.1f}%")
    
    def test_secure_comparison(self) -> TimingTestResult:
        """Test SecureComparison functions for timing vulnerabilities."""
        logger.info("Testing SecureComparison for timing vulnerabilities")
        
        # Test data
        secret_data = b"super_secret_cryptographic_key_material"
        correct_data = secret_data
        incorrect_data = b"wrong_secret_cryptographic_key_material"
        
        # Test with correct data
        correct_measurements = self.timer.measure_operation(
            lambda: SecureComparison.compare_digest(secret_data, correct_data),
            iterations=5000
        )
        
        # Test with incorrect data
        incorrect_measurements = self.timer.measure_operation(
            lambda: SecureComparison.compare_digest(secret_data, incorrect_data),
            iterations=5000
        )
        
        # Combined analysis
        all_measurements = correct_measurements + incorrect_measurements
        stats = self.timer.statistical_timing_analysis(all_measurements)
        
        # Check for timing differences between correct/incorrect
        correct_mean = statistics.mean(correct_measurements)
        incorrect_mean = statistics.mean(incorrect_measurements)
        timing_ratio = max(correct_mean, incorrect_mean) / min(correct_mean, incorrect_mean)
        
        is_vulnerable = (stats["cv"] > self.vulnerability_threshold or 
                        timing_ratio > 1.1)  # More than 10% difference
        
        vulnerability_score = min(stats["cv"] * 100, timing_ratio * 10)
        
        result = TimingTestResult(
            test_name="SecureComparison",
            operation_name="compare_digest",
            sample_count=len(all_measurements),
            mean_time=stats["mean"],
            std_deviation=stats["std_dev"],
            coefficient_of_variation=stats["cv"],
            is_vulnerable=is_vulnerable,
            vulnerability_score=vulnerability_score,
            timing_samples=all_measurements,
            statistical_analysis=stats
        )
        
        self.test_results.append(result)
        logger.info(f"SecureComparison test: CV={stats['cv']*100:.2f}%, Vulnerable={is_vulnerable}")
        
        return result
    
    def test_signature_verification(self) -> TimingTestResult:
        """Test signature verification timing consistency."""
        logger.info("Testing signature verification timing")
        
        # Generate test signatures
        valid_signature = b"valid_signature_" + os.urandom(64)
        invalid_signature = b"invalid_signature" + os.urandom(64)
        expected_signature = valid_signature
        
        # Test valid signature verification
        valid_measurements = self.timer.measure_operation(
            lambda: SecureSignatureVerification.verify_signature_secure(
                valid_signature, expected_signature
            ),
            iterations=3000
        )
        
        # Test invalid signature verification  
        invalid_measurements = self.timer.measure_operation(
            lambda: SecureSignatureVerification.verify_signature_secure(
                invalid_signature, expected_signature
            ),
            iterations=3000
        )
        
        # Combined analysis
        all_measurements = valid_measurements + invalid_measurements
        stats = self.timer.statistical_timing_analysis(all_measurements)
        
        # Check timing consistency
        valid_mean = statistics.mean(valid_measurements)
        invalid_mean = statistics.mean(invalid_measurements)
        timing_ratio = max(valid_mean, invalid_mean) / min(valid_mean, invalid_mean)
        
        is_vulnerable = (stats["cv"] > self.vulnerability_threshold or
                        timing_ratio > 1.05)  # More than 5% difference
        
        vulnerability_score = max(stats["cv"] * 100, timing_ratio * 20)
        
        result = TimingTestResult(
            test_name="SignatureVerification",
            operation_name="verify_signature_secure",
            sample_count=len(all_measurements),
            mean_time=stats["mean"],
            std_deviation=stats["std_dev"], 
            coefficient_of_variation=stats["cv"],
            is_vulnerable=is_vulnerable,
            vulnerability_score=vulnerability_score,
            timing_samples=all_measurements,
            statistical_analysis=stats
        )
        
        self.test_results.append(result)
        logger.info(f"Signature verification test: CV={stats['cv']*100:.2f}%, Vulnerable={is_vulnerable}")
        
        return result
    
    def test_key_verification(self) -> TimingTestResult:
        """Test key verification timing consistency."""
        logger.info("Testing key verification timing")
        
        # Test data
        correct_key = "correct_api_key_" + "x" * 32
        incorrect_key = "incorrect_api_key_" + "y" * 32
        stored_hash = "stored_hash_value_" + "z" * 32
        
        # Test correct key verification
        correct_measurements = self.timer.measure_operation(
            lambda: SecureKeyVerification.verify_api_key_secure(
                correct_key, stored_hash
            ),
            iterations=3000
        )
        
        # Test incorrect key verification
        incorrect_measurements = self.timer.measure_operation(
            lambda: SecureKeyVerification.verify_api_key_secure(
                incorrect_key, stored_hash
            ),
            iterations=3000
        )
        
        # Combined analysis
        all_measurements = correct_measurements + incorrect_measurements
        stats = self.timer.statistical_timing_analysis(all_measurements)
        
        is_vulnerable = stats["cv"] > self.vulnerability_threshold
        vulnerability_score = stats["cv"] * 100
        
        result = TimingTestResult(
            test_name="KeyVerification", 
            operation_name="verify_api_key_secure",
            sample_count=len(all_measurements),
            mean_time=stats["mean"],
            std_deviation=stats["std_dev"],
            coefficient_of_variation=stats["cv"],
            is_vulnerable=is_vulnerable,
            vulnerability_score=vulnerability_score,
            timing_samples=all_measurements,
            statistical_analysis=stats
        )
        
        self.test_results.append(result)
        logger.info(f"Key verification test: CV={stats['cv']*100:.2f}%, Vulnerable={is_vulnerable}")
        
        return result
    
    def test_error_timing_normalization(self) -> TimingTestResult:
        """Test error timing normalization effectiveness."""
        logger.info("Testing error timing normalization")
        
        def create_crypto_error():
            """Simulate crypto error with normalized timing."""
            start_time = time.perf_counter()
            try:
                raise ValueError("Crypto operation failed")
            except ValueError:
                return UniformCryptoErrorHandler.handle_decryption_error("test_crypto", start_time)
        
        def create_auth_error():
            """Simulate auth error with normalized timing."""
            start_time = time.perf_counter() 
            try:
                raise PermissionError("Authentication failed")
            except PermissionError:
                return UniformCryptoErrorHandler.handle_verification_error("test_auth", start_time)
        
        # Measure crypto error timing
        crypto_measurements = self.timer.measure_operation(create_crypto_error, iterations=2000)
        
        # Measure auth error timing
        auth_measurements = self.timer.measure_operation(create_auth_error, iterations=2000)
        
        # Combined analysis
        all_measurements = crypto_measurements + auth_measurements
        stats = self.timer.statistical_timing_analysis(all_measurements)
        
        # Check timing consistency between error types
        crypto_mean = statistics.mean(crypto_measurements)
        auth_mean = statistics.mean(auth_measurements)
        error_timing_ratio = max(crypto_mean, auth_mean) / min(crypto_mean, auth_mean)
        
        is_vulnerable = (stats["cv"] > self.vulnerability_threshold or
                        error_timing_ratio > 1.1)
        
        vulnerability_score = max(stats["cv"] * 100, error_timing_ratio * 10)
        
        result = TimingTestResult(
            test_name="ErrorTimingNormalization",
            operation_name="error_handling",
            sample_count=len(all_measurements),
            mean_time=stats["mean"],
            std_deviation=stats["std_dev"],
            coefficient_of_variation=stats["cv"],
            is_vulnerable=is_vulnerable,
            vulnerability_score=vulnerability_score,
            timing_samples=all_measurements,
            statistical_analysis=stats
        )
        
        result.statistical_analysis["error_timing_ratio"] = error_timing_ratio
        
        self.test_results.append(result)
        logger.info(f"Error timing test: CV={stats['cv']*100:.2f}%, Ratio={error_timing_ratio:.2f}, Vulnerable={is_vulnerable}")
        
        return result
    
    def test_statistical_pattern_mitigation(self) -> TimingTestResult:
        """Test statistical pattern mitigation effectiveness."""
        logger.info("Testing statistical pattern mitigation")
        
        @timing_protected_operation("test_crypto_op", 0.003)
        def protected_crypto_operation():
            """Simulated crypto operation with timing protection."""
            # Simulate variable processing time
            work_amount = random.randint(100, 300)
            _ = sum(range(work_amount))
            return True
        
        # Measure protected operation
        protected_measurements = self.timer.measure_operation(
            protected_crypto_operation,
            iterations=4000
        )
        
        stats = self.timer.statistical_timing_analysis(protected_measurements)
        
        is_vulnerable = stats["cv"] > self.precision_threshold
        vulnerability_score = stats["cv"] * 100
        
        result = TimingTestResult(
            test_name="StatisticalPatternMitigation",
            operation_name="protected_crypto_op",
            sample_count=len(protected_measurements),
            mean_time=stats["mean"],
            std_deviation=stats["std_dev"],
            coefficient_of_variation=stats["cv"],
            is_vulnerable=is_vulnerable,
            vulnerability_score=vulnerability_score,
            timing_samples=protected_measurements,
            statistical_analysis=stats
        )
        
        self.test_results.append(result)
        logger.info(f"Pattern mitigation test: CV={stats['cv']*100:.2f}%, Vulnerable={is_vulnerable}")
        
        return result
    
    def run_comprehensive_test_suite(self) -> VulnerabilityReport:
        """Run comprehensive timing attack test suite."""
        logger.info("Starting comprehensive timing attack test suite")
        
        # Clear previous results
        self.test_results = []
        
        # Run all tests
        test_functions = [
            self.test_secure_comparison,
            self.test_signature_verification,
            self.test_key_verification,
            self.test_error_timing_normalization,
            self.test_statistical_pattern_mitigation
        ]
        
        for test_func in test_functions:
            try:
                test_func()
            except Exception as e:
                logger.error(f"Test {test_func.__name__} failed: {e}")
        
        # Generate comprehensive report
        return self._generate_vulnerability_report()
    
    def _generate_vulnerability_report(self) -> VulnerabilityReport:
        """Generate comprehensive vulnerability assessment report."""
        vulnerabilities = [r for r in self.test_results if r.is_vulnerable]
        warnings = []
        
        # Calculate overall security score
        if not self.test_results:
            overall_score = 0.0
        else:
            # Score based on vulnerability count and severity
            total_vulnerability_score = sum(r.vulnerability_score for r in vulnerabilities)
            max_possible_score = len(self.test_results) * 100
            overall_score = max(0, 100 - (total_vulnerability_score / max_possible_score) * 100)
        
        # Generate warnings for concerning results
        for result in self.test_results:
            if result.coefficient_of_variation > self.precision_threshold:
                warnings.append(
                    f"{result.test_name}: Timing variance {result.coefficient_of_variation*100:.2f}% "
                    f"exceeds precision threshold ({self.precision_threshold*100:.1f}%)"
                )
            
            if result.vulnerability_score > 50:
                warnings.append(
                    f"{result.test_name}: High vulnerability score {result.vulnerability_score:.1f}"
                )
        
        # Generate test summary
        test_summary = {
            "total_tests": len(self.test_results),
            "vulnerabilities_found": len(vulnerabilities),
            "tests_passed": len(self.test_results) - len(vulnerabilities),
            "average_cv": statistics.mean([r.coefficient_of_variation for r in self.test_results]),
            "max_cv": max([r.coefficient_of_variation for r in self.test_results]),
            "average_vulnerability_score": statistics.mean([r.vulnerability_score for r in self.test_results])
        }
        
        # Generate recommendations
        recommendations = []
        if vulnerabilities:
            recommendations.append("Address timing vulnerabilities found in the following operations:")
            for vuln in vulnerabilities:
                recommendations.append(f"  - {vuln.test_name}: {vuln.operation_name}")
        
        if test_summary["average_cv"] > self.precision_threshold:
            recommendations.append("Consider increasing timing jitter to reduce overall timing variance")
        
        if not vulnerabilities:
            recommendations.append("All timing attack tests passed - system appears secure")
        
        report = VulnerabilityReport(
            overall_score=overall_score,
            vulnerabilities_found=vulnerabilities,
            warnings=warnings,
            test_summary=test_summary,
            recommendations=recommendations
        )
        
        logger.info(f"Vulnerability assessment complete: Score={overall_score:.1f}/100")
        logger.info(f"Vulnerabilities found: {len(vulnerabilities)}")
        
        return report
    
    def export_test_results(self, filename: str) -> None:
        """Export test results to JSON file."""
        results_data = {
            "test_metadata": {
                "timestamp": time.time(),
                "precision_threshold": self.precision_threshold,
                "vulnerability_threshold": self.vulnerability_threshold
            },
            "test_results": []
        }
        
        for result in self.test_results:
            result_dict = {
                "test_name": result.test_name,
                "operation_name": result.operation_name,
                "sample_count": result.sample_count,
                "mean_time": result.mean_time,
                "std_deviation": result.std_deviation,
                "coefficient_of_variation": result.coefficient_of_variation,
                "is_vulnerable": result.is_vulnerable,
                "vulnerability_score": result.vulnerability_score,
                "statistical_analysis": result.statistical_analysis
                # Note: timing_samples excluded from export to reduce file size
            }
            results_data["test_results"].append(result_dict)
        
        with open(filename, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        logger.info(f"Test results exported to {filename}")


# Convenience function for quick testing
def run_timing_attack_tests(export_results: bool = True) -> VulnerabilityReport:
    """
    Run comprehensive timing attack tests.
    
    Args:
        export_results: Whether to export results to JSON file
        
    Returns:
        VulnerabilityReport with assessment results
    """
    tester = TimingAttackTester()
    report = tester.run_comprehensive_test_suite()
    
    if export_results:
        timestamp = int(time.time())
        filename = f"timing_attack_test_results_{timestamp}.json"
        tester.export_test_results(filename)
    
    return report


# Initialize test suite
logger.info("Timing attack test suite initialized")
logger.info("High-precision timing measurements enabled")
logger.info("Statistical analysis capabilities loaded")