"""
Unit tests for audio_processor module.
CRITICAL module with zero current coverage - HIGH PRIORITY.
"""
import pytest
import numpy as np
from unittest.mock import patch
from talklabs_stt.audio_processor import (
    load_audio,
    ensure_mono,
    to_pcm_bytes,
    prepare_audio_for_streaming
)


class TestLoadAudio:
    """Test suite for load_audio function."""

    @pytest.mark.unit
    @patch('soundfile.read')
    def test_load_audio_success(self, mock_sf_read):
        """Test successful audio loading."""
        mock_audio = np.array([100, 200, 300], dtype='int16')
        mock_sf_read.return_value = (mock_audio, 16000)

        audio_data, sample_rate = load_audio("/fake/path.wav")

        assert np.array_equal(audio_data, mock_audio)
        assert sample_rate == 16000
        mock_sf_read.assert_called_once_with("/fake/path.wav", dtype='int16')

    @pytest.mark.unit
    @patch('soundfile.read', side_effect=Exception("File not found"))
    def test_load_audio_failure(self, mock_sf_read):
        """Test audio loading with file error."""
        with pytest.raises(Exception, match="File not found"):
            load_audio("/nonexistent.wav")

    @pytest.mark.unit
    @patch('soundfile.read')
    def test_load_audio_empty_file(self, mock_sf_read):
        """Test loading empty audio file."""
        mock_audio = np.array([], dtype='int16')
        mock_sf_read.return_value = (mock_audio, 16000)

        audio_data, sample_rate = load_audio("/empty.wav")

        assert len(audio_data) == 0
        assert sample_rate == 16000


class TestEnsureMono:
    """Test suite for ensure_mono function."""

    @pytest.mark.unit
    def test_ensure_mono_already_mono(self):
        """Test with already mono audio."""
        mono_audio = np.array([100, 200, 300], dtype='int16')
        result = ensure_mono(mono_audio)

        assert np.array_equal(result, mono_audio)
        assert result.dtype == np.int16

    @pytest.mark.unit
    def test_ensure_mono_stereo_to_mono(self):
        """Test conversion from stereo to mono."""
        stereo_audio = np.array([
            [100, 150],
            [200, 250],
            [300, 350]
        ], dtype='int16')

        result = ensure_mono(stereo_audio)

        # Should average left and right channels
        expected = np.array([125, 225, 325], dtype='int16')
        assert np.array_equal(result, expected)
        assert result.dtype == np.int16
        assert len(result.shape) == 1  # Should be 1D

    @pytest.mark.unit
    def test_ensure_mono_multichannel(self):
        """Test conversion from multi-channel audio."""
        multichannel = np.array([
            [100, 110, 120],
            [200, 210, 220]
        ], dtype='int16')

        result = ensure_mono(multichannel)

        # Should average all channels
        expected = np.array([110, 210], dtype='int16')
        assert np.array_equal(result, expected)


class TestToPcmBytes:
    """Test suite for to_pcm_bytes function."""

    @pytest.mark.unit
    def test_to_pcm_bytes_basic(self):
        """Test basic conversion to PCM bytes."""
        audio = np.array([100, 200, 300], dtype='int16')
        result = to_pcm_bytes(audio)

        assert isinstance(result, bytes)
        assert len(result) == 6  # 3 samples * 2 bytes per int16

    @pytest.mark.unit
    def test_to_pcm_bytes_empty(self):
        """Test conversion of empty array."""
        audio = np.array([], dtype='int16')
        result = to_pcm_bytes(audio)

        assert isinstance(result, bytes)
        assert len(result) == 0

    @pytest.mark.unit
    def test_to_pcm_bytes_large_array(self):
        """Test conversion of large audio array."""
        audio = np.random.randint(-32768, 32767, size=100000, dtype='int16')
        result = to_pcm_bytes(audio)

        assert isinstance(result, bytes)
        assert len(result) == 200000  # 100000 samples * 2 bytes


class TestPrepareAudioForStreaming:
    """Test suite for prepare_audio_for_streaming function."""

    @pytest.mark.unit
    @patch('talklabs_stt.audio_processor.load_audio')
    def test_prepare_audio_mono_16khz(self, mock_load):
        """Test preparing mono 16kHz audio."""
        mock_audio = np.array([100, 200, 300], dtype='int16')
        mock_load.return_value = (mock_audio, 16000)

        audio_bytes, sample_rate = prepare_audio_for_streaming("/fake.wav", 16000)

        assert isinstance(audio_bytes, bytes)
        assert sample_rate == 16000
        assert len(audio_bytes) == 6

    @pytest.mark.unit
    @patch('talklabs_stt.audio_processor.load_audio')
    def test_prepare_audio_stereo_to_mono(self, mock_load):
        """Test preparing stereo audio (should convert to mono)."""
        stereo = np.array([[100, 150], [200, 250]], dtype='int16')
        mock_load.return_value = (stereo, 16000)

        audio_bytes, sample_rate = prepare_audio_for_streaming("/fake.wav", 16000)

        assert isinstance(audio_bytes, bytes)
        assert sample_rate == 16000
        # Should have converted stereo to mono
        assert len(audio_bytes) == 4  # 2 samples * 2 bytes

    @pytest.mark.unit
    @patch('talklabs_stt.audio_processor.load_audio')
    def test_prepare_audio_different_sample_rate(self, mock_load):
        """Test preparing audio with non-16kHz sample rate."""
        mock_audio = np.array([100, 200, 300], dtype='int16')
        mock_load.return_value = (mock_audio, 44100)  # Different rate

        audio_bytes, sample_rate = prepare_audio_for_streaming("/fake.wav", 16000)

        # Should return original sample rate (server will resample)
        assert sample_rate == 44100
        assert isinstance(audio_bytes, bytes)

    @pytest.mark.unit
    @patch('talklabs_stt.audio_processor.load_audio', side_effect=Exception("Error"))
    def test_prepare_audio_error_handling(self, mock_load):
        """Test error handling during audio preparation."""
        with pytest.raises(Exception, match="Error"):
            prepare_audio_for_streaming("/bad.wav", 16000)
