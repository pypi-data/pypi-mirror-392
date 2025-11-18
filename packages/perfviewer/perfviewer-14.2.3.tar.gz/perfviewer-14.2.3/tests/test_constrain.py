from perfview.console import Console
from perfview.constrain import Constrain
from perfview.text import Text


def test_width_of_none():
    console = Console()
    constrain = Constrain(Text("foo"), width=None)
    min_width, max_width = constrain.__rich_measure__(
        console, console.options.update_width(80)
    )
    assert min_width == 3
    assert max_width == 3
