"""
Unit tests for decorators module.
CRITICAL module for error handling - HIGH PRIORITY.
"""
import pytest
import logging
from unittest.mock import Mock
from talklabs_stt.decorators import handle_errors


class TestHandleErrorsDecorator:
    """Test suite for handle_errors decorator."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_handle_errors_async_success(self):
        """Test decorator with successful async function."""
        mock_logger = Mock(spec=logging.Logger)

        @handle_errors(mock_logger)
        async def test_func(value):
            return value * 2

        result = await test_func(5)

        assert result == 10
        # Should not log error
        mock_logger.error.assert_not_called()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_handle_errors_async_failure(self):
        """Test decorator with failing async function."""
        mock_logger = Mock(spec=logging.Logger)

        @handle_errors(mock_logger)
        async def test_func():
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            await test_func()

        # Should log error
        mock_logger.error.assert_called_once()
        error_msg = mock_logger.error.call_args[0][0]
        assert "test_func" in error_msg
        assert "Test error" in error_msg

    @pytest.mark.unit
    def test_handle_errors_sync_success(self):
        """Test decorator with successful sync function."""
        mock_logger = Mock(spec=logging.Logger)

        @handle_errors(mock_logger)
        def test_func(value):
            return value * 2

        result = test_func(5)

        assert result == 10
        # Should not log error
        mock_logger.error.assert_not_called()

    @pytest.mark.unit
    def test_handle_errors_sync_failure(self):
        """Test decorator with failing sync function."""
        mock_logger = Mock(spec=logging.Logger)

        @handle_errors(mock_logger)
        def test_func():
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            test_func()

        # Should log error
        mock_logger.error.assert_called_once()
        error_msg = mock_logger.error.call_args[0][0]
        assert "test_func" in error_msg
        assert "Test error" in error_msg

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_handle_errors_preserves_function_name(self):
        """Test that decorator preserves original function name."""
        mock_logger = Mock(spec=logging.Logger)

        @handle_errors(mock_logger)
        async def my_special_function():
            return "result"

        # functools.wraps should preserve the name
        assert my_special_function.__name__ == "my_special_function"

    @pytest.mark.unit
    def test_handle_errors_multiple_exceptions(self):
        """Test decorator with different exception types."""
        mock_logger = Mock(spec=logging.Logger)

        @handle_errors(mock_logger)
        def test_func(error_type):
            if error_type == "value":
                raise ValueError("Value error")
            elif error_type == "type":
                raise TypeError("Type error")
            elif error_type == "runtime":
                raise RuntimeError("Runtime error")
            return "success"

        # Test different exception types
        with pytest.raises(ValueError):
            test_func("value")

        with pytest.raises(TypeError):
            test_func("type")

        with pytest.raises(RuntimeError):
            test_func("runtime")

        # All should be logged
        assert mock_logger.error.call_count == 3

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_handle_errors_with_arguments(self):
        """Test decorator with functions that have arguments."""
        mock_logger = Mock(spec=logging.Logger)

        @handle_errors(mock_logger)
        async def test_func(a, b, c=10):
            if a < 0:
                raise ValueError("Negative value")
            return a + b + c

        # Success case
        result = await test_func(5, 3, c=2)
        assert result == 10

        # Error case
        with pytest.raises(ValueError, match="Negative value"):
            await test_func(-1, 5)

        mock_logger.error.assert_called_once()
