# AlgoXCC

A Rust implementation of Donald Knuth’s algorithm for solving an exact cover with colors problem using the Dancing Cells data structure.

## Exact cover problems

The exact cover problem involves a set of items and a set of options, where each option is a subset of items. A solution to the problem is any subset of options in which all items are represented exactly once.

The generalized exact cover extends this with two types of items:
- primary items, which, as before, must be covered exactly once, and
- secondary items, which must be covered at most once.

The exact cover with colors problem extends this by assigning colors to secondary items within options, allowing a secondary item to be covered by multiple options if they have the same color.

## Usage

### The logic

The inputs to the algorithm are defined in a Problem with:
- primary items: list of unique item names as strings
- secondary items: list of unique item names as strings
- options: list of Options

Where an Option have:
- label: unique label as string identifying an option
- primary items: list of primary items covered by option as strings
- secondary items: list of secondary items covered by option

Secondary items covered by an option are tuples with two elements as strings:
- first element: the secondary item covered by the option
- second element: color used to cover the secondary item

Where a blank color for a secondary item is regarded as a unique color.

With prerequisites:
- A Problem must have at least one primary item.
- All items must be unique (also across primary and secondary items).
- All primary items must be represented in at least one Option.
- All items in an Option must exist in Problem list of items

### The code

Install using Pip:

```txt
pip install pyxcc
```

Example simple binary matrix (exact cover without secondary items):

```python
# import the packace as xcc
import pyxcc as xcc

# prepare problem to solve based on
# binary matrix (Knuth's example)
# [0, 0, 1, 0, 1, 0, 0],
# [1, 0, 0, 1, 0, 0, 1],
# [0, 1, 1, 0, 0, 1, 0],
# [1, 0, 0, 1, 0, 1, 0],
# [0, 1, 0, 0, 0, 0, 1],
# [0, 0, 0, 1, 1, 0, 1],
problem = xcc.Problem( 
    ['a','b','c','d','e','f','g'], 
    [],
    [
        xcc.Option('r1', ['c', 'e'], []),
        xcc.Option('r2', ['a', 'd', 'g'], []),
        xcc.Option('r3', ['b', 'c', 'f'], []),
        xcc.Option('r4', ['a', 'd', 'f'], []),
        xcc.Option('r5', ['b', 'g'], []),
        xcc.Option('r6', ['d', 'e', 'g'], []),
    ]
)

# solve
solutions: xcc.Solutions = xcc.solve(problem, True)

# verify
assert solutions.count() == 1, "1 solution"
assert len(solutions.first()) == 3, "Solution with 3 rows"
rows = set(solutions.first())
assert rows == {'r1', 'r4', 'r5'}, "Solution with rows: 1, 4 and 5"
```

Example XCC example used by Donald Knuth

```python
# import the packace as xcc
import pyxcc as xcc

problem = xcc.Problem(
    ['p','q','r'],
    ['x','y'],
    [
        xcc.Option('o1', ['p', 'q'], [('x',''), ('y','a')]),
        xcc.Option('o2', ['p', 'r'], [('x','a'), ('y','')]),
        xcc.Option('o3', ['p'], [('x','b')]),
        xcc.Option('o4', ['q'], [('x','a')]),
        xcc.Option('o5', ['r'], [('y','b')]),
    ]
)
# solve
solutions: xcc.Solutions = xcc.solve(problem, True)

# verify
assert solutions.count() == 1, "1 solution"
assert len(solutions.first()) == 2, "Solution with 5 rows"
assert solutions.first() == ['o2','o4'], "Solution with rows 2 and 4"
```

Example [8 queens puzzle](https://en.wikipedia.org/wiki/Eight_queens_puzzle):

```python
# import the packace as xcc
import pyxcc as xcc

# construct problem
problem = xcc.Problem([], [], [])
# a single queen in each row and column
for x in range(1,9):
    problem.add_primary_item(f'r{x}')
    problem.add_primary_item(f'c{x}')
# at most one queen in each diagonal
for x in range(1,16):
    problem.add_secondary_item(f'u{x}')
    problem.add_secondary_item(f'd{x}')
# an option for each field on the board
for x in range(1,9):
    for y in range(1,9):
        problem.add_option(xcc.Option(
            f'{x},{y}',
            [f'r{x}',f'c{y}'], 
            [(f'u{8-x+y}',''),(f'd{x+y-1}','')]
        ))

# solve
solutions: xcc.Solutions = xcc.solve(problem, True)

# verify
assert solutions.count() == 92, "92 solutions"
```
