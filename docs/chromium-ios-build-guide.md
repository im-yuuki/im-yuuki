# Building Chromium for iOS — On-Device, Release Build

Source: [chromium/docs/ios/build_instructions.md](https://github.com/chromium/chromium/blob/main/docs/ios/build_instructions.md)

This is a condensed guide for building Chromium and running it on your own iPhone using a **free (Personal Team) Apple Developer account**, in a **Release** configuration, with **Blink enabled** and no test targets. Google-internal instructions (Reclient, `go/` links) are stripped out since they don't apply here.

## The approach: build unsigned, sign/install as a separate step

One clarification up front: **stock iOS (no jailbreak) always requires some valid code signature to run a binary on real hardware** — there's no way around that entirely. What you *can* do is decouple signing from the Xcode/ninja build itself: build a completely unsigned `.app`, package it into a `.ipa`, and hand that off to a sideloading tool (Sideloadly or AltStore) that does the signing-with-your-free-Apple-ID and installation as a separate, later step. That sidesteps the whole "hunt down and patch Chromium's GN entitlements template" problem from before — if you never ask for App Groups in the signed output, there's nothing to strip.

Trade-offs of the free-account route either way:

- No Share/Widget/Credential/Intents extensions (they need the App Groups container a free account can't get).
- Whatever signs the final `.ipa` (Sideloadly/AltStore) issues a provisioning profile that expires after **7 days** — the app stops launching after that and needs re-sideloading.
- You're capped at 3 free-signed apps on the device at once.

---

## 1. System Requirements

- A 64-bit Mac able to run Xcode 26.0+ (still needed to build, even though signing happens outside Xcode).
- The iOS Simulator component installed via Xcode Settings → Components (required for the build regardless of target).
- A physical iPhone, plus [Sideloadly](https://sideloadly.io/) or [AltStore](https://altstore.io/) installed on your Mac for the sign+install step.

---

## 2. Get the Source

```bash
# depot_tools (one-time)
git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git
echo 'export PATH="$HOME/depot_tools:$HOME/depot_tools/python-bin:$PATH"' >> ~/.zprofile
source ~/.zprofile
gclient status   # forces depot_tools to self-update

# Fetch Chromium (30 min+; --no-history saves a lot of that)
mkdir chromium && cd chromium
fetch ios --no-history
cd src
```

---

## 3. Configure and Build — Unsigned, Release, Device

```bash
python3 ios/build/tools/setup-gn.py
```

This creates `out/Release-iphoneos` (among other configs) and the Xcode project `out/build/all.xcodeproj` (you won't need to open it — it's just a build artifact here).

Turn code signing off entirely so the build doesn't need an identity, a provisioning profile, or App Groups at all, and turn Blink on. Add this to `.setup-gn` (in `src`'s parent directory, or `$HOME/.setup-gn`):

```ini
[gn_args]
ios_enable_code_signing = false
use_blink = true
ios_deployment_target = "18.0"
ios_content_shell_bundle_identifier = "org.eu.june8th.contentshell"
ios_chromium_bundle_id = "org.eu.june8th.chrome"
```

(`ios_deployment_target` sets the minimum iOS version the build targets — without it, Xcode 26's toolchain defaults to something much newer than your actual device and links against frameworks, like `_LocationEssentials`, that don't exist on your OS yet. `17.0` gives some margin below your 18.7.9 — bump it up if you ever need an API that's only in later iOS versions.)

(`use_blink` requires those two bundle-identifier args to be set to *something* — Chromium ships them as literal `REPLACE_YOUR_BUNDLE_IDENTIFIER_HERE` placeholders otherwise, so swap in your own prefix.)

Only `content_shell` and `chrome` support Blink — build whichever (or both) you want to run:

```bash
autoninja -C out/Release-iphoneos content_shell chrome
```

This produces **unsigned** `.app` bundles: `out/Release-iphoneos/content_shell.app` and `out/Release-iphoneos/Chromium.app`. Since nothing gets signed at this stage, there's no entitlements/provisioning-profile error to fight with — that's now Sideloadly's/AltStore's problem, not GN's.

One thing worth knowing going in, purely so the result matches what you expect: Blink's JS engine (V8) normally leans on JIT compilation for speed, and JIT on iOS is an Apple-gated entitlement outside of WebKit's own process — so however you're handling that on your end, expect this to behave differently (likely slower on JS-heavy pages) than Chromium's Blink on desktop or Android until that's sorted. `content_shell` is the more minimal, better-tested Blink target if `chrome` gives you trouble.

**Re-run `setup-gn.py`** any time a `BUILD.gn` file changes (yours or from `gclient sync`) — otherwise the generated project's file list goes stale.

---

## 4. Package the .app into a .ipa

An `.ipa` is just a zip with a specific internal layout: a top-level `Payload/` folder containing the `.app`. If you built `chrome`, it bundles its extensions (Share Extension, Widget, etc.) as `PlugIns/` inside the app by default — strip those out now, since they need the App Groups container you don't have and will otherwise make signing fail later. `content_shell` doesn't have this issue.

```bash
cd out/Release-iphoneos

# for Chromium.app:
rm -rf Chromium.app/PlugIns          # drop the extensions that need App Groups
mkdir -p Payload && cp -R Chromium.app Payload/
zip -r -y Chromium.ipa Payload
rm -rf Payload

# or for content_shell.app:
mkdir -p Payload && cp -R content_shell.app Payload/
zip -r -y content_shell.ipa Payload
rm -rf Payload
```

You now have an unsigned, extension-free `.ipa` ready to hand to a sideloading tool.

(If you'd rather not fuss with `PlugIns` by hand, Sideloadly has a **"Remove App Extensions"** checkbox that does the same thing during the sideload step below — either works.)

---

## 5. Sign and Install via Sideloadly (or AltStore)

This is the step that actually needs your free Apple ID, and it happens entirely outside the Chromium build:

1. Open **Sideloadly**, plug in your iPhone (or set it up over Wi-Fi).
2. Drag your `.ipa` (`Chromium.ipa` or `content_shell.ipa`) into Sideloadly.
3. Enter your Apple ID (this is the free/Personal Team sign-in — no paid account needed).
4. If you skipped the `PlugIns` removal for `Chromium.ipa`, tick **"Remove App Extensions"**.
5. Hit **Start**. Sideloadly registers an App ID under your account, builds a matching provisioning profile, re-signs the `.ipa`, and installs it.

AltStore works the same way conceptually (via its AltServer companion app) if you'd rather use that instead.

On first launch, trust the developer certificate on the phone if prompted: **Settings → General → VPN & Device Management → [your Apple ID] → Trust**.

Remember: the install expires after **7 days** (a free-account limit enforced by Apple, not by either tool) — Sideloadly re-signs on demand, AltStore can auto-refresh in the background if AltServer stays running.

---

## 6. Keeping Your Checkout Up to Date

```bash
git rebase-update
gclient sync
```

`git rebase-update` pulls latest `main` and rebases your local branches on it. `gclient sync` updates dependencies to match and re-runs `setup-gn.py` for you.

---

## 7. Troubleshooting

### Xcode license not accepted

```bash
xcodebuild -license          # accept for your own user
sudo xcodebuild -license     # accept for all users on the machine
```

### Switched Xcode versions

1. Launch the new Xcode.app once (lets it install CLI components).
2. Reboot (stale daemons like `actool` otherwise cause cryptic failures).
3. Re-run `gn gen` (or `gclient runhooks` for a downstream checkout) so the build files pick up the new SDK paths.

### Slow `git status` in this large checkout

```bash
sudo sysctl kern.maxvnodes=$((512*1024))
echo kern.maxvnodes=$((512*1024)) | sudo tee -a /etc/sysctl.conf
git config core.untrackedCache true
git config core.fsmonitor true   # needs git >= 2.43
```

### Sideloadly says the .ipa is invalid / won't sign

Double-check the zip structure — it must be `Payload/Chromium.app` at the top level of the archive, not `Chromium.app` directly or nested another level deep. Re-zip if `unzip -l Chromium.ipa` doesn't show that exact layout.

---

*Condensed from the official Chromium docs plus general knowledge of iOS sideloading tools; the free-account limitations (App Groups, 7-day expiry, 3-app cap) reflect current Apple policy as of mid-2026 — worth a quick check against [developer.apple.com/support/compare-memberships](https://developer.apple.com/support/compare-memberships) and the tool's own docs if it's been a while.*
