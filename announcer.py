#!/usr/bin/env python3

import argparse
import glob
import os
import os.path
import pygame
import random
import re
import time

trigger_on_vote_num_static = True

announcer = None
mission_type = None
trigger_on_vote_num = 3

def play_sound(file_name):
    pygame.mixer.music.load(file_name)
    pygame.mixer.music.play()

def play_one(file_pattern):
    found_files = glob.glob(os.path.join(announcer, file_pattern))
    print(repr(found_files))
    if len(found_files) > 0:
        play_sound(random.choice(found_files))

def process_line(line):
    global trigger_on_vote_num_static

    global announcer
    global mission_type
    global trigger_on_vote_num

    if line.endswith("ThemedSquadOverlay.lua: OnSquadCountdown: 5") and not trigger_on_vote_num_static:
        trigger_on_vote_num = random.randint(0, 4)
    elif "ThemedSquadOverlay.lua: OnSquadCountdown:" in line:
        vote_num = int(line[-1])
        if vote_num == trigger_on_vote_num:
            play_one("vote_" + str(vote_num) + "_*.*")
    elif "OnStateStarted, mission type=" in line:
        mission_type = line[line.rfind("=")+1:]
        play_one(mission_type + "_*.*")
    elif line.endswith("EndOfMatch.lua: Mission Succeeded"):
        play_one("mission_success_*.*")
    #elif line.endswith("EndOfMatch.lua: Mission Succeeded"):
    #    play_one("mission_failure_*.*")

def process_log(log_file_name, log_interval, no_seek_to_end):
    curr_position = 0
    if not no_seek_to_end:
        with open(log_file_name) as log_file:
            log_file.seek(0, 2)
            curr_position = log_file.tell()

    while True:
        with open(log_file_name) as log_file:
            log_file.seek(curr_position, 0)
            line = log_file.readline()
            if not line:
                time.sleep(log_interval)
            else:
                curr_position = log_file.tell()
                process_line(line.strip())

if __name__ == "__main__":
    local_appdata_folder = os.getenv("localappdata")

    parser = argparse.ArgumentParser(description="Custom announcers for Warframe")
    parser.add_argument("--log", default=os.path.join(local_appdata_folder, "Warframe", "EE.log"), help="Log file to read", metavar="EE.log")
    parser.add_argument("--log-interval", type=float, default=1.0, help="Interval between log updates")
    parser.add_argument("--announcer", default="cy", help="Announcer")
    parser.add_argument("--no-skip", action="store_true", help="Do not seek to end of log")
    args = parser.parse_args()

    try:
        announcer = "announcer_" + args.announcer
        pygame.mixer.init()
        process_log(args.log, args.log_interval, args.no_skip)
    except KeyboardInterrupt:
        pass
