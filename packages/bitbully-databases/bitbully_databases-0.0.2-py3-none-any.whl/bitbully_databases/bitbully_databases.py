"""Module for BitBully Databases (no NumPy dependency).

This module demonstrates how to read, search, and evaluate binary files
containing Connect-4 positions and scores using pure Python (no NumPy).
For efficient/production use, prefer the BitBully C++/pybind11 API.
"""

from __future__ import annotations

import sys
from importlib.resources import as_file, files
from pathlib import Path
from typing import BinaryIO, Literal

"""Board matrix type.

Each entry is an integer:
- 0: end-of-column sentinel (no more pieces when scanning bottom→top)
- 1: player 1 token
- any other non-zero: player 2 token
"""
Board = list[list[int]]


class BitBullyDatabases:
    """Access and query packaged BitBully opening databases.

    This class provides a simple, pure-Python interface for exploring and analyzing
    BitBully database files containing Connect-4 positions and evaluation scores.

    In typical use, you will only need the static method
    [`get_database_path()`][src.bitbully_databases.bitbully_databases.BitBullyDatabases.get_database_path]
    to retrieve the path to a packaged database file.

    The remaining methods (e.g., `readline`, `read_book`, `binary_search`,
    `to_huffman`, `get_book_value`) are provided for **illustration and
    educational purposes** only. They demonstrate the binary format and logic of
    BitBully database files in a transparent, Pythonic way.

    For performance-critical or production use, rely instead on the official
    [BitBully API](https://github.com/MarkusThill/BitBully), which implements the
    same functionality in optimized C++ and exposes it to Python via **pybind11**.
    The C++ implementation is substantially faster and more memory-efficient than
    the pure-Python examples shown here.

    Example:
        Get the score for a known position with exactly 12 tokens in the 12-ply-dist database.
        Player 1 (yellow, X) can win in 29 moves.
        ```python
        import bitbully_databases as bbd

        openingbook = bbd.BitBullyDatabases(db_name="12-ply-dist")

        # Example position: a known position in the 12-ply and 12-ply-dist opening books
        # Expected score is 71 for player 1 (yellow, X) to win in (100-71) = 29 moves
        board = [
            [0, 0, 0, 0, 0, 0, 0],  #
            [0, 0, 0, 1, 0, 0, 0],  #
            [0, 1, 0, 2, 0, 0, 0],  #
            [0, 2, 0, 1, 0, 2, 0],  #
            [0, 1, 0, 2, 0, 1, 0],  #
            [0, 2, 0, 1, 0, 2, 0],  #
        ]
        expected_value = 71
        val = openingbook.get_book_value(board)
        assert val == expected_value
        ```

    Example:
        Get the score for another  position with exactly 12 tokens in the 12-ply-dist database.
        Player 1 (yellow, X) will lose in 12 moves.
        ```python
        import bitbully_databases as bbd

        openingbook = bbd.BitBullyDatabases(db_name="12-ply-dist")

        # Example position F: a known position in the 12-ply and 12-ply-dist opening books
        # Expected score is -88 for player 1 (yellow, X) to lose in (100-88) = 12 moves
        board = [
            [0, 0, 0, 0, 0, 0, 0],  #
            [0, 0, 0, 0, 0, 0, 0],  #
            [0, 0, 1, 1, 0, 0, 0],  #
            [0, 0, 2, 2, 0, 0, 0],  #
            [0, 1, 2, 1, 0, 0, 0],  #
            [0, 1, 1, 2, 0, 2, 2],
        ]
        expected_value = -88
        val = openingbook.get_book_value(board)
        assert val == expected_value
        ```

    For further examples, see
    [`get_book_value()`][src.bitbully_databases.bitbully_databases.BitBullyDatabases.get_book_value].
    """

    def __init__(self, db_name: Literal["default", "8-ply", "12-ply", "12-ply-dist"] | None = None) -> None:
        """Initialize an instance and (optionally) load a database.

        Args:
            db_name (Literal["default", "8-ply", "12-ply", "12-ply-dist"] | None):
                Database to load. Accepted values:
                - "default": 12-ply with distances
                - "8-ply": 8-ply without distances
                - "12-ply": 12-ply without distances
                - "12-ply-dist": 12-ply with distances
                - None: do not load anything
        """
        self.db_name = db_name
        self.book: list[tuple[int, int]] | None = None
        self.with_distances: bool = False
        if db_name is not None:
            db_path = Path(BitBullyDatabases.get_database_path(db_name))
            self.with_distances = db_name in ["default", "12-ply-dist"]
            self.is_8ply = db_name == "8-ply"
            self.book = BitBullyDatabases._read_book(
                file=db_path,
                with_distances=self.with_distances,
                is_8ply=self.is_8ply,
            )

    @staticmethod
    def get_database_path(db_name: Literal["default", "8-ply", "12-ply", "12-ply-dist"] = "default") -> str:
        """Return the packaged file path for a given database name.

        Args:
            db_name (Literal["default", "8-ply", "12-ply", "12-ply-dist"]):
                Database identifier.

        Returns:
            str: Absolute path to the packaged binary database file.

        Raises:
            ValueError: If `db_name` is not one of the supported values.

        Example:
            ```python
            import bitbully_databases as bbd

            db_path = bbd.BitBullyDatabases.get_database_path("12-ply-dist")
            print(db_path)
            # Outputs the absolute path to 'book_12ply_distances.dat'
            ```
        """
        if db_name == "default":
            db_path = files("bitbully_databases").joinpath("assets/book_12ply_distances.dat")
        elif db_name == "8-ply":
            db_path = files("bitbully_databases").joinpath("assets/book_8ply.dat")
        elif db_name == "12-ply":
            db_path = files("bitbully_databases").joinpath("assets/book_12ply.dat")
        elif db_name == "12-ply-dist":
            db_path = files("bitbully_databases").joinpath("assets/book_12ply_distances.dat")
        else:
            raise ValueError(
                f"Unknown database name: {db_name}. Allowed: Literal['default','8-ply','12-ply','12-ply-dist']"
            )
        with as_file(db_path) as f:
            return str(f)

    def get_book_value(self, board: Board) -> int | None:
        """Retrieve the score for a given board position.

        Note:
            Pure-Python lookup is for demonstration; prefer the C++/pybind11 API for performance.

        Args:
            board (Board):
                Board matrix shaped rows x cols (e.g., 6 x 7). Entries:
                0=end-of-column sentinel when scanning bottom→top, 1=player1, else=player2.

        Returns:
            int | None:
                Score from the book. If the database stores distances
                (`with_distances=True`), returns the stored signed distance or `None`
                if the position is not present. If it does *not* store distances,
                returns 1 when the position is not present (convention: P1 wins)
                or the stored value if present.

        Raises:
            ValueError: If no database is loaded.

        Example:
            **Example 1 — 12-ply-dist (Player 1 wins in 29 moves):**
            ```python
            import bitbully_databases as bbd

            # Example position: a known position in the 12-ply and 12-ply-dist opening books
            # Expected score is 71 for player 1 (yellow, X) to win in (100-71) = 29 moves
            board = [
                [0, 0, 0, 0, 0, 0, 0],  #
                [0, 0, 0, 1, 0, 0, 0],  #
                [0, 1, 0, 2, 0, 0, 0],  #
                [0, 2, 0, 1, 0, 2, 0],  #
                [0, 1, 0, 2, 0, 1, 0],  #
                [0, 2, 0, 1, 0, 2, 0],  #
            ]
            expected_value = 71
            val = bbd.BitBullyDatabases(db_name="12-ply-dist").get_book_value(board)
            assert val == expected_value
            ```

        Example:
            **Example 2 — 8-ply (Basic win/loss database)**
            ```python
            import bitbully_databases as bbd

            board = [
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 2, 0, 0, 0],
                [0, 2, 0, 1, 0, 0, 0],
                [0, 1, 0, 2, 0, 0, 0],
                [0, 2, 0, 1, 0, 0, 0],
            ]
            val = bbd.BitBullyDatabases("8-ply").get_book_value(board)
            print(val)  # 1 → Player 1 wins
            ```

        Example:
            **Example 3 — 8-ply (Draw position)**
            ```python
            import bitbully_databases as bbd

            board = [
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 2, 0, 0, 0],
                [0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 2, 0, 0, 0],
                [0, 0, 0, 1, 0, 2, 0],
                [0, 0, 1, 2, 0, 1, 0],
            ]
            val = bbd.BitBullyDatabases("8-ply").get_book_value(board)
            print(val)  # 0 → Draw
            ```

        Example:
            **Example 4 — 12-ply (Draw position)**
            ```python
            import bitbully_databases as bbd

            board = [
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 1, 0, 0, 0],
                [0, 0, 2, 2, 0, 0, 0],
                [0, 0, 2, 1, 2, 0, 0],
                [0, 1, 1, 2, 1, 2, 0],
            ]
            val = bbd.BitBullyDatabases("12-ply").get_book_value(board)
            print(val)  # 0 → Draw
            ```

        Example:
            **Example 5 — 12-ply-dist (Player 1 wins in 27 moves)**
            ```python
            import bitbully_databases as bbd

            board = [
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 1, 0, 0, 0, 0, 0],
                [0, 2, 2, 0, 1, 0, 0],
                [0, 2, 1, 0, 2, 0, 0],
                [1, 1, 2, 1, 2, 0, 0],
            ]
            val = bbd.BitBullyDatabases("12-ply-dist").get_book_value(board)
            print(val)  # 73 → Player 1 wins in 27 moves
            ```

        Example:
            **Example 6 — 12-ply-dist (Player 1 loses in 12 moves)**
            ```python
            import bitbully_databases as bbd

            board = [
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 1, 0, 0, 0],
                [0, 0, 2, 2, 0, 0, 0],
                [0, 1, 2, 1, 0, 0, 0],
                [0, 1, 1, 2, 0, 2, 2],
            ]
            val = bbd.BitBullyDatabases("12-ply-dist").get_book_value(board)
            print(val)  # -88 → Player 1 loses in 12 moves
            ```
        """
        if self.book is None:
            raise ValueError("No database loaded; cannot get book value.")
        return BitBullyDatabases._get_book_value(board, self.book, with_distances=self.with_distances)

    def get_book_size(self) -> int | None:
        """Return the number of entries in the loaded book.

        Returns:
            int | None: Number of entries or `None` if no book is loaded.

        Raises:
            ValueError: If no database is loaded.

        Example:
            Retrieve the number of entries for each packaged database.
            ```python
            import bitbully_databases as bbd

            # Default: loads the 12-ply-dist database automatically
            db_default = bbd.BitBullyDatabases()
            print(db_default.get_book_size())  # 4200899

            # Load the 8-ply opening book
            db8 = bbd.BitBullyDatabases("8-ply")
            print(db8.get_book_size())  # 34515

            # Load the 12-ply book without distances
            db12 = bbd.BitBullyDatabases("12-ply")
            print(db12.get_book_size())  # 1735945

            # Load the 12-ply book with distances explicitly
            db12d = bbd.BitBullyDatabases("12-ply-dist")
            print(db12d.get_book_size())  # 4200899
            ```

        Example:
            Calling this method before loading any database raises an error.
            ```python
            import bitbully_databases as bbd

            db = bbd.BitBullyDatabases(None)  # Explicitly skip loading
            try:
                db.get_book_size()
            except ValueError as e:
                print(e)
                # → "No database loaded; cannot determine book size."
            ```
        """
        if self.book is None:
            raise ValueError("No database loaded; cannot determine book size.")
        return len(self.book) if self.book is not None else None

    def get_book_memory_size(self) -> int | None:
        """Return the approximate memory size of the loaded book list.

        Returns:
            int | None: Size in bytes (via :func:`sys.getsizeof`) or `None` if not loaded.

        Raises:
            ValueError: If no database is loaded.

        Example:
            Retrieve the approximate memory usage of each packaged database.
            ```python
            import bitbully_databases as bbd

            # Default: loads the 12-ply-dist database automatically
            db_default = bbd.BitBullyDatabases()
            print(db_default.get_book_memory_size())

            # Load the 8-ply opening book
            db8 = bbd.BitBullyDatabases("8-ply")
            print(db8.get_book_memory_size())

            # Load the 12-ply book without distances
            db12 = bbd.BitBullyDatabases("12-ply")
            print(db12.get_book_memory_size())

            # Load the 12-ply book with distances explicitly
            db12d = bbd.BitBullyDatabases("12-ply-dist")
            print(db12d.get_book_memory_size())
            ```

        Example:
            Calling this method before loading any database raises an error.
            ```python
            import bitbully_databases as bbd

            db = bbd.BitBullyDatabases(None)  # Explicitly skip loading
            try:
                db.get_book_memory_size()
            except ValueError as e:
                print(e)
                # → "No database loaded; cannot determine book memory size."
            ```
        """
        if self.book is None:
            raise ValueError("No database loaded; cannot determine book memory size.")
        return sys.getsizeof(self.book) if self.book is not None else None

    def has_win_distances(self) -> bool:
        """Indicate whether the loaded database stores winning distances (scores) separately.

        Some BitBully databases store only simple win/loss outcomes
        (-1 = loss, 0 = draw, 1 = win), while others also include
        **signed distance values** that indicate *how many moves remain*
        until a win or loss.

        This method lets you check whether the currently loaded database
        contains those distance values.

        Returns:
            bool:
                `True` if the loaded database includes distance information
                (e.g., `"12-ply-dist"` or `"default"`),
                `False` otherwise (e.g., `"8-ply"` or `"12-ply"`).

        Raises:
            ValueError:
                If no database is loaded.

        Example:
            Check whether the default (12-ply-dist) database contains win distances.
            ```python
            import bitbully_databases as bbd

            db_default = bbd.BitBullyDatabases()  # default = "12-ply-dist"
            print(db_default.has_win_distances())  # True
            ```

        Example:
            Compare different databases.
            ```python
            import bitbully_databases as bbd

            db8 = bbd.BitBullyDatabases("8-ply")
            db12 = bbd.BitBullyDatabases("12-ply")
            db12d = bbd.BitBullyDatabases("12-ply-dist")

            print(db8.has_win_distances())  # False
            print(db12.has_win_distances())  # False
            print(db12d.has_win_distances())  # True
            ```

        Example:
            Calling this method before loading any database raises an error.
            ```python
            import bitbully_databases as bbd

            db = bbd.BitBullyDatabases(None)  # explicitly skip loading
            try:
                db.has_win_distances()
            except ValueError as e:
                print(e)
                # → "No database loaded; cannot determine if it has win distances."
            ```
        """
        if self.book is None:
            raise ValueError("No database loaded; cannot determine if it has win distances.")
        return self.with_distances

    # ---------- Binary file reading ----------

    @staticmethod
    def _readline(f: BinaryIO, with_distances: bool, is_8ply: bool) -> tuple[int | None, int | None]:
        """Read a single (position, score) entry; return (None, None) on EOF.

        Args:
            f (BinaryIO): Open binary file handle (positioned at the next entry).
            with_distances (bool): Whether scores are stored in a trailing byte.
            is_8ply (bool): Whether entries are in 3 bytes (8-ply) vs 4 bytes.

        Returns:
            tuple[int | None, int | None]: (huffman_position, score), or (None, None) at EOF.
        """
        bytes_position = 3 if is_8ply else 4
        x = f.read(bytes_position)
        if not x:
            return None, None  # EOF

        huffman_position = int.from_bytes(x, byteorder="big", signed=not is_8ply)
        if with_distances:
            score = int.from_bytes(f.read(1), byteorder="big", signed=True)
        else:
            # Last two bits encode the score; convention: multiply by -1.
            score = (huffman_position & 3) * (-1)
            huffman_position = (huffman_position // 4) * 4  # zero-out last 2 bits
        return huffman_position, score

    @staticmethod
    def _read_book(file: Path, with_distances: bool = True, is_8ply: bool = False) -> list[tuple[int, int]]:
        """Read the entire binary book into memory.

        Args:
            file (Path): Path to the binary book file.
            with_distances (bool): Whether scores are stored in a separate byte.
            is_8ply (bool): Whether entries are 3 bytes (8-ply) vs 4 bytes.

        Returns:
            list[tuple[int, int]]: List of (huffman_position, score) in ascending position order.
        """
        book: list[tuple[int, int]] = []
        with Path.open(file, "rb") as f:
            while True:
                position, score = BitBullyDatabases._readline(f, with_distances, is_8ply)
                if position is None:
                    break
                if score is None:
                    continue  # should not happen...
                book.append((position, score))
        return book

    # ---------- Lookup helpers ----------

    @staticmethod
    def _binary_search(book: list[tuple[int, int]], huffman_position: int) -> int | None:
        """Binary search for a position in a sorted book.

        Args:
            book (list[tuple[int, int]]): Sorted list of (position, score) pairs.
            huffman_position (int): Target position to look up.

        Returns:
            int | None: Score if found, else None.
        """
        left = 0
        right = len(book) - 1
        while right >= left:
            mid = (left + right + 1) // 2
            p = book[mid][0]
            if p == huffman_position:
                return book[mid][1]
            if p > huffman_position:
                right = mid - 1
            else:
                left = mid + 1
        return None

    # ---------- Board encoding (no NumPy) ----------

    @staticmethod
    def _dims(board: Board) -> tuple[int, int]:
        """Return (rows, cols) and perform a minimal rectangularity check.

        Args:
            board (Board): Board matrix.

        Returns:
            tuple[int, int]: (rows, cols).

        Raises:
            ValueError: If the board has zero rows or rows with differing lengths.
        """
        rows = len(board)
        if rows == 0:
            raise ValueError("Board must have at least one row.")
        cols = len(board[0])
        for r in board:
            if len(r) != cols:
                raise ValueError("Board rows must all have the same length.")
        return rows, cols

    @staticmethod
    def _to_huffman(board: Board) -> int:
        """Convert a board to its Huffman-encoded integer.

        Iteration order:
            Columns left→right; within each column, rows bottom→top.

        Encoding:
            - 0 → end-of-column sentinel (separator bit '0')
            - 1 → player 1 token ('10')
            - any other non-zero → player 2 token ('11')

        Args:
            board (Board): Board matrix.

        Returns:
            int: Signed 32-bit-compatible integer encoding of the board.
        """
        rows, cols = BitBullyDatabases._dims(board)

        bits: list[str] = ["0b"]
        for c in range(cols):  # e.g., 0..6 for 7 columns
            for r in reversed(range(rows)):  # e.g., 0..5 for 6 rows
                v = board[r][c]
                if v == 0:
                    bits.append("0")  # separator for end-of-column
                    break
                if v == 1:
                    bits.append("10")  # P1 token (2 bits)
                else:
                    bits.append("11")  # P2 token (2 bits)
                if r == 0:
                    bits.append("0")  # column full → still add separator

        bits.append("0")  # pad to full byte as original logic does
        s = "".join(bits)
        val = int(s, 2)
        # If first payload bit is '1' and total exceeds 32 bits, adjust to signed 32-bit (two's complement).
        if s[2] == "1" and len(s) > 32:
            val -= 2 << 31  # 2**32
        return val

    @staticmethod
    def _mirror_horiz(board: Board) -> Board:
        """Return a horizontally mirrored copy of the board (flip columns).

        Args:
            board (Board): Board matrix.

        Returns:
            Board: New board matrix mirrored along the vertical axis.
        """
        rows, cols = BitBullyDatabases._dims(board)
        mirrored: Board = [[0] * cols for _ in range(rows)]
        for r in range(rows):
            for c in range(cols):
                mirrored[r][cols - 1 - c] = board[r][c]
        return mirrored

    @staticmethod
    def _get_book_value(board: Board, book: list[tuple[int, int]], with_distances: bool = True) -> int | None:
        """Lookup score via Huffman encoding, trying both the board and its mirror.

        Args:
            board (Board): Board matrix.
            book (list[tuple[int, int]]): Database as (position, score) pairs.
            with_distances (bool): Whether the database stores distances separately.

        Returns:
            int | None:
                Score for the board. If `with_distances` is False and the position is
                not found, returns 1 (convention: P1 wins). Otherwise returns None if
                not found.
        """
        p = BitBullyDatabases._to_huffman(board)
        val = BitBullyDatabases._binary_search(book, p)
        if val is not None:
            return val

        p_m = BitBullyDatabases._to_huffman(BitBullyDatabases._mirror_horiz(board))
        val = BitBullyDatabases._binary_search(book, p_m)

        if not with_distances and val is None:
            # In 8/12-ply books without distances: missing ⇒ P1 wins
            return 1
        return val
