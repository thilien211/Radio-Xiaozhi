
## 🚀 Cách cài Radio-Xiaozhi
### ⭐ Có một số kênh radio không phát được mà em lười kiểm tra nên các bác bỏ qua hộ em nhé! 🥰

# Các bác nên thêm dòng sau vào role của xiaozhi:
```bash
Khi người dùng yêu cầu mở các kênh radio như vov thì sẽ mở dưới dạng bài hát và tên bài hát như tên radio.
```

Git Clone repo trước:
```bash
git clone https://github.com/thilien211/Radio-Xiaozhi.git
```
Thực hiện vào thư mục và tạo venv:
```bash
cd Radio-Xiaozhi
python3 -m venv .radio
```
Vào môi trường venv:
```bash
source .radio/bin/activate
```
Thực hiện cài requirements:
```bash
pip install flask requests
```
Chạy server:
```bash
python radio.py
```
Test server:
```bash
curl http://localhost:5005/stream_pcm?song=VOV1
