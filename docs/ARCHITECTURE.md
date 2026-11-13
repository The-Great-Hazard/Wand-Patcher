# Architecture

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

---

## Compatibility & Update Policy

**Validation status:** The patch has been validated against **Wand v12.72.0** and confirmed operational.

The patcher is engineered to remain compatible with future Wand releases by targeting structural JavaScript patterns rather than a fixed build number. It searches the extracted bundles for the `getUserAccount()` and `getBalance()` implementations that reference the `/v3/account` endpoint and rewrites them in place. If those code patterns change, the patcher aborts with an explicit "unrecognized endpoint implementations" error instead of writing a broken bundle.

Because Wand is actively developed, subsequent updates may alter the ASAR layout, the Electron integrity record, or the JavaScript patterns this patcher relies on, in ways that render the patch inoperable. If you encounter any error or unexpected behavior after a Wand update, please **open an issue on the GitHub repository** with your Wand version and a description of the failure. I will investigate and address it promptly.

**The primary risk to patch longevity is future Wand updates.** For this reason, the patcher includes an option to disable the local updater (see below). If the updater remains active, Wand may silently replace patched files with a clean, unpatched build.
