"""Tests for sentinel error patterns and classifier."""

from __future__ import annotations

from autoheal.sentinel.classifier import ErrorClassifier
from autoheal.sentinel.patterns import ErrorMatch, detect_error_in_output


class TestErrorPatterns:
    """Test error detection patterns across languages."""

    def test_python_traceback(self):
        """Detect Python TypeError from traceback."""
        output = '''Traceback (most recent call last):
  File "app.py", line 12, in process_user
    print(f"Processing user: {user['name']}")
TypeError: 'NoneType' object is not subscriptable'''

        result = detect_error_in_output(output, "python")

        assert result is not None
        assert result.error_type == "TypeError"
        assert "NoneType" in result.message
        assert result.file_path == "app.py"
        assert result.line_number == 12

    def test_python_import_error(self):
        """Detect Python ImportError."""
        output = "ModuleNotFoundError: No module named 'fastapi'"
        result = detect_error_in_output(output, "python")

        assert result is not None
        assert result.error_type == "ModuleNotFoundError"
        assert "fastapi" in result.message

    def test_node_reference_error(self):
        """Detect Node.js ReferenceError."""
        output = "ReferenceError: myVariable is not defined"
        result = detect_error_in_output(output, "javascript")

        assert result is not None
        assert result.error_type == "ReferenceError"

    def test_go_panic(self):
        """Detect Go panic."""
        output = "panic: runtime error: index out of range [5] with length 3"
        result = detect_error_in_output(output, "go")

        assert result is not None
        assert "index out of range" in result.message

    def test_rust_error(self):
        """Detect Rust compile error."""
        output = "error[E0308]: mismatched types"
        result = detect_error_in_output(output, "rust")

        assert result is not None
        assert "mismatched types" in result.message

    def test_generic_error(self):
        """Detect generic ERROR log line."""
        output = "ERROR: Connection refused to localhost:5432"
        result = detect_error_in_output(output, "unknown")

        assert result is not None
        assert "Connection refused" in result.message

    def test_no_error(self):
        """No error in clean output."""
        output = "Server started successfully on port 8000"
        result = detect_error_in_output(output, "python")

        assert result is None


class TestErrorClassifier:
    """Test error severity and category classification."""

    def test_classify_severity_p0(self):
        """Classify MemoryError as P0."""
        classifier = ErrorClassifier()
        error = ErrorMatch(
            error_type="MemoryError",
            message="Out of memory",
            language="python",
        )
        assert classifier.classify_severity(error) == "P0"

    def test_classify_severity_p2(self):
        """Classify TypeError as P2."""
        classifier = ErrorClassifier()
        error = ErrorMatch(
            error_type="TypeError",
            message="'NoneType' not subscriptable",
            language="python",
        )
        assert classifier.classify_severity(error) == "P2"

    def test_classify_severity_p3(self):
        """Classify ImportError as P3."""
        classifier = ErrorClassifier()
        error = ErrorMatch(
            error_type="ModuleNotFoundError",
            message="No module named 'foo'",
            language="python",
        )
        assert classifier.classify_severity(error) == "P3"

    def test_classify_category_runtime(self):
        """Classify TypeError as runtime."""
        classifier = ErrorClassifier()
        error = ErrorMatch(
            error_type="TypeError",
            message="cannot subscript None",
            language="python",
        )
        assert classifier.classify_category(error) == "runtime"

    def test_classify_category_dependency(self):
        """Classify ImportError as dependency."""
        classifier = ErrorClassifier()
        error = ErrorMatch(
            error_type="ImportError",
            message="No module named 'requests'",
            language="python",
        )
        assert classifier.classify_category(error) == "dependency"

    def test_classify_category_network(self):
        """Classify ConnectionError as network."""
        classifier = ErrorClassifier()
        error = ErrorMatch(
            error_type="ConnectionError",
            message="Connection refused",
            language="python",
        )
        assert classifier.classify_category(error) == "network"
