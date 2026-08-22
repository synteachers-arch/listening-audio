# 듣기 음원 관리·배포 시스템 — 프로젝트 인계 문서

> 작성일: 2026-08-21 (최종 갱신: 2026-08-22)
> 상태: **운영 가능한 상태로 배포 완료.** 실제 음원 12개가 GitHub Pages에
> 올라가 있고, 스마트폰 재생 테스트까지 확인됨. 이어서 작업할 사람은
> 10번 "인계 시점 요약" 섹션부터 읽을 것.

## 0. 인계받은 분에게

이 문서는 새로 합류하는 관리자가 맥락을 따라잡기 위한 것입니다. 전체를 다
읽을 필요는 없고, **10번 섹션(인계 시점 요약)** 먼저 보고 필요한 부분만
위로 올라와서 참고하세요.

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

## 3. 폴더/파일 구조 (실제 구현됨)

```
listening-audio/
├── source/                      # 원본 — git에는 올리지 않음(.gitignore)
│   └── 유형01/01_대표 기출.mp3   # (예시: 실제 배치된 구조)
├── dist/                        # 배포용(압축본) — 실제 GitHub Pages에서 서빙
│   └── 유형01/01_대표 기출.mp3
├── scripts/
│   └── process_audio.py         # 원본 → 배포용 자동 변환 스크립트
├── site/
│   ├── player.html              # 재생 페이지 템플릿 (쿼리 파라미터로 파일 지정)
│   └── manifest.json            # 배포된 음원 목록 (player.html이 참조)
├── .gitignore                   # source/ 폴더 제외 설정
└── README.md
```

### 폴더 구조 규칙 (당초 설계에서 변경됨)
당초 `{학기}/{반}/{단원}.mp3` 고정 3단계 구조로 설계했으나, 실제 음원이
학기/반이 아니라 **유형(문제 유형) 기준**으로 정리되어 있어서
`process_audio.py`를 임의 깊이의 폴더 구조를 그대로 미러링하는 방식으로
일반화함(2026-08-22, 8-3 참고).

- `source/` 아래에 원하는 대로 폴더를 만들면 됨 (깊이 제한 없음)
- `dist/`에는 `source/`와 동일한 폴더 구조가 그대로 mp3로 생성됨
- `manifest.json`의 각 항목은 `path`(dist 기준 상대경로), `group`(파일의
  부모 폴더 경로), `unit`(파일명, 확장자 제외)로 구성됨
- 파일명이 `_raw`로 끝나면 변환 시 제거됨 (필수 아님)

현재 실제 배치 예시: `유형01`~`유형04` 폴더 각각에 `01_대표 기출.mp3`,
`02_Mini Exercise.mp3`, `03_Listen&Check.mp3` 3개 파일.

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
- GitHub 저장소는 **공개(public)**로 설정됨 (GitHub Pages 무료 플랜 제약 때문 —
  8-2 참고. 원래는 비공개로 설계했었음)
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

**macOS 관리자용 참고** — Windows(winget) 대신 Homebrew 사용:
```bash
# Homebrew가 없다면 먼저 설치
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

brew install gh ffmpeg python git

git config --global user.name "본인 GitHub 이름"
git config --global user.email "본인 GitHub 가입 이메일"

gh auth login          # 웹 브라우저 로그인 플로우
gh auth setup-git      # git push/pull에 gh 인증을 연결
```
- macOS는 Python 명령이 `python`이 아니라 `python3`인 경우가 많음 →
  `python3 scripts/process_audio.py`로 실행
- clone 위치는 Windows와 동일하게 **Google Drive 동기화 폴더 바깥**
  (예: `~/dev/listening-audio`)이어야 함 (4번 상단 핵심 원칙 참고)

## 5. 재생 페이지 동작 방식 (구현됨 + 다음 논의 항목)

- 단원마다 별도 HTML을 만들지 않고, `player.html?id=x7k2p9` 형태로
  하나의 템플릿을 재사용 (id는 예측 불가능한 랜덤 문자열 — 8번 결정 사항 참고)
- `manifest.json`에서 id → `{path, group, unit}` 매핑을 조회해 오디오
  플레이어를 렌더링. 실제 스마트폰 재생 테스트 완료 (2026-08-22)
- 추후 옵션: 재생 횟수 제한(실제 시험처럼 2회 등), 구간 이동(스크러빙)
  제한, 재생 여부를 Apps Script로 기록해 숙제 이행 추적
- **다음 논의 중인 항목(미착수)**: 지금은 mp3 1개당 링크 1개라서 학생에게
  "유형01" 숙제를 낼 때 3개 링크를 따로 보내야 함. `site/index.html`을
  추가해서 manifest.json 전체를 유형별 목록으로 보여주는 카탈로그
  홈페이지를 만드는 방향으로 논의 중 — `player.html`(개별 재생)은 그대로
  유지하고 `index.html`은 진입점 역할만 하는 구조로 예상.

## 6. Google Sheets 카탈로그 컬럼 (초안 — 아직 미착수)

당초 컬럼안은 학기/반 기준이었으나, 실제 콘텐츠가 유형 기준으로 바뀌었으므로
착수 시 아래 컬럼안을 다시 검토할 것:

| 파일 경로 | 유형 | 항목(대표기출/Mini Exercise/Listen&Check) | 배포일 | 마감일 | 링크 상태 |
|---|---|---|---|---|---|

## 7. 다음 할 일 (TODO)

- [x] GitHub 저장소 생성(공개 전환, 8-2 참고) 및 위 폴더 구조로 초기화
- [x] `.gitignore`에 `source/` 추가
- [x] `scripts/process_audio.py` 작성 (ffmpeg 연동: 음량 정규화 + mp3 변환 +
  임의 깊이 폴더 구조 미러링 + 랜덤 id 자동 부여) — 실제 음원 12개로 검증 완료
- [x] `site/player.html` 템플릿 작성 (재생 버튼, 반응형, 브랜딩)
- [x] `site/manifest.json` 구조 확정 및 실제 데이터 반영 (12개 항목)
- [x] GitHub Pages 활성화 (https://synteachers-arch.github.io/listening-audio/)
  — 실제 음원 스마트폰 재생 테스트 완료 (2026-08-22)
- [x] 관리자 1명(`classikyu-collab`)을 GitHub Collaborator로 초대함
  (2026-08-22) — **초대 수락 대기 중**
- [ ] 관리자 2번째 인원 아직 미정 — 정해지면 동일하게 Collaborator 초대
- [ ] `site/index.html` 카탈로그(목록) 페이지 추가 — 5번 항목 참고, 설계만
  논의됐고 아직 구현 전
- [ ] Google Sheets 카탈로그 시트 생성 (6번 컬럼안 참고)
- [ ] 노트북 2~3대에 각각 clone 및 초기 설정 (4번 체크리스트 참고)
- [ ] (선택) Apps Script로 시트 ↔ manifest.json 자동 연동
- [ ] (추후) 재생 횟수 제한 / 재생 여부 추적 기능 추가 (필요성 확인되면)

## 8. 결정 사항 (2026-08-21 확정, 8-2에서 일부 수정됨)

- **URL 접근 제어**: 예측 불가능한 랜덤 ID 방식 채택.
  `player.html?id=unit12` 대신 `player.html?id=x7k2p9` 처럼 `manifest.json`의
  key를 무작위 문자열로 발급. ID 생성은 `process_audio.py`에서 파일 처리 시
  자동 부여(예: `secrets.token_urlsafe(6)`).
  ⚠️ 단, 8-2에서 저장소를 공개로 전환하면서 이 보호의 실효성이 크게
  낮아졌음 — 저장소 파일 목록 자체가 공개되므로 랜덤 ID는 "링크를 몰라도
  URL 목록에서 우연히 찾기 어렵게" 하는 정도의 의미만 남음. 자세한 내용은
  8-2 참고.
- **재생 횟수 제한**: 지금은 넣지 않음. 1차는 자유 재생으로 배포 시스템부터
  안정화하고, 필요성이 확인되면 Apps Script 연동 단계에서 추가.
- **아카이브 정책**: 별도 저장소로 옮기지 않고, 저장소 안에 학기별 폴더
  (`dist/2026-1학기/`, `dist/2026-2학기/` ...)를 계속 유지. GitHub Pages
  무료 저장 한도(~1GB) 내에서는 이 방식이 가장 단순함. 한도에 가까워지면
  그때 별도 아카이브 저장소 분리 재검토.

## 8-2. GitHub Pages 제약으로 인한 저장소 공개 전환 (2026-08-21)

구현 중 발견: **GitHub Pages는 무료(Free) 플랜에서 비공개 저장소를
지원하지 않음** (Pro 이상 필요). 애초 설계는 "비공개 저장소 + GitHub
Pages"였으나 이 조합이 무료 플랜에서 불가능함이 뒤늦게 확인됨.

세 가지 대안(Cloudflare Pages로 전환 / GitHub Pro 구독 / 저장소 공개 전환)
중 **저장소를 공개로 전환**하는 방식을 선택함
(`gh repo edit --visibility public`).

**트레이드오프 인지 필요:**
- 저장소가 공개이므로 `github.com/synteachers-arch/listening-audio`에서
  누구나 `dist/` 폴더의 반/단원명이 담긴 파일 목록과 mp3 파일 자체를 직접
  열람·다운로드할 수 있음. 랜덤 ID(8번 항목)는 "링크 없이 우연히 접근"만
  막을 뿐, 저장소를 직접 뒤지는 접근은 막지 못함
- **저작권 주의**: 출판사 교재에 딸린 상업용 듣기 음원을 그대로 업로드하면
  공개 배포로 인한 저작권 문제가 발생할 수 있음. 자체 녹음/자체 제작
  음원이거나 배포 권한이 확인된 음원만 이 저장소에 올릴 것
- 추후 이 트레이드오프가 부담되면 Cloudflare Pages로 전환(저장소는
  비공개 유지 가능) 또는 GitHub Pro 구독으로 재검토 가능

**GitHub Pages 배포 URL**: https://synteachers-arch.github.io/listening-audio/

## 8-1. 다중 관리자(2~3인) 협업 방식

- GitHub Organization은 만들지 않고, 저장소 소유자(본인) 개인 계정 저장소에
  다른 관리자 2명을 **Collaborator(Write 권한)**로 초대.
- 절차: GitHub 저장소 → Settings → Collaborators → "Add people" → 관리자의
  GitHub 계정(아이디 또는 가입 이메일)으로 초대 → 상대방이 이메일의 초대
  수락.
- 각 관리자는 본인 GitHub 계정으로 커밋/푸시 (계정 공유 금지 — 누가 무엇을
  바꿨는지 git log로 추적 가능해야 함).
- 저장소가 공개(public)로 전환됐지만(8-2 참고), Collaborator(Write 권한)
  초대는 동일하게 필요 — 초대받지 않은 사람은 코드를 볼 수는 있어도
  push는 할 수 없음.
- 인원이나 저장소가 늘어나면 그때 Organization 전환 고려(지금은 불필요).

## 8-3. 첫 실제 음원 배치 및 검증 (2026-08-22)

- 실제 음원 12개(유형01~04 × 대표기출/Mini Exercise/Listen&Check)를
  `source/`에 배치 → `process_audio.py` 실행 → `dist/`에 변환 → push
- 이 음원은 **자체 제작/학원 소유 음원**임을 확인함 (출판사 상업 음원
  아님) → 8-2의 저작권 우려는 이 배치에는 해당 없음. 단, 앞으로 다른
  배치를 올릴 때마다 출처를 다시 확인할 것
- ffmpeg 변환 스크립트에서 Windows 콘솔 인코딩(cp949) 문제로 stderr 읽기
  중 크래시가 났던 버그를 수정함 (`encoding="utf-8", errors="replace"`
  지정)
- GitHub Pages CDN이 Range 요청(`Accept-Ranges: bytes`)을 정상 지원하는
  것을 확인함 (한국 리전 엣지에서 서빙됨: `x-github-edge-region:
  koreacentral`)
- 실기기(스마트폰)에서 `player.html?id=Xpz7wlJ7` 링크로 재생 테스트 완료.
  첫 시도에서 5분 가까이 재생이 멈춰있는 현상이 있었으나 재시도 시 정상
  재생됨 — 파일 자체와 서버 설정(Range 지원, 디코딩)은 모두 정상으로
  확인됐으므로 일시적 네트워크/CDN 캐시 워밍업 문제로 추정. **재발하면
  진짜 재생 안 되는 상황인지, 첫 로딩만 느린 것인지 구분해서 다시 확인
  필요**

## 9. 참고 자료

- GitHub Pages 제한: https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits
- Google Drive 동기화가 Git 저장소를 손상시키는 사례 (Google 공식 커뮤니티):
  https://support.google.com/drive/thread/353731823/google-drive-sync-corrupting-git-repositories-via-desktop-ini-injection?hl=en
- 저장소: https://github.com/synteachers-arch/listening-audio
- 배포 사이트: https://synteachers-arch.github.io/listening-audio/
- 재생 테스트용 예시 링크: https://synteachers-arch.github.io/listening-audio/site/player.html?id=Xpz7wlJ7

## 10. 인계 시점 요약 (2026-08-22)

새로 합류하는 관리자는 여기부터 시작하면 됩니다.

**지금 바로 되는 것:**
- 저장소 clone: `git clone https://github.com/synteachers-arch/listening-audio.git`
  (Collaborator 초대를 수락한 이후에 push 권한이 생김 — clone 자체는
  공개 저장소라 누구나 가능)
- `python scripts/process_audio.py` 실행하면 `source/` 아래 새 폴더에
  넣은 mp3/wav를 자동으로 `dist/`에 변환 + `site/manifest.json`에 등록
  (Python, ffmpeg가 로컬에 설치되어 있어야 함 — 4번 체크리스트 참고)
- 아무 mp3나 하나 등록한 뒤 `git add`, `git commit`, `git push`하면
  몇 초~1분 내 GitHub Pages에 반영되고, `player.html?id=<발급된id>` 링크로
  바로 재생 확인 가능

**아직 안 된 것 (우선순위 순):**
1. 관리자 2번째 인원 확정 및 Collaborator 초대 (7번 TODO)
2. `site/index.html` 카탈로그 페이지 — 지금은 링크를 mp3 파일 단위로만
   보낼 수 있어서, 유형별로 묶어서 보여주는 목록 페이지가 필요하다는
   논의까지만 되고 구현 전 (5번 항목)
3. Google Sheets 카탈로그 시트 (6번)
4. 노트북 초기 설정 체크리스트를 각 관리자가 직접 완료 (4번)

**꼭 알아야 할 트레이드오프:**
- 저장소가 **공개(public)**입니다 — GitHub Pages 무료 플랜이 비공개
  저장소를 지원하지 않아서 어쩔 수 없이 전환했습니다(8-2). 즉 링크의
  랜덤 ID는 "우연히 못 찾게" 하는 정도이지 진짜 접근 제어가 아닙니다.
  **출판사 상업 음원 등 저작권 있는 자료는 절대 올리지 말 것.**
