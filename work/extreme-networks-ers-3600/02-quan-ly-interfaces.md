# 02 — Quản lý interface

Đánh số cổng, xem trạng thái, transceiver, MAC học được, bật/tắt, đặt tên, MLT/LACP, PoE. Ký hiệu `[*]`/`[**]` và quy ước code block: xem chương 00.

## 1. Cách đánh số

- Stack-aware: `<unit>/<port>` khi stack; máy đơn chỉ dùng `<port>`.
- 3626GTS(-PWR+): cổng 1–24 RJ45 (23–24 combo SFP), 25–26 SFP+ uplink, 27–28 SFP+ dual-use stack/uplink. Chi tiết: chương 00 §3.
- Danh sách cổng: `1,8,10-14`, `ALL`, `NONE`.

**Vào mode cấu hình cổng (VD cổng 5–10)** (Global)

```text
interface Ethernet 5-10
```

## 2. Xem thông tin & trạng thái

> [!NOTE]
> **So với Cisco IOS-XE:** `show interfaces` ≈ `show interfaces status`; `gbic-info` ≈ `show interfaces transceiver detail`. Cisco lọc MAC theo cổng bằng `show mac address-table interface <if>`, ERS không có (chỉ pipe filter, xem §4).

| Lệnh | Mục đích |
| --- | --- |
| `show interfaces` | Bảng cổng: Admin / Oper / Link / LinkTrap / Auto-Neg / Speed / Duplex / Flow |
| `show interfaces link-up` / `link-down` | Lọc theo link |
| `show interfaces admin-enabled` / `admin-disabled` | Lọc theo admin |
| `show interfaces names` | Tên cổng (rỗng nếu chưa đặt) |
| `show interfaces verbose` | Chi tiết: STP/EAP/VLACP oper, Energy Saver, BPDU-guard, SLPP-guard, Mdix |
| `show interfaces <list> config` | VLAN membership, PVID, tagging, STP per-port |
| `show interfaces ALL config` | Như trên cho mọi cổng |
| `show port-statistics` | Counters Rx/Tx, phân bố kích thước frame, dropped |
| `show auto-pvid` | `AutoPVID: Enabled` (mặc định) |

- `show interfaces config` **không tham số → `% Bad format`**: phải kèm `<list>` hoặc `ALL`/`NONE`.
- Cổng 10G SFP+ (25–28): Auto-Neg Disabled, 10 Gbps/Full cố định, `Mdix Mode: N/A`. Cổng RJ45: Auto-MDIX.
- Counter multicast Tx/Rx lớn trên cổng up là control-plane bình thường (STP/LLDP); chỉ lo khi có FCS/frame error.

**Xem trạng thái toàn bộ cổng** (Privileged)

```text
show interfaces
```

**Chỉ xem cổng đang up** (Privileged)

```text
show interfaces link-up
```

**Chỉ xem cổng đang down** (Privileged)

```text
show interfaces link-down
```

**Xem cấu hình VLAN/PVID/STP của cổng 5** (Privileged)

```text
show interfaces 5 config
```

**Xem cấu hình mọi cổng** (Privileged)

```text
show interfaces ALL config
```

**Xem chi tiết từng cổng** (Privileged)

```text
show interfaces verbose
```

**Xem counter các cổng** (Privileged)

```text
show port-statistics
```

*Xóa counter cổng (chạy trong mode cổng, không phải Privileged)* **[\*]**

```text
clear-stats port 5-10
```

## 3. Transceiver (SFP/SFP+)

- Máy mẫu: 2× `10GB-SR` Extreme (`FTLX8571D3BCL-C2`) ở cổng 25, 26.
- Lần đầu sau out-of-box có thể báo `% No gbic found.` — chạy lại khi nghi ngờ.
- Combo SFP (23–24): cắm SFP thì RJ45 tương ứng bị vô hiệu.

**Xem chi tiết module quang (type, wavelength, vendor, part #, serial)** (Privileged)

```text
show interfaces gbic-info
```

**Xem trạng thái pluggable port theo từng unit** (Privileged)

```text
show system verbose
```

## 4. Learned MAC address

- Aging mặc định **300 s**. MAC trống cột Source (VD `0C-9B-78-E6-37-00`) là MAC của chính switch.
- Pipe filter (`|`) có trên máy nhưng từ khóa lọc chưa kiểm chứng; xem tùy chọn bằng `show mac-address-table | ?`.

**Xem toàn bộ bảng MAC (MAC, VID, Source)** (Privileged)

```text
show mac-address-table
```

*Lọc MAC học trên cổng 24* **[\*\*]**

```text
show mac-address-table | include Port:24
```

*Đổi aging time (giây)* **[\*]**

```text
mac-address-table aging-time 600
```

*Xóa MAC động trên cổng* **[\*]**

```text
clear mac-address-table dynamic interface Ethernet 5
```

## 5. Bật/tắt cổng

*Tắt cổng (Admin Down) — `shutdown [port <list>]` ở Ethernet Configuration* **[\*]**

```text
interface Ethernet 5-10
shutdown
exit
```

*Bật lại cổng — `no shutdown` theo quy ước `no`* **[\*\*]**

```text
interface Ethernet 5-10
no shutdown
exit
```

**Kiểm tra trạng thái Admin của cổng** (Privileged)

```text
show interfaces 5-10
```

Khác: `shutdown` trần ở Privileged EXEC là **tắt cả máy** (chương 01).

## 6. Đặt tên (description)

> [!NOTE]
> **So với Cisco IOS-XE:** không có lệnh `description` trong interface; tên cổng đặt ở **Global** bằng `vlan ports <list> name`. `shutdown`/`no shutdown` trong `(config-if)#` dùng như Cisco.

**Đặt tên cho dải cổng** (Global)

```text
vlan ports 5-10 name "PC phong ke"
```

**Đặt tên cho cổng uplink** (Global)

```text
vlan ports 25 name "Uplink-Core"
```

**Kiểm tra tên cổng (cột `Name`; mặc định `Port n`)** (Privileged)

```text
show interfaces 5 config
```

## 7. Link aggregation: MLT / LACP

> [!IMPORTANT]
> **So với Cisco IOS-XE:** không có `channel-group N mode active` tự tạo Port-channel. Với LACP phải **bind `lacp key` vào MLT slot trống trước**, rồi mới gán cổng; làm ngược (tạo MLT trước) bị từ chối. Giới hạn 6 nhóm × 4 link, chỉ hash theo IP/MAC.

Tối đa **6 MLT**, **4 link/MLT**. Hash only (không round-robin): `loadbalance advance` = theo IP, `basic` = theo MAC. **Cổng 27–28 không thêm được vào MLT** (`% Bad port number.`).

### 7.1. MLT tĩnh

**Tạo MLT 1 tĩnh gồm cổng 1–4** (Global)

```text
mlt 1 name LAB enable member 1-4
```

**Hash theo IP** (Global)

```text
mlt 1 loadbalance advance
```

*Chế độ BPDU của MLT (`all-ports` hoặc `single-port`)* **[\*]**

```text
mlt 1 bpdu single-port
```

*STP learning của MLT (`disable`, `fast`, `normal`)* **[\*]**

```text
mlt spanning-tree 1 stp learning fast
```

**Xóa MLT 1** (Global)

```text
no mlt 1
```

**Kiểm tra cấu hình MLT** (Privileged)

```text
show running-config module mlt
```

### 7.2. MLT + LACP

**Thứ tự phải đúng:** gắn LACP key vào MLT slot **trước**, slot phải còn trống. Làm ngược bị từ chối (`% Cannot use an MLT that is already configured.` / `% Ports must not be already MLT trunk members.`).

**Bước 1 — Gỡ MLT 1 nếu đã cấu hình** (Global)

```text
no mlt 1
```

**Bước 2 — Gắn key 100 vào MLT slot 1** (Global)

```text
lacp key 100 mlt-id 1
```

**Bước 3 — Gán key, bật aggregation và mode active cho cổng 1–4** (Global → Ethernet)

```text
interface Ethernet 1
lacp key port 1-4 100
lacp aggregation port 1-4 enable
lacp mode port 1-4 active
```

*Timeout LACP (`long` hoặc `short`)* **[\*]**

```text
lacp timeout-time port 1-4 long
```

**Kiểm tra LACP key và MLT ID** (Privileged)

```text
show lacp key
```

**Kiểm tra cấu hình LACP đang chạy** (Privileged)

```text
show running-config module lacp
```

- `active` chủ động gửi LACPDU, `passive` chỉ phản hồi.
- Không trộn LACP và MLT tĩnh trong cùng nhóm.
- `show lacp ?`: `aggr | debug | key | port | port-mode | stats | system`; `show lacp` trần → incomplete.
- Phía Linux: bond `802.3ad`, `xmit_hash_policy layer2+3`/`layer3+4`.
- ⚠️ Mới xác nhận luồng cấu hình, **chưa xác nhận link-up + traffic end-to-end** (lab không cắm thiết bị đầu xa).

## 8. PoE (model -PWR+)

> [!TIP]
> **So với Cisco IOS-XE:** Cisco `power inline {auto|never|static max <mW>}`, `show power inline`; ERS tách thành `poe poe-shutdown`/`poe poe-limit`/`poe poe-priority`. Bật lại PoE là `no poe port <n>`, không phải `no poe poe-shutdown`.

Per-port trong mode cổng, global trong Global Configuration.

**Tắt PoE trên cổng 7** (Global → Ethernet)

```text
interface Ethernet 7
poe poe-shutdown port 7
```

**Bật lại PoE trên cổng 7** (Ethernet)

```text
no poe port 7
```

*Giới hạn công suất cổng 5–10 (PoE+ 3–32 W; af 3–16 W)* **[\*]**

```text
poe poe-limit port 5-10 15
```

*Ưu tiên PoE (`critical`, `high`, `low`)* **[\*]**

```text
poe poe-priority port 5-10 high
```

*Cho phép dòng khởi động lớn — cẩn thận, có thể hỏng linh kiện* **[\*]**

```text
poe poe-power-up-mode port 5 high-inrush
```

*Chế độ ngân sách PoE (`high-power-budget` / `low-power-budget`)* **[\*]**

```text
poe power-mode high-power-budget
```

*Loại PD phát hiện (`802dot3af`, `802dot3af_and_legacy`, `802dot3at`, `802dot3at_and_legacy`)* **[\*]**

```text
poe poe-pd-detect-type 802dot3at
```

*Ngưỡng cảnh báo sử dụng PoE (%)* **[\*]**

```text
poe poe-power-usage-threshold 80
```

*Tự cấp PoE cho IP phone nhận diện được* **[\*]**

```text
poe ip-phone poe-limit 15
```

**Xem ngân sách và trạng thái PoE toàn cục (máy mẫu 740 W)** (Privileged)

```text
show poe-main-status
```

**Xem trạng thái PoE từng cổng** (Privileged)

```text
show poe-port-status
```

**Xem công suất đo được từng cổng** (Privileged)

```text
show poe-power-measurement
```

- `show poe ?` → ambiguous; dùng đúng ba lệnh trên.
- Mặc định: `Admin Enable`, `Limit 32W`, `Priority Low`, `Power-up Mode 802.3at`. Cổng 25–26 không hỗ trợ PoE.
- `poe-priority critical` không bị cắt khi quá ngân sách.

## 9. Tham số khác trên cổng (xem nhanh)

| Mục | Ghi chú |
| --- | --- |
| BPDU filtering | `spanning-tree bpdu-filtering enable` trong mode cổng (chương 03) |
| Energy Saver | Mặc định Disabled |
| SLPP-guard | Mặc định Disabled |
| Flow control | `Disable` (RJ45), `Asymm` (10G) |
