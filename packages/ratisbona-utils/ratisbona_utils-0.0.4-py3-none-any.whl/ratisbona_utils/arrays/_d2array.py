from __future__ import annotations
from dataclasses import dataclass
from typing import TypeVar, Generic, Callable, Generator, Sequence, Iterable
from ._slices import slice_2d_recognition, slice_parsing

TC = TypeVar("TC")

@dataclass()
class D2Array(Generic[TC]):
    num_rows: int
    num_cols: int
    _cells: list[TC] | None = None

    def __post_init__(self):
        if self.num_rows <= 0 or self.num_cols <= 0:
            raise ValueError(f"Invalid num_rows/num_cols: {self.num_rows}/{self.num_cols}")

        if self._cells is None:
            object.__setattr__(self, "_cells", [None] * (self.num_rows * self.num_cols))

    @staticmethod
    def empty(num_rows: int, num_cols: int) -> D2Array:
        return D2Array(num_rows, num_cols, [None] * num_rows * num_cols)

    @staticmethod
    def by_generating_func(generator: Callable[[int, int], TC], num_rows: int, num_cols: int) -> "D2Array":
        d2array = D2Array.empty(num_rows, num_cols)
        for row in range(num_rows):
            for col in range(num_cols):
                d2array._cells[d2array.linear_index(row, col)] = generator(row, col)
        return d2array

    @staticmethod
    def from_cells(num_rows: int, num_cols: int, cells: list[TC]) -> "D2Array":
        if len(cells) != num_rows * num_cols:
            raise ValueError(f"Cells length {len(cells)} does not match num_rows*num_cols {num_rows*num_cols}")
        return D2Array(num_rows, num_cols, cells)

    @staticmethod
    def from_2d_list(cells_2d: list[list[TC]]) -> "D2Array":
        if not cells_2d:
            raise ValueError("cells_2d cannot be empty")
        num_rows = len(cells_2d)
        num_cols = len(cells_2d[0])
        for row in cells_2d:
            if len(row) != num_cols:
                raise ValueError("All rows must have the same number of columns")
        flat_cells = [cell for row in cells_2d for cell in row]
        return D2Array(num_rows, num_cols, flat_cells)

    def is_valid_row(self, row):
        """
        Checks if the given row index is within the valid range of rows.

        The method evaluates whether the specified row index falls within
        the inclusive range of [0, num_rows). This is used to ensure that
        operations involving rows in a data structure or similar object do
        not exceed its boundaries.

        Args:
            row (int): The row index to validate.
        Returns:
            bool: True if the row index is valid, False otherwise.
        """
        return 0 <= row < self.num_rows

    def require_valid_row(self, row):
        """
        Checks whether a given row is valid and raises an exception if it is not.

        This method ensures the provided row input meets validation criteria.
        If the row is deemed invalid, an IndexError is raised with a detailed
        message about the invalid row.

        Args:
            row (int): The row index to validate.
        Raises:
            IndexError: If the row index is invalid.
        """
        if not self.is_valid_row(row):
            raise IndexError(f"Invalid row: {row}")

    def is_valid_col(self, col):
        """
        Checks whether the provided column index is valid within the range of allowed
        columns.

        This method determines if the supplied column index falls within the valid
        bounds of 0 (inclusive) and the total number of columns (`self.num_cols`)
        (exclusive).

        Args:
            col (int): The column index to validate.
        Returns:
            bool: True if the column index is valid, False otherwise.
        """
        return 0 <= col < self.num_cols

    def require_valid_col(self, col):
        """
        Validates the given column to ensure it meets specified criteria.

        This method checks whether the provided column is valid based on custom
        validation logic. If it is not valid, an IndexError is raised.

        Args:
            col: The column to validate.
        Raises:
            IndexError: If the column is invalid.
        """
        if not self.is_valid_col(col):
            raise IndexError(f"Invalid col: {col}")

    def is_valid_lin(self, lin):
        """
        Checks if the given linear index is valid within the defined grid dimensions.

        Args:
            lin: int. A linear index to be checked for validity.

        Returns:
            bool. True if the linear index is valid within the grid dimensions,
            False otherwise.
        """
        return 0 <= lin < self.num_rows * self.num_cols

    def require_valid_lin(self, lin):
        if not self.is_valid_lin(lin):
            raise IndexError(f"Invalid linear index: {lin}")

    def linear_index(self, row: int, col: int) -> int:
        self.require_valid_row(row)
        self.require_valid_col(col)

        return row * self.num_cols + col

    def row_by_lin(self, linear_index: int) -> int:
        """
        Computes the row index in a 2D grid given a linear index.

        This method calculates the corresponding row for the provided linear
        index in a grid layout where the number of columns is predetermined.

        Args:
            linear_index (int): The linear index for which the row number
                in the grid should be calculated.

        Returns:
            int: The row index in the 2D grid that corresponds to the
            provided linear index.
        """
        self.require_valid_lin(linear_index)

        return linear_index // self.num_cols

    def col_by_lin(self, linear_index: int) -> int:
        """
        Converts a linear index to its corresponding column index in a 2D grid.

        This function computes the column index in a 2D grid based on a given linear
        index. The 2D grid dimensions are defined by `self.num_rows` and `self.num_cols`.

        Args:
            linear_index (int): The linear index to be converted. Must be a positive
                integer within the range of [0, self.num_rows * self.num_cols).

        Returns:
            int: The column index corresponding to the provided linear index.

        Raises:
            IndexError: If the provided linear index is less than 0 or greater than
                or equal to the total number of elements in the grid.
        """
        if linear_index < 0 or linear_index >= self.num_rows * self.num_cols:
            raise IndexError(f"Invalid linear index: {linear_index}")
        return linear_index % self.num_cols

    def cell_by_lin(self, linear_index: int) -> TC:
        """
        Fetches a cell by its linear index in the grid.

        A grid is conceptualized as a linear contiguous array of cells, where
        the cells are assigned a unique linear index based on their position.
        The `cell_by_lin` method maps a given linear index to the corresponding
        cell in the grid. If the provided index is out of bounds, an
        `IndexError` is raised.

        Args:
            linear_index (int): The linear index of the desired cell.

        Returns:
            TC: The cell corresponding to the given linear index.

        Raises:
            IndexError: If the linear index is out of the valid range.
        """
        if linear_index < 0 or linear_index >= self.num_rows * self.num_cols:
            raise IndexError(f"Invalid linear index: {linear_index}")
        return self._cells[linear_index]

    def cell_by_row_col(self, row: int, col: int) -> TC:
        """
        Retrieves the element located at the specified row and column indices.

        This method determines and returns the cell at the given row and column indices.
        If the provided indices are out of bounds (negative or exceed matrix dimensions),
        an IndexError is raised.

        Args:
            row (int): The row index of the desired cell.
            col (int): The column index of the desired cell.

        Raises:
            IndexError: If the specified row or column index is invalid.

        Returns:
            TC: The cell located at the given row and column indices.
        """
        if row < 0 or col < 0 or row >= self.num_rows or col >= self.num_cols:
            raise IndexError(f"Invalid row/col: {row}/{col}")
        return self._cells[self.linear_index(row, col)]

    def __setitem__(self, rowcolslice, value: Sequence[Sequence[TC]] | Iterable[TC]) -> None:
        rowslice, colslice = slice_2d_recognition(rowcolslice)
        row_start, row_end, row_step = slice_parsing(rowslice, self.num_rows)
        col_start, col_end, col_step = slice_parsing(colslice, self.num_cols)

        if isinstance(value, Sequence) and isinstance(value[0], Sequence):
            if not len(value) == (row_end - row_start + (row_step - 1)) // row_step:
                raise ValueError("Row count of value does not match slice")
            for row_index, row in value:
                if not len(row) == (col_end - col_start + (col_step - 1)) // col_step:
                    raise ValueError("Column count of value row does not match slice")
            for row_index, row in value:
                for col_index, cell_value in row:
                    self._cells[self.linear_index(row_start + row_index * row_step, col_start + col_index * col_step)] = cell_value
            return

        aslist=list(value)
        if not len(aslist) == max(0,
            ((row_end - row_start + (row_step - 1)) // row_step)
            * ((col_end - col_start + (col_step - 1)) // col_step)
        ):
            raise ValueError("Value length does not match slice")

        for row in range(row_start, row_end, row_step):
            for col in range(col_start, col_end, col_step):
                self._cells[self.linear_index(row, col)] = aslist.pop(0)

    def __getitem__(self, rowslice) -> D2Array:
        rowslice, colslice = slice_2d_recognition(rowslice)
        row_start, row_end, row_step = slice_parsing(rowslice, self.num_rows)
        col_start, col_end, col_step = slice_parsing(colslice, self.num_cols)
        return self.slice_array(row_start, row_end, row_step, col_start, col_end, col_step)

    def slice_array(
        self,
        row_start: int, row_end: int, row_step: int,
        col_start: int, col_end: int, col_step: int
    ) -> D2Array:
        new_num_rows = max(0, (row_end - row_start + (row_step - 1)) // row_step)
        new_num_cols = max(0, (col_end - col_start + (col_step - 1)) // col_step)
        if new_num_rows == 0 or new_num_cols == 0:
            raise ValueError("Resulting slice has zero rows or columns")

        new_cells = []
        for row in range(row_start, row_end, row_step):
            for col in range(col_start, col_end, col_step):
                new_cells.append(self.cell_by_row_col(row, col))
        return D2Array(new_num_rows, new_num_cols, new_cells)


    def __iter__(self):
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                yield self.cell_by_row_col(row, col)

    def row_iterator(self, row: int) -> Generator[TC, None, None]:
        self.require_valid_row(row)
        for col in range(self.num_cols):
            yield self.cell_by_row_col(row, col)

    def col_iterator(self, col: int) -> Generator[TC, None, None]:
        self.require_valid_col(col)
        for row in range(self.num_rows):
            yield self.cell_by_row_col(row, col)

    def first_diagonal(self) -> int:
        """
        Returns the index of the first diagonal in the 2D array.

        The first diagonal is defined as the diagonal that starts from the
        top-left corner of the array and extends to the bottom-right corner.
        In a 2D array, the index of the first diagonal is always 0.

        Returns:
            int: The index of the first diagonal, which is always 0.
        """
        return 0

    def min_diagonal(self) -> int:
        """
        Returns the minimum diagonal index of the 2D array.

        The minimum diagonal index is calculated as the negative of the number
        of rows minus one. This represents the lowest diagonal in the array,
        which starts from the bottom-left corner and extends to the top-right corner.

        Returns:
            int: The minimum diagonal index.
        """
        return -(self.num_rows - 1)

    def max_diagonal(self) -> int:
        """
        Returns the maximum diagonal index of the 2D array.

        The maximum diagonal index is calculated as the number of columns minus one.
        This represents the highest diagonal in the array, which starts from the
        top-right corner and extends to the bottom-left corner.

        Returns:
            int: The maximum diagonal index.
        """
        return self.num_cols - 1

    def diagonal_iterator(self, diagonal: int = 0, wrap_around: bool = False) -> Generator[TC, None, None]:
        """
        Iterates over the elements of a specified diagonal in the 2D array.

        Args:
            diagonal (int): The diagonal index to iterate over. Positive values
                indicate diagonals above the main diagonal, negative values indicate
                diagonals below the main diagonal, and zero indicates the main diagonal.
            wrap_around (bool): If True, the iteration wraps around the array boundaries.

        Yields:
            TC: The elements along the specified diagonal.
        """
        if diagonal >= 0:
            row_start = 0
            col_start = diagonal
        else:
            row_start = -diagonal
            col_start = 0

        row, col = row_start, col_start
        steps = 0
        while True:
            if not wrap_around:
                if row >= self.num_rows or col >= self.num_cols:
                    break
            else:
                row = row % self.num_rows
                col = col % self.num_cols

            yield self.cell_by_row_col(row, col)

            row += 1
            col += 1
            steps += 1

            if wrap_around and steps >= max(self.num_rows, self.num_cols):
                break

    def first_antidiagonal(self) -> int:
        """
        Returns the index of the first antidiagonal in the 2D array.

        The first antidiagonal is defined as the diagonal that starts from the
        top-right corner of the array and extends to the bottom-left corner.
        In a 2D array, the index of the first antidiagonal is always 0.

        Returns:
            int: The index of the first antidiagonal, which is always 0.
        """
        return 0

    def min_antidiagonal(self) -> int:
        """
        Returns the minimum antidiagonal index of the 2D array.

        The minimum antidiagonal index is calculated as the negative of the number
        of columns minus one. This represents the lowest antidiagonal in the array,
        which starts from the bottom-right corner and extends to the top-left corner.

        Returns:
            int: The minimum antidiagonal index.
        """
        return -(self.num_cols - 1)

    def max_antidiagonal(self) -> int:
        """
        Returns the maximum antidiagonal index of the 2D array.

        The maximum antidiagonal index is calculated as the number of rows minus one.
        This represents the highest antidiagonal in the array, which starts from the
        top-left corner and extends to the bottom-right corner.

        Returns:
            int: The maximum antidiagonal index.
        """
        return self.num_rows - 1

    def antidiagonal_iterator(self, antidiagonal: int, wrap_around: bool = False) -> Generator[TC, None, None]:
        """
        Iterates over the elements of a specified antidiagonal in the 2D array.

        Args:
            antidiagonal (int): The antidiagonal index to iterate over. Positive values
                indicate antidiagonals above the main antidiagonal, negative values indicate
                antidiagonals below the main antidiagonal, and zero indicates the main antidiagonal.
            wrap_around (bool): If True, the iteration wraps around the array boundaries.

        Yields:
            TC: The elements along the specified antidiagonal.
        """
        if antidiagonal >= 0:
            row_start = 0
            col_start = self.num_cols - 1 - antidiagonal
        else:
            row_start = -antidiagonal
            col_start = self.num_cols - 1

        row, col = row_start, col_start
        while True:
            if not wrap_around:
                if row >= self.num_rows or col < 0:
                    break
            else:
                row = row % self.num_rows
                col = col % self.num_cols

            yield self.cell_by_row_col(row, col)

            row += 1
            col -= 1

            if wrap_around and (row == row_start and col == col_start):
                break