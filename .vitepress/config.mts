import { defineConfig } from "vitepress";
import { readFileSync } from "node:fs";

const emailIcon = readFileSync(new URL("../public/icons/email.svg", import.meta.url), "utf-8");

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "Yuuki's Documents",
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
    }
  },
  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { text: "Home", link: "/" },
      { text: "Documents", link: "/docs/" },
      { text: "CDU - UET", link: "/cdu-uet/" },
      { text: "Resources", link: "https://public.june8th.eu.org/" },
    ],
    logo: "/logo.png",
    sidebar: {
      "/docs/": [
        {
          text: "Introduction",
          base: "/docs/",
          link: "."
        },
        {
          text: "RustDesk",
          base: "/docs/",
          link: "rustdesk.md"
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
      "/cdu-uet/": [
        {
          text: "CDU - UET",
          base: "/cdu-uet/",
          link: ".",
          collapsed: true,
          items: [
            {
              text: "Resources",
              link: "https://public.june8th.eu.org/cdu/",
            },
          ]
        },
        {
          text: "Cisco",
          base: "/cdu-uet/cisco/",
          link: ".",
          collapsed: false,
          items: [
            {
              text: "Administration",
              link: "administration.md"
            },
            {
              text: "Firmware",
              link: "firmware.md"
            },
            {
              text: "Reset",
              link: "reset.md"
            }
          ],
        },
        {
          text: "Ruckus",
          base: "/cdu-uet/ruckus/",
          link: ".",
          collapsed: false,
          items: [
            {
              text: "Access Points",
              link: "ap.md",
            },
            {
              text: "ZoneDirector",
              link: "zd1200.md",
            },
          ],
        },
        {
          text: "Utilities",
          base: "/cdu-uet/utils/",
          collapsed: true,
          items: [
            {
              text: "iperf3",
              link: "iperf3.md",
            },
            {
              text: "nmap",
              link: "nmap.md",
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
      { icon: "github", link: "https://github.com/im-yuuki/meomeo-docs" },
      { icon: { svg: emailIcon }, link: "mailto:me@june8th.eu.org" },
    ],
    footer: {
      message: "Released under The Unlicense license.",
      copyright: "Copyright © 2026-present Yuuki"
    },
  },
  lastUpdated: true,
  markdown: {
    math: true,
    image: {
      lazyLoading: true,
    }
  },
});
