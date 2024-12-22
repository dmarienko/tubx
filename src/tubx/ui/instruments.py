from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, ClassVar, Iterable, Iterator

from qubx import lookup
from qubx.core.basics import Instrument
from rich.style import Style
from rich.text import Text, TextType
from textual.await_complete import AwaitComplete
from textual.message import Message

# from textual.widgets.tree import Tree, TreeNode
from textual.widgets._tree import TOGGLE_STYLE, Tree, TreeNode

from tubx.data.misc import BinanceMarketsHelper


@dataclass
class InstrumentEntry:
    instrument: Instrument

    def __repr__(self) -> str:
        return self.instrument.symbol


class InstrumentsTree(Tree[InstrumentEntry]):
    class InstrumentSelected(Message):
        def __init__(self, node: TreeNode[InstrumentEntry], instrument: InstrumentEntry) -> None:
            super().__init__()
            self.node: TreeNode[InstrumentEntry] = node
            self.entry = instrument

        @property
        def control(self) -> Tree[InstrumentEntry]:
            return self.node.tree

    def __init__(
        self,
        exchange: str,
        *,
        base_currency: str,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(
            exchange,
            data=None,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self.mh = BinanceMarketsHelper()
        self._base_currency = base_currency
        self._exchange = exchange

    def load(self) -> None:
        sect = self.mh.listings_by_sector(self._base_currency, as_frame=False)

        for s, si in sect.items():
            n_sect = self.root.add(s)
            for i in si.itertuples():
                InstrumentEntry(
                    i.Symbol,
                )
                if instr := lookup.find_symbol(self._exchange, i.Symbol):
                    n_node = n_sect.add(instr.symbol, data=InstrumentEntry(instr), allow_expand=False)

        self.root.expand()

    def _on_tree_node_selected(self, event: Tree.NodeSelected[InstrumentEntry]) -> None:
        event.stop()
        instr_entry = event.node.data
        if instr_entry is None:
            return
        self.post_message(self.InstrumentSelected(event.node, instr_entry))
