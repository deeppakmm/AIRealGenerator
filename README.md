# AI Reel Generator

A Flask app that turns uploaded images and text into a narrated vertical reel. It uses ElevenLabs for speech generation and FFmpeg to build the MP4.

## Requirements

- Python 3.12 or newer
- FFmpeg available on your PATH
- An ElevenLabs API key

## Run locally

Create and activate a virtual environment, then install the Python packages:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Open `.env` and set `ELEVENLABS_API_KEY` to your new key. Do not commit `.env`. Check that FFmpeg is installed with `ffmpeg -version`, then start the app:

```powershell
python main.py
```

Open <http://127.0.0.1:5000>.

## Deploy to Render

1. Push this project to a GitHub repository after reviewing the security note below.
2. In Render, create a new Blueprint and select the repository. Render will read `render.yaml` and build the Docker image, including FFmpeg.
3. Enter a newly generated `ELEVENLABS_API_KEY` when Render prompts for it.
4. The Blueprint attaches a 10 GB persistent disk at `/var/data` for uploads and generated reels. Persistent disks require a paid Render service; check current pricing before deployment.

The disk keeps user uploads and reels across restarts and deploys. It is attached to one service instance, so this configuration uses a single instance. Increase disk capacity if generated videos need more storage.

## API key and Git history

An ElevenLabs key was previously committed in this repository. Revoke that key in ElevenLabs and use a newly generated key in `.env` or Render's environment settings. Never put the new key in source code, `render.yaml`, or GitHub.

Removing a secret from the current files does not remove it from earlier Git commits. Before making this repository public, clean the Git history to remove the old key and user-generated uploads/reels, or publish a fresh repository containing only the cleaned project files.

## Data storage

Uploads and generated reels are stored under `DATA_DIR`. Locally, the default is the project directory; on Render, it is `/var/data`. User uploads and generated reels are excluded from Git.