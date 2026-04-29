#!/bin/bash

# Launcher and authentication script for Mini Gae Hub.
# This script ensures dependencies are installed, user files exist, and
# both players are authenticated before launching the Python game hub.

# Colors

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
RESET='\033[0m'
BOLD='\033[1m'

get_term_width() {
    local w
    w="$( (tput cols 2>/dev/null || echo 80) )"
    if [[ -z "$w" || "$w" -lt 50 ]]; then
        echo 80
    else
        echo "$w"
    fi
}

draw_border_line() {
    local width="$1"
    local line
    line="$(printf '=%.0s' $(seq 1 "$width"))"
    printf "%b%s%b\n" "${CYAN}" "$line" "${RESET}"
}

center_text() {
    local width="$1"
    local text="$2"
    local text_len=${#text}
    local pad=$(( (width - text_len) / 2 ))
    if [[ $pad -lt 0 ]]; then pad=0; fi
    printf "%*s%s\n" "$pad" "" "$text"
}

draw_header() {
    clear
    BOX_WIDTH=70
    TERM_WIDTH="$(get_term_width)"
    if [[ "$TERM_WIDTH" -lt "$BOX_WIDTH" ]]; then
        BOX_WIDTH="$TERM_WIDTH"
    fi

    draw_border_line "$BOX_WIDTH"
    printf "%b" "${BOLD}${CYAN}"
    center_text "$BOX_WIDTH" "              PLAYER LOGIN              "
    printf "%b" "${RESET}\n"
    draw_border_line "$BOX_WIDTH"

    printf "%b" "${BOLD}${CYAN}"
    cat << 'EOF'
 __  __ _       _  ____                      _   _       _     
|  \/  (_)_ __ (_)/ ___| __ _ _ __ ___   ___| | | |_   _| |__  
| |\/| | | '_ \| | |  _ / _` | '_ ` _ \ / _ \ |_| | | | | '_ \ 
| |  | | | | | | | |_| | (_| | | | | | |  __/  _  | |_| | |_) |
|_|  |_|_|_| |_|_|\____|\__,_|_| |_| |_|\___|_| |_|\__,_|_.__/

EOF
    printf "%b" "${RESET}"

    printf "%b" "${YELLOW}Welcome! Two players must authenticate before starting the game hub.${RESET}\n"
}

draw_login_panel() {
    local player_name="$1"
    draw_border_line "$BOX_WIDTH"
    printf "%b" "${BOLD}${CYAN}"
    center_text "$BOX_WIDTH" " ${player_name} - AUTHENTICATION "
    printf "%b" "${RESET}\n"
    draw_border_line "$BOX_WIDTH"
}

draw_header

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
DATA_DIR="$DIR/data"
USERS_PATH="$DATA_DIR/users.tsv"
HISTORY_PATH="$DATA_DIR/history.csv"

# Ensure persistence files exist before login or game startup.
ensure_data_file_exists() {
    mkdir -p "$DATA_DIR"
    touch "$USERS_PATH"
    touch "$HISTORY_PATH"
}

prepare_venv() {
    if [[ ! -f venv/bin/activate || ! -f venv/bin/python || ! -f venv/bin/pip ]]; then
        printf "%b" "${CYAN}Setting up virtual environment...${RESET}\n"
        rm -rf venv
        python3 -m venv venv
    fi
    source venv/bin/activate
}

install_dependency() {
    local package="$1"
    # Use the virtual environment's Python to test for package availability.
    if ! python -c "import ${package}" >/dev/null 2>&1; then
        printf "%b" "${CYAN}Installing ${package}...${RESET}\n"
        pip install "${package}"
    fi
}

prompt_yes_no() {
    local prompt="$1"
    local answer
    while true; do
        read -rp "${prompt} " answer
        case "${answer,,}" in
            y|yes) return 0 ;; 
            n|no) return 1 ;; 
            *) echo "Please enter y or n." ;; 
        esac
    done
}

read_nonempty() {
    local prompt="$1"
    local value
    while true; do
        read -rp "$prompt" value
        local cleaned
        cleaned="$(printf '%s' "$value" | tr -d '[:cntrl:]' | sed 's/[^A-Za-z0-9 _.-]//g')"
        if [[ "$value" != "$cleaned" ]]; then
            printf "%b" "${RED}Username may only contain letters, numbers, spaces, dot, underscore, or hyphen. Please try again.${RESET}\n"
            continue
        fi
        if [[ -z "${cleaned// }" ]]; then
            printf "%b" "${RED}Input cannot be empty. Please try again.${RESET}\n"
            continue
        fi
        printf "%s" "$cleaned"
        return 0
    done
}

read_nonempty_password() {
    local prompt="$1"
    local value
    while true; do
        read -rsp "$prompt" value
        printf "\n" >&2
        if [[ -z "$value" ]]; then
            printf "%b" "${RED}Input cannot be empty. Please try again.${RESET}\n" >&2
            continue
        fi
        printf "%s" "$value"
        return 0
    done
}

hash_value() {
    # Create a fixed-length SHA-256 fingerprint for usernames and passwords.
    printf "%s" "$1" | sha256sum | awk '{print $1}'
}

register_user() {
    local player_name="$1"
    local username="$2"
    local sha_user
    sha_user=$(hash_value "$username")

    echo
    if ! prompt_yes_no "${player_name}: user not found. Register now? (y/n):"; then
        return 1
    fi

    local password confirm
    password="$(read_nonempty_password "${player_name}: enter new password: ")"
    printf "\n"
    confirm="$(read_nonempty_password "${player_name}: confirm password: ")"

    if [[ "$password" != "$confirm" ]]; then
        printf "%b" "${RED}${player_name}: passwords do not match. Please try again.${RESET}\n" >&2
        return 1
    fi

    local sha_pass
    sha_pass=$(hash_value "$password")
    # Save username hash and password hash separated by tab.
    printf '%s\t%s\n' "$sha_user" "$sha_pass" >> "$USERS_PATH"

    printf "%b" "${GREEN}${player_name}: registration successful! Logged in as ${username}.${RESET}\n" >&2
    echo "$username:$sha_user"
    return 0
}

login_user() {
    local player_name="$1"
    local username
    username="$(read_nonempty "${player_name}: enter username: ")"

    local sha_user
    sha_user=$(hash_value "$username")

    local found=0
    local stored_user stored_pass

    # Search for existing user hash in the stored credentials file.
    while IFS=$'\t' read -r stored_user stored_pass; do
        if [[ "$sha_user" == "$stored_user" ]]; then
            found=1
            break
        fi
    done < "$USERS_PATH"

    if [[ $found -eq 0 ]]; then
        local login_result
        login_result="$(register_user "$player_name" "$username")" || return 1
        printf "%s" "$login_result"
        return 0
    fi

    local password
    password="$(read_nonempty_password "${player_name}: enter password: ")"

    local sha_pass
    sha_pass=$(hash_value "$password")

    if [[ "$sha_pass" != "$stored_pass" ]]; then
        printf "%b" "${RED}${player_name}: incorrect password. Authentication failed.${RESET}\n" >&2
        return 1
    fi

    printf "%b" "${GREEN}${player_name}: login successful!${RESET}\n" >&2
    echo "$username:$sha_user"
    return 0
}

ensure_data_file_exists
prepare_venv
install_dependency numpy
install_dependency pygame
install_dependency matplotlib

draw_login_panel "Player 1"
user1_data="$(login_user "Player 1")" || exit 1
echo
draw_login_panel "Player 2"
user2_data="$(login_user "Player 2")" || exit 1

user1="${user1_data%%:*}"
sha_user1="${user1_data##*:}"
user2="${user2_data%%:*}"
sha_user2="${user2_data##*:}"

if [[ "$sha_user1" == "$sha_user2" ]]; then
    printf "%b" "${RED}Error: Both players cannot be the same user.${RESET}\n"
    exit 1
fi

printf "%b" "${GREEN}\nBoth users authenticated successfully! Launching the game...${RESET}\n\n"
python3 src/game.py "$user1" "$user2"
