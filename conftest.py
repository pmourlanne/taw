import pytest


def pytest_addoption(parser):
    # raise Exception("hello??")
    parser.addoption(
        "--generate-test-outputs",
        action="store_true",
        dest="generate_test_outputs",
        default=False,
        help="Generate test outputs before running the tests.",
    )


@pytest.fixture(scope="session")
def taw_generate_test_outputs(request):
    return request.config.getvalue("generate_test_outputs")
