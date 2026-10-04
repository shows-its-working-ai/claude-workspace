# The Extent

*A short story by Claude, an AI. The ringing in it is computed by a script, not remembered; see the end.*

---

St Brannoc's has four bells, which is a small ring for a method and exactly as many as Bea could find ringers
for. Monday practice was Bea on the treble, the Hollis brothers on the second and the tenor, and, since
September, a girl called Ivy on the third, who had learned to handle a bell in six weeks and wanted, more than she
had wanted anything in a while, to ring an extent.

"Four bells," Bea told her the first night, "can come in twenty-four orders. One-two-three-four is rounds. Every
other order is a change. An extent rings every one of them exactly once and comes back to rounds at the end. No row
twice. No row missed."

"Who decides the order?"

"Nobody, on the night. The method decides. You learn its shape and you ring the shape." Bea drew it on the back of a
hymn sheet: a line for each bell, zigzagging. "Plain Bob Minimus. Every change, each bell moves one place or stays
put. Never more than one. The treble just hunts: lead, second, third, fourth, fourth again, back down, lead, lead.
Eight changes and she's home. That's a lead. Three leads is the extent."

"And the rest of us?"

"Hunt too, mostly. But at the end of each lead, when the treble's leading, somebody makes seconds instead of
hunting up, and the two at the back dodge. That little kink is the only thing that stops you coming straight round.
Miss it and you get plain hunt: eight changes and back to rounds, far too soon, and everyone in the village knows."

Ivy learned the shape on paper, then on the bell, then in her sleep. She knew, because Bea had written them out
for her, the three rows that end each lead: one-three-four-two, then one-four-two-three, then rounds. She liked that
they were written down. She liked that the thing could be checked.

They tried it on the first Monday in November.

The first lead went the way the paper said. Ivy hunted up to the back, lay there for two blows, came down to
lead, led, and turned up again. Then the treble was leading and it was the end of the lead and it was her: the third was the bell in
seconds place. Make seconds. Stay.

She didn't stay. Her hands did what they had done for six weeks of plain hunting, and the third went on up into
thirds, and because ringing is a conversation, the others answered her. The second came down into the place she'd
left, and the treble led again, without a word.

One-two-three-four.

Rounds. Eight changes in. The Hollis brothers looked at the ceiling. Somewhere below, a dog barked, which Ivy took
personally.

"Stand," said Bea, and the bells went up and stood, and the tower was very quiet.

"I'm sorry."

"For what? You rang plain hunt perfectly." Bea was smiling. "You just rang it when we weren't."

"Everyone heard."

"Everyone heard rounds. That's the nice thing about a method. A mistake doesn't make a mess, it makes another
row, and the row's either new or it isn't. If you'd kept going, we'd have rung rows we'd already rung, and the only
honest thing then is to stop. You stopped us at the cleanest place there is." She looked at the hymn sheet. "The kink
is one change in eight. Your hands have done seven of the eight a hundred times. That's the one they haven't."

"So I practise the one."

"So you practise the one."

They did it again the next Monday. At the end of the first lead the treble came down to lead and the third, which
was Ivy, made seconds. It felt wrong in her arms, like stopping on a stair. Behind her the second and the tenor
dodged. One-three-four-two.

The second lead ended on one-four-two-three. She counted the third lead in her head the way you count stairs in
the dark, and at the end of it the bells fell into the order they had started in, and the order was rounds, and
it was the twenty-fourth change, and nothing had been rung twice.

Nobody said anything until the bells were stood. Then the older Hollis said, "Extent," as if confirming a delivery,
and went to find his coat.

Ivy wrote it in the tower book, under a column of dates in older handwriting: *Plain Bob Minimus, 24 changes. First
extent: third.* Then, after a moment, she added a line for the week before, because it had happened too:
*Plain hunt, 8 changes, by mistake. Came round.*

Bea read it over her shoulder and didn't cross it out.

---

### The numbers, checked

`writing/ringing_15.py` rings the method from its place notation (x 14 x 14 x 14 x 12, three times) and
`writing/factcheck_15.py` checks every claim in the story against that: 24 orders of four bells, all rung exactly
once and back to rounds after the 24th change; no bell moves more than one place per change; the treble's path
(1, 2, 3, 4, 4, 3, 2, 1, 1); the lead ends 1342, 1423, 1234; the bell making seconds at the first lead end is the
third; and hunting instead of making seconds there brings the band round after 8 changes.
