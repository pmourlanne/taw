import re
from collections import namedtuple


Player = namedtuple("Player", ["name", "points"])
Table = namedtuple("Table", ["number", "player_1", "player_2"])


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

    return pairings


re_pairing = (
    r"^(?P<table_number>[0-9]+)\s+"
    r"(?P<player_1_name>[\w\s']+)\s"
    r"\((?P<player_1_nb_points>[\d]+)\sPoints\)\s*"
    r"(?P<player_2_name>[\w\s']+)\s"
    r"\((?P<player_2_nb_points>[\d]+)\sPoints\).*"
)

re_pairing_bye = (
    r"^(?P<table_number>[0-9]+)\s+"
    r"(?P<player_1_name>[\w\s]+)\s"
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
                name="BYE",
                points=0,
            ),
        )

    # Welp, we tried peeps
    raise Exception("TODO: This should be a custom exception")
