package com.example.iot_dashboard;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
public class SensorData {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String nodeId;
    private Double temperature;
    private Double humidity;
    private Integer gasFiltered;
    private String status;
    private LocalDateTime timestamp;

    // Constructors
    public SensorData() {}

    public SensorData(String nodeId, Double temperature, Double humidity, Integer gasFiltered, String status) {
        this.nodeId = nodeId;
        this.temperature = temperature;
        this.humidity = humidity;
        this.gasFiltered = gasFiltered;
        this.status = status;
        this.timestamp = LocalDateTime.now();
    }

    // Getters and Setters (Bạn có thể dùng Generate của IDE để tạo nhanh)
    public Long getId() { return id; }
    public String getNodeId() { return nodeId; }
    public Double getTemperature() { return temperature; }
    public Double getHumidity() { return humidity; }
    public Integer getGasFiltered() { return gasFiltered; }
    public String getStatus() { return status; }
    public LocalDateTime getTimestamp() { return timestamp; }
}