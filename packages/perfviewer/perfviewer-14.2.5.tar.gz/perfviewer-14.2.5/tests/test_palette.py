from perfview._palettes import STANDARD_PALETTE
from perfview.table import Table


def test_rich_cast():
    table = STANDARD_PALETTE.__rich__()
    assert isinstance(table, Table)
    assert table.row_count == 16
