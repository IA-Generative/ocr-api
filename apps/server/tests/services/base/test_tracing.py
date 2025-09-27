import pytest
from unittest.mock import Mock, patch

from services.base.tracing import (
    TracingService,
    LoggingTracingService,
    LangFuseTracingService,
    get_tracing_service,
)


class MockTracingService(TracingService):
    def __init__(self):
        self.start_trace_called = False
        self.end_trace_called = False
        self.start_trace_error = None
        self.end_trace_error = None
        self.start_trace_args = None
        self.start_trace_kwargs = None
        self.end_trace_args = None
        self.end_trace_kwargs = None

    def _start_trace(self, trace_id: str, *args, **kwargs) -> None:
        self.start_trace_called = True
        self.start_trace_args = args
        self.start_trace_kwargs = kwargs
        if self.start_trace_error:
            raise self.start_trace_error

    def _end_trace(self, trace_id: str, *args, **kwargs) -> None:
        self.end_trace_called = True
        self.end_trace_args = args
        self.end_trace_kwargs = kwargs
        if self.end_trace_error:
            raise self.end_trace_error


@pytest.fixture
def mock_tracing_service():
    return MockTracingService()


@patch("services.base.tracing.logger")
def test_start_trace_success(mock_logger, mock_tracing_service):
    """Test successful start_trace execution"""
    trace_id = "test_trace_123"

    mock_tracing_service.start_trace(trace_id)

    assert mock_tracing_service.start_trace_called
    mock_logger.info.assert_called_once_with(f"Starting trace {trace_id}")
    mock_logger.error.assert_not_called()


@patch("services.base.tracing.logger")
def test_start_trace_with_args_kwargs(mock_logger, mock_tracing_service):
    """Test start_trace with additional arguments and keyword arguments"""
    trace_id = "test_trace_123"
    args = ("arg1", "arg2")
    kwargs = {"name": "test", "metadata": {"key": "value"}}

    mock_tracing_service.start_trace(trace_id, *args, **kwargs)

    assert mock_tracing_service.start_trace_called
    assert mock_tracing_service.start_trace_args == args
    assert mock_tracing_service.start_trace_kwargs == kwargs
    mock_logger.info.assert_called_once_with(f"Starting trace {trace_id}")


@patch("services.base.tracing.logger")
def test_end_trace_with_args_kwargs(mock_logger, mock_tracing_service):
    """Test end_trace with additional arguments and keyword arguments"""
    trace_id = "test_trace_123"
    args = ("arg1", "arg2")
    kwargs = {"metadata": {"duration": 5.0, "status": "completed"}}

    mock_tracing_service.end_trace(trace_id, *args, **kwargs)

    assert mock_tracing_service.end_trace_called
    assert mock_tracing_service.end_trace_args == args
    assert mock_tracing_service.end_trace_kwargs == kwargs
    mock_logger.info.assert_called_once_with(f"Ending trace {trace_id}")


@patch("builtins.__import__")
@patch("services.base.tracing.logger")
def test_langfuse_tracing_service_init_success(mock_logger, mock_import):
    """Test LangFuseTracingService initialization with successful auth"""
    # Mock the Langfuse class
    mock_langfuse_class = Mock()
    mock_client = Mock()
    mock_client.auth_check.return_value = True
    mock_langfuse_class.return_value = mock_client

    # Mock the import to return our mock Langfuse class
    def import_side_effect(name, *args, **kwargs):
        if name == "langfuse":
            mock_module = Mock()
            mock_module.Langfuse = mock_langfuse_class
            return mock_module
        return __import__(name, *args, **kwargs)

    mock_import.side_effect = import_side_effect

    service = LangFuseTracingService()

    assert service.client == mock_client
    assert service.is_langfuse is True
    mock_client.auth_check.assert_called_once()
    mock_logger.warning.assert_not_called()


@patch("builtins.__import__")
@patch("services.base.tracing.logger")
def test_langfuse_tracing_service_init_auth_fail(mock_logger, mock_import):
    """Test LangFuseTracingService initialization with failed auth"""
    # Mock the Langfuse class
    mock_langfuse_class = Mock()
    mock_client = Mock()
    mock_client.auth_check.return_value = False
    mock_langfuse_class.return_value = mock_client

    # Mock the import to return our mock Langfuse class
    def import_side_effect(name, *args, **kwargs):
        if name == "langfuse":
            mock_module = Mock()
            mock_module.Langfuse = mock_langfuse_class
            return mock_module
        return __import__(name, *args, **kwargs)

    mock_import.side_effect = import_side_effect

    service = LangFuseTracingService()

    assert service.client == mock_client
    assert service.is_langfuse is False
    mock_client.auth_check.assert_called_once()
    mock_logger.warning.assert_called_once_with("Langfuse authentication failed. Tracing will be disabled.")


@patch("builtins.__import__")
def test_langfuse_tracing_service_start_trace_disabled(mock_import):
    """Test LangFuseTracingService._start_trace when tracing is disabled"""
    # Mock the Langfuse class
    mock_langfuse_class = Mock()
    mock_client = Mock()
    mock_client.auth_check.return_value = False
    mock_langfuse_class.return_value = mock_client

    # Mock the import to return our mock Langfuse class
    def import_side_effect(name, *args, **kwargs):
        if name == "langfuse":
            mock_module = Mock()
            mock_module.Langfuse = mock_langfuse_class
            return mock_module
        return __import__(name, *args, **kwargs)

    mock_import.side_effect = import_side_effect

    service = LangFuseTracingService()
    trace_id = "test_trace"

    service._start_trace(trace_id, name="test")

    mock_client.start_as_current_span.assert_not_called()


@patch("builtins.__import__")
def test_langfuse_tracing_service_end_trace_disabled(mock_import):
    """Test LangFuseTracingService._end_trace when tracing is disabled"""
    # Mock the Langfuse class
    mock_langfuse_class = Mock()
    mock_client = Mock()
    mock_client.auth_check.return_value = False
    mock_langfuse_class.return_value = mock_client

    # Mock the import to return our mock Langfuse class
    def import_side_effect(name, *args, **kwargs):
        if name == "langfuse":
            mock_module = Mock()
            mock_module.Langfuse = mock_langfuse_class
            return mock_module
        return __import__(name, *args, **kwargs)

    mock_import.side_effect = import_side_effect

    service = LangFuseTracingService()
    trace_id = "test_trace"

    service._end_trace(trace_id, metadata={"duration_seconds": 5.0})

    mock_client.score.assert_not_called()
    mock_client.flush.assert_not_called()


@patch("builtins.__import__")
def test_langfuse_tracing_service_end_trace_without_duration(mock_import):
    """Test LangFuseTracingService._end_trace without duration in metadata"""
    # Mock the Langfuse class
    mock_langfuse_class = Mock()
    mock_client = Mock()
    mock_client.auth_check.return_value = True
    mock_span = Mock()
    mock_client.start_as_current_span.return_value = mock_span
    mock_langfuse_class.return_value = mock_client

    # Mock the import to return our mock Langfuse class
    def import_side_effect(name, *args, **kwargs):
        if name == "langfuse":
            mock_module = Mock()
            mock_module.Langfuse = mock_langfuse_class
            return mock_module
        return __import__(name, *args, **kwargs)

    mock_import.side_effect = import_side_effect

    service = LangFuseTracingService()
    # Simulate having a span from start_trace
    service._span = mock_span
    trace_id = "test_trace"

    service._end_trace(trace_id, metadata={"status": "completed"})

    mock_client.score.assert_not_called()
    mock_client.flush.assert_called_once()


@patch("services.base.tracing.time")
@patch("services.base.tracing.datetime")
def test_trace_context_metadata_initialization(mock_datetime, mock_time, mock_tracing_service):
    """Test that trace_context initializes metadata properly"""
    trace_id = "test_trace"
    start_time = 1000.0
    end_time = 1002.0
    mock_time.time.side_effect = [start_time, end_time]

    start_iso = "2023-01-01T10:00:00"
    end_iso = "2023-01-01T10:00:02"
    mock_datetime.now.return_value.isoformat.side_effect = [start_iso, end_iso]

    with mock_tracing_service.trace_context(trace_id):
        pass

    # Check that start_trace was called with metadata containing start_time
    start_kwargs = mock_tracing_service.start_trace_kwargs
    assert "metadata" in start_kwargs
    assert "start_time" in start_kwargs["metadata"]
    assert start_kwargs["metadata"]["start_time"] == start_iso

    # Check that end_trace was called with complete metadata
    end_kwargs = mock_tracing_service.end_trace_kwargs
    assert "metadata" in end_kwargs
    metadata = end_kwargs["metadata"]
    assert "duration_seconds" in metadata
    assert "end_time" in metadata
    assert "status" in metadata
    assert metadata["status"] == "completed"


@patch("services.base.tracing.time")
@patch("services.base.tracing.datetime")
def test_trace_context_error_metadata(mock_datetime, mock_time, mock_tracing_service):
    """Test that trace_context adds error metadata when exception occurs"""
    trace_id = "test_trace"
    start_time = 1000.0
    end_time = 1001.0
    mock_time.time.side_effect = [start_time, end_time]

    start_iso = "2023-01-01T10:00:00"
    end_iso = "2023-01-01T10:00:01"
    mock_datetime.now.return_value.isoformat.side_effect = [start_iso, end_iso]

    test_exception = ValueError("Test error")

    with pytest.raises(ValueError, match="Test error"):
        with mock_tracing_service.trace_context(trace_id):
            raise test_exception

    # Check error metadata was added
    end_kwargs = mock_tracing_service.end_trace_kwargs
    metadata = end_kwargs["metadata"]
    assert "error" in metadata
    assert "error_type" in metadata
    assert "status" in metadata
    assert metadata["error"] == "Test error"
    assert metadata["error_type"] == "ValueError"
    assert metadata["status"] == "failed"


def test_get_tracing_service_empty_string():
    """Test get_tracing_service with empty string"""
    with pytest.raises(ValueError, match="Unknown tracing service: "):
        get_tracing_service("")


def test_get_tracing_service_logging():
    """Test get_tracing_service with logging service"""
    service = get_tracing_service("logging")
    assert isinstance(service, LoggingTracingService)


def test_get_tracing_service_langfuse():
    """Test get_tracing_service with langfuse service"""
    service = get_tracing_service("langfuse")
    assert isinstance(service, LangFuseTracingService)


@patch("services.base.tracing.logger")
def test_logging_tracing_service_empty_args_kwargs(mock_logger):
    """Test LoggingTracingService with empty args and kwargs"""
    service = LoggingTracingService()
    trace_id = "test_trace"

    service._start_trace(trace_id)
    service._end_trace(trace_id)

    expected_start_msg = f"Trace {trace_id} started with args: (), kwargs: {{}}"
    expected_end_msg = f"Trace {trace_id} ended with args: (), kwargs: {{}}"

    mock_logger.info.assert_any_call(expected_start_msg)
    mock_logger.info.assert_any_call(expected_end_msg)


def test_tracing_error():
    class MockerrorTracingService(TracingService):
        def _start_trace(self, trace_id: str, *args, **kwargs) -> None:
            raise RuntimeError("Start trace error")

        def _end_trace(self, trace_id: str, *args, **kwargs) -> None:
            raise RuntimeError("End trace error")

    service = MockerrorTracingService()
    trace_id = "test_trace"
    with service.trace_context(trace_id):
        pass  # Should not raise


def test_process_error():
    class MockerrorTracingService(TracingService):
        def _start_trace(self, trace_id: str, *args, **kwargs) -> None:
            print("Starting trace")

        def _end_trace(self, trace_id: str, *args, **kwargs) -> None:
            print("Ending trace")

    service = MockerrorTracingService()
    trace_id = "test_trace"
    with pytest.raises(ValueError, match="Test error"):
        with service.trace_context(trace_id):
            raise ValueError("Test error")
