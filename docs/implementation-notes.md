# Source-based implementation findings

## Eye detection prototypes

- `test.py` and `test_v2.py` use `Picamera2`, `dlib.get_frontal_face_detector()`, 68-landmark shape prediction, the six points for each eye, and EAR = (A+B)/(2*C).
- `test.py`: calibration via ~300 accepted frames; counts low EAR frames and checks eye-position displacement before printing `detected` on the image.
- `test_v2.py`: calibration for 30 seconds, average EAR and eye y-position; `closed_count >= 10` or `eye_level > danger_level` triggers the on-screen `detected` text.
- The code draws lines and displays the camera image. It does **not** play a warning or call the voice module. It also refers to an undefined `cap` at program termination.
- Neither model accuracy nor on-device inference speed has a verified numerical result. Reproduction currently impossible without Pi/hardware and landmark file configuration.

## Voice interaction experiments

- `test1.py` synthesizes math questions via Google Cloud TTS, opens a streaming STT microphone input, and compares the recognized text with an answer; WAV sounds for correct/incorrect/non-numeric responses were stored in the original archive but are not shared here.
- Other source files test gTTS, microphone capture, transcription, and Google STT example flow.
- Observed concerns: interim STT hypotheses are appended rather than replaced, the numeric-only extraction is not used for return, test versions have potentially blocking loops and require credentials/network access.
- A development video shows problem generation and error/restart behavior; it does not conclusively establish integrated end-to-end voice interaction.

## Attribution and evidence

These are two groups of historical source files recovered from the user's backups. The **preserved 2023 original source files under `src/`** do not contain the later integrated program; `reconstruction/app/` is a separate 2026 inferred reconstruction, not a recovered original. However, additional 2023 vehicle-test recordings show camera detection and a `Listening...` interface, with a separately opened `decibel.py` measuring audio levels and a later `test.py` calling a warning WAV. This is evidence of integration attempts and on-device testing, not proof of complete correct/incorrect-answer handling or all three warning levels. See [vehicle-test evidence](vehicle-test-evidence-2023.md). No present-day live test was performed.


## 2026-10-31: Final-presentation-first reconstruction correction

The final presentation flow chart is authoritative for the three warning stages and retry decisions. User-confirmed facts: eye EAR/eye position determine drowsiness, regardless of face *shape*; observed operation with glasses and sunglasses; ~10s microphone answer window; repeat the same question until correct, repeat volume checks until sufficient, and cycle stage 3 to stage 1. The earlier max-three volume attempts and post-alert normal-frame latch were speculative and removed. The 10s audio capture must not be confused with a Google Cloud network request timeout. Historic `src/` source files remain untouched. See `reconstruction/app/docs/TRACEABILITY.md` for distinctions between slide evidence, original code, user account, and implementation adapters. Twenty-five offline logic tests passed; this is not a real-device verification.
