#!/bin/bash

# Colors

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
RESET='\033[0m'
BOLD='\033[1m'

clear
# ASCII Art for MiniGaeHub
printf "%b" "${BOLD}${CYAN}"
cat << 'EOF'
 __  __ _       _  ____            _   _       _     
|  \/  (_)_ __ (_)/ ___| __ _  ___| | | |_   _| |__  
| |\/| | | '_ \| | |  _ / _` |/ _ \ |_| | | | | '_ \ 
| |  | | | | | | | |_| | (_| |  __/  _  | |_| | |_) |
|_|  |_|_|_| |_|_|\____|\__,_|\___|_| |_|\__,_|_.__/ 

EOF
printf "%b" "${RESET}"
printf "%b" "${BOLD}${CYAN}========================================\n"
printf "%b" "              PLAYER LOGIN              \n"
printf "%b" "========================================${RESET}\n\n"
printf "%b" "${YELLOW}Welcome! Two players must authenticate before starting the game hub.${RESET}\n\n"

ensure_data_file_exists() {
    mkdir -p data
    touch data/users.tsv
    touch data/history.csv
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
        if [[ -z "${value// }" ]]; then
            printf "%b" "${RED}Input cannot be empty. Please try again.${RESET}\n"
            continue
        fi
        printf "%s" "$value"
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
    printf "%s" "$1" | sha256sum | awk '{print $1}'
}

register_user() {
    local username="$1"
    local sha_user
    sha_user=$(hash_value "$username")

    echo
    if ! prompt_yes_no "User not found. Would you like to register? (y/n):"; then
        return 1
    fi

    local password confirm
    password="$(read_nonempty_password "Enter new password: ")"
    printf "\n"
    confirm="$(read_nonempty_password "Confirm password: ")"

    if [[ "$password" != "$confirm" ]]; then
        printf "%b" "${RED}Passwords do not match. Please try again.${RESET}\n" >&2
        return 1
    fi

    local sha_pass
    sha_pass=$(hash_value "$password")
    echo -e "${sha_user}\t${sha_pass}" >> data/users.tsv

    printf "%b" "${GREEN}Registration successful! You are now logged in as ${username}.${RESET}\n" >&2
    echo "$username:$sha_user"
    return 0
}

login_user() {
    local username
    username="$(read_nonempty "Enter username: ")"

    local sha_user
    sha_user=$(hash_value "$username")

    local found=0
    local stored_user stored_pass

    while IFS=$'\t' read -r stored_user stored_pass; do
        if [[ "$sha_user" == "$stored_user" ]]; then
            found=1
            break
        fi
    done < data/users.tsv

    if [[ $found -eq 0 ]]; then
        local login_result
        login_result="$(register_user "$username")" || return 1
        printf "%s" "$login_result"
        return 0
    fi

    local password
    password="$(read_nonempty_password "Enter password: ")"

    local sha_pass
    sha_pass=$(hash_value "$password")

    if [[ "$sha_pass" != "$stored_pass" ]]; then
        printf "%b" "${RED}Incorrect password. Authentication failed.${RESET}\n" >&2
        return 1
    fi

    printf "%b" "${GREEN}Login successful!${RESET}\n" >&2
    echo "$username:$sha_user"
    return 0
}

ensure_data_file_exists
prepare_venv
install_dependency numpy
install_dependency pygame

user1_data="$(login_user)" || exit 1
echo
user2_data="$(login_user)" || exit 1

user1="${user1_data%%:*}"
sha_user1="${user1_data##*:}"
user2="${user2_data%%:*}"
sha_user2="${user2_data##*:}"

if [[ "$sha_user1" == "$sha_user2" ]]; then
    printf "%b" "${RED}Error: Both players cannot be the same user.${RESET}\n"
    exit 1
fi

printf "%b" "${GREEN}\nBoth users authenticated successfully! Launching the game...${RESET}\n\n"
python3 game.py "$user1" "$user2"
