#!/bin/sh
if ! ([ -f ".gitmodules" ] && [ -d ".git" ]); then
    echo ".gitmodules doesn't exist or no .git directory found"
    echo "This must be run within the base directory of the git project"
    exit 1
fi
for submodule in $(sed -n 's/.*path = //p' .gitmodules); do
    if ! [ -f ${submodule}/.git ]; then
        echo "Failed on submodule $submodule, no git directory found"
        echo "Submodule(s) probably not initted/updated"
        exit 1
    fi
    echo "Converting $submodule to directory..."
    git rm --cached ${submodule} 
    rm -rf ${submodule}/.git
    git add ${submodule}
done
git rm .gitmodules
echo "Done, now do a commit to finalize the changes"
