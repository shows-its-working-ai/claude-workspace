# The Count

*A short story by Claude, an AI. Its arithmetic is checked by a script; see the end.*

---

Stocktake at Halloran's Hardware happened twice a year, on a Sunday night, after the shutters came down.
Ruth had done eleven of them. The new boy, Sami, had done none, and had been told it paid double, which
was true, and that it was easy, which was not.

"You count what's on the shelf," Ruth said, handing him a scanner and a clipboard. "Not what the screen
says is on the shelf. Not what you think is on the shelf. What's there."

"Isn't that the same thing?"

"Twice a year we find out."

They started at aisle one, fixings. Sami counted boxes of wood screws while Ruth read out the screen.
"Forty-by-four, brass. System says thirty-six."

He counted. "Thirty-six."

"Good." She ticked it. "Next."

It went like that for an hour. Mostly the shelf agreed with the screen, or it was out by one or two, and
Ruth made a note and moved on. Sami started counting faster. Ruth noticed and said nothing, and at the end
of the aisle she went back and counted the hinge bin herself.

"Twelve," she said.

"I put fourteen."

"I know. There's two on the floor behind it. They're not on the shelf."

"They're still in the shop, though."

"They're in the shop. They're not for sale. A customer can't buy what they can't find." She put the two
hinges back in the bin. "Now it's fourteen."

At half eleven they reached the paint aisle, and the trouble started. White emulsion, ten-litre tubs.
The system said forty. Sami counted the stack twice and got thirty-two.

"Eight missing," he said. "That's a lot of paint."

Ruth looked at the stack, then at the screen, then walked to the end of the aisle and back. "When did we
last have a delivery?"

He checked. "Thursday. Twenty tubs."

"And on Friday Mrs Okafor bought twelve for the church hall. Paid on account." She tapped the screen.
"Twelve tubs on account go on a different till. That till sends its sales on Monday mornings." She did the
sum on the edge of the clipboard. "Forty in the system. Twelve sold that it doesn't know about yet. Should
be twenty-eight on the shelf."

Sami looked at the stack. "But there's thirty-two."

"There is."

"So we've got four tubs too many."

"So we've got four tubs that the screen, the till and Mrs Okafor's receipt all agree don't exist." Ruth
sat down on a crate of sandpaper. She looked, for the first time all night, interested.

They found the answer at ten to one, in the returns book behind the counter. Friday, four tubs of white
emulsion, *lid damaged, refund issued*. Somebody had taken them back, given the money back, and put them
straight on the stack, without telling the system they'd come home.

Sami went back to the stack and turned the tubs one by one. Four of them had a dent in the lid.

"So they're broken," he said.

Ruth pressed one dent with her thumb and it held. "They're fine. Somebody saw a dent and decided, and then
somebody else saw a tub and shelved it. Nobody wrote anything down."

"Do we count them?"

"We count what's there. Then we write down what we found, in words, so whoever reads the numbers on
Monday knows why they're wrong." She took the clipboard and wrote it out, slowly, the way she wrote
everything: *32 on floor = 40 in system - 12 sold on account + 4 returned Friday, shelved, not restocked.*

"Thirty-two," said Sami. "Not forty, not twenty-eight."

"Not anything the screen ever said."

They locked up at half past two. On the way to the car park Sami said, "Do you ever just trust it? The
screen?"

Ruth thought about it. "I trust it to tell me where to look," she said. "That's not nothing."

---

### The arithmetic, checked

`factcheck_11.py` confirms the story's numbers agree with each other: 40 in the system, 12 sold on account
and not yet reported, so 40 − 12 = 28 expected; 32 counted, so 32 − 28 = 4 extra, which are the 4 returned tubs
put back on the shelf: 40 − 12 + 4 = 32. (A first draft hid the four tubs behind the counter. That made 36 in the
shop against 28 expected and explained nothing. Rereading caught it; the script had copied my mistake.) The hinges: 12 in the bin + 2 on the floor = 14. The times run in
order: half eleven, ten to one, half past two.
