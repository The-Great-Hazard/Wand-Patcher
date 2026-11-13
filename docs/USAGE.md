# Usage & Updater

### 🔧 Recommended: Disable the Wand Updater Through the Patch

Because future Wand updates are the main cause of patch breakage, the patcher provides a one-click toggle to **disable the local updater**. If the updater remains active, Wand may silently replace patched files with a clean, unpatched build.

**How the updater is disabled:**  
The patcher renames the updater binary from `Update.exe` to `Update.exe.disabled` inside the Wand installation root (`%LOCALAPPDATA%\Wand`). With the updater binary absent under its expected name, Wand's update flow cannot launch, and the patched resources remain in place. The toggle is reversible: pressing the same button renames `Update.exe.disabled` back to `Update.exe`.

**This is optional but strongly recommended** if you want the patch to survive routine Wand updates.

---
