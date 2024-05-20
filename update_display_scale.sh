#!/bin/bash
if [ -z "$1" ]; then
    echo "enter a scale"
    exit 1
fi
scale=$1
# idea Dide.ui.scale (too lazy to read)
UI_SCALE=.5
adjusted_scale=$(echo "scale=1; $scale / $UI_SCALE" | bc)
NUM_MATCH="[0-9.]*"
echo "writing new scale $scale"
# update scale env var in .bashrc
sed -i "s/^SCALE=${NUM_MATCH}$/SCALE=$scale/" "$HOME/.bashrc"
# update scaling for current ghidra (based on ghidra in path)
sed -i "s/^\(VMARGS_LINUX=-Dsun.java2d.uiScale\)=${NUM_MATCH}$/\1=$scale/" "$(dirname $(readlink -e $(which ghidra)))/support/launch.properties"
# update vm options in all idea installs
for i in .config/JetBrains/*/idea64.vmoptions; do
    # returns 0 if present
    grep -qF -- "-Dsun.java2d.uiScale=" "$i"
    present=$?
    if [ $present -eq 0 ]; then
        # present, replace
        sed -i "s/^\(-Dsun.java2d.uiScale\)=${NUM_MATCH}$/\1=$adjusted_scale/" "$i"
    else
        # not present, append
        echo "-Dsun.java2d.uiScale=$adjusted_scale" >> "$i"
    fi
done
# search projects dir for idea projects
for i in $(find $HOME/projects -path "*.idea/workspace.xml"); do
    # update GDK_SCALE for idea projects
    sed -i "s/\(.*\)\(<entry key=\"GDK_SCALE\" value\)=\"${NUM_MATCH}\(\" \/>\)/\1\2=\"$scale\3/" "$i"
done
