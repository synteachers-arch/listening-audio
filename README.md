# 듣기 음원 관리·배포 시스템

중고등 영어 입시 학원의 듣기 숙제용 음원을 관리하고, 학생이 링크 클릭만으로
재생할 수 있도록 배포하는 시스템. 설계 배경과 전체 아키텍처는
[handoff.md](./handoff.md) 참고.

## 폴더 구조

```
source/     원본(고음질) 음원 — git에는 올리지 않음 (.gitignore)
dist/       배포용 압축 mp3 — GitHub Pages에서 실제로 서빙되는 파일
scripts/    원본 → 배포용 변환 스크립트 (process_audio.py)
site/       재생 페이지(player.html)와 카탈로그(manifest.json)
```

## 처음 시작하는 관리자라면

1. 이 저장소를 Google Drive 등 클라우드 동기화 폴더 **바깥**에 clone
2. `python -m venv .venv` 후 `pip install -r scripts/requirements.txt`
   (ffmpeg는 별도로 시스템에 설치되어 있어야 함)
3. 원본 음원은 `source/{학기}/{반}/unit12_raw.wav` 형식으로 배치
4. `python scripts/process_audio.py` 실행 → `dist/`에 배포용 mp3 생성,
   `site/manifest.json`에 랜덤 id로 등록됨
5. 커밋 후 push하면 GitHub Pages에 반영됨

자세한 다중 관리자 협업 규칙은 [handoff.md](./handoff.md)의 4번, 8-1번 섹션
참고.
