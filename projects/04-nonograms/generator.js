// Random puzzle generator (cycle 47). Noise -> majority-vote smoothing (a cellular automaton) ->
// kept only if the shared solver proves it logic-solvable (which also means one answer).
(function(){
  function rng(seed){ let a = seed >>> 0; return () => { a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
  function candidate(W, H, rand, smooth){
    let g = Array.from({length: H}, () => Array.from({length: W}, () => rand() < 0.5 ? 1 : 0));
    for (let s = 0; s < smooth; s++)
      g = g.map((row, i) => row.map((_, j) => {
        let n = 0; for (let di = -1; di <= 1; di++) for (let dj = -1; dj <= 1; dj++) {
          const r = i + di, c = j + dj; if (r >= 0 && r < H && c >= 0 && c < W) n += g[r][c]; }
        return n >= 5 ? 1 : 0; }));
    return g;
  }
  window.generatePuzzle = function(seed, W = 10, H = 10, smooth = 2, maxTries = 400){
    const rand = rng(seed);
    for (let tries = 1; tries <= maxTries; tries++){
      const g = candidate(W, H, rand, smooth);
      const filled = g.flat().reduce((a, b) => a + b, 0);
      if (filled < 0.25 * W * H || filled > 0.75 * W * H) continue;          // not trivial-looking
      const rows = g.map(clues), cols = g[0].map((_, j) => clues(g.map(r => r[j])));
      const s = lineSolve(rows, cols);
      if (s.grid.flat().some(v => v === null)) continue;
      return {name: 'Surprise #' + seed, rows, cols, solution: g, passes: s.passes, tries,
              level: s.passes <= 3 ? 'easy' : s.passes <= 6 ? 'medium' : 'hard'};
    }
    return null;
  };
  window._candidate = (seed, W, H, smooth) => candidate(W, H, rng(seed), smooth);   // for the self-test
})();
