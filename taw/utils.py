import math
import re
import unicodedata
from collections import Counter, namedtuple
from itertools import zip_longest
from operator import itemgetter

from taw.exceptions import ParsePairingException, ParseStandingException


Table = namedtuple("Table", ["number", "player_1", "player_2"])


BYE_STRING = "* * * BYE * * *"


class Player(namedtuple("Player", ["name", "points"])):
    @property
    def is_bye(self):
        return self.name == BYE_STRING


def parse_pairings(pairings_input):
    """
    Parse the pairings input and return the pairings
    Pairings are represented by a list of `Table`s, ordered by table number
    Each `Table` is a namedtuple, containing the table number and two `Player`s
    Each `Player` is a namedtuple, with a name and a positive number of poitns
    """

    pairings = []
    for pairing_line in pairings_input.split("\n"):
        pairing = _parse_pairing(pairing_line)
        # _parse_pairing will return None in some cases (eg. blank line)
        if pairing:
            pairings.append(pairing)

    # Sort by table number
    pairings = sorted(pairings, key=itemgetter(0))

    if not pairings:
        return pairings

    # Make sure no table is missing
    table_numbers = Counter([pairing.number for pairing in pairings])
    min_table_number = min(table_numbers.keys())
    max_table_number = max(table_numbers.keys())
    missing_tables = set(range(min_table_number, max_table_number + 1)) - set(
        table_numbers.keys()
    )
    if missing_tables:
        missing_tables_str = ", ".join(
            [str(table_number) for table_number in missing_tables]
        )
        raise ParsePairingException(f"Some tables are missing: {missing_tables_str}")

    # Make sure we don't have duplicate tables
    duplicate_table_numbers = sorted(
        [
            table_number
            for table_number, nb_occurrences in table_numbers.items()
            if nb_occurrences > 1
        ]
    )
    if duplicate_table_numbers:
        duplicate_table_numbers_str = ", ".join(
            [str(table_number) for table_number in duplicate_table_numbers]
        )
        raise ParsePairingException(
            f"Some table numbers are present more than once: {duplicate_table_numbers_str}"
        )

    return pairings


re_pairing = (
    r"^(?P<table_number>[0-9]+)\s+"
    r"(?P<player_1_name>[^(]+)\s"
    r"\((?P<player_1_nb_points>[\d]+)\sPoints\)\s*"
    r"(?P<player_2_name>[^(]+)\s"
    r"\((?P<player_2_nb_points>[\d]+)\sPoints\).*"
)

re_pairing_bye = (
    r"^(?P<table_number>[0-9]+)\s+"
    r"(?P<player_1_name>[^(]+)\s"
    r"\((?P<player_1_nb_points>[\d]+)\sPoints\)\s*"
    r"BYE.*"
)


def _parse_pairing(pairing_line):
    # Strip extraneous spaces
    pairing_line = pairing_line.strip()

    # If at that point the line is empty, just return None :shrug:
    if not pairing_line:
        return None

    # Try to match to "normal" pairing re
    result = re.match(re_pairing, pairing_line)
    if result:
        group_dict = result.groupdict()
        return Table(
            number=int(group_dict["table_number"]),
            player_1=Player(
                name=group_dict["player_1_name"],
                points=int(group_dict["player_1_nb_points"]),
            ),
            player_2=Player(
                name=group_dict["player_2_name"],
                points=int(group_dict["player_2_nb_points"]),
            ),
        )

    # Try to match to "BYE" pairing re
    result = re.match(re_pairing_bye, pairing_line)
    if result:
        group_dict = result.groupdict()
        return Table(
            number=int(group_dict["table_number"]),
            player_1=Player(
                name=group_dict["player_1_name"],
                points=int(group_dict["player_1_nb_points"]),
            ),
            player_2=Player(
                name=BYE_STRING,
                points=0,
            ),
        )

    # Welp, we tried peeps
    raise ParsePairingException(
        f"Could not parse the following pairing: {pairing_line}"
    )


def _remove_accents(input_str):
    """
    See https://github.com/pmourlanne/taw/issues/17
    """
    nfkd_form = unicodedata.normalize("NFKD", input_str)
    only_ascii = nfkd_form.encode("ASCII", "ignore")
    return only_ascii


def get_pairings_by_name(pairings, *, first_table_number=None):
    # 0 is not a valid first table number so a falsy check is enough,
    # we don't need to explicitly check against `None`
    first_table_number = first_table_number or 1
    table_number_offset = first_table_number - 1

    # Each table must appear twice (once for each player)
    ret = []
    for table in pairings:
        ret.append(
            Table(
                number=table.number + table_number_offset,
                player_1=table.player_1,
                player_2=table.player_2,
            ),
        )
        ret.append(
            Table(
                number=table.number + table_number_offset,
                player_1=table.player_2,
                player_2=table.player_1,
            ),
        )

    # Pairings should then be ordered by player name
    return sorted(ret, key=lambda table: _remove_accents(table.player_1.name.lower()))


def sort_pairings_for_paper_cutter(
    pairings, *, nb_slips_per_page, first_table_number=None
):
    """
    We need to sort pairings so that when we stack each page, and cut
    them up with a paper cutter, the slips are ordered within each stack.
    We also want the first pages to be as full as possible, only the last
    page may not be full.

    Let's think about the stacked sheets of paper, with eg. 5 slips on each
    of them. With 13 match slips, things should look like this:

    1   2   3
    4   5   6
    7   8   9
    10  11  12
    13

    That way, when we stack the sheets and cut, we have the slips in order:
    1 2 3, 4 5 6, 7 8 9, 10 11 12, 13.
    We want to use as few paper sheets as possible, and we want to have as
    few "incomplete" lines as possible.

    Pairings should be returned in the order we want them printed. To indicate
    incomplete columns, `None` should be present. With the example above,
    the returned pairings should be, by table number:
    [1, 4, 7, 10, 13, 2, 5, 8, 11, None, 3, 6, 9, 12, None]

    See https://github.com/pmourlanne/taw/issues/6 for more details
    """
    if not pairings:
        return pairings

    # 0 is not a valid first table number so a falsy check is enough,
    # we don't need to explicitly check against `None`
    first_table_number = first_table_number or 1
    table_number_offset = first_table_number - 1

    if table_number_offset:
        # Offset the tables before manipulating anything
        original_pairings = pairings
        pairings = []
        for original_pairing in original_pairings:
            pairings.append(
                original_pairing._replace(
                    number=original_pairing.number + table_number_offset
                )
            )

    # Let's manipulate table numbers, we'll come back to pairings after
    pairings_per_table_number = {pairing.number: pairing for pairing in pairings}
    table_numbers = sorted(pairings_per_table_number.keys())
    nb_pages = math.ceil(len(table_numbers) / nb_slips_per_page)
    nb_tables = len(table_numbers)

    def _get_nb_tables_in_row(row_idx):
        # The first row is always full, otherwise we'd done one page fewer
        if row_idx == 0:
            return nb_pages

        total_nb_slips_in_previous_rows = sum(
            [_get_nb_tables_in_row(idx) for idx in range(row_idx - 1, -1, -1)]
        )
        return min(nb_pages, nb_tables - total_nb_slips_in_previous_rows)

    # We build the "matrix" for tables. It's not really a matrix, since
    # some rows are longer than others.
    matrix = [
        # Rows are of different sizes
        [None] * _get_nb_tables_in_row(row_idx)
        # There are `nb_slips_per_page` rows
        for row_idx in range(nb_slips_per_page)
    ]

    # Now we just fill out the matrix, iterating over each line
    table_idx = 0
    for row in matrix:
        for row_idx in range(len(row)):
            row[row_idx] = table_numbers[table_idx]
            table_idx += 1

    # We "inverse" the matrix, to get the list of columns instead of the list of rows
    inversed_matrix = zip_longest(*matrix)
    # We flatten the list of columns into a simple list,
    # `zip_longest` will add `None` to "unfinished" columns
    table_numbers_in_order = [
        table_number for column in inversed_matrix for table_number in column
    ]

    # Now it's back to pairings, from table number
    return [
        pairings_per_table_number[table_number] if table_number is not None else None
        for table_number in table_numbers_in_order
    ]


Standing = namedtuple(
    "Standing", ["position", "player_name", "nb_points", "record", "omw", "gw", "ogw"]
)


def parse_standings(standings_input):
    standings = []
    for standing_line in standings_input.split("\n"):
        standing = _parse_standing(standing_line)
        # _parse_standing will return None in some cases (eg. blank line)
        if standing:
            standings.append(standing)

    # Sort by position
    standings = sorted(standings, key=itemgetter(0))

    if not standings:
        return standings

    # Make sure the first position is number 1
    positions = Counter([standing.position for standing in standings])
    min_position = min(positions.keys())
    if min_position != 1:
        raise ParseStandingException("First position should be number 1")

    # Make sure no position is missing
    max_position = max(positions.keys())
    missing_positions = set(range(min_position, max_position + 1)) - set(
        positions.keys()
    )
    if missing_positions:
        missing_positions_str = ", ".join(
            [str(position) for position in missing_positions]
        )
        raise ParseStandingException(
            f"Some positions are missing: {missing_positions_str}"
        )

    # Make sure we don't have duplicate positions
    duplicate_positions = sorted(
        [
            position
            for position, nb_occurrences in positions.items()
            if nb_occurrences > 1
        ]
    )
    if duplicate_positions:
        duplicate_positions_str = ", ".join(
            [str(position) for position in duplicate_positions]
        )
        raise ParseStandingException(
            f"Some positions are present more than once: {duplicate_positions_str}"
        )

    return standings


re_standing = (
    r"^(?P<position>[0-9]+)\s+"
    # Notice the `?` to disable the greedy behaviour
    r"(?P<player_name>.*?)\s+"
    r"(?P<nb_points>\d+)\s*"
    # Two modes, without draws (eg. `5-0`) and with draws (eg. `5-0-1`)
    r"(?P<record>(\d+\s*-\s*\d+\s*-\s*\d+)|(\d+\s*-\s*\d+))\s+"
    r"(?P<omw>[\d.]+%)\s+"
    r"(?P<gw>[\d.]+%)\s+"
    r"(?P<ogw>[\d.]+%)$"
)


def _parse_standing(standing_line):
    standing_line = standing_line.strip()

    # If at that point the line is empty, just return None :shrug:
    if not standing_line:
        return None

    # Invoking the power of regexps
    result = re.match(re_standing, standing_line)
    if not result:
        raise ParseStandingException(
            f"Could not parse the following standing: {standing_line}"
        )

    group_dict = result.groupdict()
    return Standing(
        position=int(group_dict["position"]),
        player_name=group_dict["player_name"],
        nb_points=int(group_dict["nb_points"]),
        record=group_dict["record"],
        omw=group_dict["omw"],
        gw=group_dict["gw"],
        ogw=group_dict["ogw"],
    )
