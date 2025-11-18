"""
Delivers rust based algorithm for finding solutions to exact cover 
problems using the ``Solver`` class method ``solve``

With input as class ``Problem`` with lists of primary and secondary items 
to cover and a list of options as class ``Option`` with label, a list 
of primary items and a list of secondary items with colors for covering.

Method ``solve`` can deliver all solutions or first found solution
(to speed up the process if only one is needed).

## Examples:

With a ``Problem`` without secondary items the alorithm looks for all 
sets (combinations) of options (as ``Option`` without secondary items) 
which covers all primary items exactly once (no overlapping items
in options).

Problem with four items, four options and one solution::

    import pyxcc as xcc
    solver = xcc.Solver()
    problem = xcc.Problem(
        ['i1', 'i2', 'i3', 'i4'],
        [
            xcc.Option('o1', ['i1']),
            xcc.Option('o2', ['i1', 'i2', 'i4']),
            xcc.Option('o3', ['i3']),
            xcc.Option('o4', ['i4']),
        ]
    )
    # get all possible solutions
    solutions = solver.solve(problem, True)
    # one solution found
    assert solutions.count() == 1
    solution = solutions.first()
    # solution with two options
    assert len(solution) == 2
    options = set(solution)
    # options: o2 and o3
    assert options == {'o2', 'o3'}

With a ``Problem`` with secondary items and colors the algorithm
look for all sets (combinations) of options which covers all 
primary options exactly once, and if a secondary option is covered
it can be covered more than once, if it has the same color in all 
options covering it.

Problem with three primary items, two secondary items and five options::
    
    import pyxcc as xcc
    solver = xcc.solver()
    problem = xcc.Problem(
        ['p','q','r'],
        ['x','y'],
        [
            xcc.Option('o1', [('p',''), ('q',''), ('x',''), ('y','a')]),
            xcc.Option('o2', [('p',''), ('r',''), ('x','a'), ('y','')]),
            xcc.Option('o3', [('p',''), ('x','b')]),
            xcc.Option('o4', [('q',''), ('x','a')]),
            xcc.Option('o5', [('r',''), ('y','b')]),
        ]
    )
    # solve
    solutions = solver.solve(problem, True)
    # verify
    assert solutions.count() == 1, "1 solution"
    assert len(solutions.first()) == 2, "Solution with 5 rows"
    assert solutions.first() == ['o2','o4'], "Solution with rows 2 and 4"

"""
class Solutions:
    """
    Soution to an eXact Cover with Colors Problem
    
    ## Examples

    Found solutions to a problem::

        import pyxcc as xcc
        solutions = xcc.solve(problem, true)
        # number of solutions found
        number_found = solutions.count()
        # first solution found
        first_found = solutions.first()
        # loop over all solutions found
        for solution in solutions.all():
            ...
        
    """
    def count() -> int:
        """
        Return number of solutions found.
        """
    def first() -> list[str]:
        """
        Return first solution found.
        """
    def all() -> list[list[str]]:
        """
        Return all solutions found.
        """
class Option:
    """
    Option in a Problem for eXact Cover with Colors.

    :param label: identifies option in final solution (must be unique)
    :param primary_items: names of primary items covered by option (no dublicates and no overlap with secondary item names allowed)
    :param secondary_items: names of secondary items (no dublicates and no overlap with primary item names allowed) with colors covered by option

    :raises ValueError: if the input parameters are incorrect. The returned error includes an explanatory message.
    
    ## Examples

    Option with three items (two primary and one secondary with color)::

        option = Option(
            'option1',
            ['item1', 'item2'], 
            [('item3', 'color1')]
        )

    Complex Option with mutiple items::

        option = Option('option1', [], [])
        # initialize primary items
        for ...
            option.add_primary_item("...")    
        # initialize secondary items
        for ...
            option.add_secondary_item(("..."), ("..."))    

    """
    label: str
    primary_items: list[str]
    secondary_items: list[tuple[str, str]]

    def __init__(
        self, label: str, primary_items: list[str], secondary_items: list[tuple[str, str]]
    ) -> None: ...

    def add_primary_item(self, item:str) -> None: 
        """
        Add primary item to option primary items
    
        :param item: item name 

        :raises ValueError: if the added item overlaps with an existing primary item in option

        ## Examples

        Add primary item p3 to existing option::

            option = Option(
                'option1',
                ['p1', 'p2'], 
                [('s1', 'color1'), ('s2', '')]
            )
            option.add_primary_item('p3')
        """

    def add_secondary_item(self, item:tuple[str, str]) -> None:
        """
        Add secondary item to option secondary items

        :param item: tuple with item name and color 

        :raises ValueError: if the added item overlaps with an existing secondary item in option

        ## Example

        Add secondary item s3 with color c1 to existing option::

            option = Option(
                'option1',
                ['p1', 'p2'], 
                [('s1', 'c1'), ('s2', '')]
            )
            option.add_secondary_item(('s3', 'c1'))

        """

class Problem:
    """
    Problem for the Solver class for eXact Cover with Colors.

    :param primary_items: primary items in problem (must be covered exactly once)
    :param secondary_items: secondary items in problem (can be covered and more than once with same color)
    :param options: list of options

    :raises ValueError: if the input parameters are incorrect. The returned error includes an explanatory message.
    
    ## Examples

    Simple problem with three primary items, to secondary and five options::

        problem = Problem(
            ['p', 'q', 'r'],
            ['x', 'y'],
            [
                Option('o1', ['p', 'q'], [('x', ''),('y', 'A')]),
                Option('o2', ['p', 'r'], [('x', 'A'),('y', '')]),
                Option('o3', ['p'], [('x', 'B')]),
                Option('o4', ['q'], [('x', 'A')]),
                Option('o5', ['r'], [('y', 'B')]),
            ]
        )

    Larger problem::

        problem = Problem([], [], [])
        # initialize primary items
        for ...
            problem.add_primary_item(...)    
        # initialize secondary items
        for ...
            problem.add_secondary_item(...)    
        # initialize options
        for ...
            problem.add_option(Option(...))
    """
    primary_items: list[str]
    secondary_items: list[str]
    options: list[Option]
    def __init__(self, primary_items: list[str], secondary_items: list[str], options: list[Option]) -> None: ...    

    def add_primary_item(self, primary_item: str) -> None:
        """
        Add primary item to problem primary items
    
        :param item: item name 

        :raises ValueError: if the added item overlaps with an existing primary item in problem

        ## Examples

        Add primary item p3 to existing problem::

            problem = Problem(
                ['p1', 'p2'], 
                [...], 
                [
                    Option(...),
                    ...
                ]
            )
            problem.add_primary_item('p3')
        """

    def add_secondary_item(self, secondary_item: str) -> None:
        """
        Add secondary item to problem secondary items
    
        :param item: item name 

        :raises ValueError: if the added item overlaps with an existing secondary item in problem

        ## Examples

        Add secondary item s3 to existing problem::

            problem = Problem(
                [...], 
                ['s1', 's2'], 
                [
                    Option(...),
                    ...
                ]
            )
            problem.add_secondary_item('s3')
        """

    def add_option(self, option: Option) -> None: 
        """
        Add option item to problem options
    
        :param option: An Option 

        :raises ValueError: if the added option label overlaps with an existing option in problem

        ## Examples

        Add option to existing problem::

            problem = Problem(
                [...], 
                [...], 
                [
                    Option(...),
                    ...
                ]
            )
            problem.add_option(Option(...))
        """

def solve(self, problem: Problem, get_all: bool) -> Solutions:
    """
    solve eXact Cover with Colors.

    :param problem: problem to solve
    :param get_all: true, get all solutions, false, get first found

    :returns solutions: list of solutions, each a list of options

    :raises ValueError: if the input parameters are incorrect. The returned error includes an explanatory message.
    
    ## Examples
    
    get all solutions for problem (Problem)::

        solver = Solver()
        solutions = solver.solve(problem, True)

    """
