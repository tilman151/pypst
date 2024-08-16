# Create a Typst Table from a Pandas Data Frame

Pypst can create Typst tables from Pandas data frames.
This allows you to use the full power of Pandas for data wrangling and then render the results in a Typst document.
Multiple levels for columns and indexes are supported.

## Basics

Create a data frame and do any data wrangling you need.

```python
df = pd.DataFrame({
    "Name": ["Alice", "Bob", "Charlie"],
    "Age": [25, 30, 35],
    "City": ["New York", "Los Angeles", "New York"]
})
df = df.groupby("City").agg({"Name": "count", "Age": "mean"})
```

Create a Typst table from the data frame and apply styling.
Then wrap it in a figure and save it to a file.

```python
table = pypst.Table.from_dataframe(df)
table.stroke = "none"
table.align = "(x, _) => if calc.odd(x) {left} else {right}"
table.add_hline(1, stroke="1.5pt")
table.add_hline(len(df) + df.columns.nlevels, stroke="1.5pt")

figure = pypst.Figure(table, caption='"This is my table."')

with open("my-table.typ", mode="wt") as f:
    f.write(figure.render())
```

The resulting file looks like this:

```typst
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
```

Include the file in your `main.typ` Typst document.

```typst
= My Section Heading

#lorem(100)

#include("my-table.typ")

#lorem(100)
```

Compile with `typst compile main.typ` to receive a PDF file like [this](examples/table/main.pdf).
By using `typst watch main.typ`, you can automatically recompile the when your Python script runs.

## Styling individual cells

You can style individual cells by accessing the `table.row_data` attribute.
This attribute is a list of lists, where each sublist corresponds to a row in the table.
Each sublist contains the data for the cells in that row.

```python
table = pypst.Table.from_dataframe(df)
table.row_data[0][0].fill = "red"
table.row_data[1][1].fill = "blue"
```

The resulting Typst code looks like this:

```typst
#table(
  columns: 3,
  table.header[][Name][Age],
  [#table.cell(fill: red)[Los Angeles]], [1], [30.0],
  [New York], [#table.cell(fill: blue)[2]], [30.0]
)
```

## Using Third-Party Packages

If your table uses third-party packages, you can wrap the figure in a document and include the proper imports.

```python
document = pypst.Document(figure)
document.add_import("@preview/unify:0.4.3", ["num"])
```

The resulting file looks like this:

```typst
#import "@preview/unify:0.4.3": num

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
```

## Multiple Levels for Columns and Indexes

If your data frame has multiple levels for columns, Pypst will render them correctly.

```python
df = pd.DataFrame(
    [[1, 3], [2, 4]],
    columns=pd.MultiIndex.from_tuples([("A", "mean"), ("A", "std")]),
    index=["X", "Y"]
)
table = pypst.Table.from_dataframe(df)
```

```
#table(
  columns: 3,
  table.header[#table.cell(rowspan: 2)[]][#table.cell(colspan: 2)[A]][mean][std],
  [X], [1], [3],
  [Y], [2], [4]
)
```

Multiple levels for indexes are also supported.

```python
df = pd.DataFrame(
    [[1, 3], [2, 4]],
    columns=["A", "B"],
    index=pd.MultiIndex.from_tuples([("X", "mean"), ("X", "std")])
)
table = Table.from_dataframe(df)
print(table.render())
```

```
#table(
  columns: 4,
  table.header[#table.cell(colspan: 2)[]][A][B],
  [#table.cell(rowspan: 2)[X]], [mean], [1], [3],
  [std], [2], [4]
)
```

The cells for the headers and row indexes are stored by level in the `table.header_data` and `table.index_data` attributes, respectively.
You can access them to style the cells individually.
