# 듣기 음원 관리·배포 시스템 — 프로젝트 인계 문서

> 작성일: 2026-08-21 (최종 갱신: 2026-08-21)
> 상태: 초기 구현 완료 — GitHub 저장소/Pages 배포됨, 실제 음원 반영 및
> Collaborator 초대 남음

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

- [x] GitHub 저장소 생성(공개 전환, 8-2 참고) 및 위 폴더 구조로 초기화
- [x] `.gitignore`에 `source/` 추가
- [x] `scripts/process_audio.py` 작성 (ffmpeg 연동: 음량 정규화 + mp3 변환 +
  파일명 규칙 적용 + 랜덤 id 자동 부여) — 실제 원본 파일로 아직 미검증
- [x] `site/player.html` 템플릿 작성 (재생 버튼, 반응형, 브랜딩)
- [x] `site/manifest.json` 구조 확정 (현재 빈 `{}` — 첫 샘플 데이터는
  실제 원본 음원 처리 후 생성)
- [x] GitHub Pages 활성화 (https://synteachers-arch.github.io/listening-audio/)
  — 실제 음원으로 스마트폰 배포 테스트는 아직 필요
- [ ] Google Sheets 카탈로그 시트 생성
- [ ] 다른 관리자 2명을 GitHub Collaborator로 초대 (8-1 참고)
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

## 9. 참고 자료

- GitHub Pages 제한: https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits
- Google Drive 동기화가 Git 저장소를 손상시키는 사례 (Google 공식 커뮤니티):
  https://support.google.com/drive/thread/353731823/google-drive-sync-corrupting-git-repositories-via-desktop-ini-injection?hl=en
