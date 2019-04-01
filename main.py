import midi
import Tkinter
import tkFileDialog

# for keyboard play-in:

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

    'a': 48, #C3 and up
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

    def change_mode(self, change_to):
        print ("Changing Mode . . .")
        mode_pat = self.pat
        to = change_to
        tonic = self.key_sig_num
        # print (tonic)
        # major to minor
        if self.mode == "Major" and to == "minor":
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
            midi.write_midifile("mode_changed2.mid", mode_pat)
        if self.mode == "minor" and to == "Major":
            print ("minor to Major")
            for i in mode_pat:
                for j in i:
                    if str(type(j)) == "<class 'midi.events.NoteOnEvent'>" or str(
                            type(j)) == "<class 'midi.events.NoteOffEvent'>":
                        # print (j)
                        if (j.data[0] % 12) == ((tonic + 3) % 12) or (j.data[0] % 12) == ((tonic - 4) % 12):
                            j.data[0] = j.data[0] + 1
            # print (str(self.file_path_) + "to_minor")
            midi.write_midifile("mode_changed.mid", mode_pat)

        # print mode_pat

    def signatures(self):

        key_votes = [-1] * 4  # first low note, last low note, most frequent, most frequent with dom
        vote_weights = [0.5, 1.2, 0.8, 1, 1]
        pattern = self.pat
        res = pattern.resolution
        break_point = res * 10
        do_trim = False
        key_accumulator = [0] * 12
        low_note_accumulator = [0] * 12
        first_note_tick = True
        given_key_mode = [-1] * 2
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
                    print ("Key given")
                    print j

                if str(type(j)) == "<class 'midi.events.NoteOffEvent'>" or (
                        str(type(j)) == "<class 'midi.events.NoteOnEvent'>" and j.data[1] == 0):
                    # print j
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
                            print ("breaking . . .")
                            break

                        key_accumulator[j.data[0] % 12] += 1
                        track_pitches.append(j.data[0])
                        # print ("Appended" + str(j.data[0]))
                    else:
                        print("Skipping percussion")
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

        print(track_pitch_ave)
        print ("First Notes")
        for n in first_notes_by_track:
            print n

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
        print ("First tracks pitch ave")
        print (first_track_pitch_ave)

        low_track = 0
        temp_ave = 128

        for n, p in enumerate(first_track_pitch_ave):
            print (n)
            print (p)
            # print ("temp_ave: " + str(temp_ave) + " p: " + str(p))
            if temp_ave > p != 0:
                # print ("update temp_ave")
                temp_ave = p
                low_track = n
        print ("Low track: " + str(low_track))
        print (first_notes_by_track[low_track])

        print ("Counting first low notes")
        for n, p in enumerate(first_notes_by_track[low_track]):
            print n
            print p
            low_note_accumulator[p[0] % 12] += 1
        print ("First low notes ")
        print(low_note_accumulator)
        first_bottom_key = low_note_accumulator.index(max(low_note_accumulator))

        # vote tonic
        key_votes[0] = first_bottom_key

        print (first_bottom_key)
        print self.keys[first_bottom_key]

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

        print("Most frequent notes")
        print(first)
        print(second)
        print(third)
        print(fourth)

        # vote tonic
        key_votes[2] = first[0]

        # looking at doms
        first_dom = (first[0] + 7) % 12
        second_dom = (second[0] + 7) % 12
        third_dom = (third[0] + 7) % 12

        # checking for tonic/dom relationship in case tonic is not the most frequent note
        if abs(first[1] - second[1]) <= first[1] * 0.25 and first[0] == second_dom:
            tonic = second
            print("Second")
        elif second[0] == first_dom or third[0] == first_dom or fourth[0] == first_dom:
            tonic = first
            print ("First")
        elif first[0] == second_dom or third[0] == second_dom or fourth[0] == second_dom:
            tonic = second
            print ("Second")
        elif first[0] == third_dom or second[0] == third_dom or fourth[0] == third_dom:
            tonic = third
            print ("Third")
        else:
            tonic = first
            print ("First2")
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

        print ("votes")
        print(key_votes)

        # look for tonic-dom pattern in votes

        vote_pattern = []
        for i in key_votes:
            found = False
            if i >= 0:
                for j in vote_pattern:
                    if j[0] == i:
                        print("3")
                        j[1] += 1
                        found = True
                if not found:
                    vote_pattern.append([i, 1])
        print ("vote_pattern")
        print (vote_pattern)

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
            print("pat tonic")
            votes_by_key[pat_tonic] += 1

        print("Votes by key")

        print(votes_by_key)

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
            tonic[0] = high_votes[0]

        print(tonic[0])

        # looking for mode based on tonic:

        # checking for pentatonic modes:
        print ("Penta section")
        penta = False
        note_num_ave = self.tot_notes / 12
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

        main_pitch_count = 0
        for c, i in enumerate(key_accumulator):
            if i > split_freq:
                main_pitch_count += 1
        if main_pitch_count < 6:
            penta = True

        # check melody

        print (key_accumulator)
        print (note_num_ave)
        print (split_freq)
        print (penta)

        if key_accumulator[(tonic[0] + 3) % 12] > key_accumulator[(tonic[0] + 4) % 12]:
            self.mode = "minor"
            if penta:
                self.mode = "minor pentatonic"
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
        print (event_sigs)

        if len(event_sigs) > 1 and self.first_tick >= event_sigs[1][2]:
            print ("empty sig")
            print(self.first_tick)
            self.time_sig = event_sigs[1]
        else:
            self.time_sig = event_sigs[0]

        if self.waltz:
            self.time_sig = [3, 4]

        # need to fix/get rid of the rest of this function

        note_length = 0  # in ticks, including any trailing silence
        note_lengths = []
        start_gaps = []

        for i in pattern:
            start_gap = 0
            for j in i:
                if str(j).startswith("midi.Note"):
                    if str(j).startswith("midi.NoteOn") and j.data[1] > 0:
                        if len(note_lengths) == 0:
                            start_gap = j.tick
                        if note_length > 0:
                            note_length += j.tick
                            note_lengths.append(note_length)
                            note_length = 0
                    else:
                        note_length += j.tick

            start_gaps.append(start_gap)

        note_lengths.append(note_length)

        note_length_count = {}
        for i in note_lengths:
            # print (i)
            if i in note_length_count:
                note_length_count[i] += 1
            else:
                note_length_count[i] = 1
        # print ("out")
        high_count_note_length = max(note_length_count, key=note_length_count.get)

        # print "high", high_count_note_length

        if res + (res * 0.1) > high_count_note_length > res - (res * 0.1):
            self.beat_in_ticks = res
            denominator = 4
        elif res / 2 + (res / 2 * 0.1) > high_count_note_length > res / 2 - (res / 2 * 0.1):
            self.beat_in_ticks = res / 2
            denominator = 8
        elif res * 2 + (res * 2 * 0.1) > high_count_note_length > res * 2 - (res * 2 * 0.1):
            self.beat_in_ticks = res * 2
            denominator = 2
        elif res / 4 + (res / 4 * 0.1) > high_count_note_length > res / 4 - (res / 4 * 0.1):
            self.beat_in_ticks = res / 4
            denominator = 16
        elif res / 8 + (res / 8 * 0.1) > high_count_note_length > res / 8 - (res / 8 * 0.1):
            self.beat_in_ticks = res / 8
            denominator = 32

        # print "*****************"
        # print (denominator)

        long_note = 0
        for x in note_length_count:
            if x > long_note:
                long_note = x
        if long_note != 0 and self.beat_in_ticks != 0:
            numerator = long_note / self.beat_in_ticks
        # print (numerator)

        # print "checkpoint 1"
        while numerator % 2 == 0 and denominator % 2 == 0 and numerator != 0 and denominator != 0:
            print numerator, denominator
            numerator = numerator / 2
            denominator = denominator / 2
        # print "checkpoint 2"
        while numerator % 2 == 0 and numerator != 0:
            numerator = numerator / 2
        # print "checkpoint 3"
        while numerator % 3 == 0 and numerator != 0:
            numerator = numerator / 3
        # print numerator, '/', denominator

        print("*************************")
        print(self.key_sig + " " + self.mode)
        print(str(self.time_sig[0]) + "/" + str(self.time_sig[1]) + " time")
        print("*************************")


def changevar():
    global variable
    variable = "Yep"


def printvar():
    global variable
    print(variable)


variable = "Nope"
# piece1 = None
file_path = "Music/pass1.mid"


# def main():
def load():
    root.withdraw()
    global file_path
    global piece1
    print(file_path)
    file_path = tkFileDialog.askopenfilename()
    piece1 = Piece(file_path)
    print(file_path)
    main = Tkinter.Toplevel()

    # change_mode = Tkinter.Button(main, text="Change Var", command=piece1.change_mode())
    sig = Tkinter.Button(main, text="Find key and time signatures", command=piece1.signatures)
    sig.pack()
    # change_mode.pack()

# root = Tkinter.Tk()
# root.withdraw()
root = Tkinter.Tk()
root.title("Music Minion")
# piece1 = Piece("Music/pass1.mid")
# piece1 = Piece(file_path)
load_piece = Tkinter.Button(root, text="Load a Piece", command=load)
load_piece.pack()
root.mainloop()

    # file_path = tkFileDialog.askopenfilename()
    #
    # test1 = Piece(file_path)
    # test1.signatures()
    # print(test1.key_sig + " " + test1.mode)
    #
    # #test1.change_mode("minor")
    # print(test1.key_sig + " " + test1.mode)
    # print(str(test1.time_sig[0]) + "/" + str(test1.time_sig[1]) + " time")
    #
    #
    # print("Done")


# main()
