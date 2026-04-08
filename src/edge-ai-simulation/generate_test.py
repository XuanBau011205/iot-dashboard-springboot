import pandas as pd
import numpy as np
import random

print("Đang xưởng đúc Dữ liệu Thử thách (Stress-Test Data)...")

# Khởi tạo mảng chứa dữ liệu
data = []
num_samples = 5000

for _ in range(num_samples):
    scenario = random.random()
    
    # Kịch bản 1: Bình thường (60% dữ liệu)
    if scenario < 0.6:
        temp = round(random.uniform(25.0, 38.0), 1)
        hum = round(random.uniform(50.0, 80.0), 1)
        gas = random.randint(300, 800)
        label = 0
        
    # Kịch bản 2: Cháy thật (20% dữ liệu) - Nhiệt cao, Ẩm thấp, Gas vọt
    elif scenario < 0.8:
        temp = round(random.uniform(60.0, 100.0), 1)
        hum = round(random.uniform(10.0, 30.0), 1)
        gas = random.randint(2500, 4095)
        label = 1
        
    # Kịch bản 3: Nhiễu khốn nạn 1 - Đun nấu (10%) - Nhiệt cao nhưng Gas bình thường
    elif scenario < 0.9:
        temp = round(random.uniform(55.0, 80.0), 1)
        hum = round(random.uniform(40.0, 60.0), 1)
        gas = random.randint(400, 900)
        label = 0 # Không phải cháy nhà
        
    # Kịch bản 4: Nhiễu khốn nạn 2 - Rò rỉ khí gas nhưng chưa cháy (10%)
    else:
        temp = round(random.uniform(20.0, 35.0), 1)
        hum = round(random.uniform(50.0, 70.0), 1)
        gas = random.randint(3000, 4000)
        label = 0 # Nguy hiểm, nhưng chưa phải hỏa hoạn (AI báo cháy là sai)

    data.append([temp, hum, gas, label])

# Lưu ra file CSV (Ép không có Header để khớp với simulator cũ)
df = pd.DataFrame(data)
df.to_csv("random_test_data.csv", index=False, header=False)

print(f"Đã tạo thành công {num_samples} dòng dữ liệu hỗn loạn tại file 'random_test_data.csv'")
print("Lên đạn đi ông giáo!")