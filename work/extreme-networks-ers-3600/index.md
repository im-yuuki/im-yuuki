# Extreme Networks ERS 3600 Series — Hướng dẫn cấu hình

Tài liệu nội bộ để triển khai switch **ERS 3600 Series** (SW **v6.4.2.007**, máy mẫu **ERS 3626GTS-PWR+**). Nội dung lấy từ kiểm chứng trên thiết bị thật; khi khác tài liệu hãng thì **theo thiết bị thật**.

> Các dòng ERS khác (3500/4800/5900…) có thể tham khảo nhưng **không đảm bảo** cú pháp giống.

## Mục lục

| # | Chương | Nội dung chính |
| --- | --- | --- |
| 00 | [Tổng quan thiết bị](00-tong-quan-thiet-bi.md) | So sánh 3 model, giới hạn, bản đồ cổng, khác biệt so với brand khác |
| 01 | [Làm việc với hệ thống](01-lam-viec-voi-he-thong.md) | Console, CLI mode, show thông tin, hostname, xem/lưu/backup config, reboot/reset |
| 02 | [Quản lý interface](02-quan-ly-interface.md) | Đánh số cổng, status, transceiver, MAC, shutdown, tên cổng, MLT/LACP, PoE |
| 03 | [L2 switching](03-l2-switching.md) | VLAN, configcontrol, access/trunk, STP, DHCP snooping |
| 04 | [L3 routing cơ bản](04-l3-routing-co-ban.md) | Interface VLAN, static route, RIP (không có OSPF/VRRP/VRF) |
| 05 | [Bảo mật, dịch vụ, quản trị từ xa](05-bao-mat-dich-vu-quan-tri-tu-xa.md) | Tài khoản/mật khẩu, telnet, SSH, web, SNMP, hardening |

## Tài liệu tham chiếu

- `/pdfs/9036468-00_CLIRefERS3600_6.4_CRG.pdf` — CLI Commands Reference 6.4: sự tồn tại, cú pháp, mode của lệnh đáng tin; dòng mô tả một câu hay bị copy nhầm.
- `/pdfs/9036478-00_ConfigSysERS3600_6.4_CG.pdf` — Configuring Systems 6.4.
