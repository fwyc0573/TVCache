## Modification History

| Date       | Summary of Changes                     |
| ---------- | -------------------------------------- |
| 2026-08-31 | Initialize operational notes |

# Notes

- Preserve user-owned untracked files in `.omc/` and `.serena/`.
- Store temporary logs and caches under `/data/ycfeng/tmp` rather than `/tmp`.
- Use direct case-driven verification; add persistent scripts only when the repository path or a regression check requires them.
- Keep command captures and temporary runtime logs under `/data/ycfeng/tmp/tvcache_e2e_reproduction/`.
