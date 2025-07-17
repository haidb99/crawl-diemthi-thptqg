# CRAWL ĐIỂM THI THPT QUỐC GIA

Dự án này dùng để tự động thu thập (crawl) dữ liệu điểm thi THPT Quốc Gia các năm (2020-2024) từ website chính thức

## Yêu cầu hệ thống

- Python 3.x
- Các thư viện trong `requirements.txt`

## Cài đặt

Cài đặt các thư viện cần thiết bằng lệnh:

```bash
pip install -r requirements.txt
```

## Hướng dẫn sử dụng

Chạy script chính để bắt đầu quá trình crawl và tổng hợp dữ liệu:

```bash
python src/main.py
```

Sau khi chạy xong, dữ liệu sẽ được lưu vào các file CSV trong thư mục `data/`.

## Dữ liệu đầu ra

- Các file CSV: `diemthi_2020.csv`, `diemthi_2021.csv`, `diemthi_2022.csv`, `diemthi_2023.csv`, `diemthi_2024.csv`
- Mỗi file chứa dữ liệu điểm thi của từng năm tương ứng.

## Liên hệ

- Repo: [https://github.com/haidb99/crawl-diemthi-thptqg](https://github.com/haidb99/crawl-diemthi-thptqg)
