from abc import ABC, abstractmethod
from contextlib import ExitStack, contextmanager
import time
from datetime import datetime
from src.logger import logger


class TracingService(ABC):
    @abstractmethod
    @contextmanager
    def _trace_implementation(self, trace_id: str, **kwargs):
        """Context manager abstrait pour l'implémentation du tracing"""
        pass

    @contextmanager
    def trace_context(self, trace_id: str, **kwargs):
        """Context manager pour tracer automatiquement une tâche"""
        start_time = time.time()
        kwargs.setdefault("metadata", {})["start_time"] = datetime.now().isoformat()

        with self._trace_implementation(trace_id, **kwargs):
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


class LoggingTracingService(TracingService):
    @contextmanager
    def _trace_implementation(self, trace_id: str, **kwargs):
        """Implementation du tracing avec logging"""
        logger.info(f"Trace {trace_id} started with kwargs: {kwargs}")
        try:
            yield trace_id
        finally:
            logger.info(f"Trace {trace_id} ended with kwargs: {kwargs}")


class LangFuseTracingService(TracingService):
    def __init__(self):
        """
        Initialise le service de traçage Langfuse.
        """
        self.client = None
        self.is_langfuse = False
        self._propagate_attributes = None

        try:
            from langfuse import Langfuse, propagate_attributes

            self.client = Langfuse()
            self._propagate_attributes = propagate_attributes
            self.is_langfuse = self.client.auth_check()
            if not self.is_langfuse:
                logger.warning("Langfuse authentication failed. Tracing will be disabled.")
        except Exception as e:
            logger.warning(f"Failed to initialize Langfuse client: {e}. Tracing will be disabled.")
            self.is_langfuse = False

        if not self.is_langfuse and self.client is not None:
            try:
                self.client.shutdown()
            except Exception as e:
                logger.warning(f"Failed to shut down Langfuse client: {e}")
            self.client = None
            self._propagate_attributes = None

    @contextmanager
    def _trace_implementation(self, trace_id: str, **kwargs):
        """Implementation du tracing avec Langfuse"""
        if not self.is_langfuse or not self.client:
            yield None
            return

        stack = ExitStack()
        try:
            user_id = kwargs.get("user_id")
            session_id = kwargs.get("session_id")
            if user_id or session_id:
                stack.enter_context(self._propagate_attributes(user_id=user_id, session_id=session_id))

            trace = stack.enter_context(
                self.client.start_as_current_observation(
                    trace_context={"trace_id": self.client.create_trace_id(seed=trace_id)},
                    name=kwargs.get("name", trace_id),
                    as_type="generation",
                    input=kwargs.get("input"),
                    metadata=kwargs.get("metadata", {}),
                    model=kwargs.get("model", "ocr-service"),
                )
            )
        except Exception as e:
            logger.warning(f"Error creating Langfuse trace: {e}")
            stack.close()
            yield None
            return

        try:
            yield trace
        finally:
            try:
                metadata = kwargs.get("metadata", {})
                trace.update(
                    output=metadata,
                    metadata=metadata,
                    usage_details=kwargs.get("usage_details", {}),
                    cost_details=kwargs.get("cost_details", {}),
                    model=kwargs.get("model", "ocr-service"),
                )
            except Exception as e:
                logger.warning(f"Error finalizing Langfuse trace: {e}")

            stack.close()
            try:
                self.client.flush()
            except Exception as e:
                logger.warning(f"Error flushing Langfuse trace: {e}")


def get_tracing_service(tracing_name: str) -> TracingService:
    if tracing_name == "langfuse":
        return LangFuseTracingService()
    elif tracing_name == "logging":
        return LoggingTracingService()
    raise ValueError(f"Unknown tracing service: {tracing_name}")


if __name__ == "__main__":
    from uuid import uuid4

    logging_service = get_tracing_service("logging")
    langfuse_service = get_tracing_service("langfuse")

    with langfuse_service.trace_context(
        trace_id=str(uuid4()),
        name="ocr-trace",
        input={"task_id": 123},
        user_id="user_1",
        session_id="session_1",
    ):
        time.sleep(1)
        logger.info("Inside langfuse trace context")
