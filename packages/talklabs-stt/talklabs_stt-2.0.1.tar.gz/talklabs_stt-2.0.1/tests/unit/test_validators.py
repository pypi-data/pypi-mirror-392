"""
Unit tests for validators module.
CRITICAL module for input validation - HIGH PRIORITY.
"""
import pytest
import os
import tempfile
from talklabs_stt.validators import validate_file_exists, validate_api_key


class TestValidateFileExists:
    """Test suite for validate_file_exists function."""

    @pytest.mark.unit
    def test_validate_file_exists_valid(self):
        """Test validation with existing file."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name
            tmp.write(b"test data")

        try:
            # Should not raise
            validate_file_exists(tmp_path)
        finally:
            os.unlink(tmp_path)

    @pytest.mark.unit
    def test_validate_file_exists_missing(self):
        """Test validation with non-existent file."""
        with pytest.raises(FileNotFoundError, match="Arquivo não encontrado"):
            validate_file_exists("/nonexistent/path/file.wav")

    @pytest.mark.unit
    def test_validate_file_exists_empty_path(self):
        """Test validation with empty path."""
        with pytest.raises(FileNotFoundError):
            validate_file_exists("")

    @pytest.mark.unit
    def test_validate_file_exists_directory(self):
        """Test validation with directory path (not a file)."""
        # Use temp directory
        with tempfile.TemporaryDirectory() as tmpdir:
            # Directory exists but is not a file
            # Should still pass validate_file_exists (os.path.exists checks both)
            validate_file_exists(tmpdir)


class TestValidateApiKey:
    """Test suite for validate_api_key function."""

    @pytest.mark.unit
    def test_validate_api_key_valid(self):
        """Test validation with valid API key."""
        # Should not raise
        validate_api_key("tlk_live_test_key_123")

    @pytest.mark.unit
    def test_validate_api_key_empty(self):
        """Test validation with empty API key."""
        with pytest.raises(ValueError, match="API key é obrigatória"):
            validate_api_key("")

    @pytest.mark.unit
    def test_validate_api_key_none(self):
        """Test validation with None API key."""
        with pytest.raises(ValueError, match="API key é obrigatória"):
            validate_api_key(None)

    @pytest.mark.unit
    def test_validate_api_key_whitespace(self):
        """Test validation with whitespace-only API key."""
        # Note: Current implementation doesn't strip whitespace
        # This test documents the behavior (whitespace passes validation)
        # Consider enhancing validators.py to check: if not api_key.strip()
        validate_api_key("   ")  # Currently passes
