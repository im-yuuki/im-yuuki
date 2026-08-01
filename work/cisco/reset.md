# Reset Switch Cisco
Đặt lại cấu hình switch Cisco về trạng thái mặc định nhà sản xuất.

:::warning
Áp dụng cho các dòng switch Cisco Catalyst 3850, 9300 series.

Có thể áp dụng cho cả các dòng switch hay thiết bị khác của Cisco, tuy nhiên mình chưa thử nghiệm.
:::

## Truy cập enabled console

> Về bản chất cấu hình của switch được lưu trữ dưới dạng tệp `startup-config` nằm trên NVRAM của thiết bị.
>
> Khi khởi động, hệ điều hành sẽ tải `startup-config` vào `running-config` trên RAM.
> Mọi sửa đổi cấu hình sẽ được ghi vào `running-config`. Để lưu lại cấu hình hiện tại của thiết bị qua những lần khởi động lại, cần sao chép nội dung `running-config` vào `startup-config` bằng lệnh `copy running-config startup-config` (hoặc `write memory` tuỳ phiên bản firmware có hỗ trợ)

Để đặt lại cấu hình thiết bị, chỉ cần đơn giản là xoá nội dung trong `startup-config` đi, sau đó khởi động lại thiết bị!
```sh
Switch# write erase
Switch# reload
```

:::tip
Cấu hình VLAN của switch không lưu vào config trên mà được lưu ở `flash:vlan.dat`. Nếu muốn đặt lại cả cấu hình này, dùng lệnh `delete flash:vlan.dat` trước khi `reload`.
:::

## Nếu không truy cập được console (quên mật khẩu enable, ...)

Firmware switch Cisco có một env cho phép bỏ qua nạp `startup-config` vào `running-config` khi hệ điều hành khởi động, sau đó switch sẽ chạy với cấu hình mặc định.

Thao tác để set env này như sau:

1. Kết nối serial console với thiết bị, kiểm tra console sau đó ngắt nguồn switch.

2. Cấp nguồn lại, sau đó nhấn giữ nút `MODE` mặt trước switch hoặc `Ctrl + C` trên console để interrupt quá trình boot, đưa thiết bị vào `ROMMON` mode.

3. Khi vào được shell của `ROMMON` mode, dùng các lệnh sau:
```sh
switch: set SWITCH_IGNORE_STARTUP_CFG=1
switch: boot
```

4. Switch sẽ (tạm thời) khởi động lại ở trạng thái cấu hình mặc định. Lúc này có thể reset như hướng dẫn trên để xoá cấu hình trong NVRAM, hoặc cấu hình mới rồi ghi đè `startup-config`.

5. (QUAN TRỌNG) Trước khi reboot switch, hãy unset env trên để tránh việc switch khởi động lại vẫn không tải cấu hình vào RAM:
```sh
Switch# no system ignore startupconfig switch all
```
