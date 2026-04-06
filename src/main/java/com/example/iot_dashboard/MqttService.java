package com.example.iot_dashboard;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.eclipse.paho.client.mqttv3.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Service;

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
            System.out.println("✅ Đã nối MQTT và sẵn sàng lưu DB!");
        } catch (MqttException e) {
            System.err.println("❌ Lỗi MQTT: " + e.getMessage());
        }
    }

    @Override
    public void messageArrived(String topic, MqttMessage message) throws Exception {
        String payload = new String(message.getPayload());
        System.out.println("📩 Nhận data: " + payload);

        try {
            // 1. Giải mã JSON
            ObjectMapper mapper = new ObjectMapper();
            JsonNode root = mapper.readTree(payload);
            
            // 2. Lưu vào H2 Database (Lấy đúng các key: node_id, status, temp, humi, gas_filtered)
            SensorData data = new SensorData(
                root.path("node_id").asText(),
                root.path("data").path("temp").asDouble(),
                root.path("data").path("humi").asDouble(),
                root.path("data").path("gas_filtered").asInt(),
                root.path("status").asText()
            );
            sensorRepository.save(data);
            System.out.println("💾 Đã lưu lịch sử vào Database!");

            // 3. Bắn ra Web Dashboard
            if (messagingTemplate != null) {
                messagingTemplate.convertAndSend("/topic/sensor", payload);
            }
        } catch (Exception e) {
            System.err.println("❌ Lỗi xử lý JSON/DB: " + e.getMessage());
        }
    }

    @Override public void connectionLost(Throwable cause) {}
    @Override public void deliveryComplete(IMqttDeliveryToken token) {}
}