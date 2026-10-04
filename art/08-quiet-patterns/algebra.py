"""Cycle 107: predict the symmetric quiet-pattern dimensions from polynomials alone, and compare with rect.py's solver.
GF(2) polynomials are Python ints (bit i = coefficient of s^i).
Model: quiet X solves A X = X B, A = T_m + I, B = T_n. Reversal J_k = q_k(T_k). Up-down mirror acts as q_m(s+1),
left-right as q_n(s), both by left multiplication by a polynomial in s = A, on R = GF(2)[s]/(g),
g = gcd(chi_m(s+1), chi_n(s)). Then
  dim fixed by half-turn    = deg gcd(1 + q_m(s+1) q_n(s), g)
  dim fixed by both mirrors = deg gcd(1 + q_m(s+1), 1 + q_n(s), g)."""
from rect import invariant_kernel, HALF, LR, UD

deg = lambda a: a.bit_length() - 1
def mul(a, b):
    r = 0
    while b:
        if b & 1: r ^= a
        a <<= 1; b >>= 1
    return r
def mod(a, b):
    while a and deg(a) >= deg(b): a ^= b << (deg(a) - deg(b))
    return a
def gcd(a, b):
    while b: a, b = b, mod(a, b)
    return a
def shift(p):                       # p(s) -> p(s + 1), by Horner
    r = 0
    for i in range(deg(p), -1, -1): r = mul(r, 0b11) ^ (p >> i & 1)
    return r
def chi(k):                         # characteristic polynomial of the k-path adjacency, mod 2
    a, b = 1, 0b10
    if k == 0: return a
    for _ in range(k - 1): a, b = b, mul(0b10, b) ^ a
    return b
def q(k):
    """The polynomial with q(T_k) = J_k: solve q(T) e_0 = e_{k-1}. T^i e_0 has top index i (triangular)."""
    vecs = [1]                      # vectors as ints over positions 0..k-1
    for _ in range(k - 1):
        v = vecs[-1]; w = 0
        for j in range(k):
            if v >> j & 1:
                if j > 0: w ^= 1 << (j - 1)
                if j < k - 1: w ^= 1 << (j + 1)
        vecs.append(w)
    target, p = 1 << (k - 1), 0
    for i in range(k - 1, -1, -1):
        if target >> i & 1: target ^= vecs[i]; p |= 1 << i
    assert target == 0
    return p
def matpoly_is_J(k, p):             # independent check: evaluate p(T) as a matrix and compare with J
    T = [[1 if abs(r - c) == 1 else 0 for c in range(k)] for r in range(k)]
    def mm(X, Y): return [[sum(X[r][t] & Y[t][c] for t in range(k)) & 1 for c in range(k)] for r in range(k)]
    P = [[0] * k for _ in range(k)]; Pw = [[int(r == c) for c in range(k)] for r in range(k)]
    for i in range(deg(p) + 1):
        if p >> i & 1: P = [[P[r][c] ^ Pw[r][c] for c in range(k)] for r in range(k)]
        Pw = mm(Pw, T)
    return all(P[r][c] == int(r + c == k - 1) for r in range(k) for c in range(k))

if __name__ == "__main__":
    assert all(matpoly_is_J(k, q(k)) for k in range(1, 25)), "q(T) != J"
    print("q_k(T_k) == J_k verified as matrices for k <= 24")
    mism = []; cases = 0
    for m in range(1, 41):
        for n in range(m, 41):
            g = gcd(shift(chi(m)), chi(n))
            qm, qn = shift(q(m)), q(n)
            half = deg(gcd(1 ^ mul(qm, qn), g)) if g else 0
            both = deg(gcd(gcd(1 ^ qm, 1 ^ qn), g)) if g else 0
            sh, sb = len(invariant_kernel(m, n, [HALF])), len(invariant_kernel(m, n, [LR, UD]))
            cases += 1
            if (half, both) != (sh, sb): mism.append((m, n, (half, both), (sh, sb)))
    print(f"{cases} boards compared; mismatches: {mism[:8] or 'none'}")
    print("PREDICTION", "HELD" if not mism else "FAILED", "(polynomial model == solver for all 1 <= m <= n <= 40)")
