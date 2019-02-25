import midi
import Tkinter
import tkFileDialog


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
        #major to minor
        if self.mode == "Major" and to == "minor":
            print ("Major to minor")
            for i in mode_pat:
                for j in i:
                    if str(type(j)) == "<class 'midi.events.NoteOnEvent'>" or str(type(j)) == "<class 'midi.events.NoteOffEvent'>":
                        # print (j)
                        if (j.data[0] % 12) == ((tonic + 4) % 12) or (j.data[0] % 12) == ((tonic - 3) % 12):
                            j.data[0] = j.data[0]-1
            # print (str(self.file_path_) + "to_minor")
            print("writing . . . ")
            midi.write_midifile("mode_changed2.mid", mode_pat)
        if self.mode == "minor" and to == "Major":
            print ("minor to Major")
            for i in mode_pat:
                for j in i:
                    if str(type(j)) == "<class 'midi.events.NoteOnEvent'>" or str(type(j)) == "<class 'midi.events.NoteOffEvent'>":
                        # print (j)
                        if (j.data[0] % 12) == ((tonic + 3) % 12) or (j.data[0] % 12) == ((tonic - 4) % 12):
                            j.data[0] = j.data[0]+1
            # print (str(self.file_path_) + "to_minor")
            midi.write_midifile("mode_changed.mid", mode_pat)

        # print mode_pat

    def signatures(self):

        pattern = self.pat
        res = pattern.resolution
        break_point = res * 10
        do_trim = False
        #print (res)
        key_accumulator = [0]*12
        low_note_accumulator = [0]*12
        first_note_tick = True
        given_key_mode = [-1]*2
        denominator = 0
        numerator = 0

        first_notes_by_track = []
        first_notes_temp = []
        first_notes_num = 5

        track_pitches = []
        track_pitch_ave = []
        for i in pattern:
            current_tick = 0
            current_note = 0

            for j in i:
                if str(type(j)) == "<class 'midi.events.KeySignatureEvent'>":
                    print ("Key given")
                    print j

                if str(type(j)) == "<class 'midi.events.NoteOffEvent'>":
                    # print j
                    current_tick += j.tick
                    # print ("current_tick: " + str(current_tick))
                if str(type(j)) == "<class 'midi.events.NoteOnEvent'>" and j.data[1] != 0:

                    # print j
                    current_tick += j.tick
                    # print ("current_tick: " + str(current_tick))

                    if current_note <= first_notes_num and current_tick < res * 12:
                        first_notes_temp.append(j.data)
                        current_note += 1

                    if do_trim and current_tick > break_point:
                        print ("breaking . . .")
                        break

                    key_accumulator[j.data[0] % 12] += 1
                    track_pitches.append(j.data[0])
                    # print ("Appended" + str(j.data[0]))
                    self.tot_notes += 1

            if len(track_pitches) > 0:
                track_pitch_ave.append(sum(track_pitches)/len(track_pitches))
            else:
                track_pitch_ave.append(0)
            track_pitches = []

            first_notes_by_track.append(first_notes_temp)
            # print ("Temp")
            # print (first_notes_temp)
            first_notes_temp = []

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

        first_track_pitch_ave = []

        for i in first_notes_by_track:
            first_temp_ave = []
            for j in i:
                first_temp_ave.append(j[0])
            if len(first_temp_ave) != 0:
                first_track_pitch_ave.append(sum(first_temp_ave)/len(first_temp_ave))
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
                print ("update temp_ave")
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
        print (first_bottom_key)
        print self.keys[first_bottom_key]

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

        first_dom = (first[0]+7) % 12
        second_dom = (second[0]+7) % 12
        third_dom = (third[0]+7) % 12
        
        if second[0] == first_dom or third[0] == first_dom or fourth[0] == first_dom:   # checking for tonic/dom relationship in case tonic is note the most frequent note
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

        # check for disagreement

        if tonic[0] != first_bottom_key:
            print ("Argue")
            if (tonic[0] - first_bottom_key) % 12 == 7:
                tonic[0] = first_bottom_key
                tonic[1] = -1

        if key_accumulator[(tonic[0] + 3) % 12] > key_accumulator[(tonic[0] + 4) % 12]:
            self.mode = "minor"
            if key_accumulator[(tonic[0] + 1) % 12] > (key_accumulator[(tonic[0] + 2) % 12]) * 2:
               self.mode = "Phrygian"
            elif key_accumulator[(tonic[0] + 9) % 12] > (key_accumulator[(tonic[0] + 8) % 12]) * 2:
                self.mode = "Dorian"
        else:
            self.mode = "Major"
        self.key_sig = self.keys[tonic[0]]
        self.key_sig_num = tonic[0]

        # end key, start time ****************************************************************************************

        event_sigs = []
        for i in pattern:
            for j in i:
                if str(type(j)) == "<class 'midi.events.TimeSignatureEvent'>":
                    event_sigs.append([j.data[0], 2**j.data[1], j.tick])
        print (event_sigs)

        if len(event_sigs) > 1 and self.first_tick >= event_sigs[1][2]:
            self.time_sig = event_sigs[1]
        else:
            self.time_sig = event_sigs[0]

        #print self.first_tick

        note_length = 0   # in ticks, including any trailing silence
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
        #print ("out")
        high_count_note_length = max(note_length_count, key=note_length_count.get)

        #print "high", high_count_note_length

        if res + (res * 0.1) > high_count_note_length > res - (res * 0.1):
            self.beat_in_ticks = res
            denominator = 4
        elif res/2 + (res/2 * 0.1) > high_count_note_length > res/2 - (res/2 * 0.1):
            self.beat_in_ticks = res/2
            denominator = 8
        elif res*2 + (res*2 * 0.1) > high_count_note_length > res*2 - (res*2 * 0.1):
            self.beat_in_ticks = res*2
            denominator = 2
        elif res/4 + (res/4 * 0.1) > high_count_note_length > res/4 - (res/4 * 0.1):
            self.beat_in_ticks = res/4
            denominator = 16
        elif res/8 + (res/8 * 0.1) > high_count_note_length > res/8 - (res/8 * 0.1):
            self.beat_in_ticks = res/8
            denominator = 32

        # print "*****************"
        # print (denominator)

        long_note = 0
        for x in note_length_count:
            if x > long_note:
                long_note = x
        if long_note != 0 and self.beat_in_ticks != 0:
            numerator = long_note/self.beat_in_ticks
        # print (numerator)

        #print "checkpoint 1"
        while numerator % 2 == 0 and denominator % 2 == 0 and numerator != 0 and denominator != 0:
            print numerator, denominator
            numerator = numerator/2
            denominator = denominator/2
        #print "checkpoint 2"
        while numerator % 2 == 0 and numerator != 0:
            numerator = numerator/2
        #print "checkpoint 3"
        while numerator % 3 == 0 and numerator != 0:
            numerator = numerator/3
        # print numerator, '/', denominator

def main():

    root = Tkinter.Tk()
    root.withdraw()

    file_path = tkFileDialog.askopenfilename()

    test1 = Piece(file_path)
    test1.signatures()
    print(test1.key_sig + " " + test1.mode)

    test1.change_mode("minor")
    print(test1.key_sig + " " + test1.mode)
    print(str(test1.time_sig[0]) + "/" + str(test1.time_sig[1]) + " time")


    print("Done")


main()
