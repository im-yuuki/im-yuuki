import { defineConfig } from "vitepress";

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "im-yuuki.docs",
  description: "various documentations for what I'm working on!",
  head: [["link", { rel: "icon", href: "/favicon.ico" }]],
  locales: {
    root: {
      label: "English",
      lang: "en-US",
    },
    vi: {
      label: "Tiếng Việt",
      lang: "vi-VN",
    },
  },
  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { text: "Home", link: "/" },
      { text: "About me", link: "/README.md" },
      { text: "Documents", link: "/docs/" },
      { text: "Work", link: "/work/" },
      {
        text: "Resources",
        items: [
          {
            text: "Files",
            link: "https://public.june8th.eu.org/",
          },
          {
            text: "Email",
            link: "https://mail.june8th.eu.org/",
          },
        ],
      },
    ],
    logo: "/logo.png",
    sidebar: {
      "/docs/": [
        {
          text: "Introduction",
          base: "/docs/",
          link: ".",
        },
        {
          text: "RustDesk",
          base: "/docs/",
          link: "rustdesk.md",
        },
        {
          text: "Building Chromium for iOS",
          base: "/docs/",
          link: "chromium-ios-build-guide.md",
        },
        {
          text: "Docker",
          base: "/docs/docker/",
          collapsed: false,
          items: [
            {
              text: "Install on Debian-based Linux",
              link: "install-debian.md",
            },
            {
              text: "Install on Red Hat-based Linux",
              link: "install-redhat.md",
            },
          ],
        },
      ],
      "/work/": [
        {
          text: "Work",
          base: "/work/",
          link: ".",
          items: [
            {
              text: "Resources",
              link: "https://public.june8th.eu.org/cdu/",
            },
          ],
        },
        {
          text: "Cisco",
          base: "/work/cisco/",
          collapsed: true,
          items: [
            {
              text: "Quản trị",
              link: "administration.md",
            },
            {
              text: "Reset",
              link: "reset.md",
            },
          ],
        },
        {
          text: "Extreme Networks ERS 3600 Series",
          base: "/work/extreme-networks-ers-3600/",
          link: ".",
          collapsed: true,
          items: [
            {
              text: "00: Tổng quan thiết bị",
              link: "00-tong-quan-thiet-bi.md",
            },
            {
              text: "01: Làm việc với hệ thống",
              link: "01-lam-viec-voi-he-thong.md",
            },
            {
              text: "02: Quản lý Interfaces",
              link: "02-quan-ly-interfaces.md",
            },
            {
              text: "03: Layer 2 Switching",
              link: "03-l2-switching.md",
            },
            {
              text: "04: Layer 3 Routing (cơ bản)",
              link: "04-l3-routing-co-ban.md",
            },
            {
              text: "05: Bảo mật, dịch vụ và quản trị từ xa",
              link: "05-bao-mat-dich-vu-quan-tri-tu-xa.md",
            },
          ],
        },
        {
          text: "Proxmox",
          base: "/work/proxmox/",
          collapsed: true,
          items: [
            {
              text: "iSCSI Boot",
              link: "proxmox-iscsiboot.md",
            },
          ],
        },
        {
          text: "Ruckus",
          base: "/work/ruckus/",
          collapsed: true,
          items: [
            {
              text: "ZoneDirector",
              link: "zonedirector.md",
            },
          ],
        },
      ],
    },
    search: {
      provider: "local",
    },
    socialLinks: [
      { icon: "facebook", link: "https://www.facebook.com/june8th.dan" },
      { icon: "github", link: "https://github.com/im-yuuki/im-yuuki" },
    ],
    footer: {
      message: "Released under MIT license.",
      copyright: "Copyright © 2026-present Yuuki",
    },
  },
  lastUpdated: true,
  markdown: {
    math: true,
    image: {
      lazyLoad: true,
    },
  },
});
