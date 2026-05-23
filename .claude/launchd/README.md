# launchd 자동화 설정

Mac에서 `/weekly-plan`과 `/build-approved`를 정해진 시각에 자동 실행하기 위한 `launchd` 설정.

## 구성

| 파일 | 역할 | 기본 일정 |
|---|---|---|
| `com.saboteur.weekly-plan.plist` | 매주 `/weekly-plan` 호출 (Issue 발굴) | 월요일 09:00 |
| `com.saboteur.build-approved.plist` | 매주 `/build-approved` 호출 (PR 생성 루프) | 금요일 09:00 |

두 plist는 **템플릿**입니다. `__HOME__`과 `__REPO__` 플레이스홀더가 들어있어 설치 시점에 `sed`로 실제 경로로 치환합니다.

## 사전 준비

이 머신(Mac mini)에서 한 번만 하면 되는 것들:

1. **자동 로그인 켜기** — `~/Library/LaunchAgents/`는 사용자 세션이 살아있을 때만 동작하므로, 재부팅 후에도 자동으로 로그인되어야 합니다. (시스템 설정 → 사용자 및 그룹 → 자동 로그인)
2. **Claude Code 구독 로그인** — `claude login`을 한 번 실행해서 구독 계정으로 인증. 이후 헤드리스 실행도 이 세션 자격증명을 씁니다.
3. **`gh` 인증** — `gh auth login`으로 GitHub CLI 인증. Issue/PR 작업에 필요합니다.
4. **로그 디렉토리** — 아래 설치 명령에 포함되어 있지만, 미리 만들어둬도 됩니다: `mkdir -p ~/Library/Logs`
5. **잠자기 정책 (선택)** — Mac mini가 잠자기로 가도 트리거 시각에 깨우려면:
   ```bash
   sudo pmset -a powernap 1     # 잠자기 중에도 예약 작업 실행
   sudo pmset -a sleep 0        # 또는 아예 잠자기 끄기 (Mac mini는 보통 이렇게 운영)
   ```

## 설치

레포지토리 루트에서 실행:

```bash
# 0. 변수
LA="$HOME/Library/LaunchAgents"
REPO="$(pwd)"

# 1. 디렉토리 준비
mkdir -p "$HOME/Library/Logs" "$LA"

# 2. 플레이스홀더 치환하며 LaunchAgents로 복사
for name in com.saboteur.weekly-plan com.saboteur.build-approved; do
  sed -e "s|__HOME__|$HOME|g" -e "s|__REPO__|$REPO|g" \
      ".claude/launchd/$name.plist" \
      > "$LA/$name.plist"
done

# 3. launchd에 등록
launchctl load "$LA/com.saboteur.weekly-plan.plist"
launchctl load "$LA/com.saboteur.build-approved.plist"

# 4. 등록 확인
launchctl list | grep saboteur
```

성공하면 `launchctl list` 출력에 두 줄이 보입니다:

```
-   0   com.saboteur.weekly-plan
-   0   com.saboteur.build-approved
```

(가운데 `0`은 마지막 종료 코드. 아직 실행 전이면 `-`)

## 검증 (수동 트리거)

스케줄을 기다리지 말고 지금 한 번 돌려서 동작을 확인:

```bash
launchctl start com.saboteur.weekly-plan
```

몇 초 뒤 로그 확인:

```bash
tail -f ~/Library/Logs/saboteur-weekly-plan.log
tail -f ~/Library/Logs/saboteur-weekly-plan.err.log
```

성공이면 GitHub Issue가 새로 등록됩니다. 실패면 `.err.log`에 사유가 찍힙니다.

## 운영

### 일정 변경

`StartCalendarInterval` 키만 수정한 뒤 reload:

| 키 | 의미 | 값 |
|---|---|---|
| `Weekday` | 요일 | 0=일, 1=월, ..., 6=토 |
| `Hour` | 시 (24h) | 0–23 |
| `Minute` | 분 | 0–59 |
| `Day` | 일 (월 중) | 1–31 (요일 대신 사용 가능) |

예: 화요일 14:30으로 바꾸려면 `Weekday=2`, `Hour=14`, `Minute=30`.

수정 후:

```bash
# 1. 레포의 템플릿 plist를 고치고 다시 sed 치환해서 LaunchAgents로 복사
# 2. unload → load
launchctl unload "$HOME/Library/LaunchAgents/com.saboteur.weekly-plan.plist"
launchctl load   "$HOME/Library/LaunchAgents/com.saboteur.weekly-plan.plist"
```

### 일시 중지 / 재개

휴가 등으로 일시 중단:

```bash
launchctl unload "$HOME/Library/LaunchAgents/com.saboteur.weekly-plan.plist"
launchctl unload "$HOME/Library/LaunchAgents/com.saboteur.build-approved.plist"
```

재개:

```bash
launchctl load "$HOME/Library/LaunchAgents/com.saboteur.weekly-plan.plist"
launchctl load "$HOME/Library/LaunchAgents/com.saboteur.build-approved.plist"
```

### 로그 위치

| 로그 | 경로 |
|---|---|
| weekly-plan stdout | `~/Library/Logs/saboteur-weekly-plan.log` |
| weekly-plan stderr | `~/Library/Logs/saboteur-weekly-plan.err.log` |
| build-approved stdout | `~/Library/Logs/saboteur-build-approved.log` |
| build-approved stderr | `~/Library/Logs/saboteur-build-approved.err.log` |

로그가 커지면 `logrotate`나 단순한 cron으로 주기적으로 회전시키세요. 1인 프로젝트 규모면 1~2달은 그냥 둬도 무방.

## 완전 제거

```bash
launchctl unload "$HOME/Library/LaunchAgents/com.saboteur.weekly-plan.plist"
launchctl unload "$HOME/Library/LaunchAgents/com.saboteur.build-approved.plist"
rm "$HOME/Library/LaunchAgents/com.saboteur.weekly-plan.plist"
rm "$HOME/Library/LaunchAgents/com.saboteur.build-approved.plist"
```

(레포 안의 `.claude/launchd/*.plist` 템플릿은 그대로 두면 됩니다.)

## 트러블슈팅

### `claude: command not found`가 err 로그에 찍힘

`launchd`로 띄운 zsh는 평소의 PATH를 갖지 못할 수 있습니다. 본 plist는 `/bin/zsh -l -c "..."`로 **login shell**을 띄우기 때문에 `.zprofile`/`.zshenv`가 로드되어 PATH가 잡혀야 정상입니다. 그래도 안 잡히면:

1. 어디 설치되어 있는지 확인: `which claude`
2. 그 절대경로를 plist의 명령에 직접 박기 (예: `/opt/homebrew/bin/claude -p ...`)
3. 또는 `EnvironmentVariables` 키를 plist에 추가해 PATH를 명시:
   ```xml
   <key>EnvironmentVariables</key>
   <dict>
     <key>PATH</key>
     <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
   </dict>
   ```

### 실행은 됐는데 권한 거부로 멈춤

프로젝트의 `.claude/settings.json` `allow` 목록에 필요한 명령이 다 들어있는지 확인하세요. 헤드리스 모드는 권한 프롬프트를 띄울 수 없어서, 목록에 없는 명령은 그냥 거부됩니다.

### 트리거 시각에 동작 안 함

- Mac mini가 그 시각에 잠자기였을 가능성. `pmset -g` 으로 현재 절전 정책 확인.
- 자동 로그인이 풀려있었을 가능성. 재부팅 후 사용자가 로그인된 상태인지 확인.
- `launchctl list | grep saboteur`로 작업이 여전히 등록되어 있는지 확인.

### 로그가 안 찍힘

`~/Library/Logs/` 디렉토리가 없으면 launchd가 stdout/stderr 리다이렉트에 실패합니다. `mkdir -p ~/Library/Logs` 한 번 실행.

## 모던 launchctl 문법 (참고)

위 가이드는 macOS Catalina 이전부터 동작하는 클래식 `load`/`unload` 명령을 사용했습니다. 모던 문법(Catalina 이후 권장)을 쓰고 싶으면:

```bash
# load 대신
launchctl bootstrap "gui/$(id -u)" ~/Library/LaunchAgents/com.saboteur.weekly-plan.plist

# unload 대신
launchctl bootout "gui/$(id -u)/com.saboteur.weekly-plan"

# start 대신
launchctl kickstart "gui/$(id -u)/com.saboteur.weekly-plan"
```

기능은 동일합니다.
