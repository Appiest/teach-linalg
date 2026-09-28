# Day 24: Image (range)

The lesson reuses Day 16's and Day 18's matrix as the map $T(\mathbf x) = A\mathbf x$ on $\mathbb R^3$:
$$A = \begin{bmatrix}1&0&-1\\0&1&1\\1&1&0\end{bmatrix},\qquad \operatorname{Col}A:\ x_3 = x_1 + x_2,\qquad \ker T = \operatorname{Span}\{(1,-1,1)\}.$$
Its columns stay green, red and pink, the range is teal (Day 18's color for what survives), the kernel is pink
(Day 18's color for what is crushed), and inputs are blue. Glow (orange) marks only the origin, the unreachable probe
$\mathbf b$ and the counting stamps. The 3D pictures use Day 18's flat oblique view (`OrbitingView`).

The centerpiece splits $\mathbb R^3$ into the pink kernel line and the blue floor plane $x_3 = 0$, a complement to it.
The input $\mathbf x = (2, 0, 1)$ is the floor vector $(1, 1, 0)$ plus the kernel vector $(1, -1, 1)$. As every point
slides from $\mathbf p$ to $A\mathbf p$, the floor tilts up onto the teal plane one-for-one, the kernel line shrinks
into the origin, and $\mathbf x$ lands on $T(\mathbf x) = (1, 1, 2)$, the same place as its floor part. All numbers were
checked with numpy. The final render runs 143 seconds, so the timings below are approximate.

| t (s) | State | Trigger |
|---|---|---|
| 0–8 | Title card "Image (range)", "Day 24"; glowing origin | start |
| 8–16 | $T(\mathbf x) = A\mathbf x$ writes top left with colored columns; axes draw; ten blue input dots appear in the cube; the view swings | captions "Day 18's matrix gives a map $T$ from $\mathbb R^3$ to $\mathbb R^3$.", then over the blue input dots the motivation "Yesterday we asked which inputs $T$ sends to $\mathbf 0$.", "Today we ask which outputs $T$ can reach." |
| 16–26 | Every dot slides from $\mathbf p$ to $A\mathbf p$ and turns teal; the kernel dot $(1,-1,1)$ lands on the origin; the teal sheet fades in with its tag $\operatorname{range}T$ | captions "Send each input to its output.", "Every output lands on one tilted plane." |
| 26–36 | Definition panel: $\operatorname{range}T = \{T(\mathbf x) : \mathbf x \in \mathbb R^3\}$, then $= \operatorname{Col}A$; the green and red column arrows grow inside the sheet | captions "The set of all outputs is the range, or image, of $T$.", "For a matrix map, the range is the column space." |
| 36–52 | Yellow $T(\mathbf u)$ and blue $T(\mathbf w)$ grow in the sheet; blue slides tip to tail; teal $T(\mathbf u + \mathbf w)$ grows, still in the sheet. Panel writes the three closure lines | captions "Add two outputs and you get $T(\mathbf u + \mathbf w)$, another output.", "Scaling and zero work the same way, so the range is a subspace." |
| 52–68 | Arrows leave. An orange ring marks $\mathbf b = (1, 1, 0)$ below the sheet, and a dashed orange line joins it to the sheet. Panel writes $T$ onto $\iff \operatorname{range}T = W$ | captions "Day 16 showed that no input reaches $\mathbf b = (1, 1, 0)$.", "A map is onto when its range is the whole codomain $W$.", "This range is only a plane in $\mathbb R^3$, so $T$ is not onto.", then (ring still up) the forward pointer "Day 38 finds the closest output when $\mathbf b$ is unreachable." |
| 68–80 | Stage clears back to the unmoved inputs: pink kernel line and a blue floor grid on $x_3 = 0$ | captions (goal, over the empty axes) "We want to count how many input dimensions survive $T$.", "Now split the inputs into two parts.", "The kernel line and the floor plane $x_3 = 0$ share only $\mathbf 0$." |
| 80–90 | Yellow $\mathbf x = (2,0,1)$ grows; blue floor part $(1,1,0)$ and pink kernel part $(1,-1,1)$ draw tip to tail | caption "Every input is a floor part plus a kernel part." |
| 90–104 | **Centerpiece:** everything slides to its image. The floor grid tilts up onto the teal plane, the kernel line shrinks into the origin (orange flash), the pink piece of $\mathbf x$ shrinks to nothing, and $\mathbf x$ lands on $T(\mathbf x) = (1,1,2)$ | captions "Apply $T$: the kernel part collapses to zero.", "The floor lands on the range one-for-one." |
| 104–118 | Count panel: $\dim\ker T = 1$ (pink), $\dim\operatorname{range}T = 2$ (teal), $1 + 2 = 3 = \dim\mathbb R^3$ | captions "One input dimension is crushed and two survive.", "Crushed plus surviving gives back all three." |
| 118–128 | Stage clears. Theorem writes: $\dim\ker T + \dim\operatorname{range}T = \dim V$ | caption "This works for every linear map on a finite-dimensional space." |
| 128–150 | Three budget rows. Each shows $\dim V$ cells split pink and teal, and $\dim W$ cells that the teal cells fill: $\mathbb P_2 \to \mathbb R^2$ (1 + 2, fills both, onto); $D : \mathbb P_3 \to \mathbb P_2$ (1 + 3, fills all three, onto); $\mathbb R^3 \to \mathbb R^4$ (at most 3 teal, one cell stays empty with an orange cross) | captions "Evaluating at 0 and 1 kills one dimension of $\mathbb P_2$.", "Differentiation on $\mathbb P_3$ kills only the constants.", "Three input dimensions can never fill $\mathbb R^4$." |
| 150–158 | Takeaway card with origin pulse | end |
