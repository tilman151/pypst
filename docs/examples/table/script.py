import pandas as pd

import pypst

df = pd.DataFrame(
    {
        "Name": ["Alice", "Bob", "Charlie"],
        "Age": [25, 30, 35],
        "City": ["New York", "Los Angeles", "New York"],
    }
)
df = df.groupby("City").agg({"Name": "count", "Age": "mean"})

table = pypst.Table.from_dataframe(df)
table.stroke = "none"
table.align = "(x, _) => if calc.odd(x) {left} else {right}"
table.add_hline(1, stroke="1.5pt")
table.add_hline(len(df) + df.columns.nlevels, stroke="1.5pt")

figure = pypst.Figure(table, caption='"This is my table."')

with open("my-table.typ", mode="wt") as f:
    f.write(figure.render())
