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