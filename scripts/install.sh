#!/bin/bash
# FM27 Match Lab: install or update on macOS, in one line.
#
#   curl -fsSL https://raw.githubusercontent.com/caiograco289/Fm-Match-Lab/main/scripts/install.sh | bash
#
# What it does (nothing else, and nothing outside the folders named here):
#   1. checks that FM27 is installed through Steam, Steam is running and FM27 is closed;
#   2. installs Apple's command line developer tools if missing (needed to build the engine host from source), and
#      Rosetta 2 on Apple Silicon Macs (the engine host is an Intel program);
#   3. installs uv (https://docs.astral.sh/uv/) into ~/.local/bin if missing, and uses it to get Python 3.12;
#   4. downloads the app into ~/Fm-Match-Lab (or updates it there with git pull), with its own Python environment;
#   5. runs the app's set-up (scripts/setup.py), which builds everything from source on your Mac;
#   6. puts "FM27 Match Lab.command" on your Desktop: double-click it to start the app.
#
# Running it again is safe: it updates the app and reruns the set-up. That is also how to update after an FM27 patch.
# It never changes the FM27 install and never bypasses Steam.
#
# Options, as environment variables: FM27_LAB_DIR (install folder), FM27_LAB_REPO (git URL to clone),
# FM27_LAB_SHORTCUT_DIR (where the shortcut goes; default your Desktop).

set -uo pipefail

REPO="${FM27_LAB_REPO:-https://github.com/caiograco289/Fm-Match-Lab.git}"
DIR="${FM27_LAB_DIR:-$HOME/Fm-Match-Lab}"
SHORTCUT_DIR="${FM27_LAB_SHORTCUT_DIR:-$HOME/Desktop}"
ISSUES="https://github.com/caiograco289/Fm-Match-Lab/issues"
LINE="curl -fsSL https://raw.githubusercontent.com/caiograco289/Fm-Match-Lab/main/scripts/install.sh | bash"
UV_VERSION="0.10.3"
PACKAGES=(UnityPy==1.25.4 numpy==2.5.4)
LOG="$HOME/Library/Logs/FM27 Match Lab install.log"
STEPS=6

bold=$'\033[1m'; red=$'\033[31m'; green=$'\033[32m'; plain=$'\033[0m'

step() { printf '\n%sStep %s of %s: %s%s\n' "$bold" "$1" "$STEPS" "$2" "$plain"; }
say() { printf '  %s\n' "$*"; }

# Something the user can fix themselves (FM27 open, no saved match): say what to do, no bug report.
stop() { printf '\n%s%s%s\n' "$red" "$*" "$plain"; printf 'Then run the same line again:\n  %s\n' "$LINE"; exit 1; }

# Anything else: show the end of the log (home folder hidden), copy it, and say where to send it.
fail() {
  printf '\n%sThe installation stopped: %s%s\n' "$red" "$1" "$plain"
  local report
  sleep 1   # let the log catch up
  report="$(printf 'FM27 Match Lab install failed: %s\nmacOS %s, %s\n\n' "$1" "$(sw_vers -productVersion 2>/dev/null)" "$(uname -m)"
            tail -n "+$FIRST_LINE" "$LOG" 2>/dev/null | grep -v 'The installation stopped' | tail -n 40 | sed "s/$(printf '\033')\[[0-9;]*m//g")"
  report="${report//"$HOME"/~}"
  printf '%s' "$report" | pbcopy 2>/dev/null
  cat <<EOF

What to send: the report below, already copied to your clipboard. Paste it in a new issue at
  $ISSUES
Your Mac's home folder is shown as ~. Read it before posting: it may name clubs from your saved matches.
The full log is in ~/Library/Logs/FM27 Match Lab install.log.
---------------------------------------- copy from here
$report
---------------------------------------- to here
EOF
  exit 1
}

# Wait for a condition (checked every 5 seconds), up to a limit in minutes.
wait_for() {
  local minutes="$1"; shift
  local i
  for ((i = 0; i < minutes * 12; i++)); do "$@" && return 0; sleep 5; done
  return 1
}

game_folder() {
  local lib folders=("$HOME/Library/Application Support/Steam")
  local vdf="$HOME/Library/Application Support/Steam/steamapps/libraryfolders.vdf"
  if [ -f "$vdf" ]; then
    while IFS= read -r lib; do folders+=("$lib"); done < <(sed -n 's/^[[:space:]]*"path"[[:space:]]*"\(.*\)"[[:space:]]*$/\1/p' "$vdf")
  fi
  for lib in "${folders[@]}"; do
    if [ -f "$lib/steamapps/common/Football Manager 27/fm.app/Contents/PlugIns/game_plugin.bundle/Contents/MacOS/game_plugin" ]; then
      printf '%s\n' "$lib/steamapps/common/Football Manager 27"; return 0
    fi
  done
  return 1
}
fm27_running() { pgrep -f 'fm.app/Contents/MacOS/Football Manager 27' >/dev/null 2>&1; }
steam_running() { pgrep -x steam_osx >/dev/null 2>&1; }
developer_tools() { xcode-select -p >/dev/null 2>&1 && xcrun --find clang++ >/dev/null 2>&1; }
rosetta() { arch -x86_64 /usr/bin/true >/dev/null 2>&1; }
saved_match() {
  local f
  for f in "$HOME/Library/Application Support/Sports Interactive/Football Manager 27/matches/automatic" "$HOME/fm27-port-work/saved_matches"; do
    [ -d "$f" ] && [ -n "$(find "$f" -name '*_fm.pkm' -print -quit 2>/dev/null)" ] && return 0
  done
  return 1
}

main() {
  mkdir -p "$(dirname "$LOG")"
  printf '\n==== %s\n' "$(date)" >> "$LOG"
  FIRST_LINE=$(($(wc -l < "$LOG") + 1))   # the failure report shows only this run
  exec > >(tee -a "$LOG") 2>&1

  printf '%sFM27 Match Lab: install or update%s\n' "$bold" "$plain"
  say "This takes 5 to 20 minutes the first time. Progress is also written to ~/Library/Logs/FM27 Match Lab install.log."

  step 1 "Checking your Mac, Steam and FM27"
  [ "$(uname -s)" = Darwin ] || stop "This installer is for macOS."
  local game
  game="$(game_folder)" || stop "FM27 wasn't found in your Steam libraries. Install Football Manager 27 through Steam."
  say "FM27 found: ${game//"$HOME"/~}"
  fm27_running && stop "Quit FM27 first (the set-up reads the game's files while it is closed)."
  if ! steam_running; then
    say "Steam isn't running: opening it. Log in if it asks; this continues by itself once Steam is running."
    open -a Steam >/dev/null 2>&1
    wait_for 10 steam_running || stop "Steam didn't start. Open Steam and log in."
    sleep 10
  fi
  say "Steam is running and FM27 is closed."
  if [ ! -f "$DIR/private/engine/fm27_native/fixtures/match.pkm" ] && ! saved_match; then
    stop "FM27 has no saved match yet. Play one match in FM27 first (instant result is fine), then quit FM27."
  fi

  step 2 "Developer tools"
  if developer_tools; then
    say "Apple's command line developer tools are installed."
  else
    xcode-select --install >/dev/null 2>&1
    say "A window has opened asking to install the command line developer tools."
    say "Click ${bold}Install${plain}, then ${bold}Agree${plain}. It takes 5 to 15 minutes; this continues by itself when it's done."
    say "(No window? It may be behind this one, or open System Settings > General > Software Update.)"
    wait_for 60 developer_tools || fail "the command line developer tools were not installed within an hour"
    say "Developer tools installed."
  fi
  if [ "$(uname -m)" = arm64 ]; then
    if rosetta; then
      say "Rosetta 2 is installed."
    else
      say "Installing Rosetta 2 (Apple's translator for Intel programs). Your Mac password may be asked;"
      say "nothing shows while you type it. Press Return when done."
      sudo softwareupdate --install-rosetta --agree-to-license || fail "Rosetta 2 could not be installed"
      rosetta || fail "Rosetta 2 was installed but doesn't run"
    fi
  fi

  step 3 "Python 3.12"
  local uv
  uv="$(command -v uv || true)"
  [ -z "$uv" ] && [ -x "$HOME/.local/bin/uv" ] && uv="$HOME/.local/bin/uv"
  if [ -z "$uv" ]; then
    say "Installing uv (a small Python installer) into ~/.local/bin."
    curl -fsSL "https://astral.sh/uv/$UV_VERSION/install.sh" | env UV_NO_MODIFY_PATH=1 sh || fail "uv could not be installed"
    uv="$HOME/.local/bin/uv"
    [ -x "$uv" ] || fail "uv was installed but isn't in ~/.local/bin"
  fi
  "$uv" python install 3.12 || fail "Python 3.12 could not be installed"
  say "Python 3.12 is ready."

  step 4 "Downloading FM27 Match Lab"
  if [ -d "$DIR/.git" ]; then
    say "Updating ${DIR//"$HOME"/~}."
    git -C "$DIR" pull --ff-only || fail "the app folder could not be updated (did you change files in it?)"
  elif [ -e "$DIR" ]; then
    stop "${DIR//"$HOME"/~} already exists but isn't FM27 Match Lab. Move or rename it."
  else
    git clone "$REPO" "$DIR" || fail "the app could not be downloaded"
  fi
  cd "$DIR" || fail "the app folder can't be opened"
  if ! .venv/bin/python -c 'import sys; sys.exit(sys.version_info[:2] != (3, 12))' >/dev/null 2>&1; then
    if [ -e .venv ]; then mv .venv ".venv.old-$(date +%Y%m%d-%H%M%S)" || fail "the old Python environment could not be moved aside"; fi
    "$uv" venv --managed-python --python 3.12 --seed .venv || fail "the Python environment could not be created"
  fi
  "$uv" pip install --python .venv/bin/python "${PACKAGES[@]}" || fail "the Python packages could not be installed"
  say "App and Python environment ready in ${DIR//"$HOME"/~}."

  step 5 "Setting up the engine from your FM27 install (a few minutes)"
  fm27_running && stop "Quit FM27 first (it was opened during the installation)."
  .venv/bin/python scripts/setup.py || fail "the set-up (scripts/setup.py) failed"

  step 6 "Desktop shortcut"
  mkdir -p "$SHORTCUT_DIR"
  local shortcut="$SHORTCUT_DIR/FM27 Match Lab.command"
  cat > "$shortcut" <<EOF || fail "the Desktop shortcut could not be written"
#!/bin/bash
# Starts FM27 Match Lab (written by scripts/install.sh). Close this window to stop the app.
cd "$DIR" || { echo "FM27 Match Lab isn't in $DIR any more. Install it again: $LINE"; exit 1; }
URL=http://127.0.0.1:18765
if curl -fs -o /dev/null "\$URL"; then echo "FM27 Match Lab is already running."; open "\$URL"; exit 0; fi
echo "Starting FM27 Match Lab..."
( for i in \$(seq 120); do sleep 1
    if curl -fs -o /dev/null "\$URL"; then open "\$URL"
      printf '\nFM27 Match Lab is open in your browser at %s\nClose this window to stop the app.\n\n' "\$URL"; exit; fi
  done ) &
.venv/bin/python scripts/run.py
echo
echo "FM27 Match Lab has stopped. If it says FM27 has been updated since the set-up, run the install line again:"
echo "  $LINE"
EOF
  chmod +x "$shortcut" || fail "the Desktop shortcut could not be made runnable"
  say "Made: ${shortcut//"$HOME"/~}"

  printf '\n%sDone.%s Double-click %sFM27 Match Lab%s on your Desktop to start the app; it opens in your browser.\n' "$green" "$plain" "$bold" "$plain"
  say "Steam must be running when you use it. To update the app, or after an FM27 patch, run the same line again."
}

main "$@" < /dev/null
