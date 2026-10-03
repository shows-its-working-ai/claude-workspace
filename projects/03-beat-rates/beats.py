"""Reference beat rates for 12-tone equal temperament (ideal strings, no inharmonicity).
Beat rate of an interval = |q*f_upper - p*f_lower| for the lowest coincident partials,
where the just ratio is p:q (upper:lower).  E.g. M3 = 5:4 -> |4*f_up - 5*f_low|."""
NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
INTERVALS = {"m3": (3, 6, 5), "M3": (4, 5, 4), "P4": (5, 4, 3), "P5": (7, 3, 2), "M6": (9, 5, 3)}

def freq(midi, a4=440.0):
    return a4 * 2 ** ((midi - 69) / 12)

def name(midi):
    return f"{NAMES[midi % 12]}{midi // 12 - 1}"

def beat(lower, iv, a4=440.0):
    semis, p, q = INTERVALS[iv]
    f1, f2 = freq(lower, a4), freq(lower + semis, a4)
    return abs(q * f2 - p * f1)

if __name__ == "__main__":
    for low, iv in [(53, "M3"), (57, "M3"), (60, "M3"), (53, "P5"), (60, "P5"), (57, "P5"), (53, "P4"), (60, "P4")]:
        semis = INTERVALS[iv][0]
        print(f"{name(low)}-{name(low + semis)} {iv}: {beat(low, iv):.3f} beats/s")
