## 0.7.0 (2025-09-25)

### Feat

- add further dataclass field configuration (#26)

## 0.6.1 (2025-01-09)

### Fix

- handling of empty mappings (#23)

## 0.6.0 (2025-01-08)

### BREAKING CHANGE

- to use table functionality, package now needs to be installed as 'pypst[pandas]'

### Feat

- add Content, Functional, ShowRule, SetRule, and String (#18)
- make pandas an extra (#22)

## 0.5.0 (2025-01-06)

### Feat

- additional rendering utils (#17)

## 0.4.0 (2024-12-17)

### Feat

- make rendering utils recursive (#16)

## 0.3.0 (2024-12-17)

### Feat

- add Plain import (#15)

## 0.2.0 (2024-08-16)

### Feat

- add image element (#5)
- add basic text setting elements (#4)
- extend document class to hold multiple body items (#3)
- add missing table attributes (#1)

### Fix

- missing default argument for document body (#10)
- separate each body element of a document by a blank line (#8)

### Refactor

- make creating empty documents possible (#7)
- add element imports in root init file (#6)
- declare Renderable interface (#2)

## 0.1.0 (2024-08-12)

### Feat

- add py.typed file
- add indents to rendered output
- add document class
- add figure class
- add more attributes to cell
- add align attribute
- add hline and vline
- make attributes frozen lists
- make columns and rows properties
- add custom row and col options
- parse values
- parse index
- parse table header

### Fix

- unify stroke declaration
- bump Python version to 3.10
- check for rows attribute

### Refactor

- linting issues
- move classes and functions
- extract table args rendering
- linting issues
- clean up rendering
- generalize header parsing
