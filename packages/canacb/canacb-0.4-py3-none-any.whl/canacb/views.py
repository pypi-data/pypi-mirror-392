#!/usr/bin/env python3
# pylint: disable=too-many-ancestors

"""Canadian ACB calculator - user interface components"""


import datetime
import tkinter as tk
from tkinter import messagebox, ttk

from . import cfg
from .tools import fromisoformat, is_isoformat, is_valid_year
from .info import About
from .widgets import TableFrame, ToolTip, ValidatingEntry


class ApplicationMenu(tk.Menubutton):
    """Application menu"""

    def __init__(self, parent, controller=None, preferences=None):
        """Builds the top menu"""
        super().__init__(parent, anchor="w", padx=8)

        self._controller = controller
        self._preferences = preferences

        self._about = About(self)

        menu_items = (
            (
                "command",
                {
                    "label": "Save",
                    "command": controller.save,
                    "state": "disabled",
                },
            ),
            ("command", {"label": "Exit", "command": controller.clean_exit}),
            ("separator", {}),
            (
                "command",
                {
                    "label": "Change symbol...",
                    "command": controller.change_symbol,
                },
            ),
            (
                "command",
                {"label": "Settings...", "command": controller.show_settings},
            ),
            ("separator", {}),
            ("command", {"label": "FAQ", "command": controller.show_faq}),
            ("command", {"label": "About", "command": self.show_about}),
        )

        self._menu = tk.Menu(self, tearoff=0)
        self._image = tk.PhotoImage(file=cfg.MENU_IMAGE)
        self.config(menu=self._menu, image=self._image)

        self._save_index = None
        for index, (kind, args) in enumerate(menu_items):
            self._menu.add(kind, **args)
            if "label" in args and args["label"] == "Save":
                self._save_index = index

    def show_about(self):
        """Pops up the About window near the mouse pointer"""
        self._about.geometry(
            "+{}+{}".format(
                max(0, self.winfo_pointerx() - 20),
                max(0, self.winfo_pointery() - 10),
            )
        )
        self._about.deiconify()

    def update(self):
        """Enables/disables save menu item"""
        if self._save_index is None:
            return
        self._menu.entryconfigure(
            self._save_index,
            state="normal" if self._controller.is_dirty() else "disabled",
        )


class CommonFrame(tk.Frame):
    """A Frame to hold elements common to all other Frames"""

    def __init__(self, parent, controller=None, preferences=None):
        """Lays out the common frame with portfolio/security/date info."""
        super().__init__(parent, padx=4, pady=4)

        self._controller = controller
        self._preferences = preferences

        tk.Label(self, text="Portfolio ").grid(row=0, column=0, padx=2, pady=2)
        self._pfo_box = ttk.Combobox(
            self, values=self._controller.pm.pfo_names, width=12
        )
        self._pfo_box.set(preferences.get("portfolio", ""))
        self._pfo_box.grid(row=0, column=1, sticky="w")
        self._pfo_box.bind("<<ComboboxSelected>>", self._on_pfo_change)
        self._pfo_box.bind("<FocusOut>", self._on_pfo_change)
        ToolTip(
            self._pfo_box,
            text="Pick the portfolio you want, or create one by typing a name",
        )

        tk.Label(self, text="  Symbol").grid(row=0, column=10, padx=5)
        self._symbol_box = ttk.Combobox(self, width=12, justify="center")
        if self.portfolio is not None:
            self._symbol_box.config(values=self.portfolio.holding_names)
            if "symbol" in preferences:
                if preferences["symbol"] in self.portfolio:
                    self._symbol_box.set(preferences["symbol"])
        self._symbol_box.grid(row=0, column=11, padx=2, pady=2, sticky="w")
        self._symbol_box.bind("<<ComboboxSelected>>", self._on_symbol_change)
        self._symbol_box.bind("<FocusOut>", self._on_symbol_change)
        ToolTip(
            self._symbol_box,
            text="Usually a ticker symbol, but use any name you like.",
        )

        tk.Label(self, text="  Name").grid(row=0, column=20, padx=5)
        self._name_entry = tk.Entry(
            self, width=25, justify="left", fg="gray40"
        )
        self._name_entry.insert(0, self._controller.asset_name(self.symbol))
        self._name_entry.grid(row=0, column=21, padx=2, pady=2, sticky="w")
        self._name_entry.bind("<FocusOut>", self._controller.on_name_change)
        ToolTip(
            self._name_entry,
            text="(Optional) Enter/change the asset name tied to this symbol.",
        )

        tk.Label(self, text="  Settled").grid(row=0, column=30, padx=5)
        self._settled_entry = tk.Entry(self, width=10, justify="center")
        self._settled_entry.insert(
            0, preferences.get("settled", datetime.date.today().isoformat())
        )
        self._settled_entry.grid(row=0, column=31, padx=2, pady=2, sticky="w")
        self._settled_entry.bind("<FocusOut>", self._on_date_change)
        ToolTip(
            self._settled_entry,
            text="YYYY-MM-DD\n"
            "Canadian tax law requires use of settlement not trade date.",
        )

        if self.portfolio is None:
            self._symbol_box.config(state="disabled")
            self._settled_entry.config(state="disabled")
            self._pfo_box.select_range(0, tk.END)
            self._pfo_box.focus_set()
        else:
            self._symbol_box.select_range(0, tk.END)
            self._symbol_box.focus_set()

    @property
    def portfolio_name(self):
        """The name of the portfolio currently being used by the UI"""
        name = self._pfo_box.get().strip()
        return name if name != "" else None

    @property
    def portfolio(self):
        """The portfolio currently referenced by the UI"""
        if self.portfolio_name is None:
            return None
        return self._controller.pm[self.portfolio_name]

    @property
    def symbol(self):
        """The symbol currently being used by the UI"""
        return self._symbol_box.get().strip()

    @property
    def settled(self):
        """The settlement date currently being used by the UI"""
        return self._settled_entry.get()

    def all_entries_valid(self):
        """Returns True if pfo/symbol/date entries are all valid"""
        return (
            self.portfolio_name is not None
            and self.symbol != ""
            and self._settled_entry_is_valid()
        )

    def reset_entry_fields(self):
        """Clears the settled date entry field in the UI"""
        self._settled_entry.config(state="normal")
        self._settled_entry.delete(0, tk.END)
        if self.symbol != "":
            last_settled = self.portfolio.last_transaction_date_for(
                self.symbol
            )
            if last_settled is None:
                last_settled = datetime.date.today().isoformat()
            self._settled_entry.insert(0, last_settled)

    def _on_pfo_change(self, event):
        """Handles a switch to a different portfolio,
        possibly creating a new one.
        """
        new_pfo = event.widget.get().strip()
        old_pfo = self._preferences.get("portfolio", "")
        if new_pfo == old_pfo:
            return True
        if new_pfo == "":
            self._pfo_box.set(old_pfo)
            return True
        if new_pfo not in self._controller.pm:
            failure = self._controller.add_pfo(new_pfo)
            if failure is not None:
                messagebox.showerror("Portfolio addition", failure)
                return True
            messagebox.showinfo(
                "Portfolio added", "Portfolio {} created".format(new_pfo)
            )
        self._preferences["portfolio"] = new_pfo
        self._pfo_box.set(new_pfo)
        self._pfo_box["values"] = self._controller.pm.pfo_names
        self._symbol_box.config(state="normal")
        self._symbol_box.delete(0, tk.END)
        self._symbol_box.focus_set()
        self._name_entry.delete(0, tk.END)
        self._controller.portfolio_or_symbol_changed()
        return True

    def _on_symbol_change(self, _event):
        """Informs the controller that the UI symbol field has changed."""
        new_symbol = self.symbol.upper().strip()
        old_symbol = self._preferences.get("symbol", "")
        if new_symbol == old_symbol:
            return True
        if new_symbol == "":
            self._symbol_box.set(old_symbol)
            return True
        if new_symbol not in self.portfolio:
            self._name_entry.delete(0, tk.END)
            failure = self.portfolio.add_holding(new_symbol)
            if failure is not None:
                messagebox.showerror("Symbol addition", failure)
                return True
            messagebox.showinfo(
                "Symbol addition",
                "{} added to {}".format(new_symbol, self.portfolio_name),
            )
        self._preferences["symbol"] = new_symbol
        self._symbol_box.set(new_symbol)
        self._symbol_box["values"] = self.portfolio.holding_names
        self._name_entry.delete(0, tk.END)
        self._name_entry.insert(0, self._controller.asset_name(self.symbol))
        self._controller.portfolio_or_symbol_changed()
        return True

    def _on_date_change(self, _event):
        """Handles a focusout event on the settled Entry."""
        self._settled_entry.config(
            fg="black" if self._settled_entry_is_valid() else "red"
        )
        self._controller.enable_disable_buttons()
        return True

    def _settled_entry_is_valid(self):
        """Returns True if the settled Entry looks like a date, while
        fixing minor format issues."""
        try:
            settled = self._settled_entry.get()
            fixed = fromisoformat(settled).isoformat()
            if settled != fixed:
                self._settled_entry.delete(0, tk.END)
                self._settled_entry.insert(0, fixed)
            return True
        except ValueError:
            return False


class TransactionFrame(tk.LabelFrame):
    """Frame for transaction entries and buttons"""

    def __init__(self, parent, controller, orientation, heading):
        """Lays out a transaction frame."""
        super().__init__(parent, text=heading, fg="maroon")

        self._controller = controller
        self._orientation = orientation
        self._buttons = {}
        self._entries = {}
        self._row = 0
        self._column = 0

    def _bump_grid(self):
        """Updates internal variables so next addition is placed correctly"""
        if self._orientation == tk.HORIZONTAL:
            self._column += 1
        else:
            self._row += 1

    def add_label(self, text):
        """Adds a Label to the frame"""
        tk.Label(self, text=text).grid(row=self._row, column=self._column)
        self._bump_grid()

    def add_button(self, name, invoke):
        """Adds a Button to the frame"""
        self._buttons[name] = tk.Button(self, text=name, command=invoke)
        self._buttons[name].grid(
            row=self._row, column=self._column, padx=10, pady=5
        )
        self._bump_grid()

    def add_validating_entry(self, name, optional, test):
        """Adds a ValidatingEntry to the frame"""
        self._entries[name] = ValidatingEntry(
            self,
            optional,
            test,
            self.enable_disable_buttons,
            width=10,
            justify="right",
        )
        self._entries[name].grid(
            row=self._row, column=self._column, padx=2, pady=2
        )
        self._bump_grid()

    def enable_disable_buttons(self):
        """Enables frame's buttons if all fields look valid,
        disables if there are obvious problems.
        """
        state = "normal" if self.all_entries_valid() else "disabled"
        for button in self._buttons.values():
            button.config(state=state)

    def all_entries_valid(self):
        """Returns True if all entries in this frame AND the control
        frame are valid.
        """
        for entry in self._entries.values():
            if not entry.is_valid():
                return False
        return self._controller.common_entries_valid()

    def reset_entry_fields(self):
        """Clears the entry fields in this frame."""
        for entry in self._entries.values():
            entry.delete(0, tk.END)


class BuySellFrame(TransactionFrame):
    """Frame to solicit buy and sell transactions"""

    def __init__(self, parent, controller=None, _preferences=None):
        """Lays out the buy/sell frame."""
        super().__init__(
            parent, controller, tk.HORIZONTAL, "Purchases / sales"
        )

        self.add_label("Shares")
        self.add_validating_entry("shares", False, lambda v: float(v) > 0.0)
        self.add_label("   Price")
        self.add_validating_entry("price", True, lambda v: float(v) > 0.0)
        self.add_label("   Fee")
        self.add_validating_entry("fee", True, lambda v: float(v) >= 0.0)
        ToolTip(self._entries["fee"], text="Commission or fee")
        self.add_label("   Amount")
        self.add_validating_entry("amount", True, lambda v: float(v) > 0.0)
        ToolTip(
            self._entries["amount"],
            text="Total trade amount; can override price if provided",
        )
        self._entries["amount"].bind("<FocusOut>", self._handle_amount_set)
        self.add_label("   F/X")
        self.add_validating_entry("fx", True, lambda v: float(v) > 0.0)
        ToolTip(
            self._entries["fx"],
            text="Supply an exchange rate if trading in foreign currency",
        )
        self.add_label("      ")
        self.add_button("Buy", lambda: self.trade(controller.portfolio.buy))
        ToolTip(
            self._buttons["Buy"],
            text="For reinvested distributions too!",
        )
        self.add_button("Sell", lambda: self.trade(controller.portfolio.sell))
        self.enable_disable_buttons()

    def _handle_amount_set(self, _event=None):
        if self._entries["amount"].get() != "":
            self._entries["price"].delete(0, tk.END)
        return True

    def all_entries_valid(self):
        """Returns True if all entries in this frame AND the common
        frame are valid. More complicated for a buy/sell because the
        price and amount fields are derivable from one another, so
        we really only need one or the other, but neither is no good.
        """
        return super().all_entries_valid() and (
            self._entries["price"].get() != ""
            or self._entries["amount"].get() != ""
        )

    def trade(self, func):
        """Forwards a Buy or Sell button press to the portfolio."""
        symbol = self._controller.symbol
        try:
            price = self._entries["price"].get().strip()
            price = None if price == "" else float(price)
            fee = self._entries["fee"].get().strip()
            fee = None if fee == "" else float(fee)
            amount = self._entries["amount"].get().strip()
            amount = None if amount == "" else float(amount)
            fx_rate = self._entries["fx"].get().strip()
            fx_rate = None if fx_rate == "" else float(fx_rate)
            fail = func(
                symbol,
                self._controller.settled,
                float(self._entries["shares"].get()),
                price,
                fee,
                amount,
                fx_rate,
            )
        except ValueError as exc:
            messagebox.showerror("Input Error", str(exc))
            return
        if fail is not None:
            messagebox.showerror("Input Error", fail)
            return
        self._controller.update_results()


class SplitFrame(TransactionFrame):
    """Frame to solicit split transactions"""

    def __init__(self, parent, controller=None, _preferences=None):
        """Lays out the split frame."""
        super().__init__(
            parent, controller, tk.HORIZONTAL, "Splits / consolidations"
        )

        self.add_label("Receive")
        self.add_validating_entry(
            "multiplier", False, lambda v: float(v) > 0.0
        )
        self.add_label(" new for ")
        self.add_validating_entry("divisor", False, lambda v: float(v) > 0.0)
        self.add_label(" old     ")
        self.add_button("Split", self.split)
        ToolTip(
            self._buttons["Split"],
            text="E.g. 2 new for 1 old (Royal Bank 2000 & 2006), or "
            "1 new for 10 old (Nortel 2006)",
        )
        self.enable_disable_buttons()

    def split(self):
        """Forwards a Split button press to the portfolio manager."""
        symbol = self._controller.symbol
        try:
            fail = self._controller.portfolio.split(
                symbol,
                self._controller.settled,
                float(self._entries["multiplier"].get()),
                float(self._entries["divisor"].get()),
            )
        except ValueError:
            messagebox.showerror("Input Error", "Check your input fields")
            return
        if fail is not None:
            messagebox.showerror("Input Error", fail)
            return
        self._controller.update_results()


class AdjustmentFrame(TransactionFrame):
    """Frame to solicit ACB adjustment transactions"""

    def __init__(self, parent, controller=None, _preferences=None):
        """Lays out the adjustments frame."""
        super().__init__(parent, controller, tk.HORIZONTAL, "Adjustments")

        self.add_label("Adjustment amount")
        self.add_validating_entry("amount", False, lambda v: float(v) > 0.0)
        self.add_label("   F/X")
        self.add_validating_entry("fx", True, lambda v: float(v) > 0.0)
        ToolTip(
            self._entries["fx"],
            text="Supply an exchange rate if adjustment in foreign currency",
        )
        self.add_label("   Memo")
        self.add_validating_entry("memo", True, lambda v: True)
        self._entries["memo"].configure(width=20)
        ToolTip(
            self._entries["memo"],
            text="Add something descriptive, e.g. RoC or Phantom Gain",
        )
        self.add_label("      ")
        self.add_button("Reduce ACB", lambda: self.adjust_acb(-1.0))
        ToolTip(
            self._buttons["Reduce ACB"],
            text="E.g. a distribution that contains "
            "return of capital reduces ACB; common for REITs and ETFs",
        )
        self.add_button("Increase ACB", lambda: self.adjust_acb(1.0))
        ToolTip(
            self._buttons["Increase ACB"],
            text="E.g. a phantom distribution from an ETF, usually a "
            "reinvested capital gains dividend that is immediately "
            "consolidated to avoid affecting share count",
        )
        self.enable_disable_buttons()

    def adjust_acb(self, sign):
        """Forwards user cost base adjustment request to portfolio
        manager, then updates the visible history or reports an error.

        Arguments:
            sign (float) - +1.0 for acb increase, -1.0 for decrease
        """
        symbol = self._controller.symbol
        fx_rate = self._entries["fx"].get().strip()
        fx_rate = None if fx_rate == "" else float(fx_rate)
        try:
            fail = self._controller.portfolio.adjust(
                symbol,
                self._controller.settled,
                sign * float(self._entries["amount"].get()),
                fx_rate,
                self._entries["memo"].get(),
            )
        except ValueError as exc:
            fail = str(exc)

        if fail is not None:
            messagebox.showerror("Input Error", fail)
            return
        self._controller.update_results()


class ResultsTab(tk.Frame):
    """Base class Frame inside a Notebook tab"""

    _COLUMNS = ()

    def __init__(self, parent, controller, preferences):
        """Creates the frame."""
        super().__init__(parent)

        self._parent = parent
        self._controller = controller
        self._preferences = preferences

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self._table = TableFrame(self, self._COLUMNS)
        self._table.grid(row=0, column=0, sticky="nsew")

    @property
    def title(self):
        """Generates a title"""
        return NotImplemented

    def export_contents(self):
        """Exports table contents to clipboard."""
        self._table.export_contents()

    def treeview_contents(self):
        """Retrieves contents suitable for treeview from portfolio"""
        return NotImplemented

    def update_results(self):
        """Forwards an update request to the TableFrame."""
        self._table.update_contents()


class HistoryFrame(ResultsTab):
    """Frame to display the transaction history of a holding"""

    _COLUMNS = (
        ("Settled", "center", "Settled", 90, 0),
        ("Description", "w", "Description", 400, 1),
        ("Shares", "e", "Shares", 80, 0),
        ("Total Cost", "e", "Total\n Cost", 90, 0),
        ("Average Cost", "e", "Average\n   Cost", 90, 0),
        ("Gain/Loss", "e", "Capital\n  Gain", 90, 0),
    )

    def __init__(self, parent, controller, preferences):
        """Creates the frame."""
        super().__init__(parent, controller, preferences)
        self._table.add_handler("<Delete>", self._on_delete)
        self._table.add_handler("<Double-Button-1>", self._on_double_click)

    @property
    def title(self):
        """Generates a title"""
        symbol = self._controller.symbol
        if symbol is None or len(symbol) == 0:
            return "  Transactions  "
        return "  Transactions in {}  ".format(symbol)

    def _on_delete(self, _event=None):
        """Forwards transaction deletion request to the portfolio"""
        if len(self._table.selected_rows) == 0:
            return True
        if len(self._table.selected_rows) > 1:
            if not messagebox.askyesno(
                "Confirmation",
                "You're requesting deletion of multiple transactions. "
                "Are you sure?",
            ):
                return True
        self._controller.portfolio.cancel_transactions(
            self._controller.symbol,
            self._table.total_rows,
            self._table.selected_rows,
        )
        self._controller.update_results()
        return True

    def _on_double_click(self, _event=None):
        """Initiates edit of first selected transaction"""
        if len(self._table.selected_rows) >= 1:
            self._controller.edit(
                self._table.total_rows,
                self._table.selected_rows,
            )
        return True

    def treeview_contents(self):
        """Retrieves contents suitable for treeview from portfolio"""
        symbol = self._controller.symbol
        if symbol == "":
            return []
        return self._controller.portfolio.view_transactions(symbol)


class PositionFrame(ResultsTab):
    """Displays a portfolio position on a selected date"""

    _COLUMNS = (
        ("Symbol", "center", "Symbol", 90, 0),
        ("Name", "w", "Name", 400, 1),
        ("Shares", "e", "Shares", 80, 0),
        ("Total Cost", "e", "Total\n Cost", 90, 0),
        ("Average Cost", "e", "Average\n   Cost", 90, 0),
    )

    def __init__(self, parent, controller, preferences):
        super().__init__(parent, controller, preferences)

        as_of = preferences.get("as_of", "")
        try:
            fromisoformat(as_of, strict=True)
        except (TypeError, ValueError):
            as_of = datetime.date.today().isoformat()
            self._preferences["as_of"] = as_of
        self._table.add_picker(is_isoformat, "  As of  ", as_of, "YYYY-MM-DD")

    @property
    def title(self):
        """Generates a title"""
        as_of = self._table.picker_contents
        if is_isoformat(as_of):
            if as_of != "":
                as_of = " @ {}".format(as_of)
        else:
            as_of = " @ ????"
        pfo = self._controller.portfolio_name or ""
        return "  {} Positions{}  ".format(pfo, as_of)

    def picker_changed(self):
        """Catches loss of focus"""
        if is_isoformat(self._table.picker_contents):
            self._preferences["as_of"] = self._table.picker_contents
        self._controller.update_results()

    def treeview_contents(self):
        """Retrieves contents suitable for treeview from portfolio"""
        as_of = self._table.picker_contents
        if is_isoformat(as_of) and self._controller.portfolio is not None:
            contents = self._controller.portfolio.view_holdings(as_of)
        else:
            contents = []
        for record in contents:
            record.insert(1, self._controller.asset_name(record[0]))
        return contents


class Schedule3Frame(ResultsTab):
    """Displays Schedule 3 data for a selected year"""

    _COLUMNS = (
        ("Shares", "e", "Shares", 80, 0),
        ("Symbol", "center", "Symbol", 90, 0),
        ("Name", "w", "Name", 320, 1),
        ("Acquired", "center", "   Year\nacquired", 100, 0),
        ("Proceeds", "e", "Proceeds", 90, 0),
        ("ACB", "e", "Adjusted\ncost base", 90, 0),
        ("Expenses", "e", "Outlays/\nexpenses", 90, 0),
        ("Gain", "e", "Gain/\n loss", 90, 0),
    )

    def __init__(self, parent, controller, preferences):
        super().__init__(parent, controller, preferences)

        year = preferences.get("year", "")
        if not is_valid_year(year):
            year = str(datetime.date.today().year)
            self._preferences["year"] = year
        self._table.add_picker(is_valid_year, "  Year  ", year)

    @property
    def title(self):
        """Generates a title"""
        year = self._table.picker_contents
        if is_valid_year(year):
            if year != "":
                year = " ({})".format(year)
        else:
            year = " (????)"
        return "  Schedule 3{}  ".format(year)

    def picker_changed(self):
        """Catches loss of focus"""
        if is_valid_year(self._table.picker_contents):
            self._preferences["year"] = self._table.picker_contents
        self._controller.update_results()

    def treeview_contents(self):
        """Retrieves contents suitable for treeview from portfolio"""
        year = self._table.picker_contents
        if is_valid_year(year) and self._controller.portfolio is not None:
            contents = self._controller.portfolio.s3_for(year)
        else:
            contents = []
        for record in contents:
            record.insert(2, self._controller.asset_name(record[1]))
        return contents


class ResultsFrame(tk.Frame):
    """A notebook frame to display views of transaction results"""

    _TABS = (
        ("history", HistoryFrame, "  Transactions  "),
        ("position", PositionFrame, "  Positions  "),
        ("schedule3", Schedule3Frame, "  Schedule 3  "),
    )

    def __init__(self, parent, controller, preferences):
        """Creates the notebook"""
        super().__init__(parent)

        self._parent = parent
        self._controller = controller
        self._preferences = preferences

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self._notebook = ttk.Notebook(self)
        self._notebook.grid(row=0, column=0, padx=2, pady=2, sticky="nsew")
        copy_button = tk.Button(self, relief="flat", command=self._on_copy)
        copy_button.image = tk.PhotoImage(file=cfg.COPY_IMAGE)
        copy_button.config(image=copy_button.image)
        copy_button.grid(row=0, column=0, sticky="ne", padx=5)
        ToolTip(copy_button, text="Table contents -> clipboard")

        self._tabs = []
        for preference_key, cls, label in self._TABS:
            if preference_key not in preferences:
                preferences[preference_key] = {}
            tab = cls(self, controller, preferences[preference_key])
            self._notebook.add(tab, text=label, sticky="nsew")
            self._tabs.append(tab)

    def _on_copy(self):
        """Forwards a clipboard copy request to the current tab"""
        self._tabs[self._notebook.index("current")].export_contents()
        return True

    def update_results(self):
        """Forward an update request to each tab."""
        for tab in self._tabs:
            tab.update_results()
        self.update_tab_labels()

    def update_tab_labels(self):
        """Updates the notebook's tab labels"""
        for index, tab in enumerate(self._tabs):
            self._notebook.tab(index, text=tab.title)


class Settings(tk.Toplevel):
    """A window to facilitate preference changes"""

    def __init__(self, parent, controller, preferences):
        super().__init__(parent)

        self._controller = controller

        theme_names = sorted(ttk.Style().theme_names())
        self.autosave_var = tk.StringVar()
        self.autosave_var.set(preferences["autosave"])
        self.theme_var = tk.StringVar()
        self.theme_var.set(preferences["theme"])

        self.title("Settings")
        cx, cy = self.winfo_pointerxy()
        self.geometry("+{:d}+{:d}".format(cx + 80, cy))
        self.protocol("WM_DELETE_WINDOW", self.withdraw)
        self.bind("<Escape>", lambda e: self.withdraw())

        frame = tk.Frame(self)
        tk.Label(frame, text="Autosave every").grid(row=0, column=0, padx=5)
        tk.Entry(frame, width=3, textvariable=self.autosave_var).grid(
            row=0, column=1
        )
        tk.Label(frame, text="minutes (zero to turn off)").grid(
            row=0, column=2, padx=2, pady=5
        )
        frame.grid(row=0, column=0, padx=2, pady=5, sticky="w")
        frame = tk.Frame(self)
        tk.Label(frame, text="UI theme").grid(row=1, column=0, padx=5)
        combo = ttk.Combobox(
            frame,
            width=10,
            values=theme_names,
            state="readonly",
            textvariable=self.theme_var,
        )
        combo.grid(row=1, column=1, padx=5)
        frame.grid(row=1, column=0, padx=2, pady=5, sticky="w")
        frame = tk.Frame(self)
        tk.Button(frame, text="OK", command=self._on_ok).grid(
            row=0, column=0, padx=10
        )
        tk.Button(frame, text="Cancel", command=self.withdraw).grid(
            row=0, column=1, padx=10
        )
        frame.grid(row=2, column=0, padx=2, pady=10)

    def _on_ok(self, _event=None):
        self._controller.set_theme(self.theme_var.get())
        self._controller.set_autosave_interval(self.autosave_var.get())
        self.withdraw()
        return True


class SymbolChanger(tk.Toplevel):
    """A window to facilitate symbol changes"""

    def __init__(self, parent, controller):
        super().__init__(parent)

        self._controller = controller
        if self._controller.portfolio is None:
            self.destroy()
            return

        self.title("Symbol change")
        cx, cy = self.winfo_pointerxy()
        self.geometry("+{:d}+{:d}".format(cx + 80, cy))
        self.bind("<Escape>", lambda e: self.destroy())

        tk.Label(self, text="Old symbol").grid(
            row=0, column=0, padx=5, sticky="e"
        )
        self._old = ttk.Combobox(
            self,
            width=12,
            values=controller.portfolio.holding_names,
            state="readonly",
        )
        self._old.grid(row=0, column=1, padx=15, pady=5, sticky="w")
        tk.Label(self, text="New symbol").grid(
            row=1, column=0, padx=5, sticky="e"
        )
        self._new = tk.Entry(self, width=12)
        self._new.grid(row=1, column=1, padx=15, pady=5, sticky="w")
        button_frame = tk.Frame(self)
        button_frame.grid(row=10, column=0, columnspan=2)
        tk.Button(button_frame, text="Ok", command=self._on_ok).grid(
            row=10, column=0, padx=8, pady=15, sticky="e"
        )
        tk.Button(button_frame, text="Cancel", command=self.destroy).grid(
            row=10, column=1, padx=8, pady=15, sticky="w"
        )

    def _on_ok(self):
        """Processes push of OK button"""
        old = self._old.get()
        new = self._new.get().upper().strip()
        if new == "":
            messagebox.showerror("Error", "New symbol cannot be blank")
            return True
        if new in self._controller.portfolio:
            messagebox.showerror("Error", "New symbol already in use")
            return True
        self._controller.portfolio.change_symbol(old, new)
        self.destroy()
        return True
