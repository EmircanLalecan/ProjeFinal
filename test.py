import cv2
import serial
import time
from ultralytics import YOLO

# --- Arduino Seri İletişim Ayarları ---
SERI_PORT = 'COM5'  # Arduino'nuzun bağlı olduğu port (Windows için COM_X, Linux/Mac için /dev/ttyUSB_X veya /dev/ttyACM_X)
BAUD_HIZI = 9600
ser = None

def seri_kurulumu():
    global ser
    try:
        ser = serial.Serial(SERI_PORT, BAUD_HIZI, timeout=1)
        time.sleep(2)  # Arduino'nun resetlenmesi ve bağlantının kurulması için bekleme
        print(f"Arduino'ya {SERI_PORT} üzerinden {BAUD_HIZI} baud hızıyla bağlanıldı.")
        return True
    except serial.SerialException as e:
        print(f"Hata: Seri port {SERI_PORT} açılamadı: {e}")
        return False

def arduinoya_gonder(komut):
    if ser and ser.is_open:
        try:
            mesaj = komut + '\n' # Komut sonuna yeni satır karakteri ekle
            ser.write(mesaj.encode('utf-8'))
            # print(f"Arduino'ya gönderildi: {komut}") # Hata ayıklama için açılabilir
        except Exception as e:
            print(f"Veri gönderirken hata: {e}")
    else:
        print("Seri port açık değil. Veri gönderilemiyor.")

# --- YOLO Ayarları ---
# ÖNEMLİ: 'custom_model.pt' yerine kendi eğitilmiş model dosyanızın adını yazın.
# Eğer genel bir modelle test ediyorsanız (örn: 'yolov8n.pt'),
# 'CORN_LABEL' ve 'CANNABIS_LABEL' değişkenlerini o modelin tanıdığı sınıflarla değiştirin.
MODEL_YOLU = 'yolov11_custom.pt' # <-- KENDİ MODELİNİZİN YOLUNU GİRİN veya test için 'yolov8n.pt'
CORN_LABEL = 'corn'     # <-- Modelinizde mısır için kullanılan etiket (Örnek: 'corn'). 'yolov8n.pt' için 'person'
CANNABIS_LABEL = 'cannabis' # <-- Modelinizde kenevir için kullanılan etiket (Örnek: 'cannabis'). 'yolov8n.pt' için 'car'
GUVEN_ESIGI = 0.5       # Minimum güven skoru

try:
    model = YOLO(MODEL_YOLU)
    print(f"'{MODEL_YOLU}' modeli yüklendi.")
    print(f"Modelin tanıdığı sınıflar: {model.names}") # Modelin tüm sınıflarını görmek için
except Exception as e:
    print(f"Hata: YOLO modeli yüklenemedi: {e}")
    exit()


# --- Ana Program ---
if __name__ == "__main__":
    if not seri_kurulumu():
        print("Seri bağlantı kurulamadığı için program sonlandırılıyor.")
        exit()

    # Kamera veya video dosyası
    cap = cv2.VideoCapture(0) # 0: Varsayılan kamera
    # cap = cv2.VideoCapture("test_video.mp4") # Örnek bir video dosyası, kendi videonuzla değiştirin

    if not cap.isOpened():
        print("Hata: Kamera veya video dosyası açılamadı.")
        ser.close()
        exit()

    print("Tespit başlatılıyor...")
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Video bitti veya kare okunamadı.")
                break

            # YOLO ile tespit yap
            results = model(frame, verbose=False) # verbose=False daha az konsol çıktısı verir

            corn_detected_this_frame = False
            cannabis_detected_this_frame = False

            # Tespit sonuçlarını işle
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    cls_id = int(box.cls[0])
                    label = model.names[cls_id]
                    confidence = float(box.conf[0])

                    if confidence > GUVEN_ESIGI:
                        if label.lower() == CORN_LABEL.lower(): # Etiketleri küçük harfe çevirerek karşılaştır
                            corn_detected_this_frame = True
                            # Tespit edilen nesneyi çerçevele (isteğe bağlı)
                            x1, y1, x2, y2 = map(int, box.xyxy[0])
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                            cv2.putText(frame, f"{label} {confidence:.2f}", (x1, y1 - 10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                        elif label.lower() == CANNABIS_LABEL.lower():
                            cannabis_detected_this_frame = True
                            # Tespit edilen nesneyi çerçevele (isteğe bağlı)
                            x1, y1, x2, y2 = map(int, box.xyxy[0])
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                            cv2.putText(frame, f"{label} {confidence:.2f}", (x1, y1 - 10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            # Arduino'ya komut gönder
            if cannabis_detected_this_frame: # Mısır öncelikli, eğer mısır varsa kenevir komutu gitmez
                arduinoya_gonder("CANNABIS_DETECTED")
                print(f"KOMUT: CANNABIS_DETECTED ({CANNABIS_LABEL})")
            elif corn_detected_this_frame:
                arduinoya_gonder("CORN_DETECTED")
                print(f"KOMUT: CORN_DETECTED ({CORN_LABEL})")
            
            else:
                # Eğer belirli bir süre boyunca hiçbir şey tespit edilmezse CLEAR gönderilebilir
                # Veya her karede hiçbir şey bulunamazsa gönderilir:
                arduinoya_gonder("CLEAR")
                # print("KOMUT: CLEAR") # Çok fazla çıktı üretebilir, dikkatli kullanın

            # Görüntüyü göster (isteğe bağlı)
            cv2.imshow("YOLOv8 Tespit", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Kullanıcı tarafından çıkış yapıldı.")
                break

            # Seri portu aşırı yüklememek için küçük bir gecikme
            # time.sleep(0.05) # Gerekirse bu satırı açın

    except KeyboardInterrupt:
        print("Program kullanıcı tarafından sonlandırıldı (Ctrl+C).")
    finally:
        if ser and ser.is_open:
            arduinoya_gonder("STOP_ALL") # Arduino'ya programın bittiğini bildir
            time.sleep(0.1) # Son komutun gitmesi için kısa bir bekleme
            ser.close()
            print("Seri port kapatıldı.")
        cap.release()
        cv2.destroyAllWindows()
        print("Kaynaklar serbest bırakıldı.")