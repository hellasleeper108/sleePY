"""
Code Execution Service - Validate user code submissions

Handles test case execution and validation
"""
import json
import re
from typing import Dict, List, Tuple, Any, Optional
from io import StringIO
import sys
import traceback


class TestCase:
    """Represents a single test case"""

    def __init__(self, inputs: List[Any], expected_output: Any, description: str = ""):
        self.inputs = inputs
        self.expected_output = expected_output
        self.description = description

    @staticmethod
    def from_dict(data: dict) -> 'TestCase':
        """
        Create TestCase from dictionary

        Supports both formats:
        - {"input": [...], "expected": ...}
        - {"inputs": [...], "expected_output": ...}
        """
        # Support both 'input'/'inputs' and 'expected'/'expected_output'
        inputs = data.get('inputs', data.get('input', []))
        expected = data.get('expected_output', data.get('expected'))

        # Ensure inputs is a list
        if not isinstance(inputs, list):
            inputs = [inputs] if inputs is not None else []

        return TestCase(
            inputs=inputs,
            expected_output=expected,
            description=data.get('description', '')
        )


class CodeExecutionService:
    """
    Service for executing and validating user code

    Note: This is a simplified backend validation system.
    Actual code execution happens in the browser via Pyodide.
    This service validates the execution results.
    """

    @staticmethod
    def parse_test_cases(test_cases_json: str) -> List[TestCase]:
        """
        Parse test cases from JSON string

        Args:
            test_cases_json: JSON string with test cases

        Returns:
            list: List of TestCase objects
        """
        try:
            data = json.loads(test_cases_json)
            if isinstance(data, list):
                return [TestCase.from_dict(tc) for tc in data]
            return []
        except (json.JSONDecodeError, KeyError):
            return []

    @staticmethod
    def validate_execution_result(
        test_cases: List[TestCase],
        execution_results: List[Dict]
    ) -> Dict:
        """
        Validate execution results against test cases

        Args:
            test_cases: Expected test cases
            execution_results: Actual execution results from frontend

        Returns:
            dict: Validation result with pass/fail status
        """
        total_tests = len(test_cases)
        passed_tests = 0
        failed_tests = []

        for i, (test_case, result) in enumerate(zip(test_cases, execution_results)):
            if result.get('error'):
                failed_tests.append({
                    'test_number': i + 1,
                    'inputs': test_case.inputs,
                    'expected': test_case.expected_output,
                    'actual': None,
                    'error': result['error'],
                    'description': test_case.description
                })
            elif CodeExecutionService._compare_outputs(
                test_case.expected_output,
                result.get('output')
            ):
                passed_tests += 1
            else:
                failed_tests.append({
                    'test_number': i + 1,
                    'inputs': test_case.inputs,
                    'expected': test_case.expected_output,
                    'actual': result.get('output'),
                    'error': None,
                    'description': test_case.description
                })

        success = passed_tests == total_tests

        return {
            'success': success,
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': len(failed_tests),
            'failures': failed_tests,
            'message': CodeExecutionService._generate_message(
                success, passed_tests, total_tests
            )
        }

    @staticmethod
    def _compare_outputs(expected: Any, actual: Any) -> bool:
        """
        Compare expected and actual outputs with type coercion

        Args:
            expected: Expected output
            actual: Actual output

        Returns:
            bool: True if outputs match
        """
        # Handle None/null
        if expected is None:
            return actual is None

        # Handle different types
        if type(expected) != type(actual):
            # Try converting to same type
            try:
                if isinstance(expected, (int, float)):
                    actual = type(expected)(actual)
                elif isinstance(expected, str):
                    actual = str(actual)
                elif isinstance(expected, bool):
                    actual = bool(actual)
            except (ValueError, TypeError):
                return False

        # Handle lists/arrays
        if isinstance(expected, list) and isinstance(actual, list):
            if len(expected) != len(actual):
                return False
            return all(
                CodeExecutionService._compare_outputs(e, a)
                for e, a in zip(expected, actual)
            )

        # Handle floats with tolerance
        if isinstance(expected, float) and isinstance(actual, float):
            return abs(expected - actual) < 1e-9

        # Handle strings (strip whitespace)
        if isinstance(expected, str) and isinstance(actual, str):
            return expected.strip() == actual.strip()

        # Direct comparison
        return expected == actual

    @staticmethod
    def _generate_message(success: bool, passed: int, total: int) -> str:
        """Generate result message"""
        if success:
            return f"Perfect! All {total} test cases passed! 🎉"
        else:
            return f"Not quite! {passed}/{total} test cases passed. Keep trying! 💪"

    @staticmethod
    def extract_function_name(code: str) -> Optional[str]:
        """
        Extract function name from code

        Args:
            code: Python code string

        Returns:
            str: Function name or None
        """
        # Look for def function_name(
        match = re.search(r'def\s+(\w+)\s*\(', code)
        if match:
            return match.group(1)
        return None

    @staticmethod
    def generate_test_code(function_name: str, test_cases: List[TestCase]) -> str:
        """
        Generate test code to run in Pyodide

        Args:
            function_name: Name of function to test
            test_cases: Test cases to run

        Returns:
            str: Python test code
        """
        test_lines = []

        for i, tc in enumerate(test_cases):
            inputs_str = ', '.join(repr(inp) for inp in tc.inputs)
            test_lines.append(f"# Test case {i + 1}")
            test_lines.append(f"result_{i} = {function_name}({inputs_str})")
            test_lines.append(f"print(f'TEST_{i}:{{repr(result_{i})}}')")

        return '\n'.join(test_lines)

    @staticmethod
    def create_validation_schema(challenge_id: int, test_cases: List[TestCase]) -> Dict:
        """
        Create validation schema for frontend

        Args:
            challenge_id: Challenge ID
            test_cases: Test cases

        Returns:
            dict: Validation schema
        """
        return {
            'challenge_id': challenge_id,
            'test_cases': [
                {
                    'inputs': tc.inputs,
                    'expected_output': tc.expected_output,
                    'description': tc.description
                }
                for tc in test_cases
            ],
            'total_tests': len(test_cases)
        }
