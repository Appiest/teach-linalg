# Day 13: Linear independence

The lesson opens on Day 1's arrows v = (3, 2) in yellow and w = (−1, 2) in blue, with Day 2's target
b = (5, 6) = 2v + w in pink. The centerpiece moves to space with u = (2, −1, 0) in yellow, v = (1, 2, 0) in blue
and w = (3, 1, h) in pink. Span{u, v} is the teal floor patch, and the box the three arrows build is a faint
purple-gray solid. The 3D view is a fixed oblique projection whose azimuth drifts slowly so the box reads as solid.
Orange marks only pivots and the travelling dot that walks a closed loop.

| t (s) | State | Trigger |
|---|---|---|
| 0–6 | Title card "Linear independence", "Day 13" | start |
| 6–9 | Glowing origin, grid draws outward | after title |
| 9–15 | v and w grow with labels | caption "Day 1's v and w already span the whole plane." |
| 15–19 | Pink b = (5, 6) grows | caption "Now we add a third vector, b." |
| 19–26 | A copy of v stretches to 2v; a copy of w springs to its tip and lands on b | caption "It equals 2v + w, so it adds nothing new." |
| 26–33 | b flips to point from its tip back to the origin; an orange dot walks the closed loop | caption "Walking back along −b returns you to the origin." |
| 33–38 | The relation 2v + w − b = 0 writes in the top left | caption "That loop says 2v + w − b = 0." |
| 38–47 | The relation becomes c1 v + c2 w + c3 b = 0 with live weights; weights spring to 0, the chain collapses to the origin | caption "Zero weights always work, and that is the trivial solution." |
| 47–52 | Hold at zero | caption "Vectors are independent when that is the only solution." |
| 52–58 | Weights spring back to (2, 1, −1); the loop reappears | caption "These three are dependent, because other weights also work." |
| 58–63 | Plane fades; oblique 3D axes with a floor grid draw on the right; the view starts drifting | caption "In space, u and v span a flat plane." |
| 63–68 | u and v grow; the teal patch of their span fades in | same caption |
| 68–74 | w = (3, 1, 2) grows with a dashed drop to the floor | caption "A third vector w rises above that plane." |
| 74–80 | The box's faces and edges fade in; "volume = 5 × h = 10" appears | caption "Together the three arrows build a box with real volume." |
| 80–88 | Matrix [u v w 0] writes in the top left, columns colored like the arrows | caption "Row reduce the matrix whose columns are u, v and w." |
| 88–94 | Morph to [1 0 1 0; 0 1 1 0; 0 0 h 0]; orange boxes land on the three pivots | caption "Every column has a pivot, so no variable is free." |
| 94–98 | Hold | caption "The only solution is zero, so they are independent." |
| 98–110 | **Centerpiece.** h springs 2 → 0: w sinks, the box flattens into the teal patch, the volume and the matrix's h entry fall together, and the third pivot box fades out | captions "Watch the box as w drops toward the plane." / "At h = 0 the box is flat and the pivot vanishes." |
| 110–117 | x1 = −x3, x2 = −x3, x3 free writes under the matrix | caption "Column three is free, so a nonzero solution appears." |
| 117–126 | A copy of v springs to u's tip; the orange dot walks u, v, −w; the relation u + v − w = 0 writes | caption "It reads u + v − w = 0, so w is redundant." |
| 126–131 | The 3D view clears; the plane returns with v, w, b and the loop | caption "Back in the plane, [v w b] has only two rows." |
| 131–139 | Matrix [v w b] morphs to its reduced form; two pivot boxes land, the third column gets a dashed outline | caption "Two rows hold two pivots, so one column is always free." |
| 139–143 | Hold | caption "More vectors than entries always makes a set dependent." |
| 143–151 | Takeaway card with origin pulse | end |
