import pytest

from taw.exceptions import ParsePairingException, ParseStandingException
from taw.utils import (
    get_pairings_by_name,
    sort_pairings_for_paper_cutter,
    parse_pairings,
    parse_standings,
    Player,
    Standing,
    Table,
)


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
                        name="* * * BYE * * *",
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
                        name="* * * BYE * * *",
                        points=0,
                    ),
                ),
            ],
            id="complex name with a BYE",
        ),
        # There *are* limits to what we can parse though :o
        pytest.param(
            "1   Louis IX (Saint-Louis) (15 Points)    🤡 (13 Points)     No results",
            None,
            id="cannot parse name with parenthesis",
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
    "pairings, first_table_number, pairings_by_name",
    [
        pytest.param(
            [
                Table(
                    number=1,
                    player_1=Player(
                        name="Élisabeth Borne",
                        points=0,
                    ),
                    player_2=Player(
                        name="Maurice Couve de Murville",
                        points=0,
                    ),
                ),
                Table(
                    number=2,
                    player_1=Player(
                        name="François Fillon",
                        points=0,
                    ),
                    player_2=Player(
                        name="Pierre Messmer",
                        points=0,
                    ),
                ),
                Table(
                    number=3,
                    player_1=Player(
                        name="Édith Cresson",
                        points=0,
                    ),
                    player_2=Player(
                        name="Bernard Cazeneuve",
                        points=0,
                    ),
                ),
            ],
            None,
            [
                Table(
                    number=3,
                    player_1=Player(
                        name="Bernard Cazeneuve",
                        points=0,
                    ),
                    player_2=Player(
                        name="Édith Cresson",
                        points=0,
                    ),
                ),
                Table(
                    number=3,
                    player_1=Player(
                        name="Édith Cresson",
                        points=0,
                    ),
                    player_2=Player(
                        name="Bernard Cazeneuve",
                        points=0,
                    ),
                ),
                Table(
                    number=1,
                    player_1=Player(
                        name="Élisabeth Borne",
                        points=0,
                    ),
                    player_2=Player(
                        name="Maurice Couve de Murville",
                        points=0,
                    ),
                ),
                Table(
                    number=2,
                    player_1=Player(
                        name="François Fillon",
                        points=0,
                    ),
                    player_2=Player(
                        name="Pierre Messmer",
                        points=0,
                    ),
                ),
                Table(
                    number=1,
                    player_1=Player(
                        name="Maurice Couve de Murville",
                        points=0,
                    ),
                    player_2=Player(
                        name="Élisabeth Borne",
                        points=0,
                    ),
                ),
                Table(
                    number=2,
                    player_1=Player(
                        name="Pierre Messmer",
                        points=0,
                    ),
                    player_2=Player(
                        name="François Fillon",
                        points=0,
                    ),
                ),
            ],
            id="ordering unicode characters, see https://github.com/pmourlanne/taw/issues/17",
        ),
        pytest.param(
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
            ],
            100,
            [
                Table(
                    number=100,
                    player_1=Player(
                        name="François Mitterrand",
                        points=13,
                    ),
                    player_2=Player(
                        name="Jacques Chirac",
                        points=15,
                    ),
                ),
                Table(
                    number=100,
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
                    number=101,
                    player_1=Player(
                        name="René Coty",
                        points=9,
                    ),
                    player_2=Player(
                        name="Vincent Auriol",
                        points=13,
                    ),
                ),
                Table(
                    number=101,
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
            id="table number offset",
        ),
    ],
)
def test_get_pairings_by_name(pairings, first_table_number, pairings_by_name):
    assert (
        get_pairings_by_name(pairings, first_table_number=first_table_number)
        == pairings_by_name
    )


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


@pytest.mark.parametrize(
    "min_table_nb, max_table_nb, first_table_number, expected_table_numbers",
    [
        pytest.param(1, 1, None, [1, None, None, None, None], id="one slip"),
        pytest.param(1, 5, None, [1, 2, 3, 4, 5], id="one full page"),
        pytest.param(1, 10, None, [1, 3, 5, 7, 9, 2, 4, 6, 8, 10], id="two full pages"),
        pytest.param(
            1,
            6,
            None,
            [1, 3, 5, None, None, 2, 4, 6, None, None],
            id="just over one page",
        ),
        pytest.param(
            1,
            24,
            None,
            [
                1,
                6,
                11,
                16,
                21,
                2,
                7,
                12,
                17,
                22,
                3,
                8,
                13,
                18,
                23,
                4,
                9,
                14,
                19,
                24,
                5,
                10,
                15,
                20,
                None,
            ],
            id="almost five pages",
        ),
        pytest.param(
            1,
            17,
            None,
            [
                1,
                5,
                9,
                13,
                17,
                2,
                6,
                10,
                14,
                None,
                3,
                7,
                11,
                15,
                None,
                4,
                8,
                12,
                16,
                None,
            ],
            id="last row only has one slip",
        ),
        pytest.param(
            1,
            12,
            None,
            [1, 4, 7, 10, None, 2, 5, 8, 11, None, 3, 6, 9, 12, None],
            id="there are only four match slips per page",
        ),
        pytest.param(
            1, 5, 1, [1, 2, 3, 4, 5], id="one full page with 1 table number offset"
        ),
        pytest.param(
            1,
            5,
            100,
            [100, 101, 102, 103, 104],
            id="one full page with 100 table number offset",
        ),
        pytest.param(
            1,
            8,
            50,
            [50, 52, 54, 56, None, 51, 53, 55, 57, None],
            id="a bit over a page with 50 table number offset",
        ),
    ],
)
def test_sort_pairings_for_paper_cutter(
    min_table_nb, max_table_nb, first_table_number, expected_table_numbers
):
    pairings = [
        Table(
            number=idx,
            player_1=Player(name=f"name_1_{idx}", points=0),
            player_2=Player(name=f"name_2_{idx}", points=0),
        )
        for idx in range(min_table_nb, max_table_nb + 1)
    ]

    table_numbers = [
        table.number if table is not None else None
        for table in sort_pairings_for_paper_cutter(
            pairings,
            nb_slips_per_page=5,
            first_table_number=first_table_number,
        )
    ]
    assert table_numbers == expected_table_numbers
