# Release Check

## What Changed
- Added `run.py` as the canonical CLI entrypoint wrapping `run_bhoolamind.py`.
- Added a proper `--help` CLI via `argparse` in `run_bhoolamind.py`.
- `run.py --help` now prints without importing heavy ML modules.
- Split dependencies: `requirements.txt` is lightweight; `requirements-ml.txt` holds optional heavy ML/voice/vector/dashboard deps.
- Pinned `huggingface-hub` to a compatible version for ML stacks.
- Added `env.sh` to set `HF_HOME` and `TRANSFORMERS_CACHE` to a writable local folder.
- Updated `README.md` with a single-command Quickstart and CLI usage.

## How to Run
```bash
cd bhoolamind_v1.5
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python run.py --help
python run.py interactive
```

Optional dashboard:
```bash
streamlit run frontend/dashboard.py
```

## What Still Won't Work (If Anything)
- First run will download large ML models (transformers, whisper, sentence-transformers), which may be slow and require enough disk space.
- Voice transcription requires compatible audio files and may be slow on CPU-only machines.
- Vector search features depend on ChromaDB initialization and will be empty until interactions are logged.
