from .play_frequencies import play_frequencies
from .note_frequencies import get_note_frequencies

def play_guitar_standard():
    '''
        Plays E-A-D-G-B-E
    '''
    nf = get_note_frequencies()
    freqs = [nf['E'] / 2, nf['A'] / 2, nf['D'], nf['G'], nf['B'], nf['E'] * 2]
    play_frequencies(freqs)

# play_guitar_standard()