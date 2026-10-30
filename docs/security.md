# Security, provenance, and responsible disclosure

- Google Cloud service-account JSON files containing private keys were intentionally **excluded** from this public repository. Any still-active 2023 keys should be revoked and replaced.
- Credentials must be configured outside source code, e.g. via `GOOGLE_APPLICATION_CREDENTIALS` on a local machine.
- No recordings of identifiable people or original demonstration videos were included, pending permissions.
- The original dlib 68-landmark model was not included. Obtain model files and check upstream distribution conditions independently.
- `stt_test1.py` contains Google's Apache 2.0 sample header; the historical embedded credential path was replaced with a comment. Preserve attribution in the source.
- Files are archived as historical class-project experiments and are not represented as verified road-safety software.
- Team and third-party code licensing have not been fully established; no repo-wide open-source license is asserted.
