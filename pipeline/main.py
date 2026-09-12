import cv2
import time
from detector import PlateDetector
from ocr import TextExtractor
from validator import validate_plate

def main():
    print("Iniciando ALPR Pipeline...")
    detector = PlateDetector()
    ocr = TextExtractor()
    
    # Simulación de captura de cámara
    # cap = cv2.VideoCapture(0) # o RTSP url
    
    try:
        while True:
            # ret, frame = cap.read()
            # if not ret: break
            
            # 1. Detección
            # plates = detector.detect(frame)
            
            # 2. OCR
            # for plate_img in plates:
            #     text = ocr.extract(plate_img)
            #     
            #     # 3. Validación
            #     if validate_plate(text):
            #         print(f"Patente detectada y válida: {text}")
            
            time.sleep(1) # Simular procesamiento continuo
    except KeyboardInterrupt:
        print("Pipeline detenido.")

if __name__ == "__main__":
    main()
