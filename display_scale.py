#!/usr/bin/python3
# Note: use system python3, not /usr/bin/env, because whichever python3 is on
# $PATH may not have dbus, but the system python3 does.

"""Toggle display scaling

Based on https://gist.github.com/strycore/ca11203fd63cafcac76d4b04235d8759

For data structure definitions, see
https://gitlab.gnome.org/GNOME/mutter/blob/master/src/org.gnome.Mutter.DisplayConfig.xml
"""

import os
import sys

import dbus


def usage():
    print(f"{sys.argv[0]} <scale_float>")
    sys.exit(1)


if len(sys.argv) == 1:
    scale = None
elif len(sys.argv) == 2:
    try:
        scale = float(sys.argv[1])
    except ValueError:
        usage()
else:
    usage()
namespace = "org.gnome.Mutter.DisplayConfig"
dbus_path = "/org/gnome/Mutter/DisplayConfig"

session_bus = dbus.SessionBus()
obj = session_bus.get_object(namespace, dbus_path)
interface = dbus.Interface(obj, dbus_interface=namespace)

current_state = interface.GetCurrentState()
serial = current_state[0]
connected_monitors = current_state[1]
logical_monitors = current_state[2]

# Multiple monitors are more complicated. For now, since I only use one monitor
# in Ubuntu, everything is hard-coded so that only info about the first monitor
# is used, and only it will be connected after running the script.
#
# If someday updating this script: a logical monitor may appear on mutiple
# connected monitors due to mirroring.
connector = connected_monitors[0][0][0]
current_mode = None
# ApplyMonitorsConfig() needs (connector name, mode ID) for each connected
# monitor of a logical monitor, but GetCurrentState() only returns the
# connector name for each connected monitor of a logical monitor. So iterate
# through the globally connected monitors to find the mode ID.
for mode in connected_monitors[0][1]:
    if mode[6].get("is-current", False):
        current_mode = mode[0]
updated_connected_monitors = [[connector, current_mode, {}]]

x, y, _scale, transform, primary, monitors, props = logical_monitors[0]
# this has to be an integer, unless fractional scaling is enabled (display settings -> tick fractional scaling)
# if scaling is a non-integer with fractional scaling disabled, this will silently fail
DEFAULT_SCALE = 1.5
HIGHER_SCALE = 2.0
if scale is None:
    scale = HIGHER_SCALE if _scale == DEFAULT_SCALE else DEFAULT_SCALE
if scale == _scale:
    print("Nothing to change")
    sys.exit(0)
# round if integer value
if scale == int(scale):
    scale = int(scale)
print(f"Attempting to scale to {int(scale * 100)}%")

monitor_config = [[x, y, scale, transform, primary, updated_connected_monitors]]

# Change the 1 to a 2 if you want a "Revert Settings / Keep Changes" dialog
interface.ApplyMonitorsConfig(serial, 1, monitor_config, {})
# this has to be an integer (and is not used if you enable fractional scaling);
# this is needed because if the display resets due to e.g. resizing, this value
# will be used
os.system('gsettings set org.gnome.desktop.interface scaling-factor ' + str(scale))
# text scaling (if separately desired)
#os.system('gsettings set org.gnome.desktop.interface text-scaling-factor ' + str(scale))
# enable fractional scaling (x11)
#os.system('gsettings set org.gnome.mutter experimental-features "[\'x11-randr-fractional-scaling\']"')
# disable fractional scaling (x11)
#os.system('gsettings set org.gnome.mutter experimental-features "[]"')
