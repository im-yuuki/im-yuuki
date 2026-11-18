# 04 — L3 routing cơ bản

ERS 3600 là access switch L3 nhẹ: **static route + RIP**. **Không có OSPF, BGP, VRRP, VRF** (một bảng route global duy nhất; muốn FHRP hoặc tách bảng route phải dùng thiết bị khác). Routing toàn cục **tắt mặc định**. Ký hiệu `[*]`/`[**]` và quy ước code block: xem chương 00.

## 1. Giới hạn

| Hạng mục | Giá trị |
| --- | --- |
| IP interface (L3 VLAN) | 32 |
| IP route | 256 (32 static) |
| ARP | 512 (256 static) |
| RIP | 16 interface / 256 route |
| Route policy | 64 |

## 2. Hai loại IP — đừng nhầm

| | Lệnh | Vai trò |
| --- | --- | --- |
| IP quản trị switch/stack | `ip address` + `ip default-gateway` (Global) | IP để SSH/SNMP/EDM vào chính switch |
| IP VLAN interface | `interface vlan <id>` → `ip address` | Gateway phục vụ client, routing giữa VLAN |

> [!NOTE]
> **So với Cisco IOS-XE:** giống switch Cisco L2 — `ip default-gateway` bị bỏ qua khi bật `ip routing`; IP quản trị là một địa chỉ riêng của switch, không gắn VLAN interface như Cisco (SVI quản trị).

`ip default-gateway` chỉ có ý nghĩa khi switch **không** routing IP. *Khi bật routing, dùng default route (§4).* **[\*]**

*Đặt IP quản trị cho switch* **[\*]**

```text
ip address switch 10.0.0.5 netmask 255.255.255.0
```

*Đặt default gateway của switch (khi không routing)* **[\*]**

```text
ip default-gateway 10.0.0.1
```

**Xem IP quản trị** (Privileged)

```text
show ip address
```

## 3. Routing giữa các VLAN

> [!IMPORTANT]
> **So với Cisco IOS-XE:** phải bật `ip routing` ở **cả** global và từng `interface vlan` (Cisco chỉ cần global); mask dotted bắt buộc, `interface vlan` không tự tạo VLAN. Hiện tượng "route chỉ lên khi có cổng link-up" giống autostate của SVI Cisco — *nhiều khả năng cùng nguyên nhân, chưa xác nhận.* **[\*\*]**

- VLAN phải **tồn tại trước** (`% VLAN X does not exist`).
- Dotted mask bắt buộc (`/24` bị từ chối).
- *L3 VLAN có thể chỉ xuất hiện trong `show ip route` khi có ít nhất một cổng link-up trong VLAN. Quan sát trên lab: không có cổng up thì `192.168.10.1` đặt được nhưng `ping` báo `Host is not reachable`; chưa xác nhận điều kiện chính xác — kiểm tra khi triển khai.* **[\*]**
- *Thứ tự `ip routing` global trước hay sau `interface vlan` chưa kiểm chứng ngược.* **[\*]**

**Bật routing toàn cục** (Global)

```text
ip routing
```

**Đặt IP cho VLAN 10 và bật routing trên VLAN** (Global → VLAN Interface)

```text
interface vlan 10
ip address 192.168.10.1 255.255.255.0
ip routing
exit
```

**Xem trạng thái routing toàn cục** (Privileged)

```text
show ip routing
```

**Xem bảng route** (Privileged)

```text
show ip route
```

**Tắt routing toàn cục** (Global)

```text
no ip routing
```

*Bật Proxy ARP trên VLAN* **[\*]**

```text
interface vlan 10
ip arp-proxy enable
exit
```

*Bật DHCP relay trên VLAN* **[\*]**

```text
interface vlan 10
ip dhcp-relay
exit
```

## 4. Static route

> [!WARNING]
> **So với Cisco IOS-XE:** `ip route` **bắt buộc có cost** (Cisco: admin distance tùy chọn), tối đa 32 static route. Chỉ có RIP — không OSPF/EIGRP/BGP, không HSRP/VRRP, không VRF; thiết kế cần các tính năng này phải dùng thiết bị khác.

- Thiếu cost → `% Incomplete command`. `enable`/`disable`/`weight` chỉ áp lên route **đã tồn tại** (`% Cannot Find Entry to Modify`).
- Route không hiện trong `show ip route` nếu next-hop không resolve được (cùng điều kiện L3 VLAN ở §3).

**Default route qua next-hop 192.168.20.254, cost 1** (Global)

```text
ip route 0.0.0.0 0.0.0.0 192.168.20.254 1
```

**Route tới 10.10.0.0/16** (Global)

```text
ip route 10.10.0.0 255.255.0.0 192.168.20.254 1
```

**Đổi cost route đã có** (Global)

```text
ip route 10.10.0.0 255.255.0.0 192.168.20.254 weight 5
```

**Tạm vô hiệu hóa route đã có (hoặc `enable`)** (Global)

```text
ip route 10.10.0.0 255.255.0.0 192.168.20.254 disable
```

*Xem riêng route tĩnh* **[\*]**

```text
show ip route static
```

*Xem route theo địa chỉ đích* **[\*]**

```text
show ip route 10.10.0.0
```

*Xem tóm tắt bảng route* **[\*]**

```text
show ip route summary
```

*Route-policy: `route-map` và `ip prefix-list <name> A.B.C.D/<len> [ge n] [le n]`, dùng cho RIP `in-policy`/`out-policy`.* **[\*]**

## 5. RIP

Chỉ dùng khi bắt buộc; static route đủ cho phần lớn mạng nhỏ.

Mặc định `show ip rip`: Update 30 s, Timeout 180 s, HoldDown 120 s, Default Import Metric 8. Mặc định `show ip rip interface`: send `rip1Compatible`, receive `rip1OrRip2`.

**Bật RIP toàn cục** (Global)

```text
router rip enable
```

**Bật RIP trên VLAN 10** (Global → VLAN Interface)

```text
interface vlan 10
ip rip enable
exit
```

**Xem cấu hình RIP toàn cục** (Privileged)

```text
show ip rip
```

**Xem RIP theo interface** (Privileged)

```text
show ip rip interface
```

**Tắt RIP toàn cục** (Global)

```text
no router rip enable
```

| Lệnh per-VLAN (VLAN Interface) | Ghi chú |
| --- | --- |
| *`ip rip receive version {rip1\|rip1orrip2\|rip2}`* **[\*]** | Phiên bản nhận |
| *`ip rip send version {notsend\|rip1\|rip1comp\|rip2}`* **[\*]** | Phiên bản gửi |
| *`ip rip cost <n>`, `holddown`, `timeout`, `poison`, `triggered`* **[\*]** | Tinh chỉnh |
| *`ip rip default-supply / default-listen / supply / listen`* **[\*]** | Quảng bá/nhận default route |
| *`ip rip in-policy / out-policy <route-map>`* **[\*]** | Lọc route |

*Kích RIP update thủ công trên VLAN 10* **[\*]** (Privileged)

```text
manualtrigger ip rip interface vlan 10
```

*Xem thống kê RIP* **[\*]**

```text
show ip rip stats
```

## 6. Scenario: 2 VLAN + uplink ra core

VLAN 10 (users, cổng 5–10), VLAN 20 (servers, cổng 21–24), uplink cổng 25 PVID 20 tag-all, core gateway `192.168.20.254`.

**1. Cho phép đổi membership** (Global)

```text
vlan configcontrol flexible
```

**2a. Tạo VLAN users** (Global)

```text
vlan create 10 name USERS type port
```

**2b. Tạo VLAN servers** (Global)

```text
vlan create 20 name SERVERS type port
```

**3. Gán cổng vào VLAN, gỡ khỏi VLAN 1, đặt PVID/tagging** (Global)

```text
vlan members add 10 5-10
vlan members add 20 21-25
vlan members remove 1 5-10,21-25
vlan ports 5-10 tagging untagPvidOnly pvid 10
vlan ports 21-24 tagging untagPvidOnly pvid 20
vlan ports 25 tagging tagAll pvid 20
```

**4. Bật routing và đặt IP gateway cho từng VLAN** (Global)

```text
ip routing
interface vlan 10
ip address 192.168.10.1 255.255.255.0
ip routing
exit
interface vlan 20
ip address 192.168.20.1 255.255.255.0
ip routing
exit
```

**5. Default route về core** (Global)

```text
ip route 0.0.0.0 0.0.0.0 192.168.20.254 1
```

**6. Thoát và lưu cấu hình** (Global → Privileged)

```text
end
write memory
```

**Kiểm tra: routing toàn cục** (Privileged)

```text
show ip routing
```

**Kiểm tra: bảng route** (Privileged)

```text
show ip route
```

**Kiểm tra: cổng đã vào đúng VLAN** (Privileged)

```text
show interfaces 5 config
```

**Kiểm tra: thông tới gateway core** (Privileged)

```text
ping 192.168.20.254
```

⚠️ *Cần ít nhất một cổng up trong mỗi VLAN để thấy route connected (xem §3). Chương này chưa được chốt cho production cho đến khi điều kiện đó và việc gỡ `ip routing`/`interface vlan` trả cấu hình về sạch được kiểm chứng trên lab có cổng up.* **[\*]**
