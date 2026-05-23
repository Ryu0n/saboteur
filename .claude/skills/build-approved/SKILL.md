---
name: build-approved
description: 'approved' 라벨이 붙은 GitHub Issue 각각에 대해 developer → tester → reviewer 루프를 돌려 draft PR을 만든다. 최대 3회 반복하며, 실패시 draft PR로 남기고 멈춘다.
disable-model-invocation: true
---

# build-approved

승인된 Issue들을 받아 자동 구현/리뷰/테스트 루프를 실행합니다.

## 사전 조건

- `weekly-plan` 스킬이 먼저 실행되어 `approved` 라벨이 붙은 Issue가 존재해야 함
- `gh` CLI 인증 완료
- 기본 브랜치(`main`)가 깨끗한 상태

## 파라미터 (상수)

- `MAX_ITERATIONS = 3` — Issue 1개당 dev↔test↔review 루프 최대 횟수
- `PR_UNIT = 1 issue per PR` — 한 PR에 여러 Issue 묶지 않음

## 실행 단계

### Step 1. 대상 Issue 수집

```bash
gh issue list --label approved --state open --json number,title,labels
```

다음 항목은 **반드시 제외**:

- **`epic` 라벨이 붙은 Issue**. epic은 PR을 만들지 않는 조직용 Issue다. epic은 사람의 승인 신호로만 쓰이고, 실제 작업은 그 epic의 sub-issue(`Part of #<epic-num>` + `new-domain` 라벨)에서 일어난다.
- 이미 PR이 존재하는 Issue (각 Issue에 대해 `gh pr list --search "closes #<num>"` 또는 PR 본문에서 `Closes #<num>` 검색).

대상이 0개면 사용자에게 알리고 종료. (epic만 승인된 상태라면 "epic은 승인됐지만 sub-issue가 아직 없습니다. 다음 `/weekly-plan` 실행 시 sub-issue가 생성됩니다"라고 안내.)

### Step 2. 각 Issue에 대해 루프 실행

각 Issue를 순차 처리 (병렬은 머지 충돌 위험 때문에 피한다):

```
for issue in approved_issues:
    pr_num = None
    last_feedback = None

    for iteration in 1..MAX_ITERATIONS:
        if iteration == 1:
            # 최초 구현
            call developer agent:
                "Issue #<num>를 구현하고 draft PR을 만들어줘."
            → pr_num 수령
        else:
            # 피드백 반영
            call developer agent:
                "이전 PR #<pr_num>에 대한 피드백을 반영해줘:
                <last_feedback>"

        # 테스트
        call tester agent:
            "PR #<pr_num>을 실행해줘."
        → tester_result

        if tester_result == FAIL:
            last_feedback = tester_result.log
            continue

        # 리뷰
        call reviewer agent:
            "PR #<pr_num>를 리뷰해줘."
        → reviewer_result

        if reviewer_result == CHANGES_REQUESTED:
            last_feedback = reviewer_result.fix_list
            continue

        # 둘 다 통과
        gh pr ready <pr_num>
        gh pr edit <pr_num> --add-label merge-ready --remove-label automated
        gh issue edit <num> --remove-label approved --add-label in-pr
        break

    else:
        # MAX_ITERATIONS 도달
        gh pr comment <pr_num> --body "⚠️ Automated loop exhausted after ${MAX_ITERATIONS} iterations. Last failure:\n\n${last_feedback}\n\nHuman intervention needed."
        gh pr edit <pr_num> --add-label blocked
        gh issue edit <num> --add-label blocked
```

### Step 3. 최종 보고

처리 완료 후 사용자에게 요약:

```
🛠️ Build cycle complete.

Ready for human merge (N개):
- PR #X1 <title>  (Issue #N1)
- PR #X2 ...

Blocked, needs intervention (M개):
- PR #Y1 <title>  (Issue #N3) — last failure: <짧은 사유>
- ...

다음 단계:
- ready PR은 검토 후 merge
- blocked PR은 코멘트 확인 후 수동 개입
```

## 안전 가드

- **main 브랜치 직접 변경 절대 금지.** 모든 작업은 `auto/issue-<num>-*` 브랜치에서.
- **force push 금지.**
- **draft PR을 자동으로 ready 상태로 바꾸는 것은 review+test 모두 통과한 경우에 한정.**
- 한 사이클에서 처리할 Issue 수 상한선 없음 (planner가 알아서 3~5개로 제한). 다만 안전을 위해 한 번에 5개 초과 시 사용자 확인 요구.

## 실패 처리

- developer가 PR 생성 자체에 실패하면 (예: 빌드 불가 코드만 생성) 해당 Issue는 건너뛰고 사용자에게 보고.
- 네트워크 / `gh` 인증 등 환경 문제는 즉시 중단.

## 호출 빈도

매주 1회 (`weekly-plan` 실행 후 사람이 승인 라벨을 붙인 후). 트리거 인프라는 별도.
