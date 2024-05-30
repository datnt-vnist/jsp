# Dự án Lập lịch Sản xuất

## Tổng quan:
Dự án này nhằm tối ưu hóa việc lập lịch sản xuất bằng hai phương pháp khác nhau: Particle Swarm Optimization (PSO) và Google OR-Tools. Nó bao gồm hai thư mục, mỗi thư mục chứa các triển khai của phương pháp tương ứng.

## Cấu trúc Thư mục:
1. **Thư mục MRFJSP**:
   - Chứa triển khai của việc lập lịch sản xuất bằng Particle Swarm Optimization.
   - Các tệp:
     - `data`: Chứa dữ liệu thử nghiệm và code sinh dữ liệu.
     - `results/`: Thư mục để lưu trữ kết quả của quá trình lập lịch.

2. **Thư mục OR-Tools**:
   - Chứa triển khai của việc lập lịch sản xuất bằng Google OR-Tools.
   - Các tệp:
     - `data.py`: Chứa dữ liệu thử nghiệm và code sinh dữ liệu.
     - `results/`: Thư mục để lưu trữ kết quả của quá trình lập lịch.

## Sử dụng:
### Phương pháp PSO:
1. Di chuyển đến thư mục MRFJSP.
2. Chạy tệp kịch bản `DPSO.py`.
4. Kịch bản sẽ đọc các tệp dữ liệu đầu vào từ thư mục `data/`, thực hiện lập lịch bằng thuật toán PSO và lưu kết quả trong thư mục `results/`.

### Phương pháp OR-Tools:
1. Di chuyển đến thư mục OR-Tools.
2. Chạy tệp kịch bản `OR.py`.
4. Kịch bản sẽ đọc các tệp dữ liệu đầu vào từ thư mục `data/`, thực hiện lập lịch bằng OR-Tools và lưu kết quả trong thư mục `results/`.

## Dữ liệu Đầu vào:
Cả hai phương pháp đều mong đợi các tệp dữ liệu đầu vào trong thư mục `data/`. Các tệp này chứa thông tin về các nhiệm vụ sản xuất, tài nguyên, ràng buộc và các tham số quan trọng khác.

## Đầu ra:
Kết quả lập lịch sẽ được lưu trong thư mục `results/`. Những kết quả này sẽ bao gồm lịch sản xuất được tối ưu hóa, có thể dưới dạng biểu đồ Gantt hoặc các biểu diễn liên quan khác, tùy thuộc vào cách triển khai.

## Yêu cầu hệ thống:
- Python 3.x
- OR-Tools
- pyswarms
- numpy
- pandas
