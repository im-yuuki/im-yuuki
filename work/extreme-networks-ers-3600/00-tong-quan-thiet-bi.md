# 00 — Tổng quan thiết bị

Dòng **ERS 3600 Series** (Extreme Networks): access switch L2/L3 IPv4, fixed 1U, nguồn AC tích hợp. Phần mềm kiểm chứng: **SW v6.4.2.007**, máy mẫu **ERS 3626GTS-PWR+**.

> Quy ước đánh dấu trong toàn bộ guide:
>
> | Cách đánh dấu | Ý nghĩa |
> | --- | --- |
> | Văn bản thường, không dấu | Đã chạy và xác nhận trên thiết bị thật |
> | *Chữ in nghiêng* kết thúc bằng **[\*]** | Chỉ có trong tài liệu hãng 6.4, **chưa chạy** trên thiết bị |
> | *Chữ in nghiêng* kết thúc bằng **[\*\*]** | Không có trong ghi chú thực tế lẫn tài liệu hãng; suy ra từ họ ERS, **phải kiểm tra bằng `?`** trước khi dùng |
>
> Với code block: dấu hiệu nằm ở **dòng tiêu đề phía trên block** (in đậm = đã kiểm chứng; in nghiêng + `[*]`/`[**]` = chưa). Nội dung bên trong block luôn là lệnh thuần để copy.
>
> | Quy ước code block | |
> | --- | --- |
> | Tiêu đề | `**Việc lệnh làm** (Mode)` — Mode: Privileged, Global, Ethernet, VLAN Interface |
> | Nội dung | Chỉ lệnh, **không prompt, không comment** — copy dán thẳng vào CLI |
> | Một block | Một việc; lệnh vào mode + lệnh con đi chung một block khi phải chạy liền |
>
> Khi tài liệu hãng và thiết bị thật khác nhau, guide này theo thiết bị thật.

## 1. So sánh 3 model đang vận hành

| Hạng mục | 3626GTS | **3626GTS-PWR+** (máy mẫu) | 3650GTS |
| --- | --- | --- | --- |
| Cổng access | 24× 10/100/1000 | 24× 10/100/1000 | 48× 10/100/1000 |
| Combo SFP | 2 (cổng 23–24) | 2 (cổng 23–24) | 2 |
| Uplink 10G SFP+ | 2 | 2 | 2 |
| Stack/Uplink 10G SFP+ (dual-use) | 2 | 2 | 2 |
| PoE | Không | 802.3af/at, 30 W/cổng, **740 W** (đọc từ `show poe-main-status`; datasheet ghi 720 W) | Không |
| Fabric / Forwarding | 128 Gbps / 95 Mpps | 128 Gbps / 95 Mpps | 188 Gbps / 130 Mpps |
| Part number | AL3600A05-E6 | AL3600A15-E6 | AL3600A06-E6 |

## 2. Giới hạn đáng nhớ (cả dòng)

| Hạng mục | Giá trị |
| --- | --- |
| Stack | tối đa 8 unit, qua 2 cổng 10G SFP+ dual-use (khi stack thì không dùng làm uplink) |
| VLAN | 256 (port-based) |
| MAC table | 16.384 |
| MLT/LACP | 6 nhóm, tối đa 4 link/nhóm |
| MSTP | 8 instance |
| DHCP snooping binding | 512 |
| ARP | 512 (256 static) |
| IP interface | 32 (một số tài liệu ghi 64 — chưa kiểm chứng) |
| IP route | 256 (32 static) |
| RIP | 16 interface / 256 route |
| Jumbo frame | 9.216 byte |
| License | Base Software |

## 3. Bản đồ cổng (26-port)

| Cổng | Loại | Ghi chú |
| --- | --- | --- |
| 1–22 | RJ45 10/100/1000 | Auto-MDIX, auto-negotiation bật |
| 23–24 | RJ45 combo SFP | Cắm SFP thì RJ45 tương ứng bị vô hiệu |
| 25–26 | 10G SFP+ uplink | Auto-negotiation **Disabled**, cố định 10 Gbps/Full |
| 27–28 | 10G SFP+ dual-use stack/uplink | Như trên; **không thêm được vào MLT** (`% Bad port number.`) |

- PoE chỉ cấp trên cổng copper (1–24); cổng 25–26 báo "does not support DTE power".
- 3650GTS: 48 cổng access + 4 cổng 10G.

## 4. Khác biệt cần nhớ so với thiết bị brand khác

- **Không có `switchport mode access/trunk`**: vai trò cổng = *VLAN membership + tagging + PVID* (chương 03).
- **Không có enable password** riêng: kiểm soát bằng tài khoản RO/RW + `cli password` (chương 05).
- **Không có `description` cho interface**: tên cổng đặt bằng `vlan ports <list> name` (chương 02).
- **Không có port-channel**: dùng MLT (tĩnh) hoặc MLT + LACP (chương 02).
- **Không có OSPF/BGP/VRRP/VRF**: chỉ static route + RIP (chương 04).
- **Không có lệnh `reboot`**: dùng `reload` / `boot` (chương 01).
- Giao diện web là **EDM** (không phải CLI qua web).
- Cấu hình **autosave bật mặc định** (60 giây).

## 5. Số liệu dùng khi lập hồ sơ

- Nhiệt độ hoạt động 0–50 °C, độ ẩm 0–95 % không ngưng tụ, cần ≥ 5 cm trống hai bên.
- MTBF giữa datasheet (2023) và tài liệu cài đặt chênh nhau; lấy con số chính thức từ đúng revision datasheet đang lưu hành.
- Nguồn: *ERS 3600 Series Data Sheet* (rev. 28jul23), *Installing ERS 3600 Series* (9036470-00).
