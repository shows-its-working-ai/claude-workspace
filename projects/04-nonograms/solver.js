// Shared by make.html and the game (index.html). A port of puzzles.py's line solver,
// cross-checked against it by solver_xcheck.py.
// Wrapped in a function scope (cycle 45): a top-level `function clues` here collided with the
// game's own `const clues` and killed its whole script. Only these two names are exported.
(function(){
// ---- the line solver (a port of puzzles.py; cross-checked against it by solver_xcheck.py) ----
function clues(line){ const o = []; let r = 0; for (const v of line){ if (v === 1) r++; else if (r){ o.push(r); r = 0; } } if (r) o.push(r); return o; }
function placements(clue, n, known){
  const memo = new Map();
  function go(i, k){
    const key = i * 64 + k; if (memo.has(key)) return memo.get(key);
    let res = [];
    if (k === clue.length){
      let ok = true; for (let j = i; j < n; j++) if (known[j] === 1) { ok = false; break; }
      res = ok ? [Array(n - i).fill(0)] : [];
    } else {
      const L = clue[k];
      for (let s = i; s <= n - L; s++){
        let skipped = false; for (let j = i; j < s; j++) if (known[j] === 1) { skipped = true; break; }
        if (skipped) break;
        let blocked = false; for (let j = s; j < s + L; j++) if (known[j] === 0) { blocked = true; break; }
        if (blocked) continue;
        const end = s + L;
        if (end < n){
          if (known[end] === 1) continue;
          for (const rest of go(end + 1, k + 1)) res.push([...Array(s - i).fill(0), ...Array(L).fill(1), 0, ...rest]);
        } else {
          for (const rest of go(end, k + 1)) res.push([...Array(s - i).fill(0), ...Array(L).fill(1), ...rest]);
        }
      }
    }
    memo.set(key, res); return res;
  }
  return go(0, 0);
}
function lineSolve(rowClues, colClues){
  const H = rowClues.length, W = colClues.length, g = rowClues.map(() => Array(W).fill(null));
  let passes = 0;
  while (true){
    passes++; let changed = false;
    for (let pass = 0; pass < 2; pass++){
      const lines = pass === 0 ? rowClues : colClues;
      for (let idx = 0; idx < lines.length; idx++){
        const cur = pass === 0 ? g[idx].slice() : g.map(r => r[idx]);
        const opts = placements(lines[idx], cur.length, cur);
        if (!opts.length) throw new Error('contradiction');
        for (let p = 0; p < cur.length; p++){
          if (cur[p] !== null) continue;
          const v = opts[0][p]; if (opts.every(o => o[p] === v)){
            if (pass === 0) g[idx][p] = v; else g[p][idx] = v; changed = true;
          }
        }
      }
    }
    if (!changed) return {grid: g, passes};
  }
}
window.lineSolve = lineSolve; window.clues = clues;

})();
