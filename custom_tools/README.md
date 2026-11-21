# AetherVault Studio — Custom Tools Plugin Folder

Drop any `.py` file here (or let the AI create & test one via `vault.create_tool(name, code, test_code)`).
All public functions (not starting with `_`) are hot-reloaded into `vault.plugins.<module>.<func>()`.
This folder is preserved across GitHub OTA updates and included in `.ZIP` workspace exports.
