"""
Unit tests for WebSocketStreamer lifecycle and resource management.
PHASE 2 - HIGH PRIORITY - Resource cleanup and connection management.
"""
import pytest
from unittest.mock import AsyncMock, patch
from talklabs_stt.websocket_stream import WebSocketStreamer


class TestWebSocketStreamerResourceCleanup:
    """Test suite for WebSocketStreamer resource cleanup"""

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_close_when_no_connection(self):
        """Test calling close() when no connection exists"""
        streamer = WebSocketStreamer(
            api_key="test_key",
            base_url="https://api.test.com"
        )

        # Should not raise
        await streamer.close()

        assert streamer._ws is None

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_close_with_active_connection(self):
        """Test closing active WebSocket connection"""
        streamer = WebSocketStreamer(
            api_key="test_key",
            base_url="https://api.test.com"
        )

        mock_ws = AsyncMock()
        streamer._ws = mock_ws

        await streamer.close()

        mock_ws.close.assert_called_once()
        assert streamer._ws is None

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_close_multiple_times(self):
        """Test calling close() multiple times is safe"""
        streamer = WebSocketStreamer(
            api_key="test_key",
            base_url="https://api.test.com"
        )

        mock_ws = AsyncMock()
        streamer._ws = mock_ws

        # First close
        await streamer.close()
        assert mock_ws.close.call_count == 1

        # Second close - should be safe
        await streamer.close()
        # Should not call ws.close again since _ws is None
        assert mock_ws.close.call_count == 1

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_close_error_handling(self):
        """Test error handling during close"""
        streamer = WebSocketStreamer(
            api_key="test_key",
            base_url="https://api.test.com"
        )

        mock_ws = AsyncMock()
        mock_ws.close.side_effect = Exception("WebSocket close error")
        streamer._ws = mock_ws

        # Should not raise - errors should be logged
        await streamer.close()

        # _ws should still be set to None even on error
        assert streamer._ws is None

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_close_clears_params(self):
        """Test that close() clears connection parameters"""
        streamer = WebSocketStreamer(
            api_key="test_key",
            base_url="https://api.test.com"
        )

        mock_ws = AsyncMock()
        streamer._ws = mock_ws
        streamer._ws_params = {"sample_rate": 16000, "language": "pt"}

        await streamer.close()

        assert streamer._ws is None
        assert streamer._ws_params is None


class TestWebSocketStreamerConnectionLifecycle:
    """Test suite for WebSocket connection lifecycle management"""

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_lifecycle_connect_stream_close(self):
        """Test complete lifecycle: connect -> stream -> close"""
        streamer = WebSocketStreamer(
            api_key="test_key",
            base_url="https://api.test.com"
        )

        with patch('websockets.connect', new_callable=AsyncMock) as mock_connect:
            mock_ws = AsyncMock()
            mock_ws.closed = False
            mock_ws.close_code = None
            mock_connect.return_value = mock_ws

            # Mock audio processing and file validation
            with (
                patch('talklabs_stt.websocket_stream.prepare_audio_for_streaming') as mock_prep,
                patch('talklabs_stt.websocket_stream.validate_file_exists')
            ):
                mock_prep.return_value = (b"audio_data", 16000)

                # Mock WebSocket messages
                async def mock_messages():
                    yield '{"type": "Metadata"}'
                    msg = '{"type": "Results", "is_final": true, "channel": '
                    msg += '{"alternatives": [{"transcript": "test"}]}}'
                    yield msg

                mock_ws.__aiter__.return_value = mock_messages()

                # Stream once
                transcripts = []
                await streamer.stream(
                    audio_path="/fake/test.wav",
                    on_transcript=lambda d: transcripts.append(d)
                )

                # Should have connected
                assert mock_connect.called
                assert streamer._ws is not None

                # Close
                await streamer.close()

                # Should have closed connection
                mock_ws.close.assert_called_once()
                assert streamer._ws is None

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_lifecycle_reuse_connection(self):
        """Test connection reuse across multiple streams"""
        streamer = WebSocketStreamer(
            api_key="test_key",
            base_url="https://api.test.com"
        )

        with patch('websockets.connect', new_callable=AsyncMock) as mock_connect:
            mock_ws = AsyncMock()
            mock_ws.closed = False
            mock_ws.close_code = None
            mock_connect.return_value = mock_ws

            with (
                patch('talklabs_stt.websocket_stream.prepare_audio_for_streaming') as mock_prep,
                patch('talklabs_stt.websocket_stream.validate_file_exists')
            ):
                mock_prep.return_value = (b"audio_data", 16000)

                async def mock_messages():
                    msg = '{"type": "Results", "is_final": true, "channel": '
                    msg += '{"alternatives": [{"transcript": "test"}]}}'
                    yield msg

                mock_ws.__aiter__.return_value = mock_messages()

                # First stream
                await streamer.stream(audio_path="/fake/test1.wav")
                assert mock_connect.call_count == 1

                # Second stream - should reuse connection
                mock_ws.closed = False  # Still open
                mock_ws.__aiter__.return_value = mock_messages()
                await streamer.stream(audio_path="/fake/test2.wav")

                # Should NOT have reconnected
                assert mock_connect.call_count == 1

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_lifecycle_reconnect_after_close(self):
        """Test reconnection after manual close"""
        streamer = WebSocketStreamer(
            api_key="test_key",
            base_url="https://api.test.com"
        )

        with patch('websockets.connect', new_callable=AsyncMock) as mock_connect:
            mock_ws = AsyncMock()
            mock_ws.closed = False
            mock_ws.close_code = None
            mock_connect.return_value = mock_ws

            with (
                patch('talklabs_stt.websocket_stream.prepare_audio_for_streaming') as mock_prep,
                patch('talklabs_stt.websocket_stream.validate_file_exists')
            ):
                mock_prep.return_value = (b"audio_data", 16000)

                async def mock_messages():
                    msg = '{"type": "Results", "is_final": true, "channel": '
                    msg += '{"alternatives": [{"transcript": "test"}]}}'
                    yield msg

                mock_ws.__aiter__.return_value = mock_messages()

                # First stream
                await streamer.stream(audio_path="/fake/test1.wav")
                first_call_count = mock_connect.call_count

                # Close connection
                await streamer.close()
                assert streamer._ws is None

                # Stream again - should reconnect
                mock_ws2 = AsyncMock()
                mock_ws2.closed = False
                mock_ws2.close_code = None
                mock_ws2.__aiter__.return_value = mock_messages()
                mock_connect.return_value = mock_ws2

                await streamer.stream(audio_path="/fake/test2.wav")

                # Should have reconnected
                assert mock_connect.call_count == first_call_count + 1


class TestWebSocketStreamerExceptionHandling:
    """Test suite for exception handling during streaming"""

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_connection_closed_error_retries(self):
        """Test retry on ConnectionClosed error"""
        streamer = WebSocketStreamer(
            api_key="test_key",
            base_url="https://api.test.com"
        )

        with patch('websockets.connect', new_callable=AsyncMock) as mock_connect:
            import websockets

            # First attempt fails, second succeeds
            mock_ws1 = AsyncMock()
            mock_ws1.send.side_effect = websockets.exceptions.ConnectionClosed(None, None)

            mock_ws2 = AsyncMock()
            mock_ws2.closed = False
            mock_ws2.close_code = None

            async def mock_messages():
                msg = '{"type": "Results", "is_final": true, "channel": '
                msg += '{"alternatives": [{"transcript": "success"}]}}'
                yield msg

            mock_ws2.__aiter__.return_value = mock_messages()

            mock_connect.side_effect = [mock_ws1, mock_ws2]

            with (
                patch('talklabs_stt.websocket_stream.prepare_audio_for_streaming') as mock_prep,
                patch('talklabs_stt.websocket_stream.validate_file_exists')
            ):
                mock_prep.return_value = (b"audio", 16000)

                # Should retry and succeed
                await streamer.stream(audio_path="/fake/test.wav")

                # Should have tried twice
                assert mock_connect.call_count == 2
