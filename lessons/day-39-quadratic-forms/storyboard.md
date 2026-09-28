# Day 39: Quadratic forms

The video keeps Day 30's symmetric matrix $A = \begin{bmatrix} 2 & 1 \\ 1 & 2 \end{bmatrix}$. Its eigenvalue $3$ lives on the
yellow line through $\mathbf u_1 = (1, 1)/\sqrt2$ and its eigenvalue $1$ on the blue line through $\mathbf u_2 = (-1, 1)/\sqrt2$,
the same two lines as Day 30. The form is $Q(\mathbf x) = \mathbf x^TA\mathbf x = 2x_1^2 + 2x_1x_2 + 2x_2^2$. Its level curve
$Q = 14$ passes through twelve lattice points such as $(1, 2)$, so the ellipse can be built from dots before it is drawn.
The sample input $\mathbf x = (1, 2)$ is purple-gray, as ordinary inputs were on Day 32, and the curve and every value of $Q$
are teal because they are results. The rotating grid is purple-gray like Day 32's eigen-grid, and orange marks only the
cross term and small highlights.

The plane sits left of centre, 1 scene unit per step, so the equation panel fits on the right. The 3D half is drawn in a flat
scene through `OrbitingView`, with a polar mesh sorted back to front (`height_field` in `engine/theme.py`). Heights are
drawn at 0.4 of their true size so the bowl and the saddle both fit. The mesh is teal where $Q > 0$ and pink where $Q < 0$.

| t (s) | State | Trigger |
|---|---|---|
| 0–8 | Title card "Quadratic forms", "Day 39"; glowing origin; grid draws | start |
| 8–30 | Panel top right: $A$ with its two off-diagonal 1s. $Q(\mathbf x) = \mathbf x^TA\mathbf x$ writes in, then expands to $2x_1^2 + 2x_1x_2 + 2x_2^2$. The diagonal 2s and the squared terms glow together, then both 1s and the cross term glow | captions "Day 34 gave every symmetric matrix perpendicular eigenvectors." / "Today we ask what shape $\mathbf x^TA\mathbf x$ has, and where it peaks." (yellow and blue eigen-lines with $\lambda = 3$, $\lambda = 1$ on the plane) / "A symmetric $A$ turns each vector $\mathbf x$ into one number." / "Squared lengths and variances are numbers of this kind." (held on the expanded form) / "The diagonal gives the squares, and both 1s make the cross term." |
| 30–42 | Gray $\mathbf x = (1, 2)$ grows; $Q(1, 2) = 2 + 4 + 8 = 14$ writes under the form. Eleven more teal dots pop in where $Q = 14$, then the teal ellipse draws through all twelve | captions "At $\mathbf x = (1, 2)$ the form gives $14$." / "Every point with $Q = 14$ lies on one tilted ellipse." |
| 42–70 | **Centerpiece.** The cross term gets an orange box. A purple-gray copy of the grid appears with axes $y_1, y_2$, and a live readout $Q = a\,y_1^2 + b\,y_1y_2 + c\,y_2^2$. The grid turns 20°: $b$ drops from $2$ to $1.53$. It turns on to 45°: $b$ reaches $0$, the axes turn yellow and blue, and the readout settles on $3y_1^2 + 1y_2^2 = 14$. The coefficients 3 and 1 glow against $\lambda = 3$, $\lambda = 1$ on the lines. Half-axis bars of length $2.16$ (yellow) and $3.74$ (blue) grow. $\mathbf x = P\mathbf y$, $\mathbf x^TA\mathbf x = \mathbf y^TD\mathbf y$ lands in the panel | captions "The cross term $2x_1x_2$ is what tilts the ellipse." / "We want axes where the cross term disappears." / "Along the eigenvectors the cross term reaches zero." / "The new coefficients are the eigenvalues 3 and 1." / "The bigger eigenvalue gives the shorter axis." / "$A = PDP^T$ from Day 34 does this for any form." |
| 70–96 | Plane leaves. Oblique 3D view: floor grid with the yellow and blue eigen-lines, then the teal bowl $z = Q(\mathbf x)$ fades up while the view turns slowly. A white unit circle on the floor lifts onto the bowl, and an orange dot walks around it with a live readout of $Q$. It stops above $\mathbf u_1$ (yellow mark, $Q = 3$) and above $\mathbf u_2$ (blue mark, $Q = 1$) | captions "Now graph $z = Q(\mathbf x)$ above the plane." / "Which unit vector makes $Q$ largest? Walk the circle." / "The highest point sits above $\mathbf u_1$, at height $3$." / "Day 40 uses this peak to find singular values." / "The lowest sits above $\mathbf u_2$, at height $1$." |
| 96–118 | Readout becomes a number line with a yellow dot at $\lambda_1 = 3$ and a blue dot at $\lambda_2$, and a name under it. $\lambda_2$ slides $1 \to 0$: the bowl flattens into a trough along $\mathbf u_2$ ("positive semidefinite"). $\lambda_2$ slides $0 \to -2$: the blue direction bends down, pink appears, and the bowl becomes a saddle ("indefinite"). The lifted unit circle follows, dipping to $-2$ above $\mathbf u_2$ | captions "The eigenvalues decide whether $Q$ is ever negative." / "Both eigenvalues are positive, so every value is positive." / "At $\lambda_2 = 0$ the bowl flattens into a trough." / "A negative eigenvalue bends the bowl into a saddle." |
| 118–126 | Takeaway card with origin pulse | end |

Stills: `FigPrincipalAxes` (the tilted ellipse under the turned grid, with both equations), `FigBowlTroughSaddle` (three
surfaces with their eigenvalues), `FigUnitCircleHeights` (the graph of $Q(\cos\theta, \sin\theta) = 2 + \sin 2\theta$ with its
top at $\theta = 45^\circ$ and bottom at $\theta = 135^\circ$). The poster is the saddle with its teal and pink halves, the
eigen-lines and the lifted unit circle.
