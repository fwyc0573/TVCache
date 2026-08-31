## Modification History

| Date       | Summary of Changes |
| ---------- | ------------------ |
| 2026-08-31 | Record the verified TVCache server lock-alignment recipe |

# Environment Handbook

## TVCache server lock alignment (2026-08-31)

### Observed condition

`tvcache/server/pyproject.toml` declared `gunicorn>=20.0.0`, while the committed `tvcache/server/uv.lock` omitted the `gunicorn` package and root metadata. With `uv 0.11.14`, `cd tvcache/server && uv lock --check` exited `1` and reported that the lockfile needed an update.

### Verified recipe

```bash
cd "$TVCACHE_ROOT/tvcache/server"
uv lock
uv lock --check
uv sync --locked
```

The generated lock adds `gunicorn==26.2.0`. After the alignment, `uv lock --check` exits `0`; `uv sync --locked --dry-run` resolves `15` packages and reports `Would make no changes`.

### Evidence

The reproduction task records the root-cause comparison and command output in `task_memory/task_2026-08-31_tvcache_e2e_reproduction/findings.md`, `progress.md`, and `test_report_2026-08-31_train_sandbox_preflight.md`.
