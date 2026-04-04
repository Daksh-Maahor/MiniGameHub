#!/bin/bash

if [[ ! -f venv/bin/activate || ! -f venv/bin/python || ! -f venv/bin/pip ]]
then
    rm -rf venv
    python3 -m venv venv
fi

source venv/bin/activate

if [ ! -d venv/lib/python*/site-packages/numpy ]
then
    pip install numpy
fi

if [ ! -d venv/lib/python*/site-packages/pygame ]
then
    pip install pygame
fi

hash() {
    printf "%s" "$1" | sha256sum | awk '{print $1}'
}

register() {
    local username="$1"
    local sha_user
    sha_user=$(hash "$username")

    echo "User not found. Do you want to register? (y/n)"
    read -r choice

    if [[ "$choice" != "y" ]]
    then
        return 1
    fi

    local password confirm
    read -sp "Enter new password: " password
    echo
    read -sp "Confirm password: " confirm
    echo

    if [[ "$password" != "$confirm" ]]
    then
        echo "Passwords do not match!"
        return 1
    fi

    local sha_pass
    sha_pass=$(hash "$password")

    # Append to database
    echo -e "${sha_user}\t${sha_pass}" >> users.tsv

    echo "Registration successful!"
    echo "$sha_user"
    return 0
}

login() {
    local username
    read -p "Enter username: " username

    echo "Hashing username..."

    local sha_user
    sha_user=$(hash "$username")

    local found=0
    local stored_user stored_pass

    echo "Checking user in database..."

    while IFS=$'\t' read -r stored_user stored_pass
    do
        if [[ "$sha_user" == "$stored_user" ]]
        then
            found=1
            break
        fi
    done < users.tsv

    echo "User check complete."

    if [[ $found -eq 0 ]]
    then
        register "$username" || return 1
    else
        local password
        read -sp "Enter password: " password
        echo

        local sha_pass
        sha_pass=$(hash "$password")

        if [[ "$sha_pass" != "$stored_pass" ]]
        then
            echo "Incorrect Password!!!"
            return 1
        fi

        echo "Login successful!!"
    fi

    echo "$username:$sha_user"
    return 0
}

user1_data=$(login) || exit 1
user2_data=$(login) || exit 1

user1="${user1_data%%:*}"
sha_user1="${user1_data##*:}"

user2="${user2_data%%:*}"
sha_user2="${user2_data##*:}"

if [[ "$sha_user1" == "$sha_user2" ]]
then
    echo "Both users cannot be same"
    exit 1
fi

echo "Both users authenticated successfully!"

python3 game.py "$user1" "$user2"
