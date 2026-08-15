import pypst

doc = pypst.Document()
doc.add_import("@preview/unify:0.6.0", ["qty"])

doc.add(pypst.Heading("My Document", level=1))
doc.add(
    "You can add a paragraph by simply passing a string. "
    "Each element is separated in the rendered Typst code by a blank line."
)
doc.add("You can all any builtin function. #lorem(50)")

doc.add(pypst.Heading("Using Imported Functions", level=2))
doc.add('You can use the function imported earlier. It works #qty("100", "%").')

doc.add(pypst.Heading("Including Lists", level=2))
doc.add("You can include bullet point lists:")
doc.add(
    pypst.Itemize(
        [
            "You can also include lists.",
            "This is the second item.",
            "This is the third item.",
        ]
    )
)
doc.add("You can also include numbered lists:")
doc.add(
    pypst.Enumerate(
        [
            "You can also include lists.",
            "This is the second item.",
            "This is the third item.",
        ]
    )
)

doc.add("Lists can also be nested:")
doc.add(
    pypst.Itemize(
        [
            "This is the first item.",
            pypst.Itemize(
                [
                    "This is the first nested item.",
                    "This is the second nested item.",
                ]
            ),
            "This is the second item.",
        ]
    )
)

doc.add(pypst.Heading("Dynamically Generate Elements", level=2))
doc.add("You can dynamically generate elements by using a loop")
items = pypst.Itemize([])
for i in range(1, 4):
    items.add(f"This is item {i}.")
doc.add(items)

doc.add(pypst.Heading("Including Figures", level=2))
doc.add("You can include figures:")
doc.add(
    pypst.Figure(
        pypst.Image("img.png"),
        caption='"This is a placeholder image."',
    )
)

with open("my-document.typ", mode="wt") as f:
    f.write(doc.render())
