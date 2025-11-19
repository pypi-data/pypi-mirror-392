"""
Unit tests for HTTPTranscriber class - REST API client.
PHASE 2 - HIGH PRIORITY - HTTP methods and error handling.
"""
import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from talklabs_stt.http_client import HTTPTranscriber
from talklabs_stt.models import TranscriptionOptions


class TestHTTPTranscriberInit:
    """Test suite for HTTPTranscriber initialization"""

    @pytest.mark.unit
    def test_init_basic(self):
        """Test basic initialization"""
        transcriber = HTTPTranscriber(
            api_key="test_key",
            base_url="https://api.test.com",
            timeout=300
        )

        assert transcriber.api_key == "test_key"
        assert transcriber.base_url == "https://api.test.com"
        assert transcriber.timeout == 300

    @pytest.mark.unit
    def test_init_custom_timeout(self):
        """Test initialization with custom timeout"""
        transcriber = HTTPTranscriber(
            api_key="test_key",
            base_url="https://api.test.com",
            timeout=600
        )

        assert transcriber.timeout == 600


class TestHTTPTranscriberTranscribe:
    """Test suite for HTTPTranscriber.transcribe() method"""

    @pytest.mark.unit
    def test_transcribe_file_not_found(self):
        """Test transcribe with non-existent file"""
        transcriber = HTTPTranscriber(
            api_key="test_key",
            base_url="https://api.test.com"
        )

        with pytest.raises(FileNotFoundError):
            transcriber.transcribe("/nonexistent/file.wav")

    @pytest.mark.unit
    @patch('talklabs_stt.http_client.requests.post')
    def test_transcribe_success(self, mock_post):
        """Test successful transcription"""
        transcriber = HTTPTranscriber(
            api_key="test_key",
            base_url="https://api.test.com"
        )

        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": {
                "channels": [{
                    "alternatives": [{"transcript": "test transcription"}]
                }]
            }
        }
        mock_post.return_value = mock_response

        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(b"fake_audio_data")
            tmp_path = tmp.name

        try:
            result = transcriber.transcribe(tmp_path)

            # Verify API call
            mock_post.assert_called_once()
            call_args = mock_post.call_args

            # Check URL
            assert "v1/listen" in call_args[0][0]

            # Check headers
            assert call_args[1]["headers"]["xi-api-key"] == "test_key"
            assert call_args[1]["headers"]["Content-Type"] == "audio/wav"

            # Check result
            transcript = result["results"]["channels"][0]["alternatives"][0]
            assert transcript["transcript"] == "test transcription"

        finally:
            os.unlink(tmp_path)

    @pytest.mark.unit
    @patch('talklabs_stt.http_client.requests.post')
    def test_transcribe_with_options(self, mock_post):
        """Test transcription with custom options"""
        transcriber = HTTPTranscriber(
            api_key="test_key",
            base_url="https://api.test.com"
        )

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": {}}
        mock_post.return_value = mock_response

        options = TranscriptionOptions(language="en")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(b"audio")
            tmp_path = tmp.name

        try:
            transcriber.transcribe(tmp_path, options=options)

            # Check params
            call_args = mock_post.call_args
            params = call_args[1]["params"]

            assert params["language"] == "en"
            assert params["punctuate"] == "true"
            assert params["smart_format"] == "true"
            assert params["model"] == "turbo"  # Should be forced

        finally:
            os.unlink(tmp_path)

    @pytest.mark.unit
    @patch('talklabs_stt.http_client.requests.post')
    def test_transcribe_forces_turbo_model(self, mock_post):
        """Test that model is always forced to 'turbo'"""
        transcriber = HTTPTranscriber(
            api_key="test_key",
            base_url="https://api.test.com"
        )

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": {}}
        mock_post.return_value = mock_response

        options = TranscriptionOptions(language="pt")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(b"audio")
            tmp_path = tmp.name

        try:
            transcriber.transcribe(tmp_path, options=options)

            # Model is always forced to turbo internally
            params = mock_post.call_args[1]["params"]
            assert params["model"] == "turbo"

        finally:
            os.unlink(tmp_path)

    @pytest.mark.unit
    @patch('talklabs_stt.http_client.requests.post')
    def test_transcribe_http_error(self, mock_post):
        """Test handling of HTTP errors"""
        transcriber = HTTPTranscriber(
            api_key="test_key",
            base_url="https://api.test.com"
        )

        # Mock HTTP error
        import requests
        mock_post.side_effect = requests.HTTPError("401 Unauthorized")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(b"audio")
            tmp_path = tmp.name

        try:
            with pytest.raises(requests.HTTPError):
                transcriber.transcribe(tmp_path)
        finally:
            os.unlink(tmp_path)

    @pytest.mark.unit
    @patch('talklabs_stt.http_client.requests.post')
    def test_transcribe_timeout(self, mock_post):
        """Test handling of timeout errors"""
        import requests

        transcriber = HTTPTranscriber(
            api_key="test_key",
            base_url="https://api.test.com",
            timeout=1
        )

        mock_post.side_effect = requests.Timeout("Request timed out")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(b"audio")
            tmp_path = tmp.name

        try:
            with pytest.raises(requests.Timeout):
                transcriber.transcribe(tmp_path)
        finally:
            os.unlink(tmp_path)

    @pytest.mark.unit
    @patch('talklabs_stt.http_client.requests.post')
    def test_transcribe_with_kwargs(self, mock_post):
        """Test transcription with kwargs override"""
        transcriber = HTTPTranscriber(
            api_key="test_key",
            base_url="https://api.test.com"
        )

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": {}}
        mock_post.return_value = mock_response

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(b"audio")
            tmp_path = tmp.name

        try:
            transcriber.transcribe(tmp_path, language="es")

            params = mock_post.call_args[1]["params"]
            assert params["language"] == "es"

        finally:
            os.unlink(tmp_path)

    @pytest.mark.unit
    @patch('talklabs_stt.http_client.requests.post')
    def test_transcribe_reads_file_content(self, mock_post):
        """Test that file content is read and sent correctly"""
        transcriber = HTTPTranscriber(
            api_key="test_key",
            base_url="https://api.test.com"
        )

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": {}}
        mock_post.return_value = mock_response

        test_audio = b"fake_audio_content_12345"

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(test_audio)
            tmp_path = tmp.name

        try:
            transcriber.transcribe(tmp_path)

            # Check that file data was sent
            call_args = mock_post.call_args
            sent_data = call_args[1]["data"]
            assert sent_data == test_audio

        finally:
            os.unlink(tmp_path)

    @pytest.mark.unit
    @patch('talklabs_stt.http_client.requests.post')
    def test_transcribe_uses_correct_url(self, mock_post):
        """Test that correct API URL is used"""
        transcriber = HTTPTranscriber(
            api_key="test_key",
            base_url="https://custom.api.com/stt"
        )

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": {}}
        mock_post.return_value = mock_response

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(b"audio")
            tmp_path = tmp.name

        try:
            transcriber.transcribe(tmp_path)

            # Check URL
            called_url = mock_post.call_args[0][0]
            assert called_url == "https://custom.api.com/stt/v1/listen"

        finally:
            os.unlink(tmp_path)
