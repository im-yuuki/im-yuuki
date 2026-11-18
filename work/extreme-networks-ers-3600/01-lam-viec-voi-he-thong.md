# 01 — Làm việc với hệ thống

Kết nối console, CLI, xem thông tin thiết bị, hostname, lưu/backup cấu hình, reboot/reset. Ký hiệu `[*]`/`[**]` và quy ước code block: xem chương 00.

## 1. Kết nối console

| Thông số | Giá trị |
| --- | --- |
| Cổng | RJ45 console mặt trước |
| Baud / Data / Parity / Stop | **9600 / 8 / None / 1** |
| Flow control | None |

Quy trình lần đầu: cắm dây → mở terminal 9600 8N1 → cấp nguồn → khi thấy `Enter Ctrl-Y to begin.` nhấn **`Ctrl+Y`** → vào User EXEC.

**Bẫy:** console **không tự kích hoạt**. Cắm dây sau khi máy đã boot, hoặc terminal im lặng → nhấn `Ctrl+Y` trước khi kết luận máy lỗi. Vẫn không được: kiểm tra cổng COM/baud, thử terminal khác, hoặc reboot và xem từ đầu boot log.

Boot log có sẵn: U-Boot, Serial Number, MAC, `HW / FW / SW` (máy mẫu: `HW:18  FW:6.1.0.0  SW:v6.4.2.007`).

### Truy cập qua IP mặc định (không cần console)

| | Mặc định |
| --- | --- |
| Switch IP | `192.168.1.1/24` |
| Stack IP | `192.168.1.2` |
| Mật khẩu | Không có (vào thẳng, `enable` không hỏi) |

PC đặt IP tĩnh `192.168.1.x/24`, rồi kiểm tra thông mạng tới switch, sau đó SSH/Telnet/EDM.

**Kiểm tra thông mạng tới IP mặc định** (từ PC)

```text
ping 192.168.1.1
```

Mọi switch mới đều trùng IP này: **không cắm nhiều máy mới vào cùng mạng**, đặt IP quản trị riêng cho từng máy trước.

## 2. Khái niệm CLI

| Mode | Prompt | Vào bằng | Thoát |
| --- | --- | --- | --- |
| User EXEC | `3626GTS-PWR+>` | đăng nhập | `exit` / `logout` |
| Privileged EXEC | `3626GTS-PWR+#` | `enable` | `disable` |
| Global Configuration | `3626GTS-PWR+(config)#` | `configure terminal` | `end` / `Ctrl+Z` |
| Ethernet Configuration | `(config-if)#` | `interface Ethernet <list>` | `exit` |
| VLAN Interface Configuration | `(config-if)#` | `interface vlan <id>` | `exit` |

> [!NOTE]
> **So với Cisco IOS-XE:** `show` chạy trực tiếp trong config mode (không cần `do show`); không có `interface range`/tên `Gi1/0/1` — cổng chỉ là số (`interface Ethernet 5-10`).

- `?` liệt kê lệnh hợp lệ (đặt sau khoảng trắng để xem tham số tiếp theo). Hãy `?` sau từng tham số — **thứ tự tham số có ý nghĩa** (VD `vlan ports`).
- Pager: `Space`/`Enter` đọc tiếp, `q` thoát (mặc định `terminal length 23`).
- `no <lệnh>` hủy cấu hình; `default <lệnh>` về mặc định.
- Lệnh `show` chạy được ở cả Privileged EXEC lẫn Global Configuration.
- Phải gõ đủ từ khi bị `% Ambiguous command`.
- Nhóm lệnh Global hay dùng: `vlan`, `interface`, `mlt`, `lacp`, `spanning-tree`, `poe`, `ip`, `router`, `snmp-server`, `telnet-access`, `ssh`, `web-server`, `cli`, `username`, `password`.
- Privileged EXEC hay dùng: `write memory`, `reload`, `boot`, `restore`, `shutdown`, `copy`, `ping`, `traceroute`, `blink-leds` (nháy LED nhận diện thiết bị).

**Vào Privileged EXEC** (User EXEC)

```text
enable
```

**Vào Global Configuration** (Privileged)

```text
configure terminal
```

**Thoát về Privileged EXEC** (Global)

```text
end
```

**Nháy LED nhận diện thiết bị** (Privileged)

```text
blink-leds
```

## 3. Xem thông tin chung của thiết bị

| Lệnh | Mục đích |
| --- | --- |
| `show sys-info` | Bản gọn: mode, MAC, uptime, serial, license, sysDescr |
| `show system verbose` | Bản đầy đủ + `Unit #1` (fan, pluggable port, version RAM/FLASH) |
| `show stack-info` | Danh sách unit trong stack |
| `show stack health` | Tình trạng stack link |
| `show stack ?` | Bắt buộc có sub-command (`show stack` trần → `% Incomplete command`) |
| `show autosave` | Trạng thái autosave |
| `show cli password` | Tài khoản RW/RO đang hiệu lực |
| `show ip address` | IP quản trị: Configured / In Use / Last BootP-DHCP |
| `show ip route` | Bảng route |
| `show ip mgmt route` | Route quản trị (báo "disabled or blocking" khi routing tắt) |
| *`show flash unit <1-8>`* **[\*]** | Dung lượng/ghi FLASH |
| *`show boot [diag \| image]`* **[\*]** | Image đang active |

Các trường cần đọc trong `show system verbose`:

| Trường | Cách dùng |
| --- | --- |
| `Software Version` vs `Software FLASH` | Đối chiếu khi nâng/hạ firmware |
| `Reset Count` / `Last Reset Type` | Audit lịch sử reboot (`Power Cycle`, `Management Factory Reset`…) |
| `sysName` / `sysContact` / `sysLocation` | Trống trên máy mới — phải đặt (mục 4) |
| `sysNtpTime` | `NTP not synchronized` khi chưa cấu hình |
| `Serial Number`, `Manufacturing Date` | Bảo hành, kiểm kê |
| `Fan #1–3 Status` | Phải là `Normal` |
| `PoE Module FW` | Máy mẫu `1.5.0.11` |

**Xem thông tin hệ thống đầy đủ** (Privileged)

```text
show system verbose
```

**Xem thông tin hệ thống bản gọn** (Privileged)

```text
show sys-info
```

**Xem IP quản trị đang dùng** (Privileged)

```text
show ip address
```

## 4. Hostname và thông tin định danh

> [!NOTE]
> **So với Cisco IOS-XE:** Cisco dùng `hostname <tên>` (đổi prompt ngay); ERS chỉ có `snmp-server name` (sysName). Cisco `show version`/`show inventory` ≈ `show system verbose`.

*Hostname của ERS chính là `sysName` (MIB); trạng thái đổi prompt CLI theo tên chưa được kiểm chứng.* **[\*]**

*Đặt hostname (sysName)* **[\*]**

```text
snmp-server name ERS3626-CORE1
```

*Đặt vị trí lắp đặt (sysLocation)* **[\*]**

```text
snmp-server location "Tầng 3 rack A2"
```

*Đặt thông tin liên hệ (sysContact)* **[\*]**

```text
snmp-server contact "NetOps"
```

**Kiểm tra sysName / sysLocation / sysContact** (Privileged)

```text
show system verbose
```

*Gỡ hostname* **[\*]**

```text
no snmp-server name
```

## 5. Xem / lưu cấu hình hiện tại

### 5.1. Xem

| Lệnh | Kết quả |
| --- | --- |
| `show running-config` | Chỉ tham số **khác mặc định** |
| `show running-config verbose` | Toàn bộ tham số, kể cả mặc định |
| `show running-config module <tên>` | Theo module (ghép được nhiều module) |

Tên module hợp lệ: `802.1ab`, `aaur`, `adac`, `arp-inspection`, `asset-id`, `aur`, `banner`, `brouter`, `cfm`, `core`, `dhcp-relay`, `dhcp-snooping`, `eap`, `energy-saver`, `igmp`, `interface`, `ip`, `ip-source-guard`, `ipfix`, `ipmgr`, `ipv6`, `l3`, `l3-protocols`, `lacp`, `link-state`, `logging`, `mac-security`, `mlt`, `poe`, `port-mirroring`, `qos`, `rate-limit`, `rmon`, `rtc`, `slamon`, `slpp`, `snmp`, `spbm`, `stack`, `stkmon`, `stp`, `vlacp`, `vlan`.

- STP là module **`stp`** (không phải `spanning-tree`); cấu hình cổng là **`interface`** (không phải `ethernet`).
- IP quản trị mặc định `192.168.1.1` không xuất hiện trong `show running-config` (là giá trị default). Với cấu hình xuất ra file ASCII, IP quản trị luôn bị comment bằng `!`. *Chủ ý để bê sang switch khác không trùng IP.* **[\*]**

**Xem cấu hình khác mặc định** (Privileged)

```text
show running-config
```

**Xem toàn bộ cấu hình kể cả mặc định** (Privileged)

```text
show running-config verbose
```

**Xem cấu hình theo module (VD VLAN)** (Privileged)

```text
show running-config module vlan
```

### 5.2. Lưu

| Lệnh | Trạng thái |
| --- | --- |
| `write memory` | **Dùng lệnh này** |
| `save` trần | `% Incomplete command` |
| `write` trần | `% Incomplete command` |
| `copy config nvram` | **Bị từ chối** (`% Invalid input`) dù tài liệu hãng có |
| *`save config`* **[\*]** | Cú pháp trong CLI Ref, chưa chạy trên máy |

**Lưu cấu hình vào NVRAM** (Privileged)

```text
write memory
```

*Lưu cấu hình (cú pháp tài liệu hãng)* **[\*]**

```text
save config
```

> [!IMPORTANT]
> **So với Cisco IOS-XE:** Cisco **không autosave** (phải `copy running-config startup-config`), nên "không save thì reboot sẽ hoàn tác" là đúng. ERS **autosave 60 s mặc định** → thay đổi sai cũng tự được lưu, không còn đường lùi bằng reboot; đặt hẹn giờ `reload` trước khi đổi (§6).

**Autosave:** bật mặc định. Mỗi 60 giây switch kiểm tra và tự ghi cấu hình + log vào flash; cũng tự ghi khi gọi lệnh reset. Lệnh `autosave` chỉ chạy ở Global Configuration.

⚠️ Không cắt nguồn trong vòng **60 giây** sau khi đổi cấu hình.

**Xem trạng thái autosave** (Privileged)

```text
show autosave
```

**Tắt autosave** (Global)

```text
no autosave enable
```

**Bật autosave** (Global)

```text
autosave enable
```

**Đưa autosave về mặc định** (Global)

```text
default autosave enable
```

### 5.3. Backup / restore cấu hình

- Phân biệt chiều: backup là `copy running-config tftp`; `copy tftp config` / `copy sftp` là chiều **về máy** — tài liệu hãng mô tả hai chiều này lẫn lộn, **gõ `?` kiểm tra trước khi chạy**; restore có thể ghi đè cấu hình đang chạy.
- **Không có lệnh backup config ra USB** trên 6.4 (USB chỉ dùng để nạp image).
- Không nhầm `restore` (= factory default, mục 6) với restore config.

*Backup cấu hình lên TFTP (`verbose` và `module` tùy chọn)* **[\*]**

```text
copy running-config tftp filename <file> address <A.B.C.D>
```

*Backup lên TFTP kèm cả tham số mặc định* **[\*]**

```text
copy running-config tftp verbose filename <file> address <A.B.C.D>
```

*Restore cấu hình từ TFTP về máy* **[\*]**

```text
copy tftp config address <A.B.C.D> filename <file>
```

*Restore cấu hình từ SFTP về máy (chỉ có chiều về máy)* **[\*]**

```text
copy sftp
```

*Xem TFTP server đã cấu hình* **[\*]**

```text
show tftp-server
```

## 6. Reboot / Reset

Tất cả ở Privileged EXEC. **Không có lệnh `reboot`.**

> [!WARNING]
> **So với Cisco IOS-XE:** `reload in <phút>` ≈ `reload force minutes-to-wait`; `configure terminal revert timer` (tự rollback) và `configure replace` **không có** trên ERS. Về xuất xưởng: Cisco `write erase` + `reload` (hoặc `factory-reset`), ERS `restore factory-default` — chạy là xóa ngay.

| Lệnh | Tác dụng | Tự lưu config? | Hỏi xác nhận |
| --- | --- | --- | --- |
| `reload` | Reboot ngay | Không | `Reload (y/n) ?` |
| `reload force minutes-to-wait <1-60>` | Hẹn reboot | Không | Không |
| `reload cancel` | Hủy hẹn giờ | — | — |
| `shutdown [force] minutes-to-wait <1-60>` | Lưu config rồi tắt | **Có** | Có (trừ `force`) |
| `shutdown cancel` | Hủy | — | — |
| `boot [unit <1-8>]` | Reboot switch/stack, hoặc 1 unit | Không nói rõ | — |
| `boot default [unit <1-8>]` | Reboot với factory default config | — | — |
| `restore factory-default [-y]` | Xóa sạch, về xuất xưởng | Config bị xóa | Có (`-y` bỏ qua; **chỉ có `-y`**, không có `force`) |

- Reload countdown: **autosave tạm dừng**; hết giờ máy reboot và nạp lại NVRAM (bản cũ). Hủy bằng `reload cancel`. Mọi thay đổi chưa `write memory` sẽ mất sau reboot.
- Sau `restore factory-default`: `Last Reset Type: Management Factory Reset`, IP về `192.168.1.1`, không mật khẩu, chỉ VLAN 1.
- Stack: `boot unit <n>` chỉ reboot 1 unit; `reload`/`boot` ảnh hưởng toàn stack — xem `show stack-info` trước.
- PoE không bị ảnh hưởng bởi reboot (cấp lại khi máy lên).

**Reboot ngay (hỏi xác nhận)** (Privileged)

```text
reload
```

**Hẹn reboot sau 15 phút, không hỏi xác nhận** (Privileged)

```text
reload force minutes-to-wait 15
```

**Hủy hẹn giờ reload** (Privileged)

```text
reload cancel
```

**Lưu config rồi tắt máy sau 10 phút** (Privileged)

```text
shutdown minutes-to-wait 10
```

**Hủy hẹn giờ shutdown** (Privileged)

```text
shutdown cancel
```

**Reboot riêng một unit trong stack** (Privileged)

```text
boot unit 2
```

**Reboot về factory default** (Privileged)

```text
boot default
```

**Đưa máy về xuất xưởng (hỏi xác nhận, gõ `y`)** (Privileged)

```text
restore factory-default
```

### Scenario: đổi cấu hình từ xa an toàn

Luôn đặt hẹn giờ **trước** khi áp thay đổi. Nếu hỏng thì không làm gì: sau 15 phút máy tự reboot về cấu hình NVRAM cũ.

**Bước 1 — Hẹn reboot 15 phút làm lưới an toàn** (Privileged)

```text
reload force minutes-to-wait 15
```

**Bước 2a — Vào Global Configuration rồi áp thay đổi** (Privileged)

```text
configure terminal
```

**Bước 2b — Sau khi áp xong, thoát về Privileged** (Global)

```text
end
```

**Bước 3 — Test từ máy khác (ping, SSH, dịch vụ). Nếu OK: lưu cấu hình** (Privileged)

```text
write memory
```

**Bước 4 — Hủy hẹn giờ** (Privileged)

```text
reload cancel
```

### Scenario: đưa máy lab về xuất xưởng

**Xóa sạch cấu hình, gõ `y` khi được hỏi** (Privileged)

```text
restore factory-default
```

## 7. Bẫy & quy tắc

1. Chưa `write memory` (hoặc chưa đủ 60 giây autosave) mà reboot → mất cấu hình.
2. `reload force`, `shutdown force`, `restore factory-default -y` **không hỏi gì** — không copy-paste nguyên khối.
3. `shutdown` ở Privileged EXEC = lưu + tắt máy; `shutdown` ở Ethernet Configuration = tắt cổng (chương 02). Khác hoàn toàn.
4. Không reboot khi đang `download` image hoặc `copy` config.
