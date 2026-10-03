"""Is "00010011011111" really Rule 110's ether, and do single flips in it make gliders?"""
from levels import run

TILE = [int(c) for c in "00010011011111"]

def periodic(W, dt):
    base = TILE * (W // 14)
    rows = run(110, [], W, dt + 1, base=base)
    for dx in range(W):
        if rows[dt] == base[dx:] + base[:dx]:
            return dx
    return None

def defect_profile(W, T, flip):
    base = TILE * (W // 14)
    clean, hit = run(110, [], W, T, base=base), run(110, [flip], W, T, base=base)
    diff = [[a != b for a, b in zip(r1, r2)] for r1, r2 in zip(clean, hit)]
    last = diff[-1]
    width = (max(i for i, v in enumerate(last) if v) - min(i for i, v in enumerate(last) if v) + 1) if any(last) else 0
    return sum(last), width

if __name__ == "__main__":
    for W in (14, 28, 42):
        for dt in range(1, 15):
            dx = periodic(W, dt)
            if dx is not None:
                print(f"W={W}: smallest period dt={dt} (shift dx={dx})"); break
        else:
            print(f"W={W}: NOT periodic within 14 steps")
    W, T = 42, 28
    print(f"\nsingle flips in ether, W={W}, after {T} steps: (#cells differing, spread width)")
    kinds = {"dies": 0, "localized": 0, "spreads": 0}
    for x in range(14, 28):
        n, w = defect_profile(W, T, x)
        k = "dies" if n == 0 else "localized" if w <= 14 else "spreads"
        kinds[k] += 1
        print(f"  flip {x}: diff={n:3d} width={w:2d} -> {k}")
    print(kinds)
