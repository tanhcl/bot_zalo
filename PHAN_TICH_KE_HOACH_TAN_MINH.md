# Phân tích và kế hoạch phát triển Bot Zalo – Shop Tân Minh

**Phiên bản tài liệu:** 1.0  
**Mục tiêu:** chuyển bot hiện tại thành kênh bán hàng, chăm sóc khách hàng và marketing cho **Shop Tân Minh**.

## 1. Tóm tắt định hướng

Dự án hiện là một bot Flask nhận webhook từ Zalo, trả lời câu hỏi cơ bản, cung cấp link sản phẩm/mã giảm giá và cho phép quản trị viên phát thông báo tới người dùng đã từng nhắn bot. Nền tảng này phù hợp để làm MVP bán hàng qua Zalo vì đã có luồng thu thập người dùng, quản lý link sản phẩm và broadcast.

Định hướng cho Tân Minh:

- Biến bot thành “trợ lý bán hàng” hoạt động 24/7.
- Dẫn khách từ nội dung marketing → xem sản phẩm → nhận hướng dẫn → gửi bằng chứng đặt hàng → chăm sóc sau bán.
- Quản lý sản phẩm, mã ưu đãi, chiến dịch và khách hàng từ các lệnh admin.
- Đo lường được lượt tiếp cận, lượt nhấp, lượt hỏi mua và đơn hàng.

## 2. Hiện trạng dự án

### Công nghệ và cấu trúc

| Thành phần | Vai trò hiện tại |
|---|---|
| `app.py` | Flask server, nhận webhook `/bot`, phân loại admin/người dùng và gửi tin nhắn |
| `FAQ.py` | FAQ tĩnh, trả link sản phẩm và mã giảm giá |
| `admin.py` | Các lệnh quản trị: cập nhật/xóa/xem link, đổi mã, broadcast, xem user |
| `storage.py` | Gọi Upstash Redis REST API để lưu link, mã giảm giá, user và trạng thái tạm |
| `users.py` | Đăng ký và đọc danh sách người dùng |
| `tkho.md` | Ví dụ cấu trúc payload webhook |
| `requirements.txt` | Flask và requests |

### Luồng hoạt động hiện tại

1. Zalo gửi sự kiện vào `POST /bot`.
2. Bot kiểm tra secret token, ghi log và lấy `chat_id`, `user_id`, nội dung tin nhắn.
3. Người dùng được thêm vào danh sách lưu trữ.
4. Admin được nhận diện bằng `ADMIN_ID`.
5. Người dùng thường có thể dùng `tt1`, `sos`, `hi`; nội dung khác nhận câu trả lời mặc định.
6. Admin cập nhật link, mã giảm giá hoặc broadcast cho toàn bộ user.

### Chức năng đã có

- Trả lời FAQ cơ bản.
- Hiển thị danh sách link sản phẩm động.
- Hiển thị mã giảm giá.
- Hướng dẫn đặt hàng qua từ khóa `sos`.
- Broadcast sự kiện bằng `/sukien`.
- Quản lý link bằng `/setlink`, `/xemlink`, `/xoalink`.
- Quản lý mã bằng `/mabuff`.
- Đếm người dùng bằng `/xemuser`.
- Lưu dữ liệu qua Redis để không mất khi Render khởi động lại.

## 3. Đánh giá theo mục tiêu kinh doanh

### Điểm mạnh

- Kiến trúc nhỏ, dễ tiếp tục phát triển.
- Có sẵn luồng bán hàng cơ bản và kênh broadcast.
- Lưu trữ bên ngoài giúp dữ liệu không phụ thuộc vào filesystem của server.
- Có thể triển khai nhanh trên Render hoặc dịch vụ tương tự.
- Từ khóa đơn giản, phù hợp với khách hàng không quen bot.

### Hạn chế hiện tại

- Chỉ quản lý link theo vị trí; chưa có tên, giá, tồn kho, ảnh, mô tả hoặc trạng thái sản phẩm.
- FAQ đang viết cứng trong mã nguồn, khó thay đổi bởi người bán.
- Broadcast chưa có phân nhóm khách, lịch gửi, giới hạn tốc độ hoặc chống gửi trùng.
- Chưa có đơn hàng, trạng thái đơn, thanh toán và quy trình hậu mãi.
- Chưa có thống kê lượt xem, lượt nhấp, tỷ lệ chuyển đổi và doanh thu.
- Lưu toàn bộ user trong một mảng Redis; khi số lượng lớn sẽ khó mở rộng và khó tra cứu.
- Xử lý lỗi mạng/API còn hạn chế; chưa có timeout, retry có kiểm soát và hàng đợi gửi tin.
- Log có thể chứa dữ liệu người dùng và đang ghi trực tiếp ra file.
- Chưa có kiểm thử tự động, tài liệu triển khai hoặc cấu hình môi trường mẫu.

## 4. Rủi ro bảo mật cần xử lý ngay

Trong `storage.py` hiện có giá trị mặc định giống thông tin truy cập Upstash. Vì repository là công khai, cần coi các thông tin này đã bị lộ.

Thứ tự xử lý bắt buộc:

1. Thu hồi và tạo lại `UPSTASH_TOKEN` trên Upstash.
2. Kiểm tra lịch sử Git/repository và xóa secret khỏi mã nguồn, không chỉ sửa ở commit mới.
3. Chỉ đọc `UPSTASH_URL`, `UPSTASH_TOKEN`, `BOT_TOKEN`, `ADMIN_ID`, `SECRET_TOKEN` từ biến môi trường.
4. Đổi `SECRET_TOKEN` hiện tại; không dùng chuỗi cố định trong `app.py`.
5. Không in `BOT_TOKEN` ra log.
6. Thêm timeout cho mọi request và không ghi token, thông tin nhạy cảm vào `log.txt`.
7. Kiểm tra quyền admin bằng ID kiểu dữ liệu thống nhất, tránh lỗi so sánh chuỗi/số.
8. Thiết lập giới hạn quyền, backup và cảnh báo truy cập bất thường trên kho dữ liệu.

Đây là điều kiện trước khi chạy quảng cáo hoặc đưa bot cho nhiều khách hàng.

## 5. Mô hình kinh doanh đề xuất cho Tân Minh

### Định vị

**Tân Minh – sản phẩm chọn lọc, tư vấn nhanh, hỗ trợ rõ ràng qua Zalo.**

Nên bắt đầu bằng một nhóm sản phẩm hẹp, dễ giải thích và có biên lợi nhuận rõ ràng. Mỗi sản phẩm cần có:

- Mã sản phẩm và tên dễ nhớ.
- Ảnh/video thật.
- Giá niêm yết, giá khuyến mãi và điều kiện áp dụng.
- Tình trạng còn hàng.
- Link mua hoặc cách đặt hàng.
- Chính sách giao hàng, đổi trả và hỗ trợ.

### Phễu bán hàng

```text
Nội dung marketing
        ↓
Khách nhắn Zalo / quét QR
        ↓
Bot giới thiệu sản phẩm phù hợp
        ↓
Khách xem link, giá, ưu đãi
        ↓
Khách đặt hàng hoặc gửi nhu cầu
        ↓
Tân Minh xác nhận và hỗ trợ
        ↓
Chăm sóc sau bán + xin đánh giá + mua lại
```

## 6. Kế hoạch phát triển theo giai đoạn

### Giai đoạn 0 – An toàn và ổn định (1–3 ngày)

- Thu hồi toàn bộ secret đã lộ.
- Tách cấu hình sang biến môi trường và tạo `.env.example`.
- Thêm `timeout`, xử lý lỗi HTTP/API và log có cấu trúc.
- Xác minh webhook, secret và quyền admin.
- Viết README triển khai, quy trình backup và hướng dẫn khôi phục.
- Tạo bộ test tối thiểu cho FAQ, quyền admin và lưu dữ liệu.

**Kết quả cần đạt:** bot chạy ổn định, không còn credential trong source và có thể triển khai lại từ đầu.

### Giai đoạn 1 – MVP bán hàng Tân Minh (1–2 tuần)

- Thay danh sách link bằng danh mục sản phẩm có mã, tên, giá, mô tả, ảnh và link.
- Thêm menu/từ khóa: `sanpham`, `gia`, `uudai`, `dat hang`, `hotro`, `chinhsach`.
- Chuẩn hóa nội dung `sos` theo đúng quy trình đặt hàng của Tân Minh.
- Thêm nút hoặc cú pháp chọn sản phẩm, không bắt khách nhớ số index.
- Thêm thông tin liên hệ, giờ hỗ trợ và khu vực giao hàng.
- Cho admin tạo/sửa/ẩn sản phẩm mà không cần sửa mã nguồn.

**Kết quả cần đạt:** khách mới có thể tự xem sản phẩm và biết bước tiếp theo trong dưới 2 phút.

### Giai đoạn 2 – Quản lý khách và đơn hàng (2–4 tuần)

- Lưu hồ sơ khách: tên, Zalo ID, sản phẩm quan tâm, nguồn chiến dịch, lần tương tác cuối.
- Tạo đơn hàng với trạng thái: `mới`, `đã xác nhận`, `đang giao`, `hoàn tất`, `hủy`.
- Cho khách gửi số điện thoại/địa chỉ theo quy trình có xác nhận.
- Gửi thông báo trạng thái đơn và nhắc hoàn tất đặt hàng.
- Thêm phân nhóm: khách mới, đã mua, khách quan tâm sản phẩm A, khách không hoạt động.
- Ghi nhận consent/đồng ý nhận thông tin marketing và hỗ trợ lệnh dừng nhận tin.

### Giai đoạn 3 – Marketing có đo lường (1–2 tháng)

- Tạo chiến dịch có mã riêng, ví dụ `TM-THANG10`, `TM-KHACHMOI`.
- Tạo link tracking theo sản phẩm và chiến dịch.
- Đo lượt gửi, lượt phản hồi, lượt nhấp, số đơn và doanh thu.
- Lập lịch gửi nội dung, giới hạn tần suất và chống broadcast trùng.
- A/B test tiêu đề, ưu đãi và nội dung kêu gọi hành động.
- Tự động nhắc lại khách đã xem nhưng chưa mua, với tần suất hợp lý.

### Giai đoạn 4 – Mở rộng (sau khi MVP có đơn ổn định)

- Dashboard doanh thu, sản phẩm bán chạy, khách quay lại và hiệu quả chiến dịch.
- Tích hợp Google Sheets/CRM hoặc hệ thống quản lý đơn hàng.
- Tích hợp thanh toán và đối soát nếu quy mô phù hợp.
- Hỗ trợ nhiều admin với phân quyền.
- Chuyển gửi tin sang queue/background worker khi số user tăng.
- Bổ sung tìm kiếm ngôn ngữ tự nhiên hoặc AI sau khi dữ liệu FAQ và sản phẩm đủ tốt.

## 7. Bộ lệnh đề xuất

### Cho khách hàng

| Lệnh/từ khóa | Mục đích |
|---|---|
| `menu` | Hiển thị các lựa chọn chính |
| `sanpham` | Xem danh mục sản phẩm |
| `sp TM01` | Xem chi tiết sản phẩm |
| `uudai` | Xem mã giảm giá hiện hành |
| `dat hang` | Bắt đầu quy trình đặt hàng |
| `don hang` | Tra cứu đơn |
| `hotro` | Gặp người hỗ trợ |
| `dung nhan tin` | Từ chối marketing |

### Cho admin

Giữ các lệnh hiện có nhưng nên nâng cấp thành:

- `/themsp`, `/suasp`, `/an sp`, `/danhsachsp`.
- `/taochiendich`, `/gui <ma_chien_dich>`.
- `/taodon`, `/capnhatdon`, `/xemdon`.
- `/phannhom`, `/xemnhom`.
- `/baocao ngay`, `/baocao thang`.
- `/help_admin` hiển thị cú pháp mới và ví dụ thực tế.

## 8. Chiến lược marketing cho Shop Tân Minh

### Nội dung hàng tuần

- 2–3 bài giới thiệu lợi ích và cách dùng sản phẩm.
- 1–2 video ngắn/feedback thực tế.
- 1 chương trình ưu đãi có thời hạn rõ ràng.
- 1 nội dung giải đáp câu hỏi thường gặp.
- 1 nội dung chăm sóc khách đã mua.

### Kênh kéo khách vào Zalo

- QR code đặt ở bio, bài đăng, bao bì và hóa đơn.
- CTA thống nhất: “Nhắn `SANPHAM` để nhận danh mục Tân Minh”.
- Mỗi kênh dùng một mã chiến dịch riêng để biết khách đến từ đâu.
- Tặng mã giảm giá cho khách mới, nhưng giới hạn thời hạn và điều kiện.
- Khuyến khích khách cũ giới thiệu bạn bè bằng mã giới thiệu.

### Mẫu tin nhắn marketing

```text
🌟 TÂN MINH – ƯU ĐÃI HÔM NAY

Sản phẩm: [Tên sản phẩm]
Điểm nổi bật: [1 lợi ích chính]
Giá ưu đãi: [Giá] đến [Thời hạn]

Nhắn “SP [MÃ]” để xem chi tiết.
Nhắn “DUNG NHAN TIN” nếu bạn không muốn nhận thông báo.
```

Không nên gửi quá dày, dùng nội dung gây hiểu nhầm hoặc quảng cáo khi khách chưa đồng ý. Mỗi chiến dịch cần có thời hạn, điều kiện và thông tin hỗ trợ minh bạch.

## 9. Kiến trúc kỹ thuật mục tiêu

Nên tách rõ các lớp sau:

```text
Webhook/API
   ├── Xác thực và chuẩn hóa sự kiện
   ├── Router lệnh người dùng/admin
   ├── Service sản phẩm, khách hàng, đơn hàng, chiến dịch
   ├── Repository/Storage (Redis hoặc database)
   └── Message service + retry/queue
```

Đề xuất dữ liệu tối thiểu:

- `products`: mã, tên, mô tả, giá, ảnh, link, tồn kho, trạng thái.
- `customers`: chat ID, tên, nguồn, nhóm, consent marketing, thời gian tương tác.
- `orders`: mã đơn, khách, sản phẩm, tổng tiền, trạng thái, ghi chú.
- `campaigns`: mã chiến dịch, nội dung, nhóm nhận, thời gian, kết quả.
- `events`: loại sự kiện, user, sản phẩm/chiến dịch, thời gian.

Khi dữ liệu vượt quy mô nhỏ, nên dùng cấu trúc key riêng hoặc database có truy vấn thay vì lưu toàn bộ user trong một JSON array.

## 10. Chỉ số cần theo dõi

- Số người dùng mới mỗi ngày/tuần.
- Tỷ lệ người nhắn sau khi thấy nội dung.
- Tỷ lệ xem sản phẩm → hỏi mua.
- Tỷ lệ hỏi mua → tạo đơn.
- Tỷ lệ đơn hoàn tất.
- Doanh thu và lợi nhuận theo sản phẩm.
- Hiệu quả từng mã giảm giá/chiến dịch.
- Tỷ lệ khách quay lại.
- Tỷ lệ hủy, hoàn và khiếu nại.
- Tỷ lệ khách từ chối nhận marketing.

## 11. Tiêu chí nghiệm thu MVP

- Webhook xác thực đúng và không lộ secret.
- Khách mới xem được menu, danh mục, chi tiết sản phẩm và ưu đãi.
- Admin cập nhật sản phẩm/mã ưu đãi mà không sửa file Python.
- Mỗi chiến dịch có mã tracking riêng.
- Có quy trình tiếp nhận yêu cầu hỗ trợ và chuyển người thật.
- Broadcast có giới hạn tốc độ, log kết quả và không gửi cho khách đã từ chối.
- Có test cho các luồng chính và hướng dẫn triển khai.
- Có backup dữ liệu và phương án khôi phục.

## 12. Việc nên làm ngay trong tuần đầu

1. Đổi toàn bộ credential đã xuất hiện trong mã nguồn.
2. Chốt 5–10 sản phẩm đầu tiên và chuẩn hóa dữ liệu sản phẩm.
3. Viết lại FAQ, hướng dẫn đặt hàng và chính sách của Tân Minh.
4. Xây menu khách hàng và danh mục sản phẩm có mã.
5. Thêm consent marketing và lệnh dừng nhận tin.
6. Tạo một chiến dịch thử nghiệm với nhóm khách nhỏ.
7. Ghi nhận số liệu nền: user mới, lượt hỏi sản phẩm, số đơn và doanh thu.
8. Sau khi kiểm tra ổn định mới mở rộng broadcast/quảng cáo.

## Kết luận

Dự án hiện đủ tốt để làm nền tảng MVP cho Shop Tân Minh, nhưng mới ở mức bot phát link và FAQ. Giá trị kinh doanh lớn nhất trong giai đoạn tiếp theo là chuyển từ “link theo index + broadcast toàn bộ” sang “danh mục sản phẩm + hồ sơ khách + chiến dịch đo lường + quy trình đơn hàng”. Ưu tiên đầu tiên là bảo mật credential, sau đó hoàn thiện trải nghiệm mua hàng và đo lường trước khi tăng ngân sách marketing.

**Nguồn tham khảo mã nguồn:** [github.com/tanhcl/bot_zalo](https://github.com/tanhcl/bot_zalo)
