#import "@preview/unify:0.6.0": qty

= My Document

You can add a paragraph by simply passing a string. Each element is separated in the rendered Typst code by a blank line.

You can all any builtin function. #lorem(50)

== Using Imported Functions

You can use the function imported earlier. It works #qty("100", "%").

== Including Lists

You can include bullet point lists:

- You can also include lists.
- This is the second item.
- This is the third item.

You can also include numbered lists:

+ You can also include lists.
+ This is the second item.
+ This is the third item.

Lists can also be nested:

- This is the first item.
  - This is the first nested item.
  - This is the second nested item.
- This is the second item.

== Dynamically Generate Elements

You can dynamically generate elements by using a loop

- This is item 1.
- This is item 2.
- This is item 3.

== Including Figures

You can include figures:

#figure(
  image("img.png"),
  caption: "This is a placeholder image."
)