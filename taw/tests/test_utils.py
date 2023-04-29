import pytest

from taw.utils import parse_pairings, Table, Player


@pytest.mark.parametrize(
    "pairings_input, expected_output",
    [
        # Standard example
        (
            "1   Jacques Chirac (0 Points)     François Mitterrand (0 Points)   No results   ",
            [
                Table(
                    number=1,
                    player_1=Player(
                        name="Jacques Chirac",
                        points=0,
                    ),
                    player_2=Player(
                        name="François Mitterrand",
                        points=0,
                    ),
                ),
            ],
        ),
        # Standard example, result already entered but ignored
        (
            "1   Jacques Chirac (0 Points)     François Mitterrand (0 Points)   1 - 2   ",
            [
                Table(
                    number=1,
                    player_1=Player(
                        name="Jacques Chirac",
                        points=0,
                    ),
                    player_2=Player(
                        name="François Mitterrand",
                        points=0,
                    ),
                ),
            ],
        ),
        # BYE example
        (
            "1   Jacques Chirac (0 Points)    BYE     2 - 0   ",
            [
                Table(
                    number=1,
                    player_1=Player(
                        name="Jacques Chirac",
                        points=0,
                    ),
                    player_2=Player(
                        name="BYE",
                        points=0,
                    ),
                ),
            ],
        ),
        # Multiple tables, with non zero points, and a result already entered
        (
            """1   Jacques Chirac (15 Points)    François Mitterrand (13 Points)     No results
2   Vincent Auriol (13 Points)     René Coty (9 Points)  2 - 1
3   Valéry Giscard d'Estaing (12 Points)   Charles de Gaulle (12 Points)     No results  """,
            [
                Table(
                    number=1,
                    player_1=Player(
                        name="Jacques Chirac",
                        points=15,
                    ),
                    player_2=Player(
                        name="François Mitterrand",
                        points=13,
                    ),
                ),
                Table(
                    number=2,
                    player_1=Player(
                        name="Vincent Auriol",
                        points=13,
                    ),
                    player_2=Player(
                        name="René Coty",
                        points=9,
                    ),
                ),
                Table(
                    number=3,
                    player_1=Player(
                        name="Valéry Giscard d'Estaing",
                        points=12,
                    ),
                    player_2=Player(
                        name="Charles de Gaulle",
                        points=12,
                    ),
                ),
            ],
        ),
        # One table with empty lines and blank spaces
        (
            "1   Jacques Chirac (15 Points)    François Mitterrand (13 Points)     No results\n\t\t\n\t",
            [
                Table(
                    number=1,
                    player_1=Player(
                        name="Jacques Chirac",
                        points=15,
                    ),
                    player_2=Player(
                        name="François Mitterrand",
                        points=13,
                    ),
                ),
            ],
        ),
        # Empty input
        ("", []),
        # TODO: Tables not in the correct order are re-ordered
        # TODO: Missing table number?
        # TODO: Multiple tables with the same number should raise
        # TODO: A single name appearing in multiple tables should raise
    ],
)
def test_parse_pairings(pairings_input, expected_output):
    assert parse_pairings(pairings_input) == expected_output
