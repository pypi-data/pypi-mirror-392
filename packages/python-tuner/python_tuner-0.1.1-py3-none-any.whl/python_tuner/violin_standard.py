from .play_frequencies import play_frequencies
from .note_frequencies import get_note_frequencies

def play_violin_standard():
    '''
        Plays C-G-D-A-E
    '''
    nf = get_note_frequencies()
    freqs = [nf['C'] / 2, nf['G'] / 2, nf['D'], nf['A'], nf['E'] * 2]
    play_frequencies(freqs)

#  play_violin_standard()