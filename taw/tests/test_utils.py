import pytest

from taw.exceptions import ParsePairingException, ParseStandingException
from taw.utils import parse_pairings, parse_standings, Player, Standing, Table


@pytest.mark.parametrize(
    "pairings_input, expected_output",
    [
        # Standard example
        pytest.param(
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
            id="standard one liner",
        ),
        # Standard example, result already entered but ignored
        pytest.param(
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
            id="standard one liner with results",
        ),
        # BYE example
        pytest.param(
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
            id="bye one liner",
        ),
        # Multiple tables, with non zero points, and a result already entered
        pytest.param(
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
            id="multiple tables",
        ),
        # One table with empty lines and blank spaces
        pytest.param(
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
            id="empty lines and blank spaces",
        ),
        # Empty input
        pytest.param("", [], id="empty input"),
        # Tables in the incorrect order are re-ordered
        pytest.param(
            """2   Jacques Chirac (15 Points)    François Mitterrand (13 Points)     No results
3   Vincent Auriol (13 Points)     René Coty (9 Points)  2 - 1
1   Valéry Giscard d'Estaing (12 Points)   Charles de Gaulle (12 Points)     No results  """,
            [
                Table(
                    number=1,
                    player_1=Player(
                        name="Valéry Giscard d'Estaing",
                        points=12,
                    ),
                    player_2=Player(
                        name="Charles de Gaulle",
                        points=12,
                    ),
                ),
                Table(
                    number=2,
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
                    number=3,
                    player_1=Player(
                        name="Vincent Auriol",
                        points=13,
                    ),
                    player_2=Player(
                        name="René Coty",
                        points=9,
                    ),
                ),
            ],
            id="multiple tables in the incorrect order",
        ),
        # Pairing cannot be parsed
        pytest.param(
            "1 There's something wrong with this pairing :o",
            None,
            id="pairing cannot be parsed",
        ),
        # We aren't very regarding when it comes to names
        pytest.param(
            "1   M.C. Hammer - U Can't Touch This!! (15 Points)    🤡 (13 Points)     No results",
            [
                Table(
                    number=1,
                    player_1=Player(
                        name="M.C. Hammer - U Can't Touch This!!",
                        points=15,
                    ),
                    player_2=Player(
                        name="🤡",
                        points=13,
                    ),
                ),
            ],
            id="complex name",
        ),
        pytest.param(
            "1   M.C. Hammer - U Can't Touch This!! (15 Points)    BYE   2 - 0",
            [
                Table(
                    number=1,
                    player_1=Player(
                        name="M.C. Hammer - U Can't Touch This!!",
                        points=15,
                    ),
                    player_2=Player(
                        name="BYE",
                        points=0,
                    ),
                ),
            ],
            id="complex name with a BYE",
        ),
        pytest.param(
            """1   Jacques Chirac (15 Points)    François Mitterrand (13 Points)     No results
3   Valéry Giscard d'Estaing (12 Points)   Charles de Gaulle (12 Points)     No results  """,
            None,
            id="a table is missing",
        ),
        pytest.param(
            """1   Jacques Chirac (15 Points)    François Mitterrand (13 Points)     No results
2   Vincent Auriol (13 Points)     René Coty (9 Points)  2 - 1
2   Valéry Giscard d'Estaing (12 Points)   Charles de Gaulle (12 Points)     No results  """,
            None,
            id="two tables have the same number",
        ),
        # TODO: A single name appearing in multiple tables should raise (?)
    ],
)
def test_parse_pairings(pairings_input, expected_output):
    if expected_output is None:
        with pytest.raises(ParsePairingException):
            parse_pairings(pairings_input)

    else:
        assert parse_pairings(pairings_input) == expected_output


@pytest.mark.parametrize(
    "standings_input, expected_output",
    [
        pytest.param(
            "1  Jacques Chirac    15  5 - 0   68.0000%    71.4285%    58.0696%",
            [
                Standing(
                    position=1,
                    player_name="Jacques Chirac",
                    nb_points=15,
                    record="5 - 0",
                    omw="68.0000%",
                    gw="71.4285%",
                    ogw="58.0696%",
                ),
            ],
            id="normal standing",
        ),
        pytest.param(
            "1  Jacques Chirac    45  15 - 12   68.0000%    71.4285%    58.0696%",
            [
                Standing(
                    position=1,
                    player_name="Jacques Chirac",
                    nb_points=45,
                    record="15 - 12",
                    omw="68.0000%",
                    gw="71.4285%",
                    ogw="58.0696%",
                ),
            ],
            id="normal standing with a lot of matches",
        ),
        pytest.param(
            "1  Vincent Auriol     13  4 - 0 - 1   64.0000%    61.5384%    53.2121% ",
            [
                Standing(
                    position=1,
                    player_name="Vincent Auriol",
                    nb_points=13,
                    record="4 - 0 - 1",
                    omw="64.0000%",
                    gw="61.5384%",
                    ogw="53.2121%",
                ),
            ],
            id="normal standing with draws",
        ),
        pytest.param(
            """1   Jacques Chirac    15  5 - 0   68.0000%    71.4285%    58.0696%
2   Vincent Auriol     13  4 - 0 - 1   64.0000%    61.5384%    53.2121%
3   M.C. Hammer - U Can't Touch This!!     13  4 - 0 - 1   62.0000%    61.5384%    53.2051%
4   🤡     12  4 - 1   61.3333%    75.0000%    53.9743% """,
            [
                Standing(
                    position=1,
                    player_name="Jacques Chirac",
                    nb_points=15,
                    record="5 - 0",
                    omw="68.0000%",
                    gw="71.4285%",
                    ogw="58.0696%",
                ),
                Standing(
                    position=2,
                    player_name="Vincent Auriol",
                    nb_points=13,
                    record="4 - 0 - 1",
                    omw="64.0000%",
                    gw="61.5384%",
                    ogw="53.2121%",
                ),
                Standing(
                    position=3,
                    player_name="M.C. Hammer - U Can't Touch This!!",
                    nb_points=13,
                    record="4 - 0 - 1",
                    omw="62.0000%",
                    gw="61.5384%",
                    ogw="53.2051%",
                ),
                Standing(
                    position=4,
                    player_name="🤡",
                    nb_points=12,
                    record="4 - 1",
                    omw="61.3333%",
                    gw="75.0000%",
                    ogw="53.9743%",
                ),
            ],
            id="multiple rows of standings, with unexpected names",
        ),
        pytest.param(
            """4   🤡     12  4 - 1   61.3333%    75.0000%    53.9743%
3   M.C. Hammer - U Can't Touch This!!     13  4 - 0 - 1   62.0000%    61.5384%    53.2051%
2   Vincent Auriol     13  4 - 0 - 1   64.0000%    61.5384%    53.2121%
1   Jacques Chirac    15  5 - 0   68.0000%    71.4285%    58.0696% """,
            [
                Standing(
                    position=1,
                    player_name="Jacques Chirac",
                    nb_points=15,
                    record="5 - 0",
                    omw="68.0000%",
                    gw="71.4285%",
                    ogw="58.0696%",
                ),
                Standing(
                    position=2,
                    player_name="Vincent Auriol",
                    nb_points=13,
                    record="4 - 0 - 1",
                    omw="64.0000%",
                    gw="61.5384%",
                    ogw="53.2121%",
                ),
                Standing(
                    position=3,
                    player_name="M.C. Hammer - U Can't Touch This!!",
                    nb_points=13,
                    record="4 - 0 - 1",
                    omw="62.0000%",
                    gw="61.5384%",
                    ogw="53.2051%",
                ),
                Standing(
                    position=4,
                    player_name="🤡",
                    nb_points=12,
                    record="4 - 1",
                    omw="61.3333%",
                    gw="75.0000%",
                    ogw="53.9743%",
                ),
            ],
            id="multiple rows of standings, not in order",
        ),
        pytest.param(
            """1   Jacques Chirac    15  5 - 0   68.0000%    71.4285%    58.0696%
3   Vincent Auriol     13  4 - 0 - 1   64.0000%    61.5384%    53.2121% """,
            None,
            id="missing position in standing",
        ),
        pytest.param(
            """1   Jacques Chirac    15  5 - 0   68.0000%    71.4285%    58.0696%
1   Vincent Auriol     13  4 - 0 - 1   64.0000%    61.5384%    53.2121% """,
            None,
            id="duplicate position in standing",
        ),
        pytest.param(
            """2   Jacques Chirac    15  5 - 0   68.0000%    71.4285%    58.0696%""",
            None,
            id="position 1 is missing",
        ),
        pytest.param("", [], id="empty string"),
    ],
)
def test_parse_standings(standings_input, expected_output):
    if expected_output is None:
        with pytest.raises(ParseStandingException):
            parse_standings(standings_input)
    else:
        assert parse_standings(standings_input) == expected_output
