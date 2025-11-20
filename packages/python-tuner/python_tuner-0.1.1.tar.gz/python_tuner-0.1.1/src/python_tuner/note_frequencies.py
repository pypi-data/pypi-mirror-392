def get_note_frequencies():
    '''
        Returns a dictionary of frequencies.
    '''

    # Starts at C, base note used for frequency calculations
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'] 
    #         0    1     2    3     4    5    6     7    8     9    10    11              

    # Frequency of middle C (C4)
    base_freq = 261.63

    # 12 tone equal temperament: note_freq = base_freq * 2^(n/12) where n is number of notes from base note
    note_freqs = {notes[i]: base_freq * pow(2,(i/12)) for i in range(len(notes))} 

    return note_freqs