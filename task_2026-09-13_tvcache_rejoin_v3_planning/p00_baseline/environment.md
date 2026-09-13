## Modification History

| Date       | Summary of Changes |
| ---------- | ------------------ |
| 2026-09-13 | Recorded the P00 runtime and package-resolution environment. |

# P00 Environment

| Item | Observed value |
|---|---|
| Host Python | CPython 3.10.6, `/usr/bin/python3.10` |
| uv | `0.11.14 (x86_64-unknown-linux-gnu)` |
| Project | `tvcache/client` |
| Test group | `dev` |
| Temporary path | `/data/ycfeng/tmp/rejoin-p00-tmp` |
| Package cache | `/data/ycfeng/tmp/uv-cache` |
| Package index used for successful run | `http://mirrors.i.basemind.com/pypi/simple/` |
| Extra index | `http://pypi.i.basemind.com/brain/dev/+simple` |
| Hardware path | CPU only |

The public PyPI route failed while resolving `hatchling`; the mirror route completed package build and test startup. The modified lock file generated during mirror resolution was restored to the checkout version after the run.
