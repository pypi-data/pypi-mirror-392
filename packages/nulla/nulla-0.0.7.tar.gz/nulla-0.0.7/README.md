# Nulla

*A local Windows bootstrapper for a talkative AI companion — sets up Whisper (ASR), XTTS v2 (TTS), llama.cpp with OpenHermes GGUF, and ships sample mini-games.*

---

### Status
**Alpha — functional CLI.** `nulla setup` creates isolated venvs, fetches llama.cpp Windows binaries and the OpenHermes-2.5-Mistral-7B GGUF from **official upstreams**, and wires in Whisper (CPU) + XTTS v2 (CUDA/CPU).  
This package **does not redistribute** third-party models/binaries; they are downloaded during setup under their respective licenses.

### Tested Environment
- **GPU:** RTX 5070 Ti 16 GB  
- **CPU:** Ryzen 5 5600X  
- **RAM:** 32 GB  
- **Storage:** ~20 GB free recommended  
- **OS:** Windows 11  
- **Python:** **3.11.6 (required)**

### Requirements
- Windows 11
- **Python 3.11.6 exactly**
- NVIDIA CUDA (optional; CPU fallbacks exist but are slower)

**Python requirement:** This project targets **Python 3.11.6 exactly**.

**What this package does *not* include:**  
- No Whisper code/weights, no llama.cpp binaries, no XTTS-v2 models, no GGUF models.  

## Credits & Tools
- **Author/Maintainer/Creative Director:** Tsoxer — <tsoxercontact@gmail.com>  
- **Code scaffolding & helper scripts:** co-authored with **ChatGPT-5**  
- **Image assets:** generated with **ChatGPT-5** (OpenAI)

## Third-Party Notices (not bundled)
- **OpenAI Whisper** — MIT License. Source: openai/whisper.  
- **llama.cpp** — MIT-licensed C/C++ inference project.  
- **XTTS-v2 (Coqui)** — licensed under the Coqui Public Model License (non-commercial). You must review and comply with their terms.  
- **OpenHermes-2.5-Mistral-7B-GGUF (TheBloke)** — GGUF conversions hosted on Hugging Face; follow the original/model repo licenses.  

## Third-Party Notices (bundled)

- **salutations.wav by shadoWisp** — used in demos; licensed **CC BY 3.0**. If you use it, give attribution and link the source: https://freesound.org/s/260931/

- **intro.wav** — generated with **AudioLDM 2**. Used under **CC BY-NC-SA 4.0** for non-commercial, research/educational purposes only.  

- **Other AI-generated audio** (button presses, UI/game SFX, music, etc.) — generated with **TangoFlux**. These clips were created using a model whose checkpoints are licensed for **non-commercial research use only**, subject to the Stability AI Community License (Stable Audio Open) and WavCaps’ academic-use terms. They are included here only for non-commercial, research/educational use.
  
This package is © 2025 Tsoxer (MIT). See `LICENSE`.
