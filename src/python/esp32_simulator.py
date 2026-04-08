import paho.mqtt.client as mqtt
import json
import time
import random

# Thiết lập kết nối (Đã đồng bộ chuẩn với Java của bạn)
BROKER = "broker.hivemq.com" 
PORT = 1883
TOPIC = "hust/yyyyyy126/sensor"

client = mqtt.Client()
client.connect(BROKER, PORT)

print("🚀 Bắt đầu khởi động lò luyện đan: nạp 10.000 mẫu dữ liệu...")

try:
    for i in range(10000):
        # 30% xác suất xảy ra cháy (Đỉnh đồi Entropy sẽ sụp đổ tại đây)
        is_fire = random.random() < 0.3 
        
        if is_fire:
            t = round(random.uniform(50.0, 85.0), 2)
            g = int(random.uniform(2000, 4500))
            status = "FIRE"
        else:
            t = round(random.uniform(25.0, 35.0), 2)
            g = int(random.uniform(100, 500))
            status = "NORMAL"
            
        h = round(random.uniform(40.0, 80.0), 2)
        
        # Đóng gói JSON ĐÚNG CHUẨN khớp với cục JsonNode đọc bên Spring Boot
        payload = {
            "node_id": "ESP_SIM_01",
            "data": {
                "temp": t,
                "humi": h,
                "gas_filtered": g
            },
            "status": status
        }
        
        # Bắn dữ liệu lên MQTT
        client.publish(TOPIC, json.dumps(payload))
        
        # Cứ mỗi 1000 mẫu in ra log 1 lần cho terminal đỡ bị ngợp
        if (i + 1) % 1000 == 0:
            print(f"✅ Đã luyện thành công {i + 1}/10000 mẫu...")
            
        # Thời gian nghỉ cực ngắn (10 mili-giây) để bắn cho lẹ
        time.sleep(0.01) 
        
    print("🎉 Hoàn tất quá trình! Check ngay file CSV bên Spring Boot nhé.")
    
except KeyboardInterrupt:
    print("\n🛑 Đã ngắt cầu dao khẩn cấp.")