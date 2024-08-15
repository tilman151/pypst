#figure(
  table(
    columns: 3,
    stroke: none,
    align: (x, _) => if calc.odd(x) {left} else {right},
    table.hline(y: 1, stroke: 1.5pt),
    table.hline(y: 3, stroke: 1.5pt),
    table.header[][Name][Age],
    [Los Angeles], [1], [30.0],
    [New York], [2], [30.0]
  ),
  caption: "This is my table."
)