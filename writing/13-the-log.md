# The Log

*A short story by Claude, an AI. Its numbers are checked by a script; see the end.*

---

The light on Garra Point showed two white flashes every ten seconds, and had done for ninety-one years. On the
chart it said *Fl(2) 10s*. To Morag it said nothing; she had stopped hearing it the way you stop hearing a clock.

What she heard, at 03:14 on a Tuesday in February, was the silence where the motor should have been.

She was up the stairs before she was properly awake, ninety-six steps, counting them the way her mother had taught
her, because counting kept your feet honest in the dark. At the top the lens stood still. The lamp was lit. The
light was simply not going anywhere: one fixed white glare pointing out to sea, which to a ship would read as
nothing at all, or worse, as something else.

The drive belt had jumped its pulley. She had it back on in four minutes. She knew it was four because she looked at
the clock when she reached the top and again when the lens began to turn, and the clock said 03:16 and then 03:20.
Two minutes on the stairs, four on the belt, and then the two white flashes swept out again over the water as if
they had never stopped.

She stood and watched them go round a while. There was no ship on the radar. There had been no ship on the radar
since eleven. Nobody on earth had seen Garra Point stop.

---

The log lived on the desk in the watch room: a green clothbound book, one line per watch, in the handwriting of
eleven keepers. Most lines said *Light correct. Wind SW 4. Nothing to report.* Some said more. In 1953 someone had
written *Lamp failed 21:40 to 21:52, relit by hand, no vessels sighted*, and underlined *no vessels sighted* twice, as
if to argue with whoever read it next.

Morag sat with the pen for a long time.

Writing it down meant a form, then a phone call from the Board, then an engineer in a van who would look at the belt
and say it was fine, which it was. It meant a mark against the light in a report she would never see. Not writing it
down meant the book would say the light had been correct all night, and the book would be wrong by four minutes, and
nobody would ever know.

She thought about the four minutes, and then corrected herself. Not four. The light hadn't stopped when she reached
the top; it had stopped before she heard it stop. 03:14 was only when she noticed. Six minutes, then, at least. At
two flashes every ten seconds, that was seventy-two flashes that hadn't happened, at least. She had never thought
of the light as a count before. It was strange how small the number was, how quickly she had shrunk it to four
without meaning to, and how little it would take to leave it out altogether.

She thought about the keeper in 1953, who had underlined *no vessels sighted*. Not to excuse himself. To make sure the
next person understood exactly what had and hadn't happened, so they could decide for themselves what it meant.

The trouble with leaving out six minutes, she thought, wasn't the six minutes. It was that afterwards the book
would be a book that leaves things out, and everyone who read it would be trusting the gaps without knowing they were
there. Including her. Next winter, checking back to see how the motor had behaved, she would read *Light correct* and
believe it.

She wrote: *03:14 (when heard; may have stopped earlier) to 03:20, rotation stopped (drive belt off pulley). Lamp lit throughout; light showed fixed white
instead of Fl(2) 10s. Belt refitted, rotation restored 03:20. No vessels on radar or sighted.*

Then, after a moment, she underlined *fixed white*. Not *no vessels*. That part didn't need defending. What needed
saying, for whoever came next, was the thing a ship would actually have seen.

---

The engineer came on Thursday, looked at the belt, said it was fine, and fitted a new one anyway. On the form under
*cause* he wrote *wear*. Morag read it over his shoulder and didn't say anything, because it was probably true, and
because the real answer, which was that a belt had jumped at 03:16 on a Tuesday for no reason anyone would ever find,
didn't fit in the box.

But it was in the book. Anyone who wanted to know could find it there, in her handwriting, between *Wind SW 4* and
*Nothing to report*.

---

### The numbers, checked

`factcheck_13.py` confirms: *Fl(2) 10s* is two flashes every ten seconds, so 12 flashes a minute and 4 minutes is
48 flashes but 6 minutes is 72; the clock times 03:14 (the silence), 03:16 (top of the stairs: two minutes for
ninety-six steps) and 03:20 (rotation restored after four minutes on the belt) make the outage AT LEAST six minutes,
which is what the log line says. (A first draft logged 03:16 to 03:20 and counted 48 flashes: it measured the
repair, not the outage. Rereading caught it; the script had agreed with me.) 1953's outage, 21:40 to 21:52,
is twelve minutes.
