# Usage

Pypst can be used to create Typst documents programmatically.
This can be useful for generating reports, slides, or other documents directly in Python to avoid copy-pasting data.
A full example can be found in the [examples](https://github.com/tilman151/pypst/docs/examples/document) directory of the repository.

## Basics

Pypst contains classes that represent Typst elements.
You can create a Typst document by instantiating these classes and nesting them as needed.

```pycon
>>> import pypst
>>> heading = pypst.Heading("My Heading", level=1)
>>> itemize = pypst.Itemize(["First item", "Second item", "Third item"])

```

Each of these classes has a `render` method that returns the Typst code as a string.

```pycon
>>> print(heading.render())
= My Heading
>>> print(itemize.render())
- First item
- Second item
- Third item

```

If you want to combine multiple elements into a single document, you can use the `Document` class.
You can even add imports for other Typst files or packages.

```pycon
>>> document = pypst.Document([heading, itemize])
>>> document.add_import("utils.typ")
>>> print(document.render())
#import "utils.typ"
<BLANKLINE>
= My Heading
<BLANKLINE>
- First item
- Second item
- Third item

```

The output of the `render` method can be written to a `.typ` file for compilation.

## Dynamic Generation

You can use Python loops and conditionals to generate Typst elements.
This can be useful for creating lists or other repetitive structures.

```pycon
>>> enum = pypst.Enumerate([])
>>> for i in range(1, 4):  # (1)!
...     enum.add(f"Item {i}")
>>> print(enum.render())
+ Item 1
+ Item 2
+ Item 3
+ Item 4
>>> if len(enum.items) > 3:  # (2)!
...     doc.add(enum)

```

1. By using loops, you fill a list with your data. It may come from experiment results, database queries, or even API calls.
2. Add elements conditionally, based on your data. This way you can include information about optional data only when it is available.

## Including Figures

You can include figures in your document by using the `Figure` class.
The body of the figure can be any Typst element, but the most common, images and tables, are supported directly by Pypst.
    
```pycon
>>> figure = pypst.Figure("examples/example.png", caption="Example script and output")
>>> print(figure.render())
#figure(
  image("examples/example.png"),
  caption: "Example script and output"
)

```

You can create images or plots with your favorite Python library and include them in your Typst document.
Tables can be generated from Pandas data frames, as shown [here](pandas.md).

## Using Templates

To use your own template or external ones, you can use a wrapper Typst file.
Here is an example for using the IEEE template:

```
#import "@preview/charged-ieee:0.1.0": ieee

#show: ieee.with(
  title: [Using Templates with Pypst],
  abstract: [#lorem(100)],
  authors: (
    (
      name: "Alice",
      department: [Co-Author],
      organization: [Best University],
      email: "alice@university.org"
    ),
    (
      name: "Bob",
      department: [Co-Author],
      organization: [Best University],
      email: "bob@university.com"
    ),
  ),
  index-terms: ("Scientific writing", "Typesetting", "Document creation", "Syntax")
)

// include generated file
#include("my-document.typ")
```

The wrapper file imports and sets up the template.
It then includes the generated file created with Pypst.

## What about show and set rules?

Pypst doesn't support the `show` and `set` rules by design.
We think it is easier to set up your global rules in a template file and then include your generated document, like shown [above](usage.md#using-templates).
Generating dynamic rules doesn't seem like a common use case.
If you still want to include rules, you can always add them as a string to your document.

```pycon
>>> document.add("#set: text(size: 12pt)")
```