# Quản lý switch Cisco

::: danger
Nên dùng `secret` thay cho `password` trong mọi trường hợp.
Trong file cấu hình, `secret` được băm trong khi `password` lưu dưới dạng plaintext (hoặc chỉ obfuscate nhẹ nếu bật `service password-encryption`)
:::

## Đặt mật khẩu enable
Xác thực người dùng trước khi leo thang đặc quyền ở kết nối console vật lý.

```sh
Switch(config)# enable secret <...>
```

## Tạo người đùng và truy cập ssh, webui
Khi đã có thể kết nối layer 3 tới switch, có thể truy cập và cấu hình switch từ xa.

### Tạo local user
```sh
Switch(config)# username cisco privilege 15 password <...>
```

### Mở dịch vụ http(s)
```sh
Switch(config)# ip http server
Switch(config)# ip http secure-server
Switch(config)# ip http authentication local
```

### Mở ssh
```sh
```

