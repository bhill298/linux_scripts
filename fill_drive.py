#!/usr/bin/env python3.7
# must be at least python3.6 for random.choices
# won't work on windows (may not work on macOS either) due to some os calls
import argparse
import os
import random
import re
import shutil
import tempfile

# probability, if we are creating something in the current directory, of it being a directory
# file probability is 1 - DIR_PROBABILITY
DIR_PROBABILITY = .6
# relative weight of choosing current directory rather than a deeper directory, 1 = weight the same
# as everything else
CURRENT_DIR_REL_WEIGHT = .2
# stop when the free space reaches this percentage
FREE_SPACE_TARGET = .05
MAX_PATH = 260
# these entries must be all lowercase
FOLDER_BLACKLIST = ('__macosx', 'system volume information')


def get_free_bytes():
    return shutil.disk_usage('.').free


def get_storage_size():
    return shutil.disk_usage('.').total


def get_block_size():
    return os.statvfs('.').f_bsize


def clamp_down(x, base):
    return base * round(x/base)


def clean_current_dir():
    for filename in os.listdir('.'):
        if os.path.isfile(filename) or os.path.islink(filename):
            os.unlink(filename)
        elif os.path.isdir(filename) and filename.lower() not in FOLDER_BLACKLIST:
            shutil.rmtree(filename)


def single_sided_int_gauss(mu, sigma):
    val = random.gauss(mu, sigma)
    diff = val - mu
    if diff < 0:
        val += 2 * -diff
    return round(val)


def create_random_dir(path):
    tempfile.mkdtemp(dir=path)


def create_random_file(path, size):
    filename = tempfile.mkstemp(dir=path)[1]
    with open(filename, 'wb') as f:
        f.write(os.urandom(size))


def get_local_dirs(folder_path):
    dirs = [re.sub(r'^\.\/', '', f.path) for f in os.scandir(folder_path) if f.is_dir()]
    dirs = [f for f in dirs if f.lower() not in FOLDER_BLACKLIST]
    return dirs


def choose_dir():
    current_path = '.'
    choice = None
    while choice != '.':
        dirs = get_local_dirs(current_path)
        choice = random.choices(['.', *dirs],
                                weights=[CURRENT_DIR_REL_WEIGHT,
                                *[1] * len(dirs)])[0]
        # leave a bit of headroom for the file name
        if len(choice) > MAX_PATH - 16:
            choice = '.'
        if choice != '.':
            current_path = choice
    return current_path


parser = argparse.ArgumentParser(description='Fill a drive with random files and lots of folders')
parser.add_argument('drive_path',
                    help='Path to the mounted drive to fill')
parser.add_argument('-c', '--clean', action='store_true',
                    help='Delete the contents of the drive before starting')
args = parser.parse_args()
path_str = args.drive_path
os.chdir(path_str)
if args.clean:
    clean_current_dir()

drive_size = get_storage_size()
initial_free_bytes = get_free_bytes()
block_size = get_block_size()
lower_bound = initial_free_bytes // 1024 // 4
stdev_bytes = lower_bound * 10

free_bytes = initial_free_bytes
while free_bytes > FREE_SPACE_TARGET * initial_free_bytes:
    dir_path = choose_dir()
    choice = random.choices(['f', 'd'], cum_weights=[1 - DIR_PROBABILITY, 1])[0]
    if choice == 'f':
        # arbitrary decision to always leave at least 1 byte remaining
        size = min(single_sided_int_gauss(lower_bound, stdev_bytes),
                   clamp_down(free_bytes - 1, block_size))
        create_random_file(dir_path, size)
    elif choice == 'd':
        create_random_dir(dir_path)
    free_bytes = get_free_bytes()
    print('Free space remaining:', '{0:.2%}'.format(free_bytes / drive_size))
