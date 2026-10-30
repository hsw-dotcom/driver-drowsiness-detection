# External assets, not inside this repository
Place a legitimate local copy of `shape_predictor_68_face_landmarks.dat` into `assets/models/`.
Place the actual historic WAV files (if available) under `assets/audio/`:
- `wa.wav`, `warning.wav` — first trigger audio sequence
- `da.wav`, `danger.wav` — second trigger audio sequence
- `da.wav`, `decibel.wav` — third trigger audio sequence
- `success.wav` — volume-response success

Without these files, `--demo` works but real camera alerts cannot reproduce the historical audio.
NEVER put Google Cloud service-account JSON, API secrets or private voices in this ZIP.
