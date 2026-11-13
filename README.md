# Wand Patcher

> **A clean, client-side Pro unlock for the Windows Wand (WeMod) application.**

[![Status](https://img.shields.io/badge/status-validated%20v12.72.0-brightgreen)]()
[![Platform](https://img.shields.io/badge/platform-Windows-blue)]()
[![Python](https://img.shields.io/badge/python-3.x-yellow)]()

Wand Patcher modifies the local Wand/WeMod Electron bundle to bypass the client-side subscription gates that separate Free from Pro. It is built for users who want unrestricted local modding without a recurring subscription, while keeping the application's normal login flow and online connectivity intact.

> **Scope:** This is a **local resource patch only**. It does not create a real Pro entitlement on Wand's servers. Wand and WeMod are trademarks of their respective owners; this project is independent and claims no affiliation.

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

## ⚠️ Patch Status, Update Policy & the Wand Updater

**Validation status:** The patch has been validated against **Wand v12.72.0** and confirmed operational.

The patcher is engineered to remain compatible with future Wand releases by targeting structural JavaScript patterns rather than a fixed build number. It searches the extracted bundles for the `getUserAccount()` and `getBalance()` implementations that reference the `/v3/account` endpoint and rewrites them in place. If those code patterns change, the patcher aborts with an explicit "unrecognized endpoint implementations" error instead of writing a broken bundle.

Because Wand is actively developed, subsequent updates may alter the ASAR layout, the Electron integrity record, or the JavaScript patterns this patcher relies on, in ways that render the patch inoperable. If you encounter any error or unexpected behavior after a Wand update, please **open an issue on the GitHub repository** with your Wand version and a description of the failure. I will investigate and address it promptly.

**The primary risk to patch longevity is future Wand updates.** For this reason, the patcher includes an option to disable the local updater (see below). If the updater remains active, Wand may silently replace patched files with a clean, unpatched build.

### 🔧 Recommended: Disable the Wand Updater Through the Patch

Because future Wand updates are the main cause of patch breakage, the patcher provides a one-click toggle to **disable the local updater**. If the updater remains active, Wand may silently replace patched files with a clean, unpatched build.

**How the updater is disabled:**  
The patcher renames the updater binary from `Update.exe` to `Update.exe.disabled` inside the Wand installation root (`%LOCALAPPDATA%\Wand`). With the updater binary absent under its expected name, Wand's update flow cannot launch, and the patched resources remain in place. The toggle is reversible: pressing the same button renames `Update.exe.disabled` back to `Update.exe`.

**This is optional but strongly recommended** if you want the patch to survive routine Wand updates.

---

## 🗑️ Uninstalling Wand After Patching (Important)

Wand's uninstall flow depends on `Update.exe`. If you disabled the updater via the patch, the standard uninstall entry point will be missing.

**Before uninstalling Wand:**

1. Navigate to `%LOCALAPPDATA%\Wand\`.
2. Rename `Update.exe.disabled` back to **`Update.exe`**.
3. Proceed with the normal uninstall.

If you skip this step, the uninstaller may fail or leave residual files. **Restore the filename before attempting removal.**

---

## 🌐 Server-Side Features & the Custom Server Roadmap

The official **Wand Remote mobile application** (and any other feature that depends on Wand's backend validating an active subscription) **will not work** with a local patch alone. These features require a real server-side Pro entitlement.

**Can server-based features be supported?**  
Yes — but it requires infrastructure beyond a local file patch:

1. A **custom server** that emulates Wand's API subscription-validation endpoints closely enough for the desktop client to accept a Pro state.
2. Patching or proxying the **Wand mobile application** so it communicates with that custom server instead of Wand's production backend.

This involves ongoing hosting and maintenance costs. I can only commit to it if there is enough demand.

**If the number of requests reaches a sufficient level**, I can offer server-based Pro features as a **low-cost subscription — likely around $15 USD per year**.

**How to request it:**  
**Contact me directly** or **open a feature-request issue** on the repository. Include the specific server-side feature you need and how often you would use it. Demand is tracked from those requests.

---

## 🛠️ Technical Overview

Wand/WeMod is an Electron application. The patcher operates on the local application bundle located at `%LOCALAPPDATA%\Wand\app-<version>\`:

- **ASAR resource modification** — The patcher opens `resources\app.asar`, extracts all packed entries, merges the contents of `resources\app.asar.unpacked` on top, and scans every `*.js` file for the `/v3/account` endpoint. Files that reference it are rewritten so `getUserAccount()` and `getBalance()` inject `{"subscription": "Pro"}` into the account object before returning it. The bundle is then repacked with the original unpack rules preserved.
- **Integrity fuse handling** — Wand's `Wand.exe` embeds an ELECTRONASAR record of the form `{"file":"resources\\app.asar","alg":"SHA256","value":"<hash>"}`. The patcher computes the SHA-256 of the new ASAR header and rewrites the hash in place, so the client's own integrity check accepts the modified archive. If no embedded record exists in the target build, the EXE rewrite is skipped gracefully.
- **Installation discovery** — The patcher scans `%LOCALAPPDATA%\Wand` for folders named `app-<semver>` that contain both `resources\app.asar` and `Wand.exe`, then offers them in a version selector (newest first).
- **Background worker** — The extraction, patching, repacking, backup, and replacement steps run in a worker thread. The UI receives progress and log lines through a queue, so the interface stays responsive throughout.
- **Backup creation** — The original `Wand.exe` and `app.asar` are copied to a timestamped `Wand-Patcher\Backup (N)\` directory next to the patcher, along with a `patch-info.json` describing versions and hashes. The unpacked sidecar is not modified, so it is not backed up.
- **Updater control** — Optional toggle that renames `Update.exe` ↔ `Update.exe.disabled` in the Wand root to prevent auto-updates from reverting the patch.

The patcher does **not** inject into a running process, does **not** require a driver, and does **not** contact an external update or telemetry service. All patching is performed on local files.

---

## ❓ Q&A / Troubleshooting

**VirusTotal or Windows Defender flags the patcher as malware/trojan. Is this a false positive?**  
Yes. Unsigned patchers that modify Electron resources often trigger generic antivirus heuristics. The project is open-source; review the source or build it yourself if you are concerned. The patcher does not download files of unknown origin or transmit data externally.

**Does this application transfer any data to the Internet from my computer?**  
No. The patcher itself performs all operations locally. Wand remains an online application and will still communicate with its own servers for login and any server-side features you use, but the patcher adds no network behavior of its own.

**The patch stopped working after a Wand update.**  
This is expected if the updater was not disabled. Open an issue with your Wand version. For future use, enable the "Disable Update.exe" toggle in the patcher.

**Does the patch require admin rights?**  
No. All patched files live under `%LOCALAPPDATA%\Wand`, which is writable by the current user.

**What gets backed up, and where?**  
`Wand.exe` and `app.asar` are copied to `Wand-Patcher\Backup (N)\` alongside the patcher executable, together with `patch-info.json` (versions and hashes). The unpacked sidecar is untouched by the patch and is not backed up.

---

## 🔒 Safety & Transparency

- **Open-source** — Review the Python sources before running the executable.
- **No external downloads during patching** — The patcher does not fetch remote payloads to apply the patch.
- **Fail-safe pattern matching** — If the endpoint code patterns do not match, the patcher aborts rather than writing a partially patched bundle.
- **Backup and rollback** — Original `Wand.exe` and `app.asar` are backed up before replacement. However, backup creation does not guarantee recovery if a replacement or rollback fails. Do not delete the backup directory until you have verified that Wand runs correctly after patching.
- **Unsigned executable** — The distributed executable is unsigned. Generic antivirus heuristics may flag it. Build from source if you require a locally compiled binary.

These observations are transparency notes, not a security certification.

---

## 📄 License

This project is licensed under the MIT License.
See the [LICENSE](LICENSE) file for details.

Copyright (c) 2026 Ali Hosseini (The Great Hazard).

---

## 👤 Author

**AliHo55eini**  
[GitHub](https://github.com/AliHo55eini) · [The Great Hazard](https://thegreathazard.com)

---

## ☕ Support the Project

If you find this project useful, consider supporting its development through PayPal:

**[Support Me on PayPal →](https://paypal.me/AliHo55eini)**

Your support helps maintain the patcher, improve compatibility, and fund future updates.

Donations are entirely optional and greatly appreciated!
