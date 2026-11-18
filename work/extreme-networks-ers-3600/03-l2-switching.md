# 03 — L2 switching

VLAN, access/trunk, STP, DHCP snooping. Ký hiệu `[*]`/`[**]` và quy ước code block: xem chương 00.

## 1. Mô hình cổng ERS (khác brand khác)

Không có `switchport mode access/trunk`. Vai trò cổng = tổ hợp 3 thứ:

| Thành phần | Lệnh |
| --- | --- |
| Membership (≈ allowed VLAN) | `vlan members add/remove <vlans> <ports>` |
| Tagging egress | `vlan ports <ports> tagging <mode>` |
| PVID (≈ native/access VLAN) | `vlan ports <ports> pvid <id>` |

Không có từ khóa `trunk`, `native`, `allowed` — đọc cấu hình bằng cách xem cả ba.

> [!IMPORTANT]
> **So với Cisco IOS-XE:** Cisco có `switchport mode access|trunk` + `switchport access vlan` / `trunk allowed vlan` / `trunk native vlan`; ERS **không có chế độ cổng**, chỉ có membership + tagging + PVID. Cổng access phải tự `vlan members remove 1`; mặc định egress là `untagAll` (khác trunk Cisco luôn tag trừ native).

## 2. Tạo & quản lý VLAN

- **Thứ tự cố định:** `vlan create <id> name <tên> type port` — `type` đứng **cuối**; `name` phải có tên đi kèm. `vlan create 10 type port name X` và `vlan create 10 name X` đều bị từ chối.
- Giới hạn 256 VLAN; máy mới chỉ có VLAN 1.

**Tạo VLAN 10 tên DATA** (Global)

```text
vlan create 10 name DATA type port
```

**Tạo VLAN 20 tên VOICE** (Global)

```text
vlan create 20 name VOICE type port
```

*Đổi tên VLAN* **[\*]**

```text
vlan name 10 DATA2
```

*Xóa VLAN* **[\*]**

```text
vlan delete 20
```

**Xem tổng số VLAN** (Privileged)

```text
show vlan summary
```

**Xem VLAN membership từng cổng** (Privileged)

```text
show vlan interface vids
```

**Xem PVID/tagging từng cổng** (Privileged)

```text
show vlan interface info
```

*Xem một VLAN theo ID* **[\*]**

```text
show vlan id 10
```

*Xem VLAN theo loại* **[\*]**

```text
show vlan type port
```

*Xem VLAN quản trị* **[\*]**

```text
show vlan mgmt
```

### 2.1. VLAN Configuration Control (mặc định `strict`)

> [!WARNING]
> **So với Cisco IOS-XE:** Cisco không có cơ chế tương đương. ERS mới ở `strict` nên `vlan members add` bị từ chối; nếu quen Cisco sẽ tưởng lệnh sai cú pháp.

**Output mẫu khi bị chặn**

```text
% Cannot modify settings
% VLAN Configuration Control is 'Strict'
```

| Giá trị | Ý nghĩa |
| --- | --- |
| `strict` | AutoPVID + hạn chế add cổng vào VLAN / đổi tagging (mặc định) |
| `flexible` | Không hạn chế, không tự đổi |
| `autopvid` | Tự đổi PVID |
| `automatic` | AutoPVID + tự đổi membership |

- Gõ đủ từ (`auto` → `% Ambiguous command`); lệnh chỉ chạy ở Global Configuration.
- Lab: dùng `flexible`. Production: chủ động chọn mode, không đổi để "cho qua lỗi". Phạm vi ràng buộc chính xác của `strict` chưa mô tả đầy đủ — thử trên lab trước.

**Xem mode đang dùng** (Privileged)

```text
show vlan configcontrol
```

**Chuyển sang flexible** (Global)

```text
vlan configcontrol flexible
```

*Đưa về mặc định* **[\*]**

```text
default vlan configcontrol
```

## 3. Access port

Ví dụ cổng 5–10 thuộc VLAN 10.

- `vlan members add` **không gỡ VLAN 1** — cổng thuộc cả VLAN 1 lẫn VLAN mới. Bước `remove 1` rất hay bị quên.
- **Thứ tự `vlan ports`:** `tagging` → `pvid` → `filter-untagged-frame` → `priority` → `name`. Sau `pvid` không còn nhận `tagging`. `?` sau từng tham số.
- Mặc định: `PVID 1`, `Tagging UntagAll`, `Filter Untagged = No`, `Filter Unregistered = Yes`.

**Bước 1 — Thêm cổng 5–10 vào VLAN 10** (Global)

```text
vlan members add 10 5-10
```

**Bước 2 — Gỡ cổng khỏi VLAN 1 (bắt buộc cho access thuần)** (Global)

```text
vlan members remove 1 5-10
```

**Bước 3 — Untag VLAN 10 khi ra, PVID 10 khi vào** (Global)

```text
vlan ports 5-10 tagging untagPvidOnly pvid 10
```

**Kiểm tra cổng access** (Privileged)

```text
show interfaces 5 config
```

## 4. Trunk port

Ví dụ uplink cổng 25: VLAN 10, 20 tagged, PVID 99.

| `tagging` | Frame đi ra |
| --- | --- |
| `untagAll` | Tất cả VLAN member **không tag** (mặc định) |
| `tagAll` | Tất cả **có tag** (kể cả PVID/VLAN 1) |
| `untagPvidOnly` | PVID không tag, VLAN khác có tag |
| `tagPvidOnly` | PVID có tag, VLAN khác không tag |
| `enable` / `disable` | Chấp nhận được; ngữ nghĩa chính xác chưa xác định |

- `tagAll` ⇒ không có native VLAN theo chiều egress; untagged frame **đi vào** vẫn nhận PVID.

**Bước 1 — Thêm "allowed VLAN" 10, 20, 99 vào cổng 25** (Global)

```text
vlan members add 10,20,99 25
```

**Bước 2 — Tag mọi VLAN khi ra, PVID 99 cho frame untagged vào** (Global)

```text
vlan ports 25 tagging tagAll pvid 99
```

**Bớt VLAN 20 khỏi trunk** (Global)

```text
vlan members remove 20 25
```

**Kiểm tra trunk (kỳ vọng: `TagAll`, PVID 99, member 1/10/99)** (Privileged)

```text
show interfaces 25 config
```

### Scenario: access + uplink

**1. Cho phép đổi VLAN membership** (Global)

```text
vlan configcontrol flexible
```

**2a. Tạo VLAN dữ liệu** (Global)

```text
vlan create 10 name DATA type port
```

**2b. Tạo VLAN quản trị** (Global)

```text
vlan create 99 name MGMT type port
```

**3. Cổng access 5–10 vào VLAN 10 thuần** (Global)

```text
vlan members add 10 5-10
vlan members remove 1 5-10
vlan ports 5-10 tagging untagPvidOnly pvid 10
```

**4. Uplink cổng 25 mang VLAN 10, 99; PVID 99** (Global)

```text
vlan members add 10,99 25
vlan ports 25 tagging tagAll pvid 99
```

**5. Lưu cấu hình** (Privileged)

```text
write memory
```

Kiểm tra: `show interfaces 5 config` (PVID 10, chỉ VLAN 10) · `show interfaces 25 config` (`TagAll`, PVID 99, member 1/10/99).

## 5. Spanning-tree

> [!NOTE]
> **So với Cisco IOS-XE:** Cisco Catalyst 9000 mặc định Rapid-PVST+ (per-VLAN), đổi mode áp dụng ngay, có `portfast`/`bpduguard` per-port. ERS mặc định **MSTP**, đổi mode **phải reboot**, không có lệnh edge-port/cost/priority per-port.

- Mặc định **MSTP**. `show spanning-tree mode` → `Current STP Operation Mode: MSTP`.
- Đổi mode **chỉ có hiệu lực sau reboot**: `spanning-tree mode rstp` → `New operational mode RSTP will take effect upon reset`. *Cú pháp hãng: `spanning-tree mode [mst | rstp | stpg]`.* **[\*]**
- **Không có `spanning-tree rstp ...`** trên 6.4.2.007. `spanning-tree ?` chỉ có `bpdu-filtering`, `mode`, `mstp`.
- Cấu hình MSTP theo mô hình **CIST** (bridge-wide); **không có** `cost`/`priority`/`edge-port` per-port ở đây.
- Edge port xử lý tự động bởi MSTP — *chưa kiểm chứng bằng lab.* **[\*\*]**
- Chỉ chỉnh `priority`/`region`/`msti` khi triển khai nhiều switch cùng domain.

**Xem mode STP hiện tại** (Privileged)

```text
show spanning-tree mode
```

**Đổi sang RSTP (hiệu lực sau reboot)** (Global)

```text
spanning-tree mode rstp
```

**Liệt kê tùy chọn MSTP (CIST)** (Global)

```text
spanning-tree mstp ?
```

**Output mẫu của `spanning-tree mstp ?`**

```text
add-vlan | forward-time | max-age | max-hop | msti | pathcost-type
priority | region | remove-vlan | tx-holdcount | version
```

*Bật BPDU filtering cho cổng 5–10* **[\*]**

```text
interface Ethernet 5-10
spanning-tree bpdu-filtering enable
```

*Đặt timeout BPDU filtering* **[\*]**

```text
spanning-tree bpdu-filtering timeout 10
```

**Kiểm tra STP** (Privileged)

```text
show running-config module stp
```

## 6. DHCP snooping

> [!NOTE]
> **So với Cisco IOS-XE:** ERS viết có gạch nối (`ip dhcp-snooping`), cần `ip dhcp-snooping enable` toàn cục **và** `vlan <id>`; cổng tin cậy là `trusted` (Cisco `trust`). Option 82 mặc định **tắt** trên ERS; Cisco IOS-XE mặc định chèn Option 82.

**Bật DHCP snooping toàn cục (bắt buộc; chỉ `vlan X` là không đủ)** (Global)

```text
ip dhcp-snooping enable
```

**Bật snooping trên VLAN 10** (Global)

```text
ip dhcp-snooping vlan 10
```

**Chèn Option 82 trên VLAN 10** (Global)

```text
ip dhcp-snooping vlan 10 option82
```

**Thêm static binding cho VLAN** (Global)

```text
ip dhcp-snooping binding <1-4094>
```

**Đánh dấu cổng 25 là trusted (uplink / DHCP server)** (Global → Ethernet)

```text
interface Ethernet 25
ip dhcp-snooping trusted
```

**Đặt cổng client về untrusted (mặc định)** (Global → Ethernet)

```text
interface Ethernet 5-10
ip dhcp-snooping untrusted
```

**Xem trạng thái snooping** (Privileged)

```text
show ip dhcp-snooping
```

**Xem snooping theo VLAN** (Privileged)

```text
show ip dhcp-snooping vlan 10
```

**Xem số binding (Learned / Static / Total)** (Privileged)

```text
show ip dhcp-snooping binding summary
```

*Xem trusted/untrusted theo cổng* **[\*]**

```text
show ip dhcp-snooping interface
```

**Xóa binding động (hỏi `y/n`)** (Privileged)

```text
clear ip dhcp-snooping binding dynamic
```

**Xóa binding tĩnh** (Privileged)

```text
clear ip dhcp-snooping binding static
```

Giới hạn: 512 binding. Liên quan: `ip arp-inspection`, `ip source` / `ip verify` (IP Source Guard) có trong `show ip ?` nhưng chưa có hướng dẫn trong guide này.

## 7. Bẫy thường gặp

1. `% VLAN Configuration Control is 'Strict'` → xem §2.1.
2. Cổng "access" vẫn nhận VLAN 1 → quên `vlan members remove 1`.
3. `vlan ports ... pvid X tagging ...` bị từ chối → đảo thứ tự (`tagging` trước `pvid`).
4. `interface vlan X` / `vlan members` báo VLAN không tồn tại → `vlan create` trước.
5. Đổi STP mode không có tác dụng ngay → cần reboot (dùng hẹn giờ `reload`, chương 01).
