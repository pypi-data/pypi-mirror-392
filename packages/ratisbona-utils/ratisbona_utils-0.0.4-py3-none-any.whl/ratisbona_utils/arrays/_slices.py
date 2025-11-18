
def slice_2d_recognition(aslice: slice | int | tuple) -> tuple[slice | int, slice | int | None]:
    """
    Utility routine for writing __getent__ methods, in case they need to handle 2D slicing.

    Example:

        ```python
        def __getitem__(self, aslice):
        rowslice, colslice = slice_2d_recognition(aslice)
        ...
        ```

        would handle element access like:
        - array[2, 3]: Row 2, Column 3
        - array[2:5, 1:4]: Rows 2 to 4, Columns 1 to 3
        - array[2]: Row 2, all columns
        - array[:, 3]: All rows, Column 3

        The first value is thereby always the rowslice, the second the colslice (or None if not provided).

    Args:
        aslice: The slice as obtained from __getitem__. Can be a slice, int, or tuple of maximum 2 slices/ints.

    Returns:
        A tuple of (rowslice, colslice). If aslice is not a tuple, colslice is None.

    """
    # Handle tuple slices for rows and columns
    if isinstance(aslice, tuple):
        if len(aslice) != 2:
            raise ValueError(f"Invalid rowslice tuple length: {len(aslice)}")
        colclice = aslice[1]
        rowslice = aslice[0]
    else:
        colclice = None
        rowslice = aslice
    return rowslice, colclice


def slice_parsing(row_or_col_slice: slice | int | None, maxval: int) -> tuple[int, int, int]:
    """
    Parses a slice or integer into start, end, and step values.
    Args:
        row_or_col_slice:
            The slice or integer to parse, as getitem might have obtained it. Or for a 2d array, one of the two
            slices. Meybe use slice_2d_recognition first.
            Argument might be None, in which case the full range is assumed. Useful for not having to check for None
            in return values of slice_2d_recognition, for example.
        maxval: The maximum value for the slice end, one bigger as the greatest valid index (num_rows or num_cols).

    Returns:
        A tuple of (start, end, step) integers.
    """
    start, end, step = 0, maxval, 1
    if row_or_col_slice is None:
        pass
    elif isinstance(row_or_col_slice, slice):
        if row_or_col_slice.start is not None:
            start = row_or_col_slice.start
        if row_or_col_slice.stop is not None:
            end = row_or_col_slice.stop
        if row_or_col_slice.step is not None:
            step = row_or_col_slice.step
    elif isinstance(row_or_col_slice, int):
        start = row_or_col_slice
        end = row_or_col_slice + 1
    else:
        raise ValueError(f"Invalid slice: {row_or_col_slice}")
    return start, end, step

def is_valid_slice(start, end, step, maxlength) -> tuple[bool, str]:
    """
    Validates the slice parameters.
    Args:
        start: The start index.
        end: The end index.
        step: The step size.

    Returns:
        True if the slice parameters are valid, False otherwise.
    """
    if step == 0:
        return False, "Step cannot be zero."
    if step > 0 and start >= end:
        return False, "Start must be less than end for positive step."
    if step < 0 and start <= end:
        return False, "Start must be greater than end for negative step."
    return True, ""

def ensure_valid_slice(start, end, step, maxlength):
    """
    Ensures the slice parameters are valid.
    Args:
        start: The start index.
        end: The end index.
        step: The step size.

    Raises:
        ValueError: If the slice parameters are invalid.
    """
    is_valid, message = is_valid_slice(start, end, step, maxlength)
    if not is_valid:
        raise ValueError(f"Invalid slice parameters: {message}")