import json
import sys
from pathlib import Path

# from asphalt.core import CLIApplicationComponent, Context
# from asphalt.core.cli import run as asphalt_run
import numpy as np
import pandas as pd
from qubx import lookup
from qubx.utils.misc import version

# from textual.layout import WidgetPlacement
from rich.text import Text
from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, HorizontalGroup, VerticalScroll
from textual.reactive import reactive, var
from textual.widgets import Button, DirectoryTree, Footer, Header, Input, Label, Static, Tree
from textual.widgets.tree import TreeNode
from textual_plotext import PlotextPlot

from tubx.ui.instruments import InstrumentsTree


class QubixTerminal(App):
    """Textual Qubix terminal POC."""

    CSS_PATH = "app.tcss"
    BINDINGS = [
        ("s", "toggle_instruments", "Toggle Instruments"),
        ("q", "quit", "Quit"),
    ]
    TITLE = f"Terminal (QUBX {version()})"

    show_tree = var(True)
    path: reactive[str | None] = reactive(None)

    def watch_show_tree(self, show_tree: bool) -> None:
        """Called when show_tree is modified."""
        self.set_class(show_tree, "-show-tree")

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container():
            yield InstrumentsTree("BINANCE.UM", base_currency="USDT", id="tree-view")
            with VerticalScroll(id="main-view"):
                yield PlotextPlot(id="chart")
                yield Static(id="main", expand=True)
            with HorizontalGroup():
                yield Button("Read symbols")
                yield Input(placeholder="Enter command")
        yield Footer()

    @on(Button.Pressed)
    async def on_press(self, event: Button.Pressed) -> None:
        """When the user hits return."""
        main_view = self.query_one("#main-view")
        # event.input.clear()
        # await main_view.mount(Label("BBB"))

        # instrs = lookup.find_instruments("BINANCE.UM")
        # await main_view.mount(Label(",".join([str(i) for i in instrs])))

    @on(Input.Submitted)
    async def on_input(self, event: Input.Submitted) -> None:
        main_view = self.query_one("#main-view")
        event.input.clear()
        await main_view.mount(Label(event.value))

        # await main_view.mount(response := Response())
        # response.anchor()
        # self.send_prompt(event.value, response)

    def on_mount(self) -> None:
        i_tree = self.query_one(InstrumentsTree)
        i_tree = i_tree.focus()
        i_tree.load()

        chart_view = self.query_one("#chart", PlotextPlot)
        chart_view.plt.title("Price")
        chart_view.plt.xlabel("Time")
        chart_view.plt.date_form("Y-m-d H:M")

    async def on_instruments_tree_instrument_selected(self, event: InstrumentsTree.InstrumentSelected) -> None:
        """Called when the user click a file in the directory tree."""
        event.stop()
        main_view = self.query_one("#main-view")
        await main_view.mount(Label(str(event.entry.instrument)))
        chart_view = self.query_one("#chart", PlotextPlot)

        chart_view.plt.clear_data()
        # chart_view.plt.plot(
        #     list(
        #         map(
        #             lambda x: pd.Timestamp(x).strftime("%Y-%m-%d %H:%M"),
        #             pd.date_range("2021-01-01", periods=100, freq="1d").values,
        #         )
        #     ),
        #     (100 + np.random.randn(100).cumsum()).tolist(),
        #     marker="braille",
        # )
        c = 100 + np.random.randn(100).cumsum()
        chart_view.plt.candlestick(
            list(
                map(
                    lambda x: pd.Timestamp(x).strftime("%Y-%m-%d %H:%M"),
                    pd.date_range("2021-01-01", periods=100, freq="1d").values,
                )
            ),
            {
                "Open": (c + 0.5).tolist(),
                "High": (c + 1).tolist(),
                "Low": (c - 1).tolist(),
                "Close": c.tolist(),
            },
        )
        chart_view.plt.title(str(event.entry.instrument))

    def watch_path(self, path: str | None) -> None:
        """Called when path changes."""
        chart_view = self.query_one("#main", Static)
        if path is None:
            chart_view.update("")
            return

        chart_view.update(path)
        self.query_one("#main-view").scroll_home(animate=False)
        self.sub_title = path

    def action_toggle_instruments(self) -> None:
        """Called in response to key binding."""
        self.show_tree = not self.show_tree


def run() -> None:
    QubixTerminal().run()


if __name__ == "__main__":
    run()
