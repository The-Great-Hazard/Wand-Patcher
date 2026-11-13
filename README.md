# Wand Patcher

> **A clean, client-side Pro unlock for the Windows Wand (WeMod) application.**

[![Status](https://img.shields.io/badge/status-validated%20v12.72.0-brightgreen)]()
[![Platform](https://img.shields.io/badge/platform-Windows-blue)]()
[![Python](https://img.shields.io/badge/python-3.x-yellow)]()

Wand Patcher modifies the local Wand/WeMod Electron bundle to bypass the client-side subscription gates that separate Free from Pro. It is built for users who want unrestricted local modding without a recurring subscription, while keeping the application's normal login flow and online connectivity intact.

> **Scope:** This is a **local resource patch only**. It does not create a real Pro entitlement on Wand's servers. Wand and WeMod are trademarks of their respective owners; this project is independent and claims no affiliation.

---

---

## ⚡ What You Get

The patcher overrides the `subscription` field in Wand's local account response to `"Pro"`. Any feature whose access is decided by that local flag is unlocked after you log in with your own Wand account.

| Feature | Status |
| :--- | :--- |
| **Unlimited modding time** (removes the 2-hour daily Free limit) | ✅ |
| **Saved Mods** (customizations persist between sessions) | ✅ |
| **Mod Collections** (group and switch custom setups) | ✅ |
| **Pinned / Favourite Mods** | ✅ |
| **Precision Mods** (exact value entry, slider fine-tuning) | ✅ |
| **AI Game Guides** (local access) | ✅ |
| **Ad-free interface** | ✅ |
| **Official Wand Remote mobile app** (iOS/Android) | ❌ Server-side only |
| **Any feature requiring a real Pro API entitlement** | ❌ Server-side only |

**You must log in to Wand with your own account** for the patch to take effect. This project does not bypass authentication — it changes how the client handles the subscription state locally.

---

---

## 📦 What This Patch Does (and Doesn't)

**It does:**
- Patch the ASAR bundle inside your local Wand installation.
- Replace the client-side `getUserAccount()` / `getBalance()` response logic so the account object reports `subscription: "Pro"`.
- Account for Electron's embedded ELECTRONASAR integrity record by rewriting the SHA-256 hash inside `Wand.exe` to match the new ASAR header.
- Back up `Wand.exe` and `app.asar` before replacement.
- Optionally disable the local updater to prevent future Wand updates from overwriting the patch.

**It does not:**
- Contact an external licensing server.
- Inject into a running Wand process.
- Install a driver or background service.
- Modify `app.asar.unpacked` — the sidecar directory is read during patching but is not written to in the installation.
- Grant server-validated Pro entitlements (see *Server-Side Features* below).

---

---

## ⚠️ Patch Status & Compatibility

**Validation status:** The patch has been validated against **Wand v12.72.0** and confirmed operational.

Because Wand is actively developed, subsequent updates may alter the ASAR layout, the Electron integrity record, or the JavaScript patterns this patcher relies on, in ways that render the patch inoperable. If you encounter any error or unexpected behavior after a Wand update, please **open an issue on the GitHub repository** with your Wand version and a description of the failure. I will investigate and address it promptly.

For details about update behavior and the updater toggle, see [Usage](docs/USAGE.md) and [Architecture](docs/ARCHITECTURE.md).

---

## 📥 Download & Building

For a packaged executable, see the repository's **Releases** page (when a release has been published).

To build from source on Windows, see [Building from Source](docs/BUILDING.md).

For updater management, see [Usage](docs/USAGE.md). For uninstall instructions and questions, see [Troubleshooting](docs/TROUBLESHOOTING.md).

---

## 📚 Documentation

- [Technical Architecture](docs/ARCHITECTURE.md)
- [Usage & Updater](docs/USAGE.md)
- [Troubleshooting & Uninstall](docs/TROUBLESHOOTING.md)
- [Building from Source](docs/BUILDING.md)
- [Server-Side Features & Roadmap](ROADMAP.md)

---

## 🔒 Safety & Transparency

- **Open-source** — Review the Python sources before running the executable.
- **No external downloads during patching** — The patcher does not fetch remote payloads to apply the patch.
- **Fail-safe pattern matching** — If the endpoint code patterns do not match, the patcher aborts rather than writing a partially patched bundle.
- **Backup and rollback** — Original `Wand.exe` and `app.asar` are backed up before replacement. However, backup creation does not guarantee recovery if a replacement or rollback fails. Do not delete the backup directory until you have verified that Wand runs correctly after patching.
- **Unsigned executable** — The distributed executable is unsigned. Generic antivirus heuristics may flag it. Build from source if you require a locally compiled binary.

These observations are transparency notes, not a security certification.

---

---

## 📄 License

This project is licensed under the MIT License.
See the [LICENSE](LICENSE) file for details.

Copyright (c) 2026 Ali Hosseini (The Great Hazard).

---

---

## 👤 Author

**AliHo55eini**  
[GitHub](https://github.com/AliHo55eini) · [The Great Hazard](https://thegreathazard.com)

---

---

## ☕ Support the Project

If you find this project useful, consider supporting its development through PayPal:

**[Support Me on PayPal →](https://paypal.me/AliHo55eini)**

Your support helps maintain the patcher, improve compatibility, and fund future updates.

Donations are entirely optional and greatly appreciated!
