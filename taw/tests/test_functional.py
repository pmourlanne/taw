from pathlib import Path

import pytest

from taw import app as taw_app


@pytest.fixture
def app():
    app = taw_app
    app.config.update(
        {
            "TESTING": True,
        }
    )

    yield app


@pytest.fixture
def client(app):
    return app.test_client()


TESTING_DIR = Path("taw/testing/")


def get_stem_from_path(path):
    return path.stem


def _get_html_output_path(dump_path, *, prefix=None):
    return TESTING_DIR / f"outputs/{prefix}{dump_path.stem}.html"


def _get_expected_html(dump_path, *, prefix=None):
    prefix = prefix or ""

    expected_html_path = _get_html_output_path(dump_path, prefix=prefix)
    if not expected_html_path.exists():
        raise pytest.fail(
            f"There is no expected HTML output in the repo for {dump_path} "
            f"Generate the html output by running pytest --generate-test-outputs, "
            "making sure the generated HTML looks OK and committing the file to the repo"
        )

    with expected_html_path.open() as f:
        expected_html = f.read()

    return expected_html


@pytest.fixture
def assert_generated_html(taw_generate_test_outputs, client):
    def _func(dump_path, mode):
        with dump_path.open() as f:
            dump = f.read()

        response = client.post(
            "/",
            data={
                "tournament_name": "Testing Tournament",
                "round_number": "1",
                "aetherhub_dump": dump,
                "action": mode,
            },
        )
        generated_html = response.get_data(as_text=True)

        prefix = "match_slips_" if mode == "match_slips" else ""

        # If we were asked to generate the test outputs
        if taw_generate_test_outputs:
            # We save the generated html as the expected output
            html_output_path = _get_html_output_path(dump_path, prefix=prefix)
            with html_output_path.open("w") as f:
                f.write(generated_html)

        expected_html = _get_expected_html(dump_path, prefix=prefix)

        assert generated_html == expected_html

    return _func


@pytest.mark.parametrize("mode", ["pairings", "match_slips"])
@pytest.mark.parametrize(
    "dump_path",
    TESTING_DIR.glob("*pairings*.txt"),
    ids=get_stem_from_path,
)
def test_generate_from_pairings(dump_path, mode, assert_generated_html):
    assert_generated_html(dump_path, mode)


@pytest.mark.parametrize(
    "dump_path",
    TESTING_DIR.glob("*standings*.txt"),
    ids=get_stem_from_path,
)
def test_generate_from_standings(dump_path, assert_generated_html):
    assert_generated_html(dump_path, "standings")
