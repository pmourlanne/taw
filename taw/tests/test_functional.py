from pathlib import Path

import pytest

from taw import app as taw_app


@pytest.fixture()
def app():
    app = taw_app
    app.config.update(
        {
            "TESTING": True,
        }
    )

    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


TESTING_DIR = Path("taw/testing/")


def get_stem_from_path(path):
    return path.stem


def _get_expected_html(dump_path, *, prefix=None):
    prefix = prefix or ""

    expected_html_path = TESTING_DIR / f"outputs/{prefix}{dump_path.stem}.html"
    if not expected_html_path.exists():
        raise pytest.fail(
            f"There is no expected HTML output in the repo for {dump_path} "
            f"Generate the html output using the dump from {dump_path}, 'Testing Tournament' "
            f"as the tournament name and round #1. Then save the HTML in '{expected_html_path}'"
        )

    with expected_html_path.open() as f:
        expected_html = f.read()

    # Remove trailing carriage return if necessary
    expected_html = expected_html.rstrip("\n")

    return expected_html


@pytest.fixture(params=TESTING_DIR.glob("*pairings*.txt"), ids=get_stem_from_path)
def pairings_dump_with_expected_html(request):
    path = request.param
    with path.open() as f:
        pairings_dump = f.read()

    expected_html = _get_expected_html(path)

    return pairings_dump, expected_html


@pytest.fixture(params=TESTING_DIR.glob("*pairings*.txt"), ids=get_stem_from_path)
def pairings_dump_with_match_slips_expected_html(request):
    path = request.param
    with path.open() as f:
        pairings_dump = f.read()

    expected_html = _get_expected_html(path, prefix="match_slips_")

    return pairings_dump, expected_html


def test_generate_pairings(client, pairings_dump_with_expected_html):
    pairings_dump, expected_html = pairings_dump_with_expected_html

    response = client.post(
        "/",
        data={
            "tournament_name": "Testing Tournament",
            "round_number": "1",
            "aetherhub_dump": pairings_dump,
            "action": "pairings",
        },
    )
    assert response.get_data(as_text=True) == expected_html


def test_generate_match_slips(client, pairings_dump_with_match_slips_expected_html):
    pairings_dump, expected_html = pairings_dump_with_match_slips_expected_html

    response = client.post(
        "/",
        data={
            "tournament_name": "Testing Tournament",
            "round_number": "1",
            "aetherhub_dump": pairings_dump,
            "action": "match_slips",
        },
    )
    assert response.get_data(as_text=True) == expected_html
