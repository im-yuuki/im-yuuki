# 05 — Bảo mật, dịch vụ và quản trị từ xa

Tài khoản, mật khẩu, telnet/SSH/web, SNMP, hardening. Ký hiệu `[*]`/`[**]` và quy ước code block: xem chương 00.

## 1. Mô hình truy cập

> [!IMPORTANT]
> **So với Cisco IOS-XE:** không có `enable secret`, `username <n> privilege 15 secret`, `line vty` hay AAA method list. ERS chỉ có **2 tài khoản cố định RO/RW**, mật khẩu theo đường vào (`cli password telnet` dùng chung cho telnet+SSH+web), và chính sách mật khẩu 10–15 ký tự bắt buộc.

- **Không có enable password.** Quy trình: đăng nhập bằng tài khoản **RW** → `enable`.
- Kiểm soát qua: (1) đường vào `cli password {serial|telnet}`, (2) hai tài khoản local RO/RW hoặc RADIUS/TACACS+, (3) AAA tập trung (*TACACS+ privilege level `tacacs switch level <1-15>`* **[\*]**).
- Máy mới: console và telnet **vào thẳng, không mật khẩu** — phải đặt ngay.

### 1.1. Đường vào

| | Áp cho |
| --- | --- |
| `serial` | Console vật lý |
| `telnet` | **Telnet + SSH + web** (một công tắc chung) |

Giá trị: `local`, `none`, `radius`, `tacacs`. Mặc định `none` cho cả hai.

**Yêu cầu mật khẩu khi vào console** (Global)

```text
cli password serial local
```

**Yêu cầu mật khẩu khi vào telnet/SSH/web** (Global)

```text
cli password telnet local
```

### 1.2. Tài khoản RO / RW

- Hai tài khoản mặc định `RO` (read-only) / `RW` (read-write).
- *`username <name> {ro|rw}` hỏi mật khẩu qua prompt ẩn; tài khoản tạo ra không thấy trong `show cli password` và chưa kiểm tra đăng nhập thực tế — dùng `cli password read-only/read-write` để đổi mật khẩu hai tài khoản có sẵn.* **[\*]**
- *Phạm vi chính xác RO bị chặn (có `enable`/`configure` được không) chưa kiểm chứng.* **[\*\*]**

**Đặt mật khẩu tài khoản RW** (Global)

```text
cli password read-write NetOps@2026#XY
```

**Đặt mật khẩu tài khoản RO** (Global)

```text
cli password read-only Viewer@2026#XY
```

**Xem tài khoản đang hiệu lực** (Privileged)

```text
show cli password
```

**Đưa tài khoản RW về mặc định (RO tương tự)** (Global)

```text
default username rw
```

### 1.3. Chính sách mật khẩu (bật sẵn)

- **10–15 ký tự**, tối thiểu **2 HOA, 2 thường, 2 số, 2 ký tự đặc biệt** `!@#$%^&*()`. Ví dụ hợp lệ: `NetOps@2026#XY`. Không hợp lệ: `Lab@2026`, `Labro123`.
- Aging mặc định **180 ngày**.
- Tuỳ chọn trong `password security`: *`complexity`, `check-sequential`, `check-repeated`, `min-length <8-255>`, `password-history <0-12>`, `password-change-on-first-login`, `notifications <1-90>`, `password-change-rate-limiter`.* **[\*]**

**Bật ràng buộc mật khẩu (mặc định đã bật)** (Global)

```text
password security
```

**Đặt aging time 180 ngày** (Global)

```text
password aging-time day 180
```

**Tắt ràng buộc mật khẩu (chỉ dùng cho lab)** (Global)

```text
no password security
```

### 1.4. Prompt ẩn

Lệnh cần secret (`snmp-server bootstrap`, `snmp-server user ... read-view`, `username`) tự hỏi qua prompt không echo — **không đoán cú pháp inline**; dùng `?` và làm theo prompt.

## 2. Telnet

- Mặc định: `login-timeout 1` (phút), `retry 3`, `inactive-timeout 15` (phút, áp cả console), `logging all`.
- `source-ip` là danh sách tối đa 100 entry cho phép telnet từ đâu — "ACL" duy nhất cho telnet.

**Bật telnet** (Global)

```text
telnet-access enable
```

**Tắt telnet** (Global)

```text
telnet-access disable
```

**Đặt thời gian chờ đăng nhập (phút, 1–10)** (Global)

```text
telnet-access login-timeout 1
```

**Đặt số lần đăng nhập sai tối đa (1–100)** (Global)

```text
telnet-access retry 3
```

**Đặt thời gian idle trước khi ngắt (phút, 0–60)** (Global)

```text
telnet-access inactive-timeout 15
```

**Đặt mức log truy cập (`none`, `access`, `failures`, `all`)** (Global)

```text
telnet-access logging all
```

*Chỉ cho phép telnet từ một dải IP* **[\*]**

```text
telnet-access source-ip 1 10.0.0.0 mask 255.255.255.0
```

*Gỡ entry source-ip* **[\*]**

```text
no telnet-access source-ip 1
```

**Đưa telnet-access về mặc định** (Global)

```text
default telnet-access
```

## 3. SSH

> [!WARNING]
> **So với Cisco IOS-XE:** Cisco cần hostname + domain + `crypto key generate rsa` + `ip ssh version 2` + `transport input ssh` trên VTY. ERS đã có sẵn host key, chỉ SSHv2, và `ssh secure` là công tắc **tắt cả telnet, SNMP, web** — Cisco không có lệnh tương đương, dễ tự khóa mình.

Mặc định: **Version 2 only**, port 22, timeout 60 s, retries 3, auth DSA + RSA + password đều True, host key DSA/RSA `Exist`, **`Enabled: False`**.

- Mật khẩu SSH dùng chung `cli password telnet`.
- `sshc` = SSH client (cho SFTP): `sshc ?` → `authentication | dsa-host-key | dsa-key | port | rsa-host-key | rsa-key | upload-host-key`; `sftp-server {A.B.C.D | WORD}`.
- Chưa xác nhận trên lab: SSH vào bằng RW/RO, nạp pubkey qua TFTP.

**Xem trạng thái SSH** (Privileged)

```text
show ssh global
```

**Liệt kê tùy chọn SSH** (Global)

```text
ssh ?
```

**Output mẫu của `ssh ?`**

```text
download-auth-key | download-banner | dsa-auth | dsa-host-key | pass-auth | port
retries | rsa-auth | rsa-host-key | secure | timeout
```

*Bật SSH — lệnh `ssh` trần ở Global theo họ ERS, chưa có trong tài liệu 3600. Kiểm tra bằng `ssh ?` rồi `show ssh global` → `Enabled: True`* **[\*\*]**

```text
ssh
```

**SSH-only: tắt telnet, SNMP, web (hỏi `y/n`; kết quả `Enabled: Secure`)** (Global)

```text
ssh secure
```

**Sinh host key RSA mới** (Global)

```text
ssh rsa-host-key
```

**Sinh host key DSA mới** (Global)

```text
ssh dsa-host-key
```

**Đổi port SSH** (Global)

```text
ssh port 22
```

**Đặt timeout xác thực SSH (giây)** (Global)

```text
ssh timeout 60
```

**Đặt số lần thử mật khẩu SSH** (Global)

```text
ssh retries 3
```

**Nạp public key RSA qua TFTP** (Global)

```text
ssh download-auth-key address <A.B.C.D> rsa key-name <file>
```

**Xem thông tin nạp public key** (Privileged)

```text
show ssh download-auth-key
```

**Xem phiên SSH** (Privileged)

```text
show ssh session
```

*Xóa banner SSH* **[\*]**

```text
clear ssh banner
```

## 4. Web (EDM)

> [!NOTE]
> **So với Cisco IOS-XE:** `web-server` + `https-only` ≈ `ip http secure-server` + `no ip http server`. Giao diện là EDM, không phải WebUI của Catalyst.

- `show web-server`: `WEB IP List Access Control: Enabled`; entry #1 `0.0.0.0/0.0.0.0` = cho phép tất cả (50 entry IPv4 + 10 IPv6, còn lại placeholder `255.255.255.255/32`).
- `edm ?` chỉ có `help-file-path`, `inactivity-timeout` (mặc định 900 s). EDM chạy theo `web-server`.
- Production: `https-only`, không telnet. EDM là giao diện riêng, không phải CLI qua web.
- *EDM Remote Access (Telnet / SNMP / Web / SSH, mỗi loại có Access + Use List) là điểm duy nhất ghim IP nguồn cho SNMP/SSH/Web.* **[\*]**

**Bật web server** (Global)

```text
web-server enable
```

**Tắt web server** (Global)

```text
web-server disable
```

**Chỉ nghe HTTPS** (Global)

```text
https-only
```

**Đổi port HTTP (1024–65535)** (Global)

```text
http-port 8080
```

**Đổi port HTTPS (1024–65535)** (Global)

```text
https-port 8443
```

**Xem certificate/reset SSL** (Global)

```text
ssl ?
```

**Xem trạng thái web server và danh sách IP được phép** (Privileged)

```text
show web-server
```

**Xem đường dẫn help file của EDM** (Privileged)

```text
show edm help-file-path
```

## 5. SNMP

> [!NOTE]
> **So với Cisco IOS-XE:** không có `snmp-server group`; user v3 gắn view trực tiếp. Chỉ MD5/SHA + AES/DES (Cisco mới hơn hỗ trợ SHA-2). Phải bật tường minh `snmp-server enable`; `bootstrap` xóa sạch SNMP, không có tương đương.

Máy mới: **SNMP Server: Disabled**.

**Bật SNMP** (Global)

```text
snmp-server enable
```

**Tắt SNMP** (Global)

```text
snmp-server disable
```

**Xem cấu hình SNMP (community hiển thị masked)** (Privileged)

```text
show snmp-server
```

**Xem user SNMPv3** (Privileged)

```text
show snmp-server user
```

**Xem trap host** (Privileged)

```text
show snmp-server host
```

### 5.1. SNMPv2c

`snmp-server community testro ro` inline trên máy báo `% Invalid input` — cần nhập chuỗi theo prompt ẩn. Production: không giữ community mặc định, chỉ dùng v2c trong mạng quản trị. Community tối đa 32 ký tự.

*Tạo community (`ro` hoặc `rw`)* **[\*]**

```text
snmp-server community <WORD> ro
```

*Tạo view giới hạn OID* **[\*]**

```text
snmp-server view <view> <OID>
```

*Đưa community về mặc định* **[\*]**

```text
default snmp-server community ro
```

*Xóa community* **[\*]**

```text
no snmp-server community <WORD>
```

### 5.2. SNMPv3

Hỗ trợ auth **MD5/SHA**, privacy **AES/DES** (tài liệu hãng chỉ ghi `md5`). **Tạo view trước**, nếu không `% View name does not exist`. Thứ tự: `user <name> → {md5|sha} → [{aes|des}] → {read-view|write-view|notify-view <view>}`. `engine-id` chỉ cần khi switch làm manager truy cập entity v3 khác. Engine ID local sinh theo serial.

**Bước 1 — Tạo view cho nhánh system** (Global)

```text
snmp-server view testview 1.3.6.1.2.1.1
```

**Bước 2 — Tạo user v3 SHA/AES, gắn read-view (hỏi passphrase qua prompt ẩn)** (Global)

```text
snmp-server user testv3 sha aes read-view testview
```

**Kiểm tra user v3** (Privileged)

```text
show snmp-server user
```

### 5.3. `snmp-server bootstrap`

⚠️ **Xóa toàn bộ cấu hình SNMP hiện có**, sinh lại 3 user (`initial`, `templateMD5`, `templateSHA`) + 2 view (`internet`, `restricted`), hỏi passphrase auth/privacy từng user. **Sau đó SNMP vẫn Disabled** → phải `snmp-server enable`. Password nhập lại không khớp → `% Passwords do not match`, script dừng. Chỉ `minimum-secure` đã chạy thành công; không dùng `very-secure` trên production khi chưa thử ở lab. Biến thể: `minimum-secure | semi-secure | very-secure`.

**Sinh cấu hình SNMPv3 tối thiểu (xóa SNMP cũ, hỏi `y/n` + passphrase)** (Global)

```text
snmp-server bootstrap minimum-secure
```

### 5.4. Trap / notification

*Gửi trap tới một receiver (v2c)* **[\*]**

```text
snmp-server host <A.B.C.D> v2c <community>
```

*Gửi inform v2c (timeout, retries tùy chọn)* **[\*]**

```text
snmp-server host <A.B.C.D> v2c <community> inform timeout 100 retries 3
```

*Gửi trap v3 (`auth` hoặc `no-auth`)* **[\*]**

```text
snmp-server host <A.B.C.D> v3 auth <user>
```

*Bật/tắt từng loại notification* **[\*]**

```text
snmp-server notification-control <type-or-OID> <ports>
```

*Lọc OID của trap* **[\*]**

```text
snmp-server notify-filter <profile> <OID>
```

### 5.5. Thông tin định danh

**Đặt tên hệ thống (sysName)** (Global)

```text
snmp-server name ERS3626-CORE1
```

**Đặt vị trí (sysLocation)** (Global)

```text
snmp-server location "Tầng 3 rack A2"
```

**Đặt liên hệ (sysContact)** (Global)

```text
snmp-server contact "NetOps"
```

## 6. Scenario: hardening khi nhận máy mới

Chọn **một** trong hai profile. Chạy từng bước, **không** paste nguyên khối lên máy đang quản trị từ xa.

### Profile A — SSH-only (khuyến nghị)

**1. Vào Global Configuration** (Privileged)

```text
configure terminal
```

**2. Đặt mật khẩu đường vào và hai tài khoản** (Global)

```text
cli password serial local
cli password telnet local
cli password read-write NetOps@2026#XY
cli password read-only Viewer@2026#XY
```

**3. Đặt thông tin định danh** (Global)

```text
snmp-server name ERS3626-CORE1
snmp-server location "Tầng 3 rack A2"
snmp-server contact "NetOps"
```

**4. Bật SSH rồi kiểm tra SSH vào được bằng tài khoản RW** *(`ssh` trần chưa có trong tài liệu 3600)* **[\*\*]** (Global)

```text
ssh
```

**5. Chuyển sang SSH-only (gõ `y`) — chỉ sau khi bước 4 đã SSH vào thành công** (Global)

```text
ssh secure
```

**6. Thoát và kiểm tra (kỳ vọng `Enabled: Secure`)** (Global → Privileged)

```text
end
show ssh global
```

**7. Lưu cấu hình** (Privileged)

```text
write memory
```

### Profile B — SSH + HTTPS (cần EDM)

*Không dùng `ssh secure` ở profile này vì nó tắt web.*

**1. Vào Global Configuration** (Privileged)

```text
configure terminal
```

**2. Đặt mật khẩu và tài khoản** (Global)

```text
cli password serial local
cli password telnet local
cli password read-write NetOps@2026#XY
cli password read-only Viewer@2026#XY
```

**3. Tắt telnet, bật web chỉ HTTPS, bật SSH** *(`ssh` trần: xem profile A)* **[\*\*]** (Global)

```text
telnet-access disable
web-server enable
https-only
ssh
```

**4. Tắt SNMP (hoặc bootstrap minimum-secure rồi `snmp-server enable`)** (Global)

```text
snmp-server disable
```

**5. Thoát và lưu cấu hình** (Global → Privileged)

```text
end
write memory
```

Sau cả hai profile, kiểm tra: `show cli password`, `show ssh global`, `show web-server`, `show snmp-server`.
