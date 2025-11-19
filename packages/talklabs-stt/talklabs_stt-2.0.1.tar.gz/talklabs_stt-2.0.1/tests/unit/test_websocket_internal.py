"""
Critical tests for WebSocketStreamer class - Internal methods.
Priority: CRITICAL - 0% coverage on core streaming methods
"""
import pytest
import asyncio
import json
from unittest.mock import AsyncMock, patch
from talklabs_stt.websocket_stream import WebSocketStreamer
from talklabs_stt.models import TranscriptionOptions


class TestWebSocketStreamerEnsureConnected:
    """Test suite for WebSocketStreamer._ensure_connected method (CRITICAL)"""

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_ensure_connected_first_time(self):
        """Test opening WebSocket connection for first time"""
        streamer = WebSocketStreamer(
            api_key="test_key",
            base_url="https://api.test.com"
        )

        with patch('websockets.connect', new_callable=AsyncMock) as mock_connect:
            mock_ws = AsyncMock()
            mock_connect.return_value = mock_ws

            with patch('talklabs_stt.websocket_stream.prepare_audio_for_streaming') as mock_prep:
                mock_prep.return_value = (b"audio_data", 16000)

                await streamer._ensure_connected(
                    audio_path="/fake/test.wav",
                    options=TranscriptionOptions(language="pt")
                )

                # Should have connected and authenticated
                mock_connect.assert_called_once()
                mock_ws.send.assert_called_once()

                # Verify authentication message
                auth_msg = json.loads(mock_ws.send.call_args[0][0])
                assert auth_msg["xi_api_key"] == "test_key"

                assert streamer._ws == mock_ws

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_ensure_connected_reuse_existing(self):
        """Test reusing existing WebSocket connection"""
        streamer = WebSocketStreamer(
            api_key="test_key",
            base_url="https://api.test.com"
        )

        # Mock existing open connection
        mock_ws = AsyncMock()
        mock_ws.closed = False
        mock_ws.close_code = None
        streamer._ws = mock_ws
        streamer._ws_params = {"sample_rate": 16000, "language": "pt"}

        with patch('websockets.connect', new_callable=AsyncMock) as mock_connect:
            await streamer._ensure_connected(
                audio_path="/fake/test.wav",
                options=None
            )

            # Should NOT connect again
            mock_connect.assert_not_called()
            # Still using same connection
            assert streamer._ws == mock_ws

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_ensure_connected_reconnect_closed(self):
        """Test reconnecting when connection is closed"""
        streamer = WebSocketStreamer(
            api_key="test_key",
            base_url="https://api.test.com"
        )

        # Mock closed connection
        mock_old_ws = AsyncMock()
        mock_old_ws.closed = True
        mock_old_ws.close_code = 1000
        streamer._ws = mock_old_ws
        streamer._ws_params = {"sample_rate": 16000, "language": "pt"}

        with patch('websockets.connect', new_callable=AsyncMock) as mock_connect:
            mock_new_ws = AsyncMock()
            mock_connect.return_value = mock_new_ws

            await streamer._ensure_connected(
                audio_path="/fake/test.wav",
                options=None
            )

            # Should reconnect
            mock_connect.assert_called_once()
            assert streamer._ws == mock_new_ws

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_ensure_connected_url_conversion(self):
        """Test HTTPS to WSS URL conversion"""
        streamer = WebSocketStreamer(
            api_key="test_key",
            base_url="https://api.example.com"
        )

        with patch('websockets.connect', new_callable=AsyncMock) as mock_connect:
            mock_ws = AsyncMock()
            mock_connect.return_value = mock_ws

            with patch('talklabs_stt.websocket_stream.prepare_audio_for_streaming') as mock_prep:
                mock_prep.return_value = (b"audio", 16000)

                await streamer._ensure_connected(
                    audio_path="/fake/test.wav",
                    options=TranscriptionOptions()
                )

                # Verify WSS URL
                call_url = mock_connect.call_args[0][0]
                assert call_url.startswith("wss://api.example.com")
                assert "/v1/listen?" in call_url

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_ensure_connected_forces_turbo_model(self):
        """Test that model is always forced to 'turbo'"""
        streamer = WebSocketStreamer(
            api_key="test_key",
            base_url="https://api.test.com"
        )

        with patch('websockets.connect', new_callable=AsyncMock) as mock_connect:
            mock_ws = AsyncMock()
            mock_connect.return_value = mock_ws

            with patch('talklabs_stt.websocket_stream.prepare_audio_for_streaming') as mock_prep:
                mock_prep.return_value = (b"audio", 16000)

                options = TranscriptionOptions(language="pt")

                await streamer._ensure_connected(
                    audio_path="/fake/test.wav",
                    options=options
                )

                # Model is always forced to turbo internally
                call_url = mock_connect.call_args[0][0]
                assert "model=turbo" in call_url
                assert "punctuate=true" in call_url


class TestWebSocketStreamerSendAudio:
    """Test suite for WebSocketStreamer._send_audio method (CRITICAL)"""

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_send_audio_chunks(self):
        """Test sending audio in chunks"""
        streamer = WebSocketStreamer(
            api_key="test_key",
            base_url="https://api.test.com"
        )

        mock_ws = AsyncMock()
        streamer._ws = mock_ws

        audio_bytes = b"x" * 2400  # 2400 bytes
        chunk_size = 1000

        await streamer._send_audio(audio_bytes, chunk_size)

        # Should send 3 chunks (1000, 1000, 400) + Finalize
        assert mock_ws.send.call_count == 4  # 3 audio chunks + 1 finalize

        # Verify Finalize message
        finalize_call = mock_ws.send.call_args_list[-1]
        finalize_msg = json.loads(finalize_call[0][0])
        assert finalize_msg["type"] == "Finalize"

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_send_audio_empty(self):
        """Test sending empty audio"""
        streamer = WebSocketStreamer(
            api_key="test_key",
            base_url="https://api.test.com"
        )

        mock_ws = AsyncMock()
        streamer._ws = mock_ws

        await streamer._send_audio(b"", chunk_size=1000)

        # Should only send Finalize (no audio chunks)
        assert mock_ws.send.call_count == 1
        finalize_msg = json.loads(mock_ws.send.call_args[0][0])
        assert finalize_msg["type"] == "Finalize"

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_send_audio_error_handling(self):
        """Test error handling during audio send"""
        streamer = WebSocketStreamer(
            api_key="test_key",
            base_url="https://api.test.com"
        )

        mock_ws = AsyncMock()
        mock_ws.send.side_effect = Exception("Connection lost")
        streamer._ws = mock_ws

        with pytest.raises(Exception, match="Connection lost"):
            await streamer._send_audio(b"audio_data", chunk_size=100)


class TestWebSocketStreamerReceiveTranscripts:
    """Test suite for WebSocketStreamer._receive_transcripts method (CRITICAL)"""

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_receive_transcripts_final_result(self):
        """Test receiving final transcription result"""
        streamer = WebSocketStreamer(
            api_key="test_key",
            base_url="https://api.test.com"
        )

        # Mock WebSocket messages
        mock_ws = AsyncMock()
        mock_ws.__aiter__.return_value = [
            json.dumps({
                "type": "Results",
                "is_final": True,
                "channel": {
                    "alternatives": [{"transcript": "Hello world", "confidence": 0.95}]
                }
            })
        ]
        streamer._ws = mock_ws

        # Callback tracking
        transcripts_received = []

        def on_transcript(data):
            transcripts_received.append(data)

        final_event = asyncio.Event()

        await streamer._receive_transcripts(
            on_transcript=on_transcript,
            on_metadata=None,
            final_received=final_event
        )

        # Should have received transcript
        assert len(transcripts_received) == 1
        assert transcripts_received[0]["channel"]["alternatives"][0]["transcript"] == "Hello world"

        # Should have set final event
        assert final_event.is_set()

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_receive_transcripts_metadata(self):
        """Test receiving metadata message"""
        streamer = WebSocketStreamer(
            api_key="test_key",
            base_url="https://api.test.com"
        )

        mock_ws = AsyncMock()
        mock_ws.__aiter__.return_value = [
            json.dumps({"type": "Metadata", "duration": 5.2, "channels": 1})
        ]
        streamer._ws = mock_ws

        metadata_received = []

        def on_metadata(data):
            metadata_received.append(data)

        final_event = asyncio.Event()

        await streamer._receive_transcripts(
            on_transcript=None,
            on_metadata=on_metadata,
            final_received=final_event
        )

        # Should have received metadata
        assert len(metadata_received) == 1
        assert metadata_received[0]["duration"] == 5.2

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_receive_transcripts_error_message(self):
        """Test receiving error message from server"""
        streamer = WebSocketStreamer(
            api_key="test_key",
            base_url="https://api.test.com"
        )

        mock_ws = AsyncMock()
        mock_ws.__aiter__.return_value = [
            json.dumps({"type": "Error", "error": "Invalid audio format"})
        ]
        streamer._ws = mock_ws

        final_event = asyncio.Event()

        # Should log error but not raise
        await streamer._receive_transcripts(
            on_transcript=None,
            on_metadata=None,
            final_received=final_event
        )

        # Should set final event to unblock waiting
        assert final_event.is_set()

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_receive_transcripts_cancelled(self):
        """Test handling task cancellation"""
        streamer = WebSocketStreamer(
            api_key="test_key",
            base_url="https://api.test.com"
        )

        # Mock that yields slowly
        async def slow_messages():
            for _ in range(10):
                await asyncio.sleep(1)
                yield json.dumps({"type": "Results", "is_final": True})

        mock_ws = AsyncMock()
        mock_ws.__aiter__.return_value = slow_messages()
        streamer._ws = mock_ws

        final_event = asyncio.Event()

        # Create task and cancel it quickly
        task = asyncio.create_task(
            streamer._receive_transcripts(
                on_transcript=None,
                on_metadata=None,
                final_received=final_event
            )
        )

        await asyncio.sleep(0.05)  # Let it start
        task.cancel()

        # Should handle cancellation gracefully (catches CancelledError internally)
        try:
            await task
        except asyncio.CancelledError:
            pass  # Expected - task was cancelled
