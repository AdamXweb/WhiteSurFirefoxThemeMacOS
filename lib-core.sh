MY_USERNAME="$(logname 2> /dev/null || echo ${SUDO_USER:-${USER}})"
FIREFOX_DIR_HOME="/Users/${MY_USERNAME}/Library/Application Support/Firefox/Profiles"
FIREFOX_O_HOME=/Users/${MY_USERNAME}/Library/'Application Support'/Firefox/Profiles/
FIREFOX_THEME_HOME="/Users/${MY_USERNAME}/Library/Application\ Support/Firefox/Profiles"
FIREFOX_SRC_DIR="${REPO_DIR}"
LOC=""

# Colors
ESC_SEQ="\x1b["
COL_RESET=$ESC_SEQ"39;49;00m"
COL_RED=$ESC_SEQ"31;01m"
COL_GREEN=$ESC_SEQ"32;01m"
COL_LIGHTP=$ESC_SEQ"1;35m"
COL_LIGHTG=$ESC_SEQ"1;32m"
COL_YELLOW=$ESC_SEQ"33;01m"
COL_ORANGE=$ESC_SEQ"35;51m"
COL_BLUE=$ESC_SEQ"1;34m"
bold=$(tput bold)
normal=$(tput sgr0)

function warn() {
  echo -e "$COL_ORANGE[warning]$COL_RESET $1"
}
function success() {
  echo -e "$COL_GREEN[success]$COL_RESET $1"
}
function error() {
  echo -e "$COL_RED[error]$COL_RESET $1"
}
function actioninfo() {
  echo -e "$COL_YELLOW[action]:$COL_RESET ⇒ $1"
}
function cancelled() {
  echo -e "$COL_RED[cancelled]$COL_RESET $1"
}
has_command() {
  "$1" -v $1 > /dev/null 2>&1
}


userify() {
  trap true SIGINT
  sudo -u "${MY_USERNAME}" ${@} 2> "${REPO_DIR}/error_log.txt" || operation_canceled
  trap sig_c SIGINT
}

sig_c() {
  kill -13 ${process_ids[*]} &> /dev/null
  stop_animation; wait ${process_ids[*]} &> /dev/null; operation_canceled
}

operation_canceled() {
  clear

  if [[ -f "${WHITESUR_TMP_DIR}/error_log.txt" ]]; then
    error_msg="$(cat "${WHITESUR_TMP_DIR}/error_log.txt")"
  fi

  if [[ ${error_msg} != "" ]]; then
    error "Oops! An error is detected..."
    error "ERROR LOG:\n${error_msg}\n"
    error "TIP: you can google or report to us the error log above\n\n"
  else
    cancelled "\n\n  Oops! Operation has been canceled or failed...\n\n"
  fi

  exit 1
}