package com.example.iot_dashboard;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface SensorRepository extends JpaRepository<SensorData, Long> {
    // Spring sẽ tự động hiểu các hàm như save(), findAll(), delete()...
}