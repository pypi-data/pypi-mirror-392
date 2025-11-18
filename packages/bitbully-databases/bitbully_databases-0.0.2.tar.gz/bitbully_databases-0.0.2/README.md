# bitbully-databases
Opening Databases for the Board Game Connect-4.

<h1 align="center">
<img src="https://raw.githubusercontent.com/MarkusThill/bitbully-databases/master/bitbully-databases-logo.png" alt="bitbully-logo-full" width="400" >
</h1><br>

**BitBully Databases** is a companion library to [BitBully](https://github.com/MarkusThill/BitBully) that provides precomputed **Connect-4 opening books** with millions of evaluated positions.
It includes a **pure-Python reference implementation** (no NumPy dependency) demonstrating how to read, search, and interpret these binary databases — ideal for educational use and exploration.
For high-performance inference, use the native **C++/pybind11 BitBully API** to access and query the databases.


## Install

Install `bitbully-databases` via pip:

```bash
pip install bitbully-databases
```

## Usage

```python
import bitbully_databases as bbd

# Load the 12-ply book with distances (default)
db = bbd.BitBullyDatabases("12-ply-dist")

# Get the absolute file path of the packaged database
path = bbd.BitBullyDatabases.get_database_path("12-ply-dist")
print("Database path:", path)

# Check database metadata
print("Book size:", db.get_book_size())
print("Memory size (bytes):", db.get_book_memory_size())
print("Contains win distances:", db.has_win_distances())

# Example Connect-4 board (bottom → top)
# Player 1 (yellow, X) will eventually win
board = [
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0],
    [0, 1, 0, 2, 0, 0, 0],
    [0, 2, 0, 1, 0, 2, 0],
    [0, 1, 0, 2, 0, 1, 0],
    [0, 2, 0, 1, 0, 2, 0],
]

# Retrieve the evaluation score for the board
value = db.get_book_value(board)
print("Book value:", value)
if value is not None and db.has_win_distances():
    print(f"→ Player 1 wins in {100 - abs(value)} moves.")

# Display whether the database uses distances and the type of book
print("Has win distances:", db.has_win_distances())
```

## Further Usage Examples and API Reference

You will find further examples and the full API reference under [https://markusthill.github.io/bitbully-databases/](https://markusthill.github.io/bitbully-databases/)

# Development (Debian-based Systems)

## Install & Activate virtualenv

```bash
python3 -m venv venv
source venv/bin/activate
```

## Install Dependencies

```bash
pip install -e .[dev,ci]
```

```bash
pre-commit install
```

You can run pre-commit before a commit with:

```bash
pre-commit run
```

## Commitizen

### Bump Version

```bash
cz bump --dry-run # first perform a dry run
cz bump
git push origin tag x.x.x
```

An alpha release can be created like this:
```bash
cz bump --prerelease alpha
```

### Push commit and tag atomically

For example, pushing the commit and tag for `v0.0.2-a1` would be done like this:
```bash
git push --atomic origin master v0.0.2-a1
```
