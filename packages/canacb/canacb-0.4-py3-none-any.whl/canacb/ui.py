#!/usr/bin/env python3

"""Canadian ACB calculator - user interface controller"""


from copy import deepcopy
import tkinter as tk
from tkinter import ttk, messagebox

from . import cfg
from .pfo import Portfolio
from .info import FAQ, Welcome
from .views import ApplicationMenu
from .views import CommonFrame, BuySellFrame, SplitFrame, AdjustmentFrame
from .views import ResultsFrame, Settings, SymbolChanger


DEFAULT_PREFERENCES = {
    "autosave": 10,  # autosave at 10 minute intervals
    "geometry": "+50+50",  # window towards NW corner of screen
    "theme": "default",  # use default theme
}


# pylint: disable=too-many-instance-attributes, too-many-public-methods
class UserInterface:
    """The application controller"""

    def __init__(self, name_server, preferences, pm, save):
        """Creates the user interface window and starts an event loop."""

        self._name_server = name_server
        self._starting_preferences = deepcopy(preferences)
        for key, value in DEFAULT_PREFERENCES.items():
            if key not in preferences:
                preferences[key] = value
        self._preferences = preferences
        self._pm = pm
        self._save = save

        self._autosave_pending = None
        self._faq = None
        self._settings = None

        self._root = tk.Tk()
        self._root.withdraw()

        if "common" not in preferences and not self._welcome_to_continue():
            self._root.destroy()
            return

        self._layout_externals()
        self._ui_frames = self._layout_internals()
        self.update_results()

        self.set_theme(self._preferences["theme"])
        self._root.deiconify()
        self._root.geometry(self._preferences["geometry"])
        self._root.mainloop()

    def _welcome_to_continue(self):
        """Splashes a welcome window onto the screen temporarily.

        Returns False if user expresses no interest in continuing.

        Tkinter mainloop does not return anything, so we use a trick
        of having the welcome append to a list to indicate whether
        to proceed or not.  A list length of zero means pack it in.
        """
        carry_on = []
        welcome = Welcome(self._root, self.show_faq, carry_on)
        self._root.mainloop()
        welcome.destroy()
        return len(carry_on) > 0

    def _layout_externals(self):
        """Sets initial window frame and binds key controls"""
        self._set_title()

        self._root.protocol("WM_DELETE_WINDOW", self.clean_exit)
        self._root.bind("<Control-q>", self.clean_exit)
        self._root.bind("<Alt-F4>", self.clean_exit)
        self._root.bind("<Control-s>", lambda event: self.save())
        self._root.bind("<F1>", lambda event: self.show_faq())
        self._root.bind(
            "<Return>",
            lambda event: (
                event.widget.invoke()
                if isinstance(event.widget, tk.Button)
                else None
            ),
        )

    def _set_title(self):
        if self.is_dirty():
            self._root.title(cfg.APP_NAME + "*")
        else:
            self._root.title(cfg.APP_NAME)

    def set_theme(self, theme_name):
        """Sets the theme for ttk widgets"""
        ttk.Style().theme_use(theme_name)
        self._preferences["theme"] = theme_name
        self._reveal_dirt()

    def _layout_internals(self):
        """Lays out the widgets inside the user interface."""
        framework = (
            ("menu", ApplicationMenu, 0),
            ("common", CommonFrame, 0),
            ("buysell", BuySellFrame, 0),
            ("split", SplitFrame, 0),
            ("adjust", AdjustmentFrame, 0),
            ("results", ResultsFrame, 1),
        )

        frames = {}
        row = 0
        for name, frame, weight in framework:
            if name not in self._preferences:
                self._preferences[name] = {}
            widget = frame(self._root, self, self._preferences[name])
            widget.grid(row=row, column=0, sticky="nsew")
            self._root.rowconfigure(row, weight=weight)
            row += 1
            frames[name] = widget
        self._root.columnconfigure(0, weight=1)
        return frames

    def is_dirty(self):
        """Returns True if a portfolio or something in the UI has changed"""
        return (
            self._pm.is_dirty()
            or self._preferences != self._starting_preferences
            or self._name_server.is_dirty()
        )

    def clean_exit(self, _event=None):
        """Handles user interface exit cleanly.  Offers to save data if
        anything has been modified during execution.
        """
        if self.is_dirty():
            result = messagebox.askyesnocancel(
                "Exiting ...", "You have unsaved changes.\nSave before exit?"
            )
            if result is None:
                return True
            if result and self.save() is not None:
                return True
        self._root.withdraw()
        self._root.destroy()
        return True

    def change_symbol(self):
        """Allows the user to change a symbol"""
        SymbolChanger(self._root, self)

    def show_faq(self):
        """Pops up the FAQ window (which only gets built on first call)"""
        if self._faq is None:
            self._faq = FAQ(self._root)
        else:
            self._faq.deiconify()

    def show_settings(self):
        """Pops up the Settings window (which only gets built on first call)"""
        if self._settings is None:
            self._settings = Settings(self._root, self, self._preferences)
        else:
            self._settings.deiconify()

    @property
    def pm(self):
        """The portfolio manager"""
        return self._pm

    @property
    def portfolio_name(self):
        """Portfolio name from common frame"""
        return self._ui_frames["common"].portfolio_name

    @property
    def portfolio(self):
        """Portfolio referenced by common frame"""
        return self._ui_frames["common"].portfolio

    @property
    def symbol(self):
        """Symbol from common frame"""
        return self._ui_frames["common"].symbol

    @property
    def settled(self):
        """Settlement date from common frame"""
        return self._ui_frames["common"].settled

    def add_pfo(self, new_pfo):
        """Adds a new empty Portfolio to the portfolio manager."""
        try:
            self._pm[new_pfo] = Portfolio()
            return None
        except (KeyError, ValueError) as exc:
            return str(exc)

    def asset_name(self, symbol):
        """Returns the asset name that the symbol connotes, or "" """
        return self._name_server.get(symbol, "")

    def common_entries_valid(self):
        """Returns True if the CommonFrame thinks its entries are valid"""
        return self._ui_frames["common"].all_entries_valid()

    def edit(self, *args):
        """Facilitates edit of a Transaction"""
        # *** Not implemented at present

    def enable_disable_buttons(self):
        """Enables/disables the buttons in the UI"""
        for frame in self._ui_frames.values():
            if hasattr(frame, "enable_disable_buttons"):
                frame.enable_disable_buttons()

    def on_name_change(self, event=None):
        """Handles a <FocusOut> event from CommonFrame on the asset name"""
        if event is None:
            return False
        new_name = event.widget.get()
        if new_name == self.asset_name(self.symbol):
            return True
        try:
            self._name_server[self.symbol] = new_name
            self.update_results()
        except (KeyError, ValueError):
            return False
        return False

    def portfolio_or_symbol_changed(self):
        """Requests updates in child frames when user's focus moves"""
        self.reset_entry_fields()
        self.update_results()

    def reset_entry_fields(self):
        """Clears the transaction entry fields in the UI"""
        for frame in self._ui_frames.values():
            if hasattr(frame, "reset_entry_fields"):
                frame.reset_entry_fields()

    def update_results(self):
        """Forces an update of the UI's results frame,
        then enables the Save menu item and sets an autosave timer.
        """
        self._ui_frames["results"].update_results()
        self._reveal_dirt()

    def _reveal_dirt(self):
        """If transient state has changed, modifies the window title,
        enables the Save menu item, and starts an autosave timer.
        """
        if self.is_dirty():
            self._set_title()
            self._ui_frames["menu"].update()
            self._start_autosave()

    def save(self):
        """Forwards a save request to the application.

        If the save works, marks the portfolio manager and name server clean.
        If not, pops up a messagebox for the failure.

        Return None if save works, an error message otherwise.
        """
        temp_geometry_preference = self._preferences["geometry"]
        self._preferences["geometry"] = self._root.geometry()
        failure = self._save() if self.is_dirty() else None
        if failure is None:
            self._pm.mark_clean()
            self._name_server.mark_clean()
            self._starting_preferences = deepcopy(self._preferences)
            self._ui_frames["menu"].update()
            self._cancel_autosave()
        else:
            self._preferences["geometry"] = temp_geometry_preference
            if self._autosave_pending is None:
                self._start_autosave()
            messagebox.showerror("Save failed", failure)
        self._set_title()
        return failure

    def set_autosave_interval(self, interval: str):
        """Sets the autosave interval.

        *** DESIGN CHOICE: doesn't alter an already running timer ***
        """
        try:
            interval = int(interval)
            if interval >= 0:
                self._preferences["autosave"] = interval
                self._reveal_dirt()
        except ValueError:
            pass

    def _start_autosave(self):
        """Starts an autosave timer running per user preference.

        User preference is in minutes, while timers operate in millisecons.
        """
        try:
            interval = self._preferences["autosave"] * 60 * 1000
            if interval > 0:
                self._autosave_pending = self._root.after(
                    interval, self._on_autosave_fired
                )
        except (KeyError, ValueError):
            pass

    def _cancel_autosave(self):
        """Cancels a running autosave timer"""
        if self._autosave_pending is not None:
            self._root.after_cancel(self._autosave_pending)
            self._autosave_pending = None

    def _on_autosave_fired(self):
        """Handles an auto save timer firing by requesting a save;
        if the save fails, sets another timer.
        """
        if self.save() is not None:
            self._start_autosave()
        return True
