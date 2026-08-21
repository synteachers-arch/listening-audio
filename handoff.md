# 듣기 음원 관리·배포 시스템 — 프로젝트 인계 문서

> 작성일: 2026-08-21
> 상태: 설계 논의 완료, 구현 착수 전

## 1. 목표

중고등 영어 입시 학원의 듣기 숙제용 음원 파일을 관리하고, 학생이 스마트폰
링크 클릭만으로 재생할 수 있도록 배포하는 시스템 구축.
(교재/문제/스크립트는 이미 준비되어 있음 — 이 프로젝트는 **음원 파일**의
관리·배포에 한정)

작업은 2~3대의 노트북에서 나눠서 진행할 예정 → 아래 4번 "다중 기기 동기화
전략" 섹션 필독.

## 2. 확정된 아키텍처

| 구성 요소 | 역할 |
|---|---|
| GitHub 저장소 | 음원 원본(배포용) 보관 + 버전 관리 |
| GitHub Pages | 학생용 재생 페이지 호스팅 (링크 배포) |
| Python | 음원 가공 파이프라인 (음량 정규화, 포맷 변환, 파일명 규칙 적용) |
| Google Sheets | 음원 카탈로그 (파일-반-단원 매핑 목록) |
| Apps Script | (추후 확장) 카탈로그 자동화, 링크 발급, 재생 여부 추적 |
| VS Code | 코드/설정 작업 환경 (모든 노트북 공통) |

### 왜 이 구조인가
- Google Drive 공유 링크: 손쉽지만 다수 학생이 동시 접속 시
  "다운로드 용량 초과" 오류 리스크 있음 → 배제
- GitHub Pages: 소프트 리밋(저장소 ~1GB, 월 대역폭 ~100GB)이 있으나
  배포용 압축 음원(mp3 96~128kbps 모노)만 쓰면 상당 기간 여유
- 규모가 커지면 Cloudflare R2 등 오브젝트 스토리지로 이전 고려 (지금은 불필요)

## 3. 폴더/파일 구조 (제안)

```
listening-audio/
├── source/                      # 원본(고음질) — git에는 올리지 않음(.gitignore)
│   └── 2026-2학기/고1-B반/unit12_raw.wav
├── dist/                        # 배포용(압축본) — 실제 GitHub Pages에서 서빙
│   └── 2026-2학기/고1-B반/unit12.mp3
├── scripts/
│   └── process_audio.py         # 원본 → 배포용 자동 변환 스크립트
├── site/
│   ├── player.html              # 재생 페이지 템플릿 (쿼리 파라미터로 파일 지정)
│   └── manifest.json            # 배포된 음원 목록 (player.html이 참조)
├── .gitignore                   # source/ 폴더 제외 설정
└── README.md
```

### 파일 명명 규칙
`{학기}/{반}/{단원}.mp3`
예: `2026-2학기/고1-B반/unit12.mp3`

## 4. 다중 기기·다중 관리자 동기화 전략 (본인 + 학원 관리자 2대, 총 2~3인)

**핵심 원칙: Git 저장소(`dist/`, `scripts/`, `site/` 등 버전관리 대상)는
Google Drive 같은 클라우드 동기화 드라이브 안에 두지 않는다.**

이유: Google Drive/OneDrive/Dropbox 같은 파일 동기화 클라이언트는 `.git`
폴더 내부의 수많은 작은 파일을 실시간으로 건드리는 방식과 상성이 나빠서,
두 기기가 거의 동시에 저장하면 "충돌 사본" 파일이 생기고 이게 `.git`
내부에 섞이면 저장소 자체가 손상될 수 있음 (Google Drive 공식 커뮤니티에도
"Google Drive Sync Corrupting Git Repositories" 사례가 보고되어 있음).

**대신:**
- 각 노트북에 `git clone`으로 저장소를 로컬 디스크(Drive 동기화 폴더 바깥)에
  받아두고, 작업 시작 전 `git pull` → 작업 후 `git push` 로 동기화
- GitHub 저장소는 비공개(private)로 설정
- 원본 고음질 파일(`source/` 폴더, `.gitignore` 대상)은 Git으로 관리할
  필요가 없으므로 **Google Drive for Windows 가상 드라이브에 두고 여러
  노트북에서 접근하는 것은 적절함** — 단, 같은 원본 파일을 두 사람이
  동시에 편집하는 상황은 피할 것

**관리자가 여러 명이므로 추가로 지킬 점:**
- 관리자별로 **본인 소유 GitHub 계정**을 사용 (계정 공유 금지) — 커밋 이력이
  누가 작업했는지 구분돼야 실수 추적/롤백이 쉬움
- 저장소 소유자가 Settings → Collaborators에서 나머지 관리자를 초대(8-1
  참고), 초대 수락 후 각자 로컬에 `git clone`
- `dist/`, `manifest.json` 등 같은 파일을 동시에 여러 명이 수정하면 git
  merge 충돌이 날 수 있으므로, 작업 전 `git pull`로 최신화하는 습관을 관리자
  전원이 지킬 것

### 노트북(관리자)별 초기 설정 체크리스트
- [ ] Git 설치 확인, `git config --global user.name / user.email`을 **본인
  GitHub 계정 정보로** 설정
- [ ] (저장소 소유자로부터 Collaborator 초대 수락 후) GitHub 저장소를 로컬
  디스크 경로(Drive 동기화 폴더 아님)에 `git clone`
- [ ] VS Code에 Git 확장/GitHub 로그인 연결 (본인 계정으로)
- [ ] Google Drive for Desktop 설치 (원본 음원 폴더 접근용, 스트리밍 모드)
- [ ] Python + ffmpeg 설치 확인 (`process_audio.py` 실행용)

## 5. 재생 페이지 동작 방식 (설계 의도)

- 단원마다 별도 HTML을 만들지 않고, `player.html?id=x7k2p9` 형태로
  하나의 템플릿을 재사용 (id는 예측 불가능한 랜덤 문자열 — 8번 결정 사항 참고)
- `manifest.json`에서 id → 실제 mp3 경로 매핑을 조회
- 추후 옵션: 재생 횟수 제한(실제 시험처럼 2회 등), 구간 이동(스크러빙)
  제한, 재생 여부를 Apps Script로 기록해 숙제 이행 추적

## 6. Google Sheets 카탈로그 컬럼 (초안)

| 파일 경로 | 학기 | 반 | 단원명 | 배포일 | 마감일 | 링크 상태 |
|---|---|---|---|---|---|---|

## 7. 다음 할 일 (TODO)

- [ ] GitHub 비공개 저장소 생성 및 위 폴더 구조로 초기화
- [ ] `.gitignore`에 `source/` 추가
- [ ] `scripts/process_audio.py` 작성 (ffmpeg 연동: 음량 정규화 + mp3 변환 +
  파일명 규칙 적용 + 랜덤 id 자동 부여)
- [ ] `site/player.html` 템플릿 작성 (재생 버튼, 반응형, 브랜딩)
- [ ] `site/manifest.json` 구조 확정 및 첫 샘플 데이터 작성 (id는 랜덤 문자열)
- [ ] GitHub Pages 활성화 및 배포 테스트 (스마트폰 실기기 확인)
- [ ] Google Sheets 카탈로그 시트 생성
- [ ] 다른 관리자 2명을 GitHub Collaborator로 초대 (8-1 참고)
- [ ] 노트북 2~3대에 각각 clone 및 초기 설정 (4번 체크리스트 참고)
- [ ] (선택) Apps Script로 시트 ↔ manifest.json 자동 연동
- [ ] (추후) 재생 횟수 제한 / 재생 여부 추적 기능 추가 (필요성 확인되면)

## 8. 결정 사항 (2026-08-21 확정)

- **URL 접근 제어**: 예측 불가능한 랜덤 ID 방식 채택.
  `player.html?id=unit12` 대신 `player.html?id=x7k2p9` 처럼 `manifest.json`의
  key를 무작위 문자열로 발급. 로그인/비밀번호 없이도 링크를 모르면 접근이
  사실상 불가능한 수준의 최소 보호. ID 생성은 `process_audio.py`에서 파일
  처리 시 자동 부여(예: `secrets.token_urlsafe(6)`).
- **재생 횟수 제한**: 지금은 넣지 않음. 1차는 자유 재생으로 배포 시스템부터
  안정화하고, 필요성이 확인되면 Apps Script 연동 단계에서 추가.
- **아카이브 정책**: 별도 저장소로 옮기지 않고, 저장소 안에 학기별 폴더
  (`dist/2026-1학기/`, `dist/2026-2학기/` ...)를 계속 유지. GitHub Pages
  무료 저장 한도(~1GB) 내에서는 이 방식이 가장 단순함. 한도에 가까워지면
  그때 별도 아카이브 저장소 분리 재검토.

## 8-1. 다중 관리자(2~3인) 협업 방식

- GitHub Organization은 만들지 않고, 저장소 소유자(본인) 개인 계정 저장소에
  다른 관리자 2명을 **Collaborator(Write 권한)**로 초대.
- 절차: GitHub 저장소 → Settings → Collaborators → "Add people" → 관리자의
  GitHub 계정(아이디 또는 가입 이메일)으로 초대 → 상대방이 이메일의 초대
  수락.
- 각 관리자는 본인 GitHub 계정으로 커밋/푸시 (계정 공유 금지 — 누가 무엇을
  바꿨는지 git log로 추적 가능해야 함).
- 저장소는 비공개(private) 유지. Collaborator는 본인이 초대된 비공개
  저장소에 정상적으로 push 가능.
- 인원이나 저장소가 늘어나면 그때 Organization 전환 고려(지금은 불필요).

## 9. 참고 자료

- GitHub Pages 제한: https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits
- Google Drive 동기화가 Git 저장소를 손상시키는 사례 (Google 공식 커뮤니티):
  https://support.google.com/drive/thread/353731823/google-drive-sync-corrupting-git-repositories-via-desktop-ini-injection?hl=en
