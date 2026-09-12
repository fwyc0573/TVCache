## Modification History

| Date       | Summary of Changes |
|------------|--------------------|
| 2026-09-10 | Recorded verified launcher lifetime, platform verdict, HF symlink, and per-environment CUDA lessons. |
| 2026-08-14 | Created reusable-lessons register. |

# Lessons

No production-grade reusable lessons have been validated yet.


### 2026-09-10 GPU probe verdicts and launcher lifetimes

- For the observed StepMind launch configuration, CLI `--detach` still proceeded to `Connecting to pod` and maintained the foreground command session. A 60-second outer timeout issued `Stopping rjob reason=interrupt`. Keep the launcher alive longer than the bounded worker command; use short 60-second limits only for read-only status queries. This reproduces the constructor-a failure already recorded on 2026-09-10.
- Platform `Succeeded` is not a test verdict for these interactive commands: two H800 commands returned ExitCode=1 while the RJob phase reported Succeeded. Require the actual command exit code and test output.
- HF snapshots contain symlinks. Validate each expected path with `Path.is_file()` / `stat()` or use a symlink-aware listing; `find -type f` returning nothing does not prove a snapshot is empty.
- A CUDA tensor PASS using the image's Torch does not validate a separate Python venv's Torch. Record the actual venv version/build and execute the reached operation there. Here image Torch 2.10.0+cu129 passed on H200 while venv Torch 2.0.1+cu117 failed at CUDA zeros on H800.
