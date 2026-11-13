# Troubleshooting & Uninstall

## 🗑️ Uninstalling Wand After Patching (Important)

Wand's uninstall flow depends on `Update.exe`. If you disabled the updater via the patch, the standard uninstall entry point will be missing.

**Before uninstalling Wand:**

1. Navigate to `%LOCALAPPDATA%\Wand\`.
2. Rename `Update.exe.disabled` back to **`Update.exe`**.
3. Proceed with the normal uninstall.

If you skip this step, the uninstaller may fail or leave residual files. **Restore the filename before attempting removal.**

---

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
