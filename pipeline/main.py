import cv2
import time
import os
from detector import PlateDetector
from ocr import TextExtractor
from validator import validate_plate

def main():
    print("Iniciando ALPR Pipeline... ¡El entorno está listo!")
    detector = PlateDetector()
    ocr = TextExtractor()
    
    camera_source_env = os.environ.get("CAMERA_SOURCE", "0")
    # Convertir a entero si es un número (como "0" para la webcam)
    if camera_source_env.isdigit():
        camera_source = int(camera_source_env)
    else:
        camera_source = camera_source_env
        
    print(f"Intentando conectar a la fuente de video: {camera_source}")
    cap = cv2.VideoCapture(camera_source)
    
    if not cap.isOpened():
        print(f"Advertencia: No se pudo abrir la fuente de video '{camera_source}'.")
        print("El pipeline continuará simulando el loop (sin imagen) para no detener el contenedor en Windows.")
    
    target_fps = 30
    frame_delay = 1.0 / target_fps
    
    try:
        while True:
            loop_start = time.time()
            
            if cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    print("No se pudo leer el frame. Reintentando...")
                    time.sleep(1)
                    continue
                
                # Preprocesamiento básico: escala de grises y contraste
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                processed_frame = cv2.equalizeHist(gray_frame)
                
                capture_end = time.time()
                processing_time_ms = (capture_end - loop_start) * 1000
                
                # Loguear tiempo (solo mostrando a veces para no saturar los logs, o mostrar siempre para prueba)
                print(f"[Latencia] Captura + Preprocesamiento: {processing_time_ms:.2f} ms")
                
                # 1. Detección (comentado por ahora hasta integrarlo completamente en el siguiente paso)
                # plates = detector.detect(processed_frame)
                # 2. OCR ...
                
            else:
                # Simular captura para que el pipeline siga vivo (útil en tu entorno actual)
                pass
            
            # Mantener ~30 FPS
            elapsed = time.time() - loop_start
            sleep_time = frame_delay - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)
                
    except KeyboardInterrupt:
        print("Pipeline detenido.")
    finally:
        if cap.isOpened():
            cap.release()

if __name__ == "__main__":
    main()
