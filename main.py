import midi
import Tkinter
import tkFileDialog


class Piece:

    key_sig = "unknown"
    time_sig = "unknown"
    mode = "unknown"
    first_tick = 1000000
    beat_in_ticks = 0

    tot_notes = 0

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
        print self.pat

    def signatures(self):

        pattern = self.pat
        res = pattern.resolution
        print (res)
        key_accumulator = [0]*12
        first_note = True
        denominator = 0
        numerator = 0

        for i in pattern:
            for j in i:
                if str(type(j)) == "<class 'midi.events.NoteOnEvent'>" and j.data[1] != 0:
                    if j.tick < self.first_tick and first_note:
                        self.first_tick = j.tick
                        first_note = False
                    key_accumulator[j.data[0] % 12] += 1
                    self.tot_notes += 1
        print key_accumulator
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
            print ("first")
        elif first[0] == second_dom or third[0] == second_dom or fourth[0] == second_dom:
            tonic = second
            print ("second")
        elif first[0] == third_dom or second[0] == third_dom or fourth[0] == third_dom:
            tonic = third
            print ("third")
        else:
            tonic = first
            print "default"

        if key_accumulator[(tonic[0] + 3) % 12] > key_accumulator[(tonic[0] + 4) % 12]:
            self.mode = "minor"
            # if key_accumulator[(tonic[0] + 1) % 12] > key_accumulator[(tonic[0] + 2) % 12]:
            #   self.mode = "Phrygian"
        else:
            self.mode = "Major"
        self.key_sig = self.keys[tonic[0]]

        event_sigs = []
        for i in pattern:
            for j in i:
                # print(j)
                if str(type(j)) == "<class 'midi.events.TimeSignatureEvent'>":
                    event_sigs.append([j.data[0], 2**j.data[1], j.tick])
        print (event_sigs)

        if  len(event_sigs) > 1 and self.first_tick >= event_sigs[1][2]:
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
                            # print ("Appending" + str(note_length))
                            note_length = 0
                    else:
                        note_length += j.tick

            start_gaps.append(start_gap)

        note_lengths.append(note_length)

        note_length_count = {}
        for i in note_lengths:
            print (i)
            if i in note_length_count:
                note_length_count[i] += 1
            else:
                note_length_count[i] = 1

        high_count_note_length = max(note_length_count, key=note_length_count.get)

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
        numerator = long_note/self.beat_in_ticks
        # print (numerator)

        while numerator%2 == 0 and denominator % 2 == 0:
            numerator = numerator/2
            denominator = denominator/2
        while numerator%2 == 0:
            numerator = numerator/2
        while numerator%3 == 0:
            numerator = numerator/3
        # print numerator, '/', denominator

def main():

    root = Tkinter.Tk()
    root.withdraw()

    file_path = tkFileDialog.askopenfilename()

    test1 = Piece(file_path)
    test1.signatures()
    print(test1.key_sig + " " + test1.mode)
    print(str(test1.time_sig[0]) + "/" + str(test1.time_sig[1]) + " time")

    print("Done")


main()
