#!/usr/bin/bash

# requires zenity, kinit
user_input=$(zenity --password --title="Enter kerberos password")
if [ $? = 0 ]; then
    # OK
    stderr=$(echo $user_input | kinit 2>&1 >/dev/null)
    if [ -n "$stderr" ]; then
        zenity --warning --text="kinit returned error: $stderr"
    fi
fi
