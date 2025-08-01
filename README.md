```markdown
# 🎧 LofiMaker

**LofiMaker** is a Python-based audio processing tool that turns any track into a lofi-style remix with optional effects like slow-down, reverb, spatial surround (3D/8D/16D), and clean normalization.

---

## 🚀 Features

- ✅ Slow down the audio tempo
- ✅ Add reverb for ambiance
- ✅ Surround audio panning (N-D sound effect)
- ✅ Normalize volume to consistent levels
- ✅ Automatic song title extraction from metadata
- ✅ Outputs high-quality MP3 to a `musics/` directory

---

## 📦 Requirements

### Python version
- Python 3.8+

### Dependencies (Pinned)

These are listed in `requirements.txt`:

```

cffi==1.17.1
mutagen==1.47.0
numpy==2.3.2
pycparser==2.22
pydub==0.25.1
scipy==1.16.1
soundfile==0.13.1

````

Install using:

```bash
pip install -r requirements.txt
````

### System dependency: FFmpeg

* **Required for reading/writing audio files**
* Install via:

```bash
# Ubuntu
sudo apt install ffmpeg

# macOS (Homebrew)
brew install ffmpeg

# Windows
Download from: https://ffmpeg.org/download.html
```

---

## 🛠️ Usage

```python
from lofi_maker import LofiMaker

input_song = "path/to/your/song.mp3"

lofi = LofiMaker(
    song_path=input_song,
    slow_down=True,
    slow_speed=0.55,
    surround=True,
    surround_cycle_duration=14.0,
    surround_depth=0.8,
    reverb=True,
    reverb_decay=0.4,
    reverb_delay_ms=120,
    reverb_repeats=2,
    target_dBFS=-1.0,
)

output_path = lofi.convert_audio()
print(f"Processed song saved to: {output_path}")
```

---

## ⚙️ Parameters

| Parameter                 | Description                               | Default |
| ------------------------- | ----------------------------------------- | ------- |
| `slow_down`               | Slow down the song                        | `True`  |
| `slow_speed`              | Factor to slow down (0.5 = 50% speed)     | `0.50`  |
| `surround`                | Enable surround/3D audio effect           | `False` |
| `surround_cycle_duration` | Duration in seconds of stereo pan cycle   | `14.0`  |
| `surround_depth`          | Stereo panning depth (0 = none, 1 = full) | `0.7`   |
| `reverb`                  | Enable reverb effect                      | `True`  |
| `reverb_decay`            | How quickly the echo fades                | `0.3`   |
| `reverb_delay_ms`         | Delay in milliseconds between echoes      | `120`   |
| `reverb_repeats`          | Number of echo layers                     | `2`     |
| `target_dBFS`             | Normalize to a loudness level (dBFS)      | `-1.0`  |

---

## 📁 Output

All output files are saved in the `musics/` directory:

```text
musics/<song_title>_converted.mp3
```

If no metadata title is found, the filename is used as a fallback.

---

## 📜 License

MIT License — Free to use and modify.

```
```
