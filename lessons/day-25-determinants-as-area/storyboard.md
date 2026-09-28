# Day 25: The determinant measures area

Day 5's picture carries over: the static grid stays underneath, dimmed, while a blue copy of the grid moves.
$\hat\imath$ and the first column are green, $\hat\jmath$ and the second column are red. The unit square and
every positively oriented parallelogram are yellow, and a flipped parallelogram is pink, which matches the web
widget `TransformExplorer` with `showArea`. The small curved arrow from the green column to the red column is
orange (a small mark), and it turns counterclockwise or clockwise with the sign of the determinant.

The main matrix is $A = \begin{bmatrix} 3 & 1 \\ 1 & 2 \end{bmatrix}$, so $a, b, c, d$ are all positive and the
bounding-box argument works with whole-number pieces: the box is $4 \times 3 = 12$, the two $\tfrac12 ac$
triangles total 3, the two $\tfrac12 bd$ triangles total 2, the two $bc$ rectangles total 2, and $12 - 7 = 5 =
3\cdot2 - 1\cdot1$. In the centerpiece the red column swings on a circle of radius $\sqrt5$ from $(1, 2)$ down to
$(2, -1)$ while the green column stays at $(3, 1)$. Along that path $\det A = \sqrt{50}\,\sin(\varphi - \varphi_0)$
with $\varphi_0 = \arctan\tfrac13$, so it runs from $5$ through $0$ (when the red column lies on the line through
$(3, 1)$) to exactly $-5$. The grid is drawn live from one 2×2 matrix (`LiveMatrix` in `engine/theme.py`), so the
blue grid, the arrows, the parallelogram, the orientation arrow and the counter are all functions of the current
matrix. The plane fills the left two thirds at 1.45 units per step; a dark side panel on the right holds the math.

| t (s) | State | Trigger |
|---|---|---|
| 0–9 | Title card "The determinant measures area", "Day 25"; glowing origin; grid draws outward | start |
| 9–16 | Static grid dims; yellow unit square fills; green $\hat\imath$ and red $\hat\jmath$ grow; a "1" sits inside the square | caption "The unit square has area 1." |
| 16–26 | Side panel slides in with $A$ (green and red columns). The blue grid morphs $I \to A$; the square rides along into the parallelogram on $(3, 1)$ and $(1, 2)$; the "1" fades | captions "Here is a matrix A." / "A carries the square onto a parallelogram." |
| 26–31 | The green column of $A$ and the green arrow pulse together, then the red pair | caption "Its sides are the two columns of A." |
| 31–60 | Blue grid fades. Dashed box around the parallelogram; side lengths a, b, c, d slide onto its edges. Panel: area $=(a+b)(c+d)$. The two $\tfrac12 ac$ triangles fill purple-gray and the panel appends $-ac$; then the two $\tfrac12 bd$ triangles and $-bd$; then the two $bc$ rectangles and $-2bc$. The terms expand and cancel into $= ad - bc$ | captions "Put a box around it, $(a+b)$ wide and $(c+d)$ tall." / "Cut away two triangles of area $\tfrac12 ac$." / "Two more triangles have area $\tfrac12 bd$." / "Two rectangles have area $bc$." / "Expand the box and almost everything cancels." |
| 60–70 | Pieces and box fade. Panel: $\det A = ad - bc = 3\cdot2 - 1\cdot1 = 5$; a "5" lands inside the parallelogram | captions "That leftover number is the determinant of A." / "For our A, it is 3·2 − 1·1 = 5." |
| 70–78 | Blue grid returns; four neighbouring grid cells fill yellow one after another | captions "Every grid square lands on a copy of this parallelogram." / "So A multiplies every area by 5." |
| 78–112 | **Centerpiece.** Panel becomes the live matrix and a live $\det A$ counter. An orange curved arrow turns counterclockwise from green to red. The red column swings down; the parallelogram thins and the counter falls. At 0 it stops: the parallelogram is a segment, the whole blue grid lies on one line, the arc vanishes. Then it swings on: the parallelogram reopens pink, the arc turns clockwise, the counter reaches −5 | captions "Swing the red column down toward the green one." / "At det A = 0 the parallelogram is flat." / "The whole plane is squashed onto one line." / "Flat means no inverse, as on Day 7." / "Past the line, the determinant turns negative." / "The turn from green to red is now clockwise." / "The plane has been flipped over, like a mirror image." / "Its area is $\|\det A\| = 5$, and the sign records the flip." |
| 112–126 | Everything resets to $I$. The matrix morphs straight to $\begin{bmatrix} 0 & 1 \\ 1 & 0 \end{bmatrix}$: the square flattens onto $y = x$ and reopens pink, counter $1 \to 0 \to -1$ | captions "Swapping the columns mirrors the plane across y = x." / "A mirror keeps area and flips the plane, so det = −1." |
| 126–135 | Takeaway card with origin pulse | end |
