# Config File Manager Widget

The `dr_widget` package ships an AnyWidget-powered config file manager so notebooks can load, inspect, edit, and save JSON configuration blobs without leaving the browser. The frontend lives under `src/dr_widget/widgets/config_file_manager`, is built with Svelte + Vite via Bun, and syncs its state to Python traitlets.

## Repository Layout

- `src/dr_widget/widgets/config_file_manager/__init__.py` – AnyWidget class with initialization helpers and traitlet contracts.
- `src/dr_widget/widgets/config_file_manager/src/` – Svelte workspace (components live under `lib/`).
- `src/dr_widget/widgets/config_file_manager/static/` – Built bundle consumed by AnyWidget.
- `notebooks/config_file_manager_widget.py` – Marimo demo that exercises the widget end-to-end.

## Traitlets

| Traitlet | Direction | Description |
| --- | --- | --- |
| `current_state` | ↔ | JSON string representing **user data only** (no metadata). |
| `baseline_state` | ↔ | Last saved value of `current_state`, used for dirty detection/diffs. |
| `version` | ↔ | String metadata displayed in the UI and written to disk alongside `current_state` (now nested under `metadata.version`). |
| `config_file` | ↔ | Path to the backing file (may be relative today). |
| `config_file_display` | ↔ | UI-friendly label derived from `config_file`. |
| `files` | ↔ | JSON array of uploaded files (`{ name, size, type }`). |
| `file_count` | ← | Derived from `files.length`; read-only in the UI. |
| `error` | ↔ | User-facing error message cleared automatically on recovery. |

Python helper properties (`current_data`, `baseline_data`, `is_dirty`) expose parsed state for notebooks.

## Initialization Patterns

```python
ConfigFileManager()  # empty widget, user loads file via UI

ConfigFileManager(config_dict={"orchard": ["Basin"]}, version="exp_v1")
# - current_state populated with data dict
# - baseline_state empty → dirty until saved
# - config_file defaults to "exp_v1.json"

ConfigFileManager(config_file="/path/to/existing.json")
# - loads and migrates the file into new format
# - baseline_state matches current_state (clean)
# - version pulled from file metadata

ConfigFileManager(
    config_file="/tmp/new.json",
    config_dict={"selections": {"foo": True}},
    version="v2",
)
# - writes wrapped payload {metadata:{version,saved_at},data}
# - baseline_state matches current_state
```

Files saved through the UI (or via `config_file` + `config_dict`) are always written as:

```json
{
  "metadata": {
    "version": "v1",
    "saved_at": "2025-11-12T10:30:00Z"
  },
  "data": { ... user data ... }
}
```

Older files that only contain `selections` or embed metadata at the top level are migrated into this structure when loaded, with legacy `version`/`saved_at` values relocated under `metadata`.

## Frontend Behavior

- `use-file-bindings.ts` manages read/write loops for every synced traitlet so Marimo reactivity stays intact.
- `ConfigFileManager.svelte` derives dirty state by comparing `current_state` vs `baseline_state`, shows the currently loaded file name/version, and exposes Browse + Save panels.
- `SaveConfigPanel.svelte` wraps the current data with metadata before writing to disk (File System Access API when available, otherwise download).

## Build & Test

```bash
bun install
npx svelte-check --tsconfig src/dr_widget/widgets/config_file_manager/tsconfig.json
bun run build:config-file-manager
bun run build  # aggregates widgets (currently same as line above)
uv build       # packages the Python wheel with fresh static assets
```

Manual validation: run `marimo run notebooks/config_file_manager_widget.py`, load/upload JSON configs (including legacy "selections" files), edit values, and save to disk. Confirm dirty badge toggles correctly and version changes propagate between the sidebar and save panel.

## Contributing Tips

- Shared UI lives in `src/dr_widget/widgets/config_file_manager/src/lib/{components,hooks}`; prefer reusing hooks like `use-file-bindings`.
- Keep Tailwind utility classes grouped logically (layout → spacing → color → effects).
- Treat `node_modules/` as generated; never edit or commit them.
- Run `bunx prettier --write src/dr_widget/widgets/config_file_manager/src` before opening a PR.
- Document new traitlets or metadata fields in `docs/architecture.md` and notebook demos to keep Python + Svelte in sync.
