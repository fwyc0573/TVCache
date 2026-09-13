## Modification History

| Date       | Summary of Changes |
| ---------- | ------------------ |
| 2026-09-13 | Recorded the pinned Terminal-Bench source checkout and runtime build readiness. |

# P03 Terminal-Bench Source Pin

## Source

- Repository: `https://github.com/harbor-framework/terminal-bench-1.git`
- Revision: `d28711d0da2675d0bb1d56de45ae5df6082438a3`
- Local checkout: `/data/ycfeng/tmp/terminal-bench-1-d28711d0da2675d0bb1d56de45ae5df6082438a3`
- Checkout state: detached HEAD at the exact revision, with no local edits.

The ten selected task directories each contain the pinned Dockerfile and `run-tests.sh`. All ten verifier shell scripts passed `bash -n` syntax validation.

## Runtime image status

The candidate manifest intentionally keeps `image_digest` as `null` until each task image is built. The requested image identity must come from the local OCI image inspection result; a Dockerfile blob SHA or a base-image tag is not a runtime image digest.

The current host has no `docker`, `podman`, `nerdctl`, or `buildah` executable, and no `/var/run/docker.sock` was found. Therefore image builds, image ID capture, and in-container verifier execution cannot be completed on this host yet.

The exact build and digest command remains recorded per manifest entry. Once a supported local container runtime is available, build the ten selected tasks at this pinned checkout, capture each image ID, update only the runtime fields, and run each verifier inside its image.

## Current decision

P03 source pinning is complete. P03 runtime preparation is pending the container runtime. P04 smoke must wait for image digests and verifier results for the four smoke tasks.
