import midi
import Tkinter
import tkFileDialog
import pygame
import pygame.midi
from pygame.locals import *
import os
import re

class_inst = {
    "Acoustic Grand Piano": 1,
    "Harpsichord": 7,
    "Orchestral Harp": 47,
    "String Ensemble 1": 49,
    "String Ensemble 2": 50,
    "French Horn": 61,
    "Oboe": 69,
    "Flute": 74
}

# for keyboard play-in/playback:

key_map = {
    'z': 36,  # C2 and up
    'x': 38,
    'c': 40,
    'v': 41,
    'b': 43,
    'n': 45,
    'm': 47,
    ',': 48,
    '.': 50,
    '/': 52,

    'Z': 37,  # sharps
    'X': 39,
    'C': 41,
    'V': 42,
    'B': 44,
    'N': 46,
    'M': 48,
    '<': 49,
    '>': 51,
    '?': 53,

    'a': 48,  # C3 and up
    's': 50,
    'd': 52,
    'f': 53,
    'g': 55,
    'h': 57,
    'j': 59,
    'k': 60,
    'l': 62,
    ';': 64,
    '\'': 65,

    'A': 49,  # C3 and up
    'S': 51,
    'D': 53,
    'F': 54,
    'G': 56,
    'H': 58,
    'J': 60,
    'K': 61,
    'L': 63,
    ':': 65,
    '\"': 66,

    'q': 60,
    'w': 62,
    'e': 64,
    'r': 65,
    't': 67,
    'y': 69,
    'u': 71,
    'i': 72,
    'o': 74,
    'p': 76,
    '[': 77,
    ']': 79,
    '\\': 81,

    'Q': 61,
    'W': 63,
    'E': 65,
    'R': 66,
    'T': 68,
    'Y': 70,
    'U': 72,
    'I': 73,
    'O': 75,
    'P': 77,
    '{': 78,
    '}': 80,
    '|': 82,

    '1': 72,  # C5
    '2': 74,  # D5
    '3': 76,  # E5
    '4': 77,  # F5
    '5': 79,  # G5
    '6': 81,  # A5
    '7': 83,  # B5
    '8': 84,  # C6
    '9': 86,  # D6
    '0': 88,  # E6
    '-': 89,  # F6
    '=': 91,  # G6

    '!': 73,  # C#5
    '@': 75,  # D#5
    '#': 77,  # E#5
    '$': 78,  # F#5
    '%': 80,  # G#5
    '^': 82,  # A#5
    '&': 84,  # B#5
    '*': 85,  # C#6
    '(': 87,  # D#6
    ')': 89,  # E#6
    '_': 90,  # F#6
    '+': 92,  # G#6
}


class Piece:
    key_sig = "unknown"
    key_sig_num = -1
    time_sig = "unknown"
    mode = "unknown"
    first_tick = 1000000
    beat_in_ticks = 0

    tot_notes = 0

    waltz = False
    goal_key = "Major"

    keys = {
        0: "C",
        1: "Db",
        2: "D",
        3: "Eb",
        4: "E",
        5: "F",
        6: "F#",
        7: "G",
        8: "Ab",
        9: "A",
        10: "Bb",
        11: "B"
    }

    def __init__(self, file_path):
        self.file_path = file_path
        self.pat = midi.read_midifile(file_path)
        # print self.pat

    def change_mode(self, change_to, pat):
        print ("Changing Mode . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .")
        # mode_pat = self.pat
        to = change_to
        mode_pat = pat
        tonic = self.key_sig_num
        # print (tonic)
        # major to minor
        # if self.mode == "Major" and to == "minor":
        if to == "minor":
            print ("Major to minor")
            for i in mode_pat:
                for j in i:
                    if str(type(j)) == "<class 'midi.events.NoteOnEvent'>" or str(
                            type(j)) == "<class 'midi.events.NoteOffEvent'>":
                        # print (j)
                        if (j.data[0] % 12) == ((tonic + 4) % 12) or (j.data[0] % 12) == ((tonic - 3) % 12):
                            j.data[0] = j.data[0] - 1
            # print (str(self.file_path_) + "to_minor")
            print("writing . . . ")
            # midi.write_midifile(out_file, mode_pat)
        if self.mode == "minor" and to == "Major":
            print ("minor to Major")
            for i in mode_pat:
                for j in i:
                    if str(type(j)) == "<class 'midi.events.NoteOnEvent'>" or \
                            str(type(j)) == "<class 'midi.events.NoteOffEvent'>":
                        # print (j)
                        if (j.data[0] % 12) == ((tonic + 3) % 12) or (j.data[0] % 12) == ((tonic - 4) % 12):
                            j.data[0] = j.data[0] + 1
            # print (str(self.file_path_) + "to_minor")
            # midi.write_midifile(out_file, mode_pat)
        return mode_pat
        # print mode_pat

    def signatures(self):
        self.key_sig = "unknown"
        self.key_sig_num = -1
        self.time_sig = "unknown"
        self.mode = "unknown"
        self.first_tick = 1000000
        self.beat_in_ticks = 0

        self.tot_notes = 0

        self.waltz = False

        key_votes = [-1] * 4  # first low note, last low note, most frequent, most frequent with dom
        vote_weights = [0.5, 1.2, 0.8, 1]
        pattern = self.pat
        res = pattern.resolution
        break_point = res * 10
        do_trim = False
        key_accumulator = [0] * 12
        low_note_accumulator = [0] * 12
        denominator = 0
        numerator = 0

        first_notes_by_track = []
        first_notes_temp = []
        first_notes_num = 5

        last_note_by_track = []

        track_pitches = []
        track_pitch_ave = []

        last_tick_sound = -1

        # loop through pattern, collect info
        for c, i, in enumerate(pattern):
            current_tick = 0
            current_note = 0

            last_note_by_track.append([-1, -1])

            for j in i:
                # print (str(j))
                try:
                    for m in j:
                        if "waltz" in m or "Waltz" in m or "WALTZ" in m:
                            self.waltz = True
                except TypeError:
                    if "waltz" in str(j) or "Waltz" in str(j) or "WALTZ" in str(j):
                        self.waltz = True

                if str(type(j)) == "<class 'midi.events.KeySignatureEvent'>":
                    # print ("Key given")
                    # print j
                    pass

                if str(type(j)) == "<class 'midi.events.NoteOffEvent'>" or (
                        str(type(j)) == "<class 'midi.events.NoteOnEvent'>" and j.data[1] == 0):
                    current_tick += j.tick
                    # print ("current_tick: " + str(current_tick))
                if str(type(j)) == "<class 'midi.events.NoteOnEvent'>" and j.data[1] != 0:

                    # print j
                    current_tick += j.tick
                    if self.first_tick > current_tick:
                        self.first_tick = current_tick

                    # print("checking channel")
                    # print(j.channel)
                    if j.channel != 9:
                        if current_tick > last_tick_sound:
                            last_tick_sound = current_tick
                        # print ("current_tick: " + str(current_tick))

                        last_note_by_track[c] = (j.data[0], current_tick)

                        if current_note <= first_notes_num and current_tick < res * 12:
                            first_notes_temp.append(j.data)
                            current_note += 1

                        if do_trim and current_tick > break_point:
                            # print ("breaking . . .")
                            break

                        key_accumulator[j.data[0] % 12] += 1
                        track_pitches.append(j.data[0])
                        # print ("Appended" + str(j.data[0]))
                    else:
                        # print("Skipping percussion")
                        pass
                    self.tot_notes += 1

            if len(track_pitches) > 0:
                track_pitch_ave.append(sum(track_pitches) / len(track_pitches))
            else:
                track_pitch_ave.append(0)
            track_pitches = []

            first_notes_by_track.append(first_notes_temp)
            # print ("Temp")
            # print (first_notes_temp)
            first_notes_temp = []

        # done looping through pattern

        # print(track_pitch_ave)
        # print ("First Notes")
        # for n in first_notes_by_track:
        # print n

        # for n, p in enumerate(track_pitch_ave):
        #     print (n)
        #     print (p)
        #     print ("temp_ave: " + str(temp_ave) + " p: " + str(p))
        #     if temp_ave > p != 0:
        #         temp_ave = p
        #         low_track = n
        # print ("Low track: " + str(low_track))
        # print (first_notes_by_track[low_track])

        # finding lowest track and first notes by track
        first_track_pitch_ave = []

        for i in first_notes_by_track:
            first_temp_ave = []
            for j in i:
                first_temp_ave.append(j[0])
            if len(first_temp_ave) != 0:
                first_track_pitch_ave.append(sum(first_temp_ave) / len(first_temp_ave))
            else:
                first_track_pitch_ave.append(0)
        # print ("First tracks pitch ave")
        # print (first_track_pitch_ave)

        low_track = 0
        temp_ave = 128

        for n, p in enumerate(first_track_pitch_ave):
            # print (n)
            # print (p)
            # print ("temp_ave: " + str(temp_ave) + " p: " + str(p))
            if temp_ave > p != 0:
                # print ("update temp_ave")
                temp_ave = p
                low_track = n
        # print ("Low track: " + str(low_track))
        # print (first_notes_by_track[low_track])

        # print ("Counting first low notes")
        for n, p in enumerate(first_notes_by_track[low_track]):
            # print n
            # print p
            low_note_accumulator[p[0] % 12] += 1
        # print ("First low notes ")
        # print(low_note_accumulator)
        first_bottom_key = low_note_accumulator.index(max(low_note_accumulator))

        # vote tonic
        key_votes[0] = first_bottom_key

        # print (first_bottom_key)
        # print self.keys[first_bottom_key]

        # find frequent notes
        first = [0, 0]
        second = [0, 0]
        third = [0, 0]
        fourth = [0, 0]

        for i, v in enumerate(key_accumulator):
            if v > first[1]:
                fourth = third
                third = second
                second = first
                first = [i, v]
            elif v > second[1]:
                fourth = third
                third = second
                second = [i, v]
            elif v > third[1]:
                fourth = third
                third = [i, v]
            elif v > fourth[1]:
                fourth = [i, v]

        # print("Most frequent notes")
        # print(first)
        # print(second)
        # print(third)
        # print(fourth)

        # vote tonic
        key_votes[2] = first[0]

        # looking at doms
        first_dom = (first[0] + 7) % 12
        second_dom = (second[0] + 7) % 12
        third_dom = (third[0] + 7) % 12

        # checking for tonic/dom relationship in case tonic is not the most frequent note
        if abs(first[1] - second[1]) <= first[1] * 0.25 and first[0] == second_dom:
            tonic = second
            # print("Second")
        elif second[0] == first_dom or third[0] == first_dom or fourth[0] == first_dom:
            tonic = first
            # print ("First")
        elif first[0] == second_dom or third[0] == second_dom or fourth[0] == second_dom:
            tonic = second
            # print ("Second")
        elif first[0] == third_dom or second[0] == third_dom or fourth[0] == third_dom:
            tonic = third
            # print ("Third")
        else:
            tonic = first
            # print ("First2")
        # vote tonic
        key_votes[3] = tonic[0]

        # check for disagreement

        # if tonic[0] != first_bottom_key:
        #     print ("Argue")
        #     if (tonic[0] - first_bottom_key) % 12 == 7:
        #         tonic[0] = first_bottom_key
        #         tonic[1] = -1

        # look at last notes
        low_last_note = 128
        for i in last_note_by_track:
            if i[0] >= 0:
                if low_last_note > i[0] and (i[1] >= last_tick_sound - (res * 200)):
                    low_last_note = i[0]

        # vote key
        key_votes[1] = low_last_note % 12

        # print ("votes")
        # print(key_votes)

        # look for tonic-dom pattern in votes

        vote_pattern = []
        for i in key_votes:
            found = False
            if i >= 0:
                for j in vote_pattern:
                    if j[0] == i:
                        # print("3")
                        j[1] += 1
                        found = True
                if not found:
                    vote_pattern.append([i, 1])
        # print ("vote_pattern")
        # print (vote_pattern)

        # need to also consider 1/3 splits?
        pat_tonic = -1
        if len(vote_pattern) == 2:
            if (vote_pattern[0][0] - vote_pattern[1][0]) % 12 == 7:
                pat_tonic = vote_pattern[1][0]
            elif (vote_pattern[1][0] - vote_pattern[0][0]) % 12 == 7:
                pat_tonic = vote_pattern[0][0]

        # apply weights
        votes_by_key = [0] * 12
        for c, v in enumerate(key_votes):
            votes_by_key[v] += vote_weights[c]

        # pattern weight
        if pat_tonic >= 0:
            # print("pat tonic")
            votes_by_key[pat_tonic] += 1

        # print("Votes by key")

        # print(votes_by_key)

        #  . . . and the result

        high_votes = []
        high_vote = 0

        for i in votes_by_key:
            if i > high_vote:
                high_vote = i
        for c, i in enumerate(votes_by_key):
            if i == high_vote:
                high_votes.append(c)

        if len(high_votes) == 1:
            tonic[0] = high_votes[0]
        else:
            print ("Multiple high votes")
            tonic[0] = high_votes[0]

        # print(tonic[0])

        # looking for mode based on tonic:

        # checking for pentatonic modes:
        # print ("Penta section")
        penta = False
        # print("Total notes: " + str(self.tot_notes))
        note_num_ave = self.tot_notes / 12
        # print("Total notes: " + str(self.tot_notes))
        # print("Ave is " + str(note_num_ave))
        split_freq = note_num_ave - note_num_ave * 0.7

        # pitch_numbers = sorted(key_accumulator)
        #
        # print(pitch_numbers)
        # large_gap = [0, 0]  # size, location
        #
        # prev_val = pitch_numbers[0]
        # for c, i in enumerate(pitch_numbers):
        #     gap = i - prev_val
        #     if gap > large_gap[0]:
        #         large_gap = [gap, c]
        #     prev_val = i
        #
        # print(large_gap)
        #
        # if large_gap[1] < 7:
        #     penta = True

        main_pitch_count = []
        for c, i in enumerate(key_accumulator):
            if i > split_freq:
                main_pitch_count.append(c)
        if len(main_pitch_count) < 6:
            penta = True
            for i, v in enumerate(main_pitch_count):
                if i == 0:
                    pass
                if i > 0:
                    if v == main_pitch_count[i - 1] + 1:
                        penta = False

        # check melody

        # print (key_accumulator)
        # print (note_num_ave)
        # print (split_freq)
        # print (penta)

        print (vote_weights)
        print (key_votes)
        print (key_accumulator)

        if abs(key_accumulator[(tonic[0] + 3) % 12] - key_accumulator[(tonic[0] + 4) % 12]) < \
                (key_accumulator[(tonic[0] + 3) % 12] + key_accumulator[(tonic[0] + 4) % 12]) * 0.2 and \
                max(key_accumulator[(tonic[0] + 3) % 12], key_accumulator[(tonic[0] + 4) % 12]) > \
                key_accumulator[(tonic[0] + 7) % 12] * 0.5:
            self.mode = "Major blues"
        elif key_accumulator[(tonic[0] + 3) % 12] > key_accumulator[(tonic[0] + 4) % 12]:
            self.mode = "minor"
            if penta:
                self.mode = "minor pentatonic"
            elif abs(key_accumulator[(tonic[0] + 7) % 12] - (key_accumulator[(tonic[0] + 6) % 12])) < (
                    key_accumulator[(tonic[0] + 7) % 12] * 0.5):
                self.mode = "minor blues"
            elif key_accumulator[(tonic[0] + 1) % 12] > (key_accumulator[(tonic[0] + 2) % 12]) * 2:
                self.mode = "Phrygian"
            elif key_accumulator[(tonic[0] + 9) % 12] > (key_accumulator[(tonic[0] + 8) % 12]) * 2:
                self.mode = "Dorian"
        else:
            self.mode = "Major"
            if penta:
                self.mode = "Major pentatonic"
            elif key_accumulator[(tonic[0] + 10) % 12] > (key_accumulator[(tonic[0] + 11) % 12]) * 2:
                self.mode = "Mixolydian"
            elif key_accumulator[(tonic[0] + 6) % 12] > (key_accumulator[(tonic[0] + 5) % 12]) * 2:
                self.mode = "Lydian"

        self.key_sig = self.keys[tonic[0]]
        self.key_sig_num = tonic[0]

        # end key, start time ****************************************************************************************

        event_sigs = []
        for i in pattern:
            for j in i:
                if str(type(j)) == "<class 'midi.events.TimeSignatureEvent'>":
                    event_sigs.append([j.data[0], 2 ** j.data[1], j.tick])
        # print (event_sigs)

        if len(event_sigs) > 1 and self.first_tick >= event_sigs[1][2]:
            # print ("empty sig")
            # print(self.first_tick)
            self.time_sig = event_sigs[1]
        elif len(event_sigs) > 0:
            self.time_sig = event_sigs[0]
        else:
            self.time_sig = [4, 4, 0]
        if self.waltz:
            self.time_sig = [3, 4]

        # print("Printing Key Frequencies Chart:")

        n = max(key_accumulator)
        while n > 0:
            prnt = [" "] * 12
            for c in range(12):
                if key_accumulator[(tonic[0] + c) % 12] >= n:
                    prnt[c] = "*"
            print("|" + str(prnt[0]) + "|" + str(prnt[1]) + "|" + str(prnt[2]) + "|" + str(prnt[3]) + "|" + str(
                prnt[4]) + "|" + str(prnt[5]) + "|" + str(prnt[6]) + "|" + str(prnt[7]) + "|" + str(
                prnt[8]) + "|" + str(prnt[9]) + "|" + str(prnt[10]) + "|" + str(prnt[11]) + "|")
            n = n - (max(key_accumulator) / 10)

        # need to fix/get rid of the rest of this function

        # note_length = 0  # in ticks, including any trailing silence
        # note_lengths = []
        # start_gaps = []
        #
        # for i in pattern:
        #     start_gap = 0
        #     for j in i:
        #         if str(j).startswith("midi.Note"):
        #             if str(j).startswith("midi.NoteOn") and j.data[1] > 0:
        #                 if len(note_lengths) == 0:
        #                     start_gap = j.tick
        #                 if note_length > 0:
        #                     note_length += j.tick
        #                     note_lengths.append(note_length)
        #                     note_length = 0
        #             else:
        #                 note_length += j.tick
        #
        #     start_gaps.append(start_gap)
        #
        # note_lengths.append(note_length)
        #
        # note_length_count = {}
        # for i in note_lengths:
        #     # print (i)
        #     if i in note_length_count:
        #         note_length_count[i] += 1
        #     else:
        #         note_length_count[i] = 1
        # # print ("out")
        # high_count_note_length = max(note_length_count, key=note_length_count.get)
        #
        # # print "high", high_count_note_length
        #
        # if res + (res * 0.1) > high_count_note_length > res - (res * 0.1):
        #     self.beat_in_ticks = res
        #     denominator = 4
        # elif res / 2 + (res / 2 * 0.1) > high_count_note_length > res / 2 - (res / 2 * 0.1):
        #     self.beat_in_ticks = res / 2
        #     denominator = 8
        # elif res * 2 + (res * 2 * 0.1) > high_count_note_length > res * 2 - (res * 2 * 0.1):
        #     self.beat_in_ticks = res * 2
        #     denominator = 2
        # elif res / 4 + (res / 4 * 0.1) > high_count_note_length > res / 4 - (res / 4 * 0.1):
        #     self.beat_in_ticks = res / 4
        #     denominator = 16
        # elif res / 8 + (res / 8 * 0.1) > high_count_note_length > res / 8 - (res / 8 * 0.1):
        #     self.beat_in_ticks = res / 8
        #     denominator = 32
        #
        # # print "*****************"
        # # print (denominator)
        #
        # long_note = 0
        # for x in note_length_count:
        #     if x > long_note:
        #         long_note = x
        # if long_note != 0 and self.beat_in_ticks != 0:
        #     numerator = long_note / self.beat_in_ticks
        # # print (numerator)
        #
        # # print "checkpoint 1"
        # while numerator % 2 == 0 and denominator % 2 == 0 and numerator != 0 and denominator != 0:
        #     print numerator, denominator
        #     numerator = numerator / 2
        #     denominator = denominator / 2
        # # print "checkpoint 2"
        # while numerator % 2 == 0 and numerator != 0:
        #     numerator = numerator / 2
        # # print "checkpoint 3"
        # while numerator % 3 == 0 and numerator != 0:
        #     numerator = numerator / 3
        # # print numerator, '/', denominator
        # print("FILE:")
        # print(self.file_path)
        # print("*************************")
        # print(self.key_sig + " " + self.mode)
        # print(str(self.time_sig[0]) + "/" + str(self.time_sig[1]) + " time")
        # print("*************************")

        show_sigs()

    def even_rhythm(self, pat, small):

        new_pat = pat
        q = self.pat.resolution
        h = 2 * q
        w = 4 * q

        e = s = t = x = o = -1

        if q % 2 == 0:
            e = q / 2
        else:
            print ("Help!  This piece is too weird!")

        if e % 2 == 0:
            s = e / 2
        if s % 2 == 0:
            t = s / 2
        if t % 2 == 0:
            x = t / 2
        if x % 2 == 0:
            o = x / 2

        notes_vals = [w, h, q, e, s, t, x, o]

        small_val = 0

        for c, i in enumerate(notes_vals):
            print("C: " + str(c) + ", 2^c: " + str(2 ** c) + "small: " + str(small))
            if i != -1 and 2 ** c <= small:
                small_val = i
                print (small_val)
            else:
                break

        print ("w: " + str(w) + "  h: " + str(h) + "  q: "
               + str(q) + "  e: " + str(e) + "  s: " + str(s) + "  t: " + str(t) + "  x: " + str(x))
        # for c, i in enumerate(self.pat):
        #     for j in i:
        #         print(str(i))

        changes = []

        print ("Small val is: " + str(small_val))
        for i in new_pat:
            current_tick = 0
            for j in i:
                js = str(j)
                if "tick" in str(j):
                    current_tick += j.tick
                    print("current tick: " + str(current_tick))
                    if "NoteOnEvent" in js or "NoteOffEvent" in js:
                        if "NoteOnEvent" in js and j.data[1] > 0:
                            # print("Note On")
                            if current_tick % small_val != 0:
                                print("TRIGGERED: Current_tick is " + str(current_tick) + ", mod is " + str(
                                    current_tick % small_val))
                                if j.tick > current_tick % small_val:
                                    print("j.tick was " + str(j.tick))
                                    j.tick = j.tick - (current_tick % small_val)
                                    print("j.tick is now " + str(j.tick))
                                else:
                                    print("j.tick was " + str(j.tick))
                                    j.tick = 0
                                    print("j.tick is now " + str(j.tick))
        return new_pat

    def find_time(self):
        track_ticks = []
        current_tick = 0
        for c, i in enumerate(self.pat):
            current_tick = 0
            for j in i:
                if "tick" in str(j):
                    current_tick += j.tick
                track_ticks.append(current_tick)
        ticks = [0] * max(track_ticks)
        for c, i in enumerate(self.pat):
            current_tick = 0
            for j in i:
                if "tick" in str(j):
                    current_tick += j.tick
                if "NoteOnEvent" in str(j) and j.data[1] > 0:
                    ticks[current_tick] += j.data[1]
        for c, i in enumerate(ticks):
            if i > 0:
                print("Tracks[" + str(c) + "] is " + str(i))

    def class_to_rock(self):
        new_pat = self.pat
        for c, i in enumerate(new_pat):
            for j in i:
                # print(str(j))
                if str(type(j)) == "<class 'midi.events.NoteOnEvent'>" and j.data[1] != 0:  # take out unpitched
                    if j.channel == 9:
                        j.data[1] = 0
                elif "ProgramChange" in str(j):
                    print("ProgramChange")
                    if j.data in class_inst.values():
                        print ("found inst")
                        # pass
                    else:
                        if j.data[0] < 25:
                            j.data[0] = 1
                        elif j.data[0] < 57:
                            j.data[0] = 50
                            is_strings = True
                        elif j.data[0] < 81:
                            j.data[0] = 61
                        else:
                            j.data[0] = 50
                            is_strings = True

    def melody_track(self):
        notes = []
        tracks = []  # for each track, true/false "are there any notes", then if true:  highest, lowest, range, ave
        for c, i in enumerate(self.pat):
            highest = -1
            lowest = 128
            pitches = []
            current_tick = 0
            notes.append([])
            tracks.append([])
            tracks[c].append(False)
            # print("Pattern track " + str(c))
            for j in i:
                if "tick" in str(j):
                    current_tick += j.tick
                if "NoteOnEvent" in str(j) and j.channel != 9 and j.data[1] > 0:
                    notes[c].append([j.data[0], current_tick, -1])
                    tracks[c][0] = True
                    pitches.append(j.data[0])
                    if j.data[0] > highest:
                        highest = j.data[0]
                    if j.data[0] < lowest:
                        lowest = j.data[0]
                elif ("NoteOffEvent" in str(j) or ("NoteOnEvent" in str(j) and j.data[1] == 0)) and j.channel != 9:
                    for n in reversed(notes[c]):
                        if n[0] == j.data[0] and n[2] == -1:
                            n[2] = current_tick
                            break
            # print("End of track")
            # print(pitches)
            if tracks[c][0]:
                tracks[c].append(len(notes[c]))
                tracks[c].append(highest)
                tracks[c].append(lowest)
                tracks[c].append(highest - lowest)
                tracks[c].append(sum(pitches) / float(len(pitches)))

        # looking at leaps, trying to skip polyphony
        for ind, t in enumerate(notes):
            leaps = []
            poly = 0
            for c, i in enumerate(t):

                if c > 0:
                    if abs(i[1] - t[c - 1][1]) > self.pat.resolution / 128 and abs(
                            i[1] - t[c - 1][1]) > 2:  # new note/chord
                        if abs(i[0] - t[c - 1][0]) != 0:  # not counting repeated notes
                            leaps.append(abs(i[0] - t[c - 1][0]))
                    else:
                        poly += 1
            if tracks[ind][0]:
                tracks[ind].append(sum(leaps) / float(len(leaps)))
                tracks[ind].append(poly)

        votes = [0] * len(tracks)

        for c, i in enumerate(votes):
            print ("Votes")
            print(votes)
            if tracks[c][0]:
                print("Has Notes")
                print(i)
                if tracks[c][4] < 24:
                    print("Small range")
                    votes[c] = votes[c] + 1
                if tracks[c][5] > 64:
                    print("Treble")
                    votes[c] = votes[c] + 0.5
                if tracks[c][6] < 4:
                    print("Small leaps")
                    votes[c] += 1
                    print(i)
                    if tracks[c][6] < 2:
                        print("Really small leaps")
                        votes[c] += 0.5
                        print(i)
                if tracks[c][7] < tracks[c][1] * 0.1:
                    print("Minimal polyphony")
                    votes[c] += 1

        print("Votes")
        print(votes)

        print("Melody track index is: " + str(votes.index(max(votes))))

        # for c, t in enumerate(notes):
        #     print("Track " + str(c))
        #     print("------------------------------------------------------")
        #     for n in t:
        #         print(n)

        for t in tracks:
            print (t)

        # for c, t in enumerate(tracks):
        #     if t[0]:
        #         for n in notes[c]:

    def rock_to_class(self):
        new_pat = self.pat
        is_strings = False
        for c, i in enumerate(new_pat):
            for j in i:
                # print(str(j))
                if str(type(j)) == "<class 'midi.events.NoteOnEvent'>" and j.data[1] != 0:  # take out unpitched
                    if j.channel == 9:
                        j.data[1] = 0
                elif "ProgramChange" in str(j):
                    print("ProgramChange")
                    if j.data in class_inst.values():
                        print ("found inst")
                        # pass
                    else:
                        if j.data[0] < 25:
                            j.data[0] = 1
                        elif j.data[0] < 57:
                            j.data[0] = 50
                            is_strings = True
                        elif j.data[0] < 81:
                            j.data[0] = 61
                        else:
                            j.data[0] = 50
                            is_strings = True
        if not is_strings:
            for c, i in enumerate(new_pat):
                for j in i:
                    if "ProgramChange" in str(j):
                        print("ProgramChange")
                        if j.data[0] < 81 and j.data[0] > 49:
                            j.data[0] = 50

        if self.mode == "Major" or self.mode == "Mixolydian" or self.mode == "Lydian":
            print ("Call mode change")
            new_pat = self.change_mode("minor", new_pat)

        new_pat = self.even_rhythm(new_pat, 8)

        midi.write_midifile("rock_to_class.mid", new_pat)
        play_class()

    def print_pat(self):
        for i in self.pat:
            print(str(i))


first_load = True
play_in_piece = False
testing = False


def load():
    global first_load
    global testing
    global test_file
    global piece
    global sig
    global play
    global stop_b
    global stop
    global rock_class
    global print_pat
    global restart_b
    global show_sigs_l
    global play_in_piece
    global function_test

    try:
        del piece
        first_load = False
    except NameError:
        first_load = True
    if not first_load:
        try:
            stop()
        except:
            pass
        try:
            restart_b.grid_forget()
        except NameError:
            pass
        sig.destroy()
        play.destroy()
        rock_class.destroy()
        try:
            function_test.destroy()
        except NameError:
            pass
        try:
            stop_b.destroy()
        except NameError:
            pass
        try:
            restart_b.destroy()
        except NameError:
            pass
        try:
            show_sigs_l.destroy()
        except NameError:
            pass

    if play_in_piece:
        file_path = "play_in.mid"
    elif testing:
        print ("Test file")
        print (test_file)
        file_path = test_file
    else:
        file_path = tkFileDialog.askopenfilename()
        play_in_piece = False
    piece = Piece(file_path)
    play = Tkinter.Button(root, text="Play the MIDI!", command=show_controls)
    sig = Tkinter.Button(root, text="Find key and time signatures", command=piece.signatures)
    rock_class = Tkinter.Button(root, text="Classicalize this piece!", command=piece.rock_to_class)
    function_test = Tkinter.Button(root, text="Where is the melody?", command=piece.melody_track)
    # change_mode = Tkinter.Button(main, text="Change Var", command=piece1.change_mode())
    sig.grid()
    play.grid()
    rock_class.grid()
    function_test.grid()

    first_load = False


def play_in():
    global play_in_piece

    pygame.init()
    pygame.midi.init()
    pygame.fastevent.init()

    pat = midi.Pattern()
    track = midi.Track()
    pat.append(track)

    event_get = pygame.fastevent.get
    input_id = pygame.midi.get_default_input_id()

    if input_id == -1:
        print ("could not find midi device!")
        return

    i = pygame.midi.Input(input_id)

    prev_event = []

    going = True

    while going:

        events = event_get()
        for e in events:
            if e.type in [QUIT]:
                going = False
            if e.type in [KEYDOWN]:
                going = False
            if e.type in [MOUSEBUTTONDOWN]:
                going = False

        if i.poll():
            midi_events = i.read(10)

            print "midi event: " + str(midi_events)
            print(len(prev_event))
            if len(prev_event) > 0:
                tick = (midi_events[0][1] - prev_event[0][1]) / 2
            else:
                tick = 0

            ev = midi.NoteOnEvent(tick=tick, velocity=midi_events[0][0][2], pitch=midi_events[0][0][1])
            print(ev)
            track.append(ev)

            prev_event = midi_events

    eot = midi.EndOfTrackEvent(tick=1)
    track.append(eot)

    midi.write_midifile("play_in.mid", pat)
    play_in_piece = True
    load()

    print "exit on press"
    i.close()
    del i
    pygame.midi.quit()


def show_sigs():
    global show_sigs_l
    sig_text = "Looks like this piece is in:\n" + piece.key_sig + " " + piece.mode + "\n" + str(piece.time_sig[0]) \
               + "/" + str(piece.time_sig[1]) + " time!"
    show_sigs_l = Tkinter.Label(root, text=sig_text)
    show_sigs_l.grid()


def play_class():
    global restart_b
    global stop_b

    try:
        restart_b.grid_forget()
        stop_b.grid_forget()
    except NameError:
        pass

    pygame.mixer.init()
    # mid_file = piece.file_path
    try:
        pygame.mixer.music.load("rock_to_class.mid")
        # print "MIDI file %s loaded!" % music_file
    except pygame.error:
        print ("File %s not found! (%s)" % ("rock_to_class.mid", pygame.get_error()))
        return
    restart_b = Tkinter.Button(root, text="Play", command=restart)
    stop_b = Tkinter.Button(root, text="Stop", command=stop)

    restart_b.grid()
    stop_b.grid()


def show_controls():
    # global play
    global restart_b
    global stop_b
    mid_file = piece.file_path
    try:
        pygame.mixer.music.load(mid_file)
        # print "MIDI file %s loaded!" % music_file
    except pygame.error:
        print ("File %s not found! (%s)" % (mid_file, pygame.get_error()))
        return

    restart_b = Tkinter.Button(root, text="Play", command=restart)
    stop_b = Tkinter.Button(root, text="Stop", command=stop)

    restart_b.grid()
    stop_b.grid()

    play.grid_forget()
    restart()
    # play_mid()


def restart():
    pygame.mixer.music.play()
    global restart_b
    restart_b.grid_forget()
    stop_b.grid()


def stop():
    pygame.mixer.music.stop()
    global stop_b
    stop_b.grid_forget()
    restart_b.grid()


test_file = ""
test_dir = ""
test_all_flag = False

def test_all():
    global test_dir
    global test_all_flag
    test_all_flag = True
    test_dir = "Project_Test_Midis"
    test()
    test_all_flag = False

def test_rock():
    global test_all_flag
    print (test_all_flag)
    global test_dir
    test_dir = "Project_Test_Midis/Rock"
    test()

def test_classical():
    global test_dir
    test_dir = "Project_Test_Midis/Classical"
    test()


def test_metal():
    global test_dir
    test_dir = "Project_Test_Midis/Metal"
    test()

def test_blues():
    global test_dir
    test_dir = "Project_Test_Midis/Blues"
    test()

def test():
    count = 0
    with_extra = 0
    tonic = 0
    mode = 0
    extra = 0
    time = 0
    all = 0
    global testing
    global test_file
    global test_dir
    global test_all_flag
    folders = ["Rock", "Classical", "Blues", "Metal"]
    testing = True
    directory = test_dir
    files = []
    print (test_all)
    if test_all_flag:
        print ("Called")
        for i in folders:
            files += os.listdir(directory + "/" + i)
    else:
        files += os.listdir(directory)

    for filename in files:
        if filename.endswith(".mid"):
            print("*****************************************************************************************")
            count += 1

            # key = re.findall(r"[A-G][b#]*_[mMDdLlPp][A-Za-z]+", str(filename))
            # time_sig = re.findall(r"[1-9]_[1-9]", str(filename))
            data = filename.split("_")
            if test_all_flag:
                test_file = directory + "/" + data[0] + "/" + filename
            else:
                test_file = directory + "/" + filename

            key = ""
            scale = []
            time_sig = []

            for i, v in enumerate(data):
                if i > 2 and len(time_sig) >= 2:
                    break
                elif i == 1:
                    key = v
                elif i > 1 and re.match("[A-Za-z]", v):
                    scale.append(v.upper())
                    if i == 3:
                        with_extra += 1
                elif i > 1 and re.match("[0-9]", v) and len(time_sig) < 2:
                    time_sig.append(v)

            load()
            piece.signatures()
            print ("Key")
            print(key)
            print ("Predicted key")
            print (piece.key_sig)
            print ("Mode/scale")
            print (scale)
            print ("Predicted mode/scale")
            print (piece.mode.upper())
            print ("Time")
            print (time_sig)
            print ("Predicted Time")
            print (piece.time_sig)
            is_all = 0
            key_mode = 0
            scale_str = ""
            if len(key):
                if key == piece.key_sig:
                    tonic += 1
                    is_all += 1
                if len(scale) == 2:
                    scale_str = scale[0] + " " + scale[1]
                    with_extra += 1
                for i in scale:
                    if i.upper() in piece.mode.upper():
                        mode += 1
                        is_all += 1
                        if is_all == 2:
                            key_mode += 1
                        break
                if len(scale) == 2 and scale_str.upper() == piece.mode.upper():
                    extra += 1
                    # is_all += 1
                if str(time_sig[0]) == str(piece.time_sig[0]) and str(time_sig[1]) == str(piece.time_sig[1]):
                    time += 1
                    is_all += 1
                if is_all == 3:
                    all += 1
                else:
                    print ("Still not perfect :(")
            else:
                print("Something is wrong with this filename!")
        print("\n")
    print (tonic)
    print (mode)
    print (extra)
    print (with_extra)
    print (time)
    print (all)
    print (count)
    print ("tonic")
    print (tonic / float(count))
    print ("mode")
    print (mode / float(count))
    if with_extra !=0:
        print ("extra")
        print (extra / float(with_extra))
    print ("time")
    print (time / float(count))
    print ("all")
    print (all / float(count))
    testing = False


# GUI
pygame.mixer.init()

root = Tkinter.Tk()
root.title("MIDI Minion")
root.geometry("300x500")
root.lift()

welcome = Tkinter.Label(root, text="Welcome to MIDI Minion!\n\nHow would you like to start?")
welcome.grid(padx=45, ipady=30)

load_piece = Tkinter.Button(root, text="Load a Piece", command=load, width=20)
load_piece.grid(padx=45, pady=10, row=2)

play_in = Tkinter.Button(root, text="Record MIDI", command=play_in, width=20)
play_in.grid(padx=45, pady=10, row=3)
play_in.configure(background='#e8d9c4')

test_b = Tkinter.Button(root, text="Test Blues", command=test_blues, width=10)
test_b.grid()

test_c = Tkinter.Button(root, text="Test Classical", command=test_classical, width=10)
test_c.grid()

test_r = Tkinter.Button(root, text="Test Rock", command=test_rock, width=10)
test_r.grid()

test_m = Tkinter.Button(root, text="Test Metal", command=test_metal, width=10)
test_m.grid()

test_a = Tkinter.Button(root, text="Test All Genres", command=test_all, width=10)
test_a.grid()

root.mainloop()
