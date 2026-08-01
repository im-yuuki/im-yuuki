---
# https://vitepress.dev/reference/default-theme-home-page
layout: home

hero:
  name: "Hello!"
  text: "LunaDocs"
  tagline: "welcome to my home on the internet!"
  image:
    src: /logo.png
  actions:
    - theme: brand
      text: About me
      link: /README.md
    - theme: alt
      text: Documents
      link: /docs/
    - theme: alt
      text: Public Files
      link: https://public.june8th.eu.org/

features:
  - icon: 📚
    title: Documents
    details: various guides about things I'm worked on
  - icon: 📝
    title: Presets
    details: configuration files for reference
  - icon: ✨
    title: Experience
    details: sharing how I resolve problems during work
---

<br />

# Contributors

<script setup>
import { VPTeamMembers } from "vitepress/theme"

const members = [
  {
    avatar: "https://www.github.com/im-yuuki.png",
    name: "Yuuki",
    title: "Owner",
    links: [
      { icon: "facebook", link: "https://www.facebook.com/june8th.dan" },
      { icon: "github", link: "https://github.com/im-yuuki" },
    ],
  },
]
</script>

<VPTeamMembers size="small" :members />
