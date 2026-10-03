"""Cycle 101: for which n is EVERY n x n Lights Out board solvable? (= the n^2 x n^2 press matrix has full rank over
GF(2); otherwise the nullity k means only 1 in 2^k boards is solvable and each has 2^k solutions.)
Prediction (written first, about mathematics): among n = 1..20, between 5 and 10 sizes are deficient.
Control: n = 5 must give rank 23 (nullity 2), as brute-forced in cycle 98."""
def nullity(n):
    cols = []
    for r in range(n):
        for c in range(n):
            v = 0
            for dr, dc in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                rr, cc = r + dr, c + dc
                if 0 <= rr < n and 0 <= cc < n: v |= 1 << (rr * n + cc)
            cols.append(v)
    pivots = {}                                      # highest bit -> vector (xor basis)
    for v in cols:
        while v:
            h = v.bit_length() - 1
            if h in pivots: v ^= pivots[h]
            else: pivots[h] = v; break
    return n * n - len(pivots)

if __name__ == "__main__":
    res = {n: nullity(n) for n in range(1, 21)}
    print("CONTROL n=5: rank", 25 - res[5], "OK" if res[5] == 2 else "MISMATCH")
    for n, k in res.items():
        print(f"n={n:2d}: nullity {k:2d}" + (f"  -> only 1 in {2**k:,} boards solvable" if k else "  -> every board solvable"))
    deficient = [n for n, k in res.items() if k]
    print("deficient sizes:", deficient, f"({len(deficient)} of 20)")
    print("PREDICTION", "HELD" if 5 <= len(deficient) <= 10 else "FAILED", "(5-10)")
    # independent source: OEIS A075462, "number of solutions to the all-ones lights out problem on an n X n square"
    # (fetched cycle 101). The all-ones board is always solvable, so its solution count is exactly 2^nullity.
    A075462 = [1, 1, 1, 16, 4, 1, 1, 1, 256, 1, 64, 1, 1, 16, 1, 256, 4, 1, 65536, 1]
    match = all(2 ** res[n] == A075462[n - 1] for n in range(1, 21))
    print("OEIS A075462 (2^nullity) matches for n = 1..20:", match)
    print("SIZES OK" if match and res[5] == 2 else "SIZES FAILED")
