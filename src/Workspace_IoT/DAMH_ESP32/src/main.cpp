#include <Arduino.h>
#include <WiFi.h>
#define MQTT_MAX_PACKET_SIZE 512
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <DHT.h>

// --- THƯ VIỆN AI ---
#include <model_data.h>
#include <TensorFlowLite_ESP32.h>
#include "tensorflow/lite/micro/all_ops_resolver.h"
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/schema/schema_generated.h"

// ================ CẤU HÌNH TFLITE =================
const int kTensorArenaSize = 4096; // Tăng lên 4KB cho an toàn, tránh tràn RAM
uint8_t tensor_arena[kTensorArenaSize];
tflite::MicroInterpreter* interpreter;
TfLiteTensor* input;
TfLiteTensor* output;
float is_fire_prob = 0.0; // Biến lưu xác suất cháy

// ================ CẤU HÌNH MẠNG & MQTT =================
const char* ssid = "Wokwi-GUEST";
const char* password = "";
const char* mqtt_server = "broker.hivemq.com";
const int mqtt_port = 1883;
const char* mqtt_topic = "DAMH_I_2025.2";

WiFiClient espClient;
PubSubClient client(espClient);

// ================= CẢM BIẾN =================
#define DHTPIN 4
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);
#define MQ2_PIN 34
#define BUZZER_PIN 18

// ================= FSM =================
enum SystemState {
  STATE_WAKEUP_SENSE,
  STATE_EVALUATE,
  STATE_LOCAL_ALARM,
  STATE_NETWORK_TX,
  STATE_DEEP_SLEEP
};
SystemState currentState = STATE_WAKEUP_SENSE;

// ================= BIẾN HỆ THỐNG =================
float temp = 0.0, humi = 0.0;
int gas_filtered = 0;
int gas_raw = 0;
bool is_alarming = false;
unsigned long lastDHTRead = 0;
const unsigned long DHT_READ_INTERVAL = 2000;

// ================= HÀM MẠNG =================
void setup_wifi() {
  Serial.print("Đang kết nối Wi-Fi: ");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWi-Fi OK!");
}

void reconnect_mqtt() {
  while (!client.connected()) {
    Serial.print("Đang kết nối MQTT...");
    String clientId = "ESP32_" + String(random(0xffff), HEX);
    if (client.connect(clientId.c_str())) {
      Serial.println(" OK");
    } else {
      delay(2000);
    }
  }
}

// ================= SETUP CHÍNH =================
void setup() {
  Serial.begin(115200);
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);
  dht.begin();
  client.setServer(mqtt_server, mqtt_port);
  analogReadResolution(12);
  analogSetAttenuation(ADC_11db);

  setup_wifi();

  // --- KHỞI TẠO BỘ NÃO AI ---
  Serial.println("Đang thức tỉnh AI...");
  const tflite::Model* model = tflite::GetModel(model_tflite);
  static tflite::AllOpsResolver resolver;
  static tflite::MicroInterpreter static_interpreter(
      model, resolver, tensor_arena, kTensorArenaSize, nullptr);
  interpreter = &static_interpreter;
  interpreter->AllocateTensors();
  input = interpreter->input(0);
  output = interpreter->output(0);
  Serial.println("AI Khai nhãn thành công!");

  lastDHTRead = millis();
}

// ================= VÒNG LẶP CHÍNH =================
void loop() {
  switch (currentState) {
    case STATE_WAKEUP_SENSE: {
      Serial.println("\n[STATE] SENSE");
      
      // Đọc DHT
      if (millis() - lastDHTRead >= DHT_READ_INTERVAL) {
        float newTemp = dht.readTemperature();
        float newHumi = dht.readHumidity();
        if (!isnan(newTemp)) temp = newTemp;
        if (!isnan(newHumi)) humi = newHumi;
        lastDHTRead = millis();
      }

      // Đọc MQ2
      long sum = 0;
      for (int i = 0; i < 10; i++) {
        sum += analogRead(MQ2_PIN);
        delay(20);
      }
      gas_filtered = sum / 10;
      
      currentState = STATE_EVALUATE;
      break;
    }

    case STATE_EVALUATE: {
      Serial.println("[STATE] EVALUATE (AI SUY NGHĨ)");

      // Nhồi dữ liệu THỰC TẾ vào mô hình
      input->data.f[0] = temp;
      input->data.f[1] = humi;
      input->data.f[2] = gas_filtered;

      // Kích hoạt suy luận
      interpreter->Invoke();

      // Đọc kết quả
      is_fire_prob = output->data.f[0];
      Serial.printf("=> Xác suất cháy từ AI: %.2f%%\n", is_fire_prob * 100);

      // Thay vì dùng GAS_THRESHOLD cứng nhắc, ta tin tưởng AI (ví dụ: > 80% là cháy)
      if (is_fire_prob > 0.8) {
        is_alarming = true;
        currentState = STATE_LOCAL_ALARM;
      } else {
        if (is_alarming) {
          digitalWrite(BUZZER_PIN, LOW); // Tắt còi nếu hết cháy
          is_alarming = false;
        }
        currentState = STATE_NETWORK_TX;
      }
      break;
    }

    case STATE_LOCAL_ALARM: {
      Serial.println("[STATE] ALARM");
      digitalWrite(BUZZER_PIN, HIGH); // Rú còi
      currentState = STATE_NETWORK_TX;
      break;
    }

    case STATE_NETWORK_TX: {
      Serial.println("[STATE] MQTT");
      if (WiFi.status() != WL_CONNECTED) setup_wifi();
      if (!client.connected()) reconnect_mqtt();
      client.loop();

      JsonDocument doc;
      doc["node_id"] = "HUST_ESP32_01";
      doc["status"] = is_alarming ? "DANGER" : "NORMAL";

      JsonObject data = doc["data"].to<JsonObject>();
      data["temp"] = (double)temp; 
      data["humi"] = (double)humi; 
      data["gas_filtered"] = gas_filtered;
      data["ai_prob"] = (double)is_fire_prob; // Gửi cả nhận định của AI lên web

      char chuoi_json[384];
      serializeJson(doc, chuoi_json);
      
      if (client.publish(mqtt_topic, chuoi_json)) {
        Serial.println("MQTT publish OK");
      }
      
      currentState = STATE_DEEP_SLEEP;
      break;
    }

    case STATE_DEEP_SLEEP: {
      Serial.println("[STATE] SLEEP\n");
      // delay(2000); 
      currentState = STATE_WAKEUP_SENSE;
      break;
    }
  }
  unsigned long start_time = millis();
interpreter->Invoke();
unsigned long end_time = millis();
Serial.printf("AI 'nghĩ' mất: %lu ms\n", end_time - start_time);
}