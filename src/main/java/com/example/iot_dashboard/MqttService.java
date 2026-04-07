package com.example.iot_dashboard;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.eclipse.paho.client.mqttv3.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Service;

import java.io.FileWriter;

@Service
public class MqttService implements MqttCallback {

    @Autowired
    private SimpMessagingTemplate messagingTemplate;

    @Autowired
    private SensorRepository sensorRepository;

    private final String BROKER_URL = "tcp://broker.hivemq.com:1883";
    private final String CLIENT_ID = "spring-boot-web-" + System.currentTimeMillis();
    private final String TOPIC = "hust/yyyyyy126/sensor";

    public MqttService() {
        try {
            MqttClient client = new MqttClient(BROKER_URL, CLIENT_ID);
            MqttConnectOptions options = new MqttConnectOptions();
            options.setCleanSession(true);
            options.setAutomaticReconnect(true);
            client.connect(options);
            client.setCallback(this);
            client.subscribe(TOPIC);
            System.out.println("✅ Đã nối MQTT và sẵn sàng lưu DB + CSV!");
        } catch (MqttException e) {
            System.err.println("❌ Lỗi MQTT: " + e.getMessage());
        }
    }

    @Override
    public void messageArrived(String topic, MqttMessage message) throws Exception {
        String payload = new String(message.getPayload());
        System.out.println("📩 Nhận data: " + payload);

        try {
            // 1. Giải mã JSON (Giữ nguyên cấu trúc xịn của bạn)
            ObjectMapper mapper = new ObjectMapper();
            JsonNode root = mapper.readTree(payload);
            
            // Tách các biến ra để dùng chung cho cả DB và CSV
            String nodeId = root.path("node_id").asText();
            double temp = root.path("data").path("temp").asDouble();
            double humi = root.path("data").path("humi").asDouble();
            int gas = root.path("data").path("gas_filtered").asInt();
            String status = root.path("status").asText();

            // 2. Lưu vào H2 Database
            SensorData data = new SensorData(nodeId, temp, humi, gas, status);
            sensorRepository.save(data);
            System.out.println("💾 Đã lưu lịch sử vào Database!");

            // 3. Tính toán nhãn AI và lưu ra file CSV (Mới)
            // Giả định: Nhiệt độ > 50 và Gas > 2000 là có biến (1), còn lại an toàn (0)
            int label = (temp > 50 && gas > 2000) ? 1 : 0;
            try (FileWriter fw = new FileWriter("training_data.csv", true)) {
                fw.write(temp + "," + humi + "," + gas + "," + label + "\n");
            }
            System.out.println("📝 Đã ghi thêm 1 dòng vào file training_data.csv");

            // 4. Bắn ra Web Dashboard
            if (messagingTemplate != null) {
                messagingTemplate.convertAndSend("/topic/sensor", payload);
            }
        } catch (Exception e) {
            System.err.println("❌ Lỗi xử lý JSON/DB/CSV: " + e.getMessage());
        }
    }

    @Override public void connectionLost(Throwable cause) {
        System.out.println("⚠️ Mất kết nối MQTT!");
    }
    
    @Override public void deliveryComplete(IMqttDeliveryToken token) {}
}