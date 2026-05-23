---
name: weekly-plan
description: 다음 주에 구현할 saboteur 기능 후보를 발굴하여 GitHub Issue로 등록하는 주간 기획 워크플로우. planner 서브에이전트를 호출한다.
disable-model-invocation: true
---

# weekly-plan

매주 한 번 실행되어 다음 한 주 동안 작업할 기능 후보를 GitHub Issue로 발굴합니다.

## 사전 조건

- `gh` CLI 인증 완료 (`gh auth status` 확인)
- 작업 디렉토리가 saboteur 리포지토리 루트
- 기본 브랜치가 깨끗한 상태 (uncommitted 변경 사항 없음)

## 실행 단계

1. **상태 점검**
   - `git status --short` — 변경사항 없는지 확인. 있으면 사용자에게 알리고 중단.
   - `git fetch origin && git checkout main && git pull --ff-only` — 최신 main 확보.
   - `gh auth status` — 인증 확인.

2. **planner 서브에이전트 호출**

   `Agent` 도구를 `subagent_type: "planner"`로 호출. 프롬프트:

   ```
   이번 주 saboteur에 추가할 기능 후보를 3~5개 발굴해서 GitHub Issue로 등록해줘.

   필수:
   - 기존 오픈/최근 닫힌 Issue와 중복되지 않을 것
   - 각 Issue 본문에 Motivation / Scope / Acceptance Criteria / Risk / Estimated Size 섹션 포함
   - 라벨 'proposed' + 카테고리 라벨 부착
   - 라벨이 없으면 먼저 생성

   완료 후 생성된 Issue 번호와 제목 목록만 반환해줘.
   ```

3. **결과 요약**

   planner의 응답을 받아 사용자에게 다음 형식으로 보고:

   ```
   📋 Weekly planning complete.

   Created issues (awaiting approval):
   - #N1 <title> (https://github.com/Ryu0n/saboteur/issues/N1)
   - #N2 ...

   다음 단계: 위 Issue를 검토하시고 진행할 것에 'approved' 라벨을 붙여주세요.
   라벨 부착 예: gh issue edit <num> --add-label approved
   ```

## 실패 처리

- planner가 Issue를 0개 생성했으면 사용자에게 사유와 함께 보고 (예: "기존 백로그에 이미 충분한 후보가 있어 새로 제안하지 않음").
- `gh` 인증 실패 등 환경 문제는 즉시 중단하고 사용자에게 알린다.

## 호출 빈도

매주 1회. 트리거 인프라(cron 등)는 별도로 구성됨 — 이 스킬은 트리거를 신경 쓰지 않는다.
