# Custom Tools (`custom_tools/`)

Drop any `.py` module into this folder to hot-load custom functions into the AetherVault Studio Python Workbench under `vault.plugins.<module_name>.<function>(...)`.

## Example (`custom_tools/greeter.py`)
```python
def hello(name: str = "Creator") -> str:
    return f"Hello from custom plugin, {name}!"
```

Reload without restarting the server via:
- Workbench: `vault.reload_tools()`
- API: `GET /api/custom_tools`
- Or let the AI author & sandbox-test one with `vault.create_tool(name, code, test_code)`.
