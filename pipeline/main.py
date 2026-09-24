import logging
import os
import queue
import signal
import threading

from capture import CapturedFrame, FrameCapture, parse_source
from detector import PlateDetector
from ocr import TextExtractor
from validator import validate_plate

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("pipeline")

# Pocos frames en cola: si la detección se atrasa, se descartan los viejos
FRAME_QUEUE_SIZE = 5


def main() -> None:
    logger.info("Iniciando ALPR Pipeline... ¡El entorno está listo!")
    detector = PlateDetector()
    ocr = TextExtractor()

    stop_event = threading.Event()
    # Docker detiene el contenedor con SIGTERM; lo tratamos igual que Ctrl+C
    signal.signal(signal.SIGTERM, lambda *_: stop_event.set())

    frame_queue: "queue.Queue[CapturedFrame]" = queue.Queue(maxsize=FRAME_QUEUE_SIZE)
    source = parse_source(os.environ.get("CAMERA_SOURCE", "0"))
    capture = FrameCapture(source, frame_queue, stop_event)
    capture.start()

    try:
        while not stop_event.is_set():
            try:
                frame = frame_queue.get(timeout=1.0)
            except queue.Empty:
                continue

            # 1. Detección (se integra en el issue #3)
            # plates = detector.detect(frame.processed)
            # 2. OCR (issue #4) y 3. validación (issue #5)
    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()
        capture.join(timeout=5)
        logger.info("Pipeline detenido.")


if __name__ == "__main__":
    main()
