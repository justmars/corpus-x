import toml

import corpus_x


def test_version():
    assert (
        toml.load("pyproject.toml")["tool"]["poetry"]["version"]
        == corpus_x.__version__
    )
