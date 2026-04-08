import pandas as pd
import numpy as np
import tensorflow.lite as tflite
import time

print("Khởi động Lò mô phỏng Hàng loạt...")
interpreter = tflite.Interpreter(model_path="model.tflite")
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Đọc trí nhớ môi trường
print("Đang nạp dữ liệu từ file random_test_data.csv...")
try:
# Ép Pandas hiểu là không có Header, và tự gán tên cột từ trái qua phải
 df = pd.read_csv("random_test_data.csv", header=None, names=['Temp', 'Humidity', 'Gas', 'Label'])
except FileNotFoundError:
    print("LỖI CẤP 1: Không tìm thấy file random_test_data.csv. Ông giáo kiểm tra lại đường dẫn nhé!")
    exit()

fire_alarms = 0
print(f"Bắt đầu ép cung {len(df)} dòng dữ liệu...")
start_time = time.time()

for index, row in df.iterrows():
    # CHÚ Ý: Ông giáo nhớ kiểm tra lại tên cột (Temp, Humidity, Gas) cho khớp với file CSV của mình!
    # Nếu tên cột trong CSV là tiếng Việt (NhietDo, DoAm...), hãy sửa lại ở đây.
    input_data = np.array([[row['Temp'], row['Humidity'], row['Gas']]], dtype=np.float32)
    
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    
    prediction = interpreter.get_tensor(output_details[0]['index'])[0][0]
    
    # Nếu xác suất > 50% thì coi như AI cảnh báo
    if prediction > 0.5:
        fire_alarms += 1

end_time = time.time()
print("="*40)
print(f"Hoàn tất chớp nhoáng trong {end_time - start_time:.4f} giây!")
print(f"Tổng số phát hiện bất thường: {fire_alarms} / {len(df)}")
print("="*40)
# ... (Phần trên giữ nguyên)
fire_alarms = 0
correct_predictions = 0   # Đoán đúng
false_positives = 0       # Báo cháy giả (Không cháy mà hú còi)
false_negatives = 0       # Bỏ lọt tội phạm (Cháy thật mà im lặng - CỰC KỲ NGUY HIỂM)

print(f"Bắt đầu ép cung {len(df)} dòng dữ liệu...")
# ...
for index, row in df.iterrows():
    input_data = np.array([[row['Temp'], row['Humidity'], row['Gas']]], dtype=np.float32)
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    
    prediction = interpreter.get_tensor(output_details[0]['index'])[0][0]
    predicted_label = 1 if prediction > 0.5 else 0
    actual_label = int(row['Label']) # Lấy nhãn thực tế từ file CSV
    
    if predicted_label == 1:
        fire_alarms += 1
        
    # So sánh với thực tế
    if predicted_label == actual_label:
        correct_predictions += 1
    elif predicted_label == 1 and actual_label == 0:
        false_positives += 1
    elif predicted_label == 0 and actual_label == 1:
        false_negatives += 1

# ... In kết quả
print(f"Độ chính xác tổng thể (Accuracy): {(correct_predictions/len(df))*100:.2f}%")
print(f"Số lần báo động giả (False Positives): {false_positives}")
print(f"Số lần BỎ LỌT ĐÁM CHÁY (False Negatives): {false_negatives}")