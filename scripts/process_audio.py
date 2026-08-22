"""
원본 음원(source/)을 배포용 mp3(dist/)로 변환하고 site/manifest.json에 등록한다.

사용법:
    python scripts/process_audio.py

전제:
    - source/ 아래에 원하는 폴더 구조로 원본 파일을 자유롭게 배치
      (폴더 깊이 제한 없음 — 예: source/유형01/01_대표 기출.mp3,
      source/2026-2학기/고1-B반/unit12_raw.wav 등 무엇이든 가능)
    - dist/에는 source/의 폴더 구조가 그대로 mp3로 미러링됨
    - 파일명이 "_raw"로 끝나면 변환 시 제거됨 (필수는 아님)
    - 시스템에 ffmpeg가 설치되어 PATH에서 실행 가능해야 함
    - 같은 원본을 다시 처리해도 manifest.json에 이미 등록된 파일의 id는
      바뀌지 않는다 (학생에게 배포한 링크가 깨지지 않도록)
"""

import json
import re
import secrets
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = ROOT / "source"
DIST_DIR = ROOT / "dist"
MANIFEST_PATH = ROOT / "site" / "manifest.json"

AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".aac", ".flac"}
RAW_SUFFIX_RE = re.compile(r"_raw$", re.IGNORECASE)


def find_source_files():
    if not SOURCE_DIR.exists():
        print(f"source/ 폴더가 없습니다: {SOURCE_DIR}")
        return []

    files = []
    for path in SOURCE_DIR.rglob("*"):
        if path.is_file() and path.suffix.lower() in AUDIO_EXTENSIONS:
            files.append(path)
    return files


def to_dist_path(source_path: Path) -> Path:
    rel = source_path.relative_to(SOURCE_DIR)
    unit = RAW_SUFFIX_RE.sub("", source_path.stem)
    return DIST_DIR / rel.parent / f"{unit}.mp3"


def convert_to_mp3(source_path: Path, dist_path: Path):
    dist_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-i", str(source_path),
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
        "-ac", "1",
        "-b:a", "128k",
        str(dist_path),
    ]
    result = subprocess.run(
        cmd, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    if result.returncode != 0:
        print(f"ffmpeg 변환 실패: {source_path}")
        print(result.stderr[-2000:])
        return False
    return True


def load_manifest():
    if MANIFEST_PATH.exists():
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_manifest(manifest):
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        f.write("\n")


def new_id(existing_ids):
    while True:
        candidate = secrets.token_urlsafe(6)
        if candidate not in existing_ids:
            return candidate


def main():
    manifest = load_manifest()
    path_to_id = {entry["path"]: id_ for id_, entry in manifest.items()}

    source_files = find_source_files()
    if not source_files:
        print("처리할 원본 파일이 없습니다.")
        return

    for source_path in source_files:
        dist_path = to_dist_path(source_path)
        dist_rel = dist_path.relative_to(DIST_DIR).as_posix()

        print(f"변환 중: {source_path.relative_to(SOURCE_DIR)} -> {dist_rel}")
        if not convert_to_mp3(source_path, dist_path):
            continue

        dist_rel_path = Path(dist_rel)
        group = dist_rel_path.parent.as_posix() if dist_rel_path.parent != Path(".") else ""
        unit = dist_rel_path.stem

        if dist_rel in path_to_id:
            id_ = path_to_id[dist_rel]
        else:
            id_ = new_id(set(manifest.keys()))
            path_to_id[dist_rel] = id_

        manifest[id_] = {
            "path": dist_rel,
            "group": group,
            "unit": unit,
        }

    save_manifest(manifest)
    print(f"완료. manifest.json에 {len(manifest)}개 항목 등록됨.")


if __name__ == "__main__":
    main()
