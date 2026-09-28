# Day 38: Least squares

Data: three points (0, 0), (1, 4), (2, 2). The line y = β₀ + β₁x gives X = [1 0; 1 1; 1 2] and y = (0, 4, 2).
Columns a₁ = (1, 1, 1) are green and a₂ = (0, 1, 2) red, y is yellow, the predictions and the fitted line are teal,
and residuals are pink. The best line is β̂ = (1, 1), with residual (−1, 2, −1) and sum of squares 6. The 3D view
draws the second entry upward so the residual rises off Col X, as b does above the plane in Lay's Figure 1.

The times below are the plan. The final render runs 135 s because the holds came out shorter.

| t (s) | State | Trigger |
|---|---|---|
| 0–6 | Title card "Least squares", "Day 38" | start |
| 6–9 | Origin pulse; small data grid draws on the left | after title |
| 9–12 | Three yellow points pop in | caption "When Ax = b has no solution, what is the best x?" |
| 12–15 | Hold on the three points | caption "Day 36's projection finds closest points, so it can answer this." |
| 15–18 | Coordinates appear beside the points | caption "Three measurements, and we want one line through them." |
| 14–18 | y = β₀ + β₁x appears at top right | caption "A line has two numbers to choose." |
| 18–26 | Each point flashes and its equation β₀ + x β₁ = y slides in | caption "Each point asks the line to pass through it." |
| 26–31 | The three equations fade into X β = y, columns green and red, y yellow | caption "Together they form one system." |
| 31–37 | Teal line y = x through (0, 0) and (2, 2); pink miss of 3 at x = 1 | caption "A line through two points misses the third." |
| 37–41 | Hold | caption "No line hits all three, so X β = y has no solution." |
| 41–47 | Line springs to the flat y = 2; pink residual segments appear | caption "Each vertical miss is a residual." |
| 47–53 | Pink squares grow on the residuals; readout r₁² + r₂² + r₃² = 8.00 | caption "Square the residuals and add them up." |
| 53–60 | Line springs to y = 1.5x; squares and the readout (7.25) follow | caption "Least squares picks the line with the smallest total." |
| 60–63 | Hold on the line y = 1.5x and its squares | caption "Rewrite the fit so that projection can find the best line." |
| 63–64 | Equations leave; oblique 3D axes draw on the right | caption "Now stack the three heights into one vector." |
| 64–70 | The column (0, 4, 2) slides out of the system and lands as the tag of the yellow arrow y | same |
| 70–78 | Green a₁ and red a₂ grow; teal sheet Col X fills between them | caption "Every prediction Xβ lies on the plane Col X." |
| 78–84 | Teal Xβ for the current line and the pink residual from Xβ to y | caption "The residual vector joins Xβ to y." |
| 84–88 | Readout gains ‖y − Xβ‖² in front | caption "Its squared length is the same sum of squares." |
| 88–96 | **Centerpiece:** β springs to (1, 1). Left: the line settles, the squares shrink, the total drops to 6.00. Right: Xβ slides to the foot of y while the view orbits slowly | caption "Let the line settle into its best position." |
| 96–101 | Orange right-angle mark at Xβ̂ | caption "The best residual is perpendicular to the plane." |
| 101–106 | Hold both pictures | caption "Xβ̂ is the projection of y onto Col X." |
| 106–109 | Hold both pictures | caption "Now turn that right angle into equations we can solve." |
| 109–112 | Data plot fades; a₁ · (y − Xβ̂) = 0 and a₂ · (y − Xβ̂) = 0 write on the left | caption "Perpendicular to the plane means perpendicular to both columns." |
| 112–117 | The two rows stack into Xᵀ(y − Xβ̂) = 0 | caption "Stack the two dot products into one equation." |
| 117–122 | It rearranges to XᵀX β̂ = Xᵀy inside an orange box | caption "These are the normal equations." |
| 122–129 | [3 3; 3 5] β̂ = [6; 8], then β̂ = (1, 1) | caption "Here they give β̂ = (1, 1), so the best line is y = 1 + x." |
| 129–133 | AᵀA x̂ = Aᵀb in general | caption "Any system Ax = b with no solution works the same way." |
| 133–137 | AᵀA pulses orange inside the box | caption "Day 40 builds the SVD from the symmetric matrix AᵀA." |
| 134–142 | Takeaway card with origin pulse | end |
