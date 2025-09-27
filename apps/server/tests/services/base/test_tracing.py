import pytest
from unittest.mock import Mock, patch
from contextlib import contextmanager

from services.base.tracing import (
    TracingService,
    LoggingTracingService,
    LangFuseTracingService,
    get_tracing_service,
)


class MockTracingService(TracingService):
    def __init__(self):
        self.trace_implementation_called = False
        self.trace_implementation_error = None
        self.trace_implementation_args = None
        self.trace_implementation_kwargs = None

    @contextmanager
    def _trace_implementation(self, trace_id: str, **kwargs):
        """Mock implementation du context manager"""
        self.trace_implementation_called = True
        self.trace_implementation_kwargs = kwargs
        if self.trace_implementation_error:
            raise self.trace_implementation_error
        try:
            yield trace_id
        finally:
            pass


@pytest.fixture
def mock_tracing_service():
    return MockTracingService()


@patch("services.base.tracing.logger")
def test_trace_context_success(mock_logger, mock_tracing_service):
    """Test successful trace_context execution"""
    trace_id = "test_trace_123"

    with mock_tracing_service.trace_context(trace_id):
        pass

    assert mock_tracing_service.trace_implementation_called


@patch("services.base.tracing.logger")
def test_trace_context_with_kwargs(mock_logger, mock_tracing_service):
    """Test trace_context with additional keyword arguments"""
    trace_id = "test_trace_123"
    kwargs = {"name": "test", "metadata": {"key": "value"}}

    with mock_tracing_service.trace_context(trace_id, **kwargs):
        pass

    assert mock_tracing_service.trace_implementation_called
    # Vérifie que les kwargs ont été passés (avec metadata enrichie)
    passed_kwargs = mock_tracing_service.trace_implementation_kwargs
    assert "name" in passed_kwargs
    assert passed_kwargs["name"] == "test"
    assert "metadata" in passed_kwargs
    assert "key" in passed_kwargs["metadata"]
    assert "start_time" in passed_kwargs["metadata"]  # Ajouté automatiquement


@patch("builtins.__import__")
@patch("services.base.tracing.logger")
def test_langfuse_tracing_service_init_success(mock_logger, mock_import):
    """Test LangFuseTracingService initialization with successful auth"""
    mock_langfuse_class = Mock()
    mock_client = Mock()
    mock_client.auth_check.return_value = True
    mock_langfuse_class.return_value = mock_client

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
    mock_langfuse_class = Mock()
    mock_client = Mock()
    mock_client.auth_check.return_value = False
    mock_langfuse_class.return_value = mock_client

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
@patch("services.base.tracing.logger")
def test_langfuse_tracing_service_init_import_error(mock_logger, mock_import):
    """Test LangFuseTracingService initialization with import error"""

    def import_side_effect(name, *args, **kwargs):
        if name == "langfuse":
            raise ImportError("No module named 'langfuse'")
        return __import__(name, *args, **kwargs)

    mock_import.side_effect = import_side_effect

    service = LangFuseTracingService()

    assert service.client is None
    assert service.is_langfuse is False
    mock_logger.warning.assert_called_once()
    assert "Failed to initialize Langfuse client" in mock_logger.warning.call_args[0][0]


@patch("builtins.__import__")
def test_langfuse_tracing_service_trace_disabled(mock_import):
    """Test LangFuseTracingService trace when disabled"""
    mock_langfuse_class = Mock()
    mock_client = Mock()
    mock_client.auth_check.return_value = False
    mock_langfuse_class.return_value = mock_client

    def import_side_effect(name, *args, **kwargs):
        if name == "langfuse":
            mock_module = Mock()
            mock_module.Langfuse = mock_langfuse_class
            return mock_module
        return __import__(name, *args, **kwargs)

    mock_import.side_effect = import_side_effect

    service = LangFuseTracingService()
    trace_id = "test_trace"

    with service.trace_context(trace_id, name="test"):
        pass

    # Vérifier qu'aucune méthode Langfuse n'a été appelée
    mock_client.create_trace_id.assert_not_called()
    mock_client.start_generation.assert_not_called()


@patch("builtins.__import__")
@patch("services.base.tracing.logger")
def test_langfuse_tracing_service_trace_enabled(mock_logger, mock_import):
    """Test LangFuseTracingService trace when enabled"""
    mock_langfuse_class = Mock()
    mock_client = Mock()
    mock_client.auth_check.return_value = True
    mock_trace = Mock()
    mock_client.create_trace_id.return_value = "generated_trace_id"
    mock_client.start_generation.return_value = mock_trace
    mock_langfuse_class.return_value = mock_client

    def import_side_effect(name, *args, **kwargs):
        if name == "langfuse":
            mock_module = Mock()
            mock_module.Langfuse = mock_langfuse_class
            return mock_module
        return __import__(name, *args, **kwargs)

    mock_import.side_effect = import_side_effect

    service = LangFuseTracingService()
    trace_id = "test_trace"

    with service.trace_context(trace_id, name="test", input={"test": "data"}):
        pass

    # Vérifier que les méthodes Langfuse ont été appelées
    mock_client.create_trace_id.assert_called_once_with(seed=trace_id)
    mock_client.start_generation.assert_called_once()
    mock_trace.update_trace.assert_called_once()
    mock_trace.update.assert_called_once()
    mock_trace.end.assert_called_once()
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

    # Vérifier que les métadonnées ont été correctement initialisées
    kwargs = mock_tracing_service.trace_implementation_kwargs
    assert "metadata" in kwargs
    assert "start_time" in kwargs["metadata"]
    assert kwargs["metadata"]["start_time"] == start_iso
    # Les métadonnées finales sont ajoutées dans le finally
    assert "duration_seconds" in kwargs["metadata"]
    assert "end_time" in kwargs["metadata"]
    assert "status" in kwargs["metadata"]
    assert kwargs["metadata"]["status"] == "completed"


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

    # Vérifier que les métadonnées d'erreur ont été ajoutées
    kwargs = mock_tracing_service.trace_implementation_kwargs
    metadata = kwargs["metadata"]
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


def test_get_tracing_service_unknown():
    """Test get_tracing_service with unknown service"""
    with pytest.raises(ValueError, match="Unknown tracing service: unknown"):
        get_tracing_service("unknown")


@patch("services.base.tracing.logger")
def test_logging_tracing_service_trace(mock_logger):
    """Test LoggingTracingService trace context"""
    service = LoggingTracingService()
    trace_id = "test_trace"
    kwargs = {"name": "test", "metadata": {"key": "value"}}

    with service.trace_context(trace_id, **kwargs):
        pass

    # Vérifier que les logs ont été appelés
    assert mock_logger.info.call_count == 2
    # Premier appel : start
    start_call = mock_logger.info.call_args_list[0][0][0]
    assert f"Trace {trace_id} started with kwargs:" in start_call
    # Deuxième appel : end
    end_call = mock_logger.info.call_args_list[1][0][0]
    assert f"Trace {trace_id} ended with kwargs:" in end_call


def test_process_error_still_propagated():
    """Test that business logic errors are still propagated"""

    class MockTracingService(TracingService):
        @contextmanager
        def _trace_implementation(self, trace_id: str, **kwargs):
            yield trace_id

    service = MockTracingService()
    trace_id = "test_trace"

    # Les erreurs métier doivent toujours être propagées
    with pytest.raises(ValueError, match="Test error"):
        with service.trace_context(trace_id):
            raise ValueError("Test error")


@patch("builtins.__import__")
@patch("services.base.tracing.logger")
def test_langfuse_tracing_service_trace_error_handling(mock_logger, mock_import):
    """Test LangFuseTracingService handles trace errors gracefully"""
    mock_langfuse_class = Mock()
    mock_client = Mock()
    mock_client.auth_check.return_value = True
    mock_client.create_trace_id.side_effect = Exception("Trace creation error")
    mock_langfuse_class.return_value = mock_client

    def import_side_effect(name, *args, **kwargs):
        if name == "langfuse":
            mock_module = Mock()
            mock_module.Langfuse = mock_langfuse_class
            return mock_module
        return __import__(name, *args, **kwargs)

    mock_import.side_effect = import_side_effect

    service = LangFuseTracingService()
    trace_id = "test_trace"

    # Ne devrait pas lever d'exception malgré l'erreur de tracing
    with service.trace_context(trace_id, name="test"):
        pass

    # Vérifier qu'un warning a été loggé
    mock_logger.warning.assert_called()
    warning_calls = [
        call for call in mock_logger.warning.call_args_list if "Error managing Langfuse trace" in str(call)
    ]
    assert len(warning_calls) > 0
