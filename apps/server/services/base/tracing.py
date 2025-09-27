from abc import ABC, abstractmethod
from contextlib import contextmanager
import time
from datetime import datetime
from src.logger import logger


class TracingService(ABC):
    @abstractmethod
    def _start_trace(self, trace_id: str, *args, **kwargs) -> None: ...

    def start_trace(self, trace_id: str, *args, **kwargs) -> None:
        logger.info(f"Starting trace {trace_id}")
        try:
            self._start_trace(trace_id, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error starting trace {trace_id}: {e}")

    @abstractmethod
    def _end_trace(self, trace_id: str, *args, **kwargs) -> None: ...

    def end_trace(self, trace_id: str, *args, **kwargs) -> None:
        logger.info(f"Ending trace {trace_id}")
        try:
            self._end_trace(trace_id, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error ending trace {trace_id}: {e}")

    @contextmanager
    def trace_context(self, trace_id: str, **kwargs):
        """Context manager pour tracer automatiquement une tâche"""
        start_time = time.time()
        kwargs.setdefault("metadata", {})["start_time"] = datetime.now().isoformat()

        self.start_trace(trace_id, **kwargs)
        try:
            yield trace_id
        except Exception as e:
            # Ajouter l'erreur dans les métadonnées
            error_metadata = {
                "error": str(e),
                "error_type": type(e).__name__,
                "status": "failed",
            }
            kwargs.get("metadata", {}).update(error_metadata)
            raise
        finally:
            # Calculer la durée et finaliser
            duration = time.time() - start_time
            kwargs.get("metadata", {}).update(
                {
                    "duration_seconds": duration,
                    "end_time": datetime.now().isoformat(),
                    "status": kwargs.get("metadata", {}).get("status", "completed"),
                }
            )
            self.end_trace(trace_id, **kwargs)


class LoggingTracingService(TracingService):
    def _start_trace(self, trace_id: str, *args, **kwargs) -> None:
        logger.info(f"Trace {trace_id} started with args: {args}, kwargs: {kwargs}")

    def _end_trace(self, trace_id: str, *args, **kwargs) -> None:
        logger.info(f"Trace {trace_id} ended with args: {args}, kwargs: {kwargs}")


class LangFuseTracingService(TracingService):
    def __init__(self):
        """
        public_key (Optional[str]): Your Langfuse public API key. Can also be set via LANGFUSE_PUBLIC_KEY environment variable.
        secret_key (Optional[str]): Your Langfuse secret API key. Can also be set via LANGFUSE_SECRET_KEY environment variable.
        host (Optional[str]): The Langfuse API host URL. Defaults to "https://cloud.langfuse.com". Can also be set via LANGFUSE_HOST environment variable.
        timeout (Optional[int]): Timeout in seconds for API requests. Defaults to 5 seconds.
        httpx_client (Optional[httpx.Client]): Custom httpx client for making non-tracing HTTP requests. If not provided, a default client will be created.
        debug (bool): Enable debug logging. Defaults to False. Can also be set via LANGFUSE_DEBUG environment variable.
        tracing_enabled (Optional[bool]): Enable or disable tracing. Defaults to True. Can also be set via LANGFUSE_TRACING_ENABLED environment variable.
        flush_at (Optional[int]): Number of spans to batch before sending to the API. Defaults to 512. Can also be set via LANGFUSE_FLUSH_AT environment variable.
        flush_interval (Optional[float]): Time in seconds between batch flushes. Defaults to 5 seconds. Can also be set via LANGFUSE_FLUSH_INTERVAL environment variable.
        environment (Optional[str]): Environment name for tracing. Default is 'default'. Can also be set via LANGFUSE_TRACING_ENVIRONMENT environment variable. Can be any lowercase alphanumeric string with hyphens and underscores that does not start with 'langfuse'.
        """
        from langfuse import Langfuse

        self.client = Langfuse()
        self.is_langfuse = True
        if not self.client.auth_check():
            logger.warning("Langfuse authentication failed. Tracing will be disabled.")
            self.is_langfuse = False

    def _start_trace(self, trace_id: str, *args, **kwargs) -> None:
        if not self.is_langfuse:
            return

        # Crée un span manuel
        self._span = self.client.start_as_current_span(
            name=kwargs.get("name", trace_id),
            trace_context={"trace_id": trace_id},
            input=kwargs.get("input"),
            metadata=kwargs.get("metadata", {}),
            tags=kwargs.get("tags", []),
            user_id=kwargs.get("user_id"),
            session_id=kwargs.get("session_id"),
        )
        # Ne pas oublier de commencer le span
        self._span.__enter__()

    def _end_trace(self, trace_id: str, *args, **kwargs) -> None:
        if not self.is_langfuse or not hasattr(self, "_span"):
            return

        metadata = kwargs.get("metadata", {})
        # Ajouter la durée comme score si disponible
        if "duration_seconds" in metadata:
            try:
                self.client.score(
                    trace_id=trace_id,
                    name="duration",
                    value=metadata["duration_seconds"],
                )
            except Exception as e:
                logger.warning(f"Unable to send score: {e}")

        # Fermer le span
        try:
            self._span.__exit__(None, None, None)
        except Exception as e:
            logger.warning(f"Error ending Langfuse span: {e}")
        finally:
            # Forcer flush
            try:
                self.client.flush()
            except Exception as e:
                logger.warning(f"Error flushing Langfuse client: {e}")


def get_tracing_service(tracing_name: str) -> TracingService:
    if tracing_name == "langfuse":
        return LangFuseTracingService()
    elif tracing_name == "logging":
        return LoggingTracingService()
    raise ValueError(f"Unknown tracing service: {tracing_name}")
