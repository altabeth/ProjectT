import midi
import Tkinter
import tkFileDialog


class Piece:

    key_sig = "unknown"
    time_sig = "unknown"
    mode = "unknown"
    first_tick = 1000000

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
        key_accumulator = [0]*12
        first_note = True
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

        if self.first_tick > 0 and len(event_sigs) > 1:
            self.time_sig = event_sigs[1]
        else:
            self.time_sig = event_sigs[0]

        print self.first_tick


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
