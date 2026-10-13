"""Clipza Rewards — video engine: smart moment detection + 9:16 clip cutting.

No ML models, no API keys: finds high-energy moments from the audio track
and cuts vertical clips with a static ffmpeg binary (imageio-ffmpeg).
"""
import re
import subprocess
import wave

import imageio_ffmpeg
import numpy as np

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()


def _run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {r.stderr[-300:]}")
    return r


def video_duration(path: str) -> float:
    r = subprocess.run([FFMPEG, "-i", path], capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r.stderr)
    if not m:
        raise RuntimeError("Could not read video duration")
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))


def detect_moments(video_path: str, count: int = 5,
                   min_len: int = 15, max_len: int = 60):
    """Energy-based viral-moment detection.

    Returns a list of {start, end, score, reason}, best first.
    """
    duration = video_duration(video_path)
    wav_path = video_path + ".energy.wav"
    _run([FFMPEG, "-y", "-i", video_path, "-ac", "1", "-ar", "16000",
          "-vn", "-c:a", "pcm_s16le", wav_path])
    try:
        with wave.open(wav_path, "rb") as w:
            raw = w.readframes(w.getnframes())
    finally:
        import os
        try:
            os.remove(wav_path)
        except OSError:
            pass

    audio = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    sr = 16000
    nwin = len(audio) // sr
    if nwin < 5:
        raise RuntimeError("Video is too short for moment detection")
    frames = audio[:nwin * sr].reshape(nwin, sr)
    rms = np.sqrt((frames ** 2).mean(axis=1) + 1e-9)
    smooth = np.convolve(rms, np.ones(3) / 3, mode="same")

    thresh = smooth.mean() + 0.6 * smooth.std()
    active = smooth > thresh

    regions, start = [], None
    for i, a in enumerate(active):
        if a and start is None:
            start = i
        elif not a and start is not None:
            regions.append((start, i))
            start = None
    if start is not None:
        regions.append((start, nwin))

    merged = []
    for s, e in regions:  # merge gaps shorter than 4s
        if merged and s - merged[-1][1] < 4:
            merged[-1] = (merged[-1][0], e)
        else:
            merged.append((s, e))

    cands = []
    for s, e in merged:
        length = e - s
        if length < 8:
            continue
        if length > max_len:  # keep the hottest max_len window inside
            best, best_e = s, -1.0
            for ws in range(s, e - max_len + 1, 5):
                ee = float(smooth[ws:ws + max_len].mean())
                if ee > best_e:
                    best, best_e = ws, ee
            s, e = best, best + max_len
        if e - s < min_len:  # extend short moments to min_len
            e = min(nwin, s + min_len)
        cands.append((s, e, float(smooth[s:e].mean())))

    if not cands:  # very flat audio — fall back to even splits
        part = max(min_len, int(duration // max(count, 1)))
        for i in range(count):
            s = int(i * duration / count)
            cands.append((s, min(nwin, s + part), 0.5))

    energies = [c[2] for c in cands]
    lo, hi = min(energies), max(energies)
    span = (hi - lo) or 1.0

    scored = []
    for s, e in ((c[0], c[1]) for c in cands):
        energy = next(c[2] for c in cands if c[0] == s and c[1] == e)
        score = 60 + round(35 * (energy - lo) / span)
        if s < duration * 0.25:  # strong opening = hook bonus
            score = min(99, score + 4)
        reason = ("Peak energy moment — loud, high-intensity section."
                  if energy >= lo + 0.66 * span else
                  "High engagement section with strong audio presence.")
        scored.append({"start": float(s), "end": float(min(e, duration)),
                       "score": score, "reason": reason})
    scored.sort(key=lambda m: m["score"], reverse=True)
    return scored[:count]


def cut_clip(video_path: str, start: float, end: float, out_path: str,
             width: int = 720, height: int = 1280) -> str:
    """Cut one vertical 9:16 clip (center crop). Returns out_path."""
    duration = max(1.0, end - start)
    vf = f"crop=ih*9/16:ih,scale={width}:{height}"
    _run([FFMPEG, "-y", "-ss", f"{start:.2f}", "-i", video_path,
          "-t", f"{duration:.2f}", "-vf", vf,
          "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
          "-c:a", "aac", "-movflags", "+faststart", out_path])
    return out_path


def fmt_time(s: float) -> str:
    s = int(s)
    return f"{s // 60}:{s % 60:02d}"
