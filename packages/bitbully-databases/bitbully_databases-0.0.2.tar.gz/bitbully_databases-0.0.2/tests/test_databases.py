"""Test the basic opening book functionality."""

import pytest

import bitbully_databases as bbd

# Example position A: a known position in the 12-ply and 12-ply-dist opening books
# Expected score is 71 for player 1 (yellow, X) to win in (100-71) = 29 moves
A = [
    [0, 0, 0, 0, 0, 0, 0],  #
    [0, 0, 0, 1, 0, 0, 0],  #
    [0, 1, 0, 2, 0, 0, 0],  #
    [0, 2, 0, 1, 0, 2, 0],  #
    [0, 1, 0, 2, 0, 1, 0],  #
    [0, 2, 0, 1, 0, 2, 0],  #
]

# Example position B: a known position in the 8-ply opening books
# Expected score is 1
B = [
    [0, 0, 0, 0, 0, 0, 0],  #
    [0, 0, 0, 1, 0, 0, 0],  #
    [0, 0, 0, 2, 0, 0, 0],  #
    [0, 2, 0, 1, 0, 0, 0],  #
    [0, 1, 0, 2, 0, 0, 0],  #
    [0, 2, 0, 1, 0, 0, 0],
]

# Example position C: a known position in the 8-ply opening books
# Expected score is 0
C = [
    [0, 0, 0, 0, 0, 0, 0],  #
    [0, 0, 0, 2, 0, 0, 0],  #
    [0, 0, 0, 1, 0, 0, 0],  #
    [0, 0, 0, 2, 0, 0, 0],  #
    [0, 0, 0, 1, 0, 2, 0],  #
    [0, 0, 1, 2, 0, 1, 0],
]

# Example position D: a known position in the 12-ply and 12-ply-dist opening books
# Expected score is 0 (draw)
D = [
    [0, 0, 0, 0, 0, 0, 0],  #
    [0, 0, 0, 0, 0, 0, 0],  #
    [0, 0, 1, 1, 0, 0, 0],  #
    [0, 0, 2, 2, 0, 0, 0],  #
    [0, 0, 2, 1, 2, 0, 0],  #
    [0, 1, 1, 2, 1, 2, 0],
]

# Example position E: a known position in the 12-ply and 12-ply-dist opening books
# Expected score is 73 for player 1 (yellow, X) to win in (100-73) = 27 moves
E = [
    [0, 0, 0, 0, 0, 0, 0],  #
    [0, 0, 0, 0, 0, 0, 0],  #
    [0, 1, 0, 0, 0, 0, 0],  #
    [0, 2, 2, 0, 1, 0, 0],  #
    [0, 2, 1, 0, 2, 0, 0],  #
    [1, 1, 2, 1, 2, 0, 0],
]

# Example position F: a known position in the 12-ply and 12-ply-dist opening books
# Expected score is -88 for player 1 (yellow, X) to lose in (100-88) = 12 moves
F = [
    [0, 0, 0, 0, 0, 0, 0],  #
    [0, 0, 0, 0, 0, 0, 0],  #
    [0, 0, 1, 1, 0, 0, 0],  #
    [0, 0, 2, 2, 0, 0, 0],  #
    [0, 1, 2, 1, 0, 0, 0],  #
    [0, 1, 1, 2, 0, 2, 2],
]


def test_dummy() -> None:
    """A dummy test to verify test discovery works."""
    assert True


@pytest.fixture(scope="session")
def openingbook_8ply() -> bbd.BitBullyDatabases:
    """Session-scoped fixture for the 8-ply BitBullyDatabases without distances.

    Returns:
        bbd.BitBullyDatabases: The 8-ply BitBullyDatabases instance.
    """
    return bbd.BitBullyDatabases(db_name="8-ply")


@pytest.fixture(scope="session")
def openingbook_12ply() -> bbd.BitBullyDatabases:
    """Session-scoped fixture for the 12-ply BitBullyDatabases without distances.

    Returns:
        bbd.BitBullyDatabases: The 12-ply BitBullyDatabases instance.
    """
    return bbd.BitBullyDatabases(db_name="12-ply")


@pytest.fixture(scope="session")
def openingbook_12ply_dist() -> bbd.BitBullyDatabases:
    """Session-scoped fixture for the 12-ply BitBullyDatabases with distances.

    Returns:
        bbd.BitBullyDatabases: The 12-ply BitBullyDatabases instance with distances.
    """
    return bbd.BitBullyDatabases(db_name="12-ply-dist")


@pytest.mark.parametrize(
    ("openingbook_fixture", "expected_size"),
    [
        ("openingbook_8ply", 34515),
        ("openingbook_12ply", 1735945),
        ("openingbook_12ply_dist", 4200899),
    ],
)
def test_get_book_size(request: pytest.FixtureRequest, openingbook_fixture: str, expected_size: int) -> None:
    """Test that the size of the BitBullyDatabases is correct for different variants.

    Args:
        request (pytest.FixtureRequest): The pytest fixture request object.
        openingbook_fixture (str): The name of the BitBullyDatabases fixture to use.
        expected_size (int): The expected size of the BitBullyDatabases.
    """
    openingbook = request.getfixturevalue(openingbook_fixture)
    size = openingbook.get_book_size()
    assert size == expected_size


@pytest.mark.parametrize(
    ("openingbook_fixture", "board", "expected_value"),
    [
        ("openingbook_12ply", A, 1),
        ("openingbook_12ply_dist", A, 71),
        ("openingbook_8ply", B, 1),
        ("openingbook_8ply", C, 0),
        ("openingbook_12ply", D, 0),
        ("openingbook_12ply_dist", D, 0),
        ("openingbook_12ply", E, 1),
        ("openingbook_12ply_dist", E, 73),
        ("openingbook_12ply", F, -1),
        ("openingbook_12ply_dist", F, -88),
    ],
)
def test_get_board_value_known_position(
    request: pytest.FixtureRequest, openingbook_fixture: str, board: list[list[int]], expected_value: int
) -> None:
    """Test that the correct value is returned for a known position in the OpeningBookCore.

    Args:
        request (pytest.FixtureRequest): The pytest fixture request object.
        openingbook_fixture (str): The name of the OpeningBookCore fixture to use.
        board (list[list[int]]): The 2D list representing the board position.
        expected_value (int): The expected value for the given position.
    """
    openingbook = request.getfixturevalue(openingbook_fixture)
    val = openingbook.get_book_value(board)
    assert val == expected_value
