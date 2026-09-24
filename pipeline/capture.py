import logging
import queue
import threading
import time
from dataclasses import dataclass

import cv2
import numpy as np

logger = logging.getLogger("capture")


@dataclass
class CapturedFrame:
    """Frame listo para la etapa de detección."""

    original: np.ndarray
    processed: np.ndarray
    timestamp: float
    capture_ms: float
    preprocess_ms: float


def parse_source(raw: str) -> int | str:
    """Convierte CAMERA_SOURCE a índice de webcam ("0") o deja la URL/ruta tal cual."""
    return int(raw) if raw.isdigit() else raw


def preprocess(frame: np.ndarray) -> np.ndarray:
    """Preprocesamiento básico: escala de grises y ecualización de contraste."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return cv2.equalizeHist(gray)


class FrameCapture(threading.Thread):
    """Hilo de captura continua que publica frames en una cola acotada.

    Si la cola está llena se descarta el frame más antiguo, de modo que la
    detección siempre trabaje sobre la imagen más reciente y la memoria no crezca.
    Si la fuente falla (cámara desconectada, RTSP caído) reintenta la conexión
    con espera exponencial sin detener el pipeline.

    Args:
        source: Índice de webcam o URL RTSP / ruta de video.
        frame_queue: Cola donde se publican los ``CapturedFrame``.
        stop_event: Evento para detener el hilo.
        target_fps: Tope de frames por segundo a capturar.
        max_backoff_s: Espera máxima entre reintentos de conexión.
        stats_every: Cada cuántos frames se loguea el resumen de latencias.
        io_timeout_ms: Tiempo máximo para abrir la fuente o leer un frame.
    """

    def __init__(
        self,
        source: int | str,
        frame_queue: "queue.Queue[CapturedFrame]",
        stop_event: threading.Event,
        target_fps: float = 30.0,
        max_backoff_s: float = 30.0,
        stats_every: int = 30,
        io_timeout_ms: int = 5000,
    ) -> None:
        super().__init__(name="frame-capture", daemon=True)
        self.source = source
        self.frame_queue = frame_queue
        self.stop_event = stop_event
        self.frame_interval = 1.0 / target_fps
        self.max_backoff_s = max_backoff_s
        self.stats_every = stats_every
        self.io_timeout_ms = io_timeout_ms
        self._cap: cv2.VideoCapture | None = None

    def run(self) -> None:
        capture_times: list[float] = []
        preprocess_times: list[float] = []
        window_start = time.perf_counter()

        while not self.stop_event.is_set():
            if not self._ensure_connected():
                break

            loop_start = time.perf_counter()
            ok, frame = self._cap.read()
            read_end = time.perf_counter()
            if not ok:
                logger.warning("No se pudo leer el frame; reconectando a la fuente")
                self._release()
                continue

            processed = preprocess(frame)
            preprocess_end = time.perf_counter()

            captured = CapturedFrame(
                original=frame,
                processed=processed,
                timestamp=time.time(),
                capture_ms=(read_end - loop_start) * 1000,
                preprocess_ms=(preprocess_end - read_end) * 1000,
            )
            self._publish(captured)

            capture_times.append(captured.capture_ms)
            preprocess_times.append(captured.preprocess_ms)
            if len(capture_times) >= self.stats_every:
                fps = len(capture_times) / (time.perf_counter() - window_start)
                logger.info(
                    "[Latencia] captura: prom %.1f ms (máx %.1f) | preprocesamiento: prom %.2f ms (máx %.2f) | %.1f FPS",
                    sum(capture_times) / len(capture_times),
                    max(capture_times),
                    sum(preprocess_times) / len(preprocess_times),
                    max(preprocess_times),
                    fps,
                )
                capture_times.clear()
                preprocess_times.clear()
                window_start = time.perf_counter()

            # Tope de ~target_fps (relevante para archivos de video, que se leen sin espera)
            sleep_time = self.frame_interval - (time.perf_counter() - loop_start)
            if sleep_time > 0:
                time.sleep(sleep_time)

        self._release()
        logger.info("Captura detenida")

    def _ensure_connected(self) -> bool:
        """Abre la fuente si no está abierta, reintentando con backoff exponencial.

        Returns:
            True si hay una fuente abierta, False si se pidió detener el hilo.
        """
        backoff = 1.0
        while self._cap is None or not self._cap.isOpened():
            if self.stop_event.is_set():
                return False
            logger.info("Conectando a la fuente de video: %s", self.source)
            # Timeouts para que una cámara RTSP caída no bloquee el hilo indefinidamente
            self._cap = cv2.VideoCapture(
                self.source,
                cv2.CAP_ANY,
                [
                    cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, self.io_timeout_ms,
                    cv2.CAP_PROP_READ_TIMEOUT_MSEC, self.io_timeout_ms,
                ],
            )
            if self._cap.isOpened():
                logger.info("Fuente de video conectada")
                return True
            self._release()
            logger.warning("No se pudo abrir la fuente de video; reintento en %.0f s", backoff)
            self.stop_event.wait(backoff)
            backoff = min(backoff * 2, self.max_backoff_s)
        return True

    def _publish(self, frame: CapturedFrame) -> None:
        """Encola el frame descartando el más antiguo si la cola está llena."""
        try:
            self.frame_queue.put_nowait(frame)
        except queue.Full:
            try:
                self.frame_queue.get_nowait()
            except queue.Empty:
                pass
            self.frame_queue.put_nowait(frame)

    def _release(self) -> None:
        if self._cap is not None:
            self._cap.release()
            self._cap = None
