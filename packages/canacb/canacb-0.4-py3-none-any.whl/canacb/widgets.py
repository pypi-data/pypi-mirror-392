#!/usr/bin/env python3

"""tkinter based widgets"""


import tkinter as tk
from tkinter import ttk


class TableFrame(tk.Frame):
    """A ttk.Treeview with some bells and whistles

    Provides a Treeview with a vertical Scrollbar attached, plus ...
        - contents exportable to the clipboard, tab delimited
        - an optional picker Entry at the top to facilitate content
            customization by the parent (which, if present, must have
            methods to allow verifying what the user types in the Entry)
        - an ability to pass on either Delete keypresses or double clicks
            to the parent, with an argument of what rows are selected
    """

    def __init__(self, parent, columns):
        """Creates the table view, attaches a scrollbar, leaves room
        for a picker."""
        super().__init__(parent)

        self._parent = parent
        self._columns = columns

        self._concordance = {}

        self.rowconfigure(10, weight=1)
        self.columnconfigure(0, weight=1)

        self._picker = None

        self._tree = ttk.Treeview(self, columns=[item[0] for item in columns])
        self._tree.grid(row=10, column=0, sticky="nsew")
        self._tree.tag_configure("even", background="gray95")

        # Hide the tree column and set a two line heading.
        # Tkinter magic. Don't mess with this.
        self._tree.column("#0", width=0, minwidth=0, stretch=0)
        self._tree.heading("#0", text="\n")
        ttk.Style().configure("Treeview.Heading", foreground="black")

        for name, align, heading, width, stretch in columns:
            self._tree.column(name, anchor=align, width=width, stretch=stretch)
            self._tree.heading(name, text=heading)

        self._tree.bind(
            "<Escape>",
            lambda event: self._tree.selection_remove(
                event.widget.selection()
            ),
        )

        y_scroll = ttk.Scrollbar(self, command=self._tree.yview)
        self._tree["yscrollcommand"] = y_scroll.set
        y_scroll.grid(row=10, column=1, sticky="ns")

    @property
    def picker_contents(self):
        """The contents of the picker Entry"""
        return self._picker.get()

    def add_handler(self, event, handler):
        """Lets parent bind an event on the tree."""
        self._tree.bind(event, handler)

    def add_picker(self, test, label=None, start_text=None, tooltip_text=None):
        """Adds a "picker" above the treeview"""
        frame = tk.Frame(self)
        frame.grid(row=0, column=0, sticky="w")
        tk.Label(frame, text=label).grid(row=0, column=0, padx=5, sticky="w")
        self._picker = ValidatingEntry(
            frame,
            True,
            test,
            self._on_picker_change_finished,
            when="focusout",
            width=10,
            justify="center",
        )
        self._picker.insert(0, start_text)
        self._picker.grid(row=0, column=1, padx=2, pady=2, sticky="w")
        if tooltip_text is not None:
            ToolTip(self._picker, text=tooltip_text)

    def _on_picker_change_finished(self, _event=None):
        """Handles finished picker change by updating tree contents and
        informing parent.
        """
        self.update_contents()
        self._parent.picker_changed()
        return True

    def export_contents(self):
        """Copies the treeview's headings and contents to the clipboard"""
        self.clipboard_clear()
        if hasattr(self._parent, "title"):
            self.clipboard_append(self._parent.title + "\n\n")
        self.clipboard_append(
            "\t".join([column[0] for column in self._columns]) + "\n"
        )
        for iid in self._tree.get_children():
            values = self._tree.item(iid, "values")
            self.clipboard_append("\t".join(values) + "\n")
        return True

    def update_contents(self):
        """Replaces the contents of the treeview."""

        self._tree.delete(*self._tree.get_children())
        self._concordance.clear()

        even = False
        contents = self._parent.treeview_contents()
        for i, line in enumerate(contents):
            tags = "even" if even else "odd"
            even = not even
            iid = self._tree.insert("", "end", values=line, tags=tags)
            self._concordance[iid] = i
        if len(contents) > 0:
            self._tree.see(iid)

    def _inform_parent(self, _event=None, parent_handler=None):
        """Informs parent handler with list of indices of selections"""
        if parent_handler is None:
            return False
        parent_handler(self.total_rows, self.selected_rows)
        return True

    @property
    def selected_rows(self):
        """List of indices for the rows selected in the table"""
        return [self._concordance[iid] for iid in self._tree.selection()]

    @property
    def total_rows(self):
        """Total number of rows in the table"""
        return len(self._concordance)


class ToolTip:
    """A tooltip class that pops up when the mouse is over the widget.

    2014-09-09: (vegaseat) www.daniweb.com/programming/
        software-development/code/484591/a-tooltip-class-for-tkinter
    2016-03-25: (Victor Zaccardo) include a wait time
    2024-05-01: (Norbert Schlenker) create tooltip window only once
    """

    _WAIT_TIME = 800  # milliseconds
    _WRAP_LENGTH = 200  # pixels
    _X_OFFSET = +25  # x offset from top left of widget
    _Y_OFFSET = +25  # y offset from top left of widget

    def __init__(self, widget, text="Lorem ipsum dolor sit amet"):
        """Creates a tooltip for a widget."""
        self.widget = widget
        widget.bind("<Enter>", self.enter)
        widget.bind("<Leave>", self.leave)
        widget.bind("<ButtonPress>", self.leave)
        self.tip = tk.Toplevel(widget)
        self.tip.withdraw()
        self.tip.wm_overrideredirect(True)
        label = tk.Label(
            self.tip,
            text=text,
            justify="left",
            background="#ffffff",
            relief="solid",
            borderwidth=1,
            wraplength=self._WRAP_LENGTH,
        )
        label.pack(ipadx=3)
        self._id = None

    def enter(self, _event=None):
        """Fired on mouse entry to widget."""
        self.schedule()

    def leave(self, _event=None):
        """Fired on mouse leaving widget."""
        self.unschedule()
        self.hidetip()

    def schedule(self):
        """Schedules a wakeup call to show tip."""
        self.unschedule()
        self._id = self.widget.after(self._WAIT_TIME, self.showtip)

    def unschedule(self):
        """Cancels the wakeup call."""
        if self._id is None:
            return
        self.widget.after_cancel(self._id)
        self._id = None

    def showtip(self, _event=None):
        """Pops up the tooltip near the widget's current position."""
        (x, y, _cx, _cy) = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + self._X_OFFSET
        y += self.widget.winfo_rooty() + self._Y_OFFSET
        self.tip.wm_geometry("+{:d}+{:d}".format(x, y))
        self.tip.deiconify()

    def hidetip(self):
        """Hides the tooltip."""
        self.tip.withdraw()


# pylint: disable=too-many-ancestors
# pylint: disable=too-many-arguments, too-many-positional-arguments
class ValidatingEntry(tk.Entry):
    """A tkinter Entry that validates contents on the fly per supplied test.
    Invalid contents are displayed in red as a visual cue to the user.
    """

    def __init__(self, parent, optional, test, callback, when="all", **kwargs):
        """Instantiates the Entry.

        Arguments:
            parent - the parent widget
            optional - True if a blank entry is to be considered valid
            test - function to be called to test for validity
            callback - function to be called when contents change
            when - when the Entry is to be tested (default is "all")
            kwargs - the usual tk.Entry keyword arguments, passed through
        """
        super().__init__(parent, **kwargs)
        if self.config("validate")[-1] != "none":
            return

        self._optional = optional
        self._test = test
        self._callback = callback

        self._valid = self._is_valid(self.get().strip())

        self.config(
            validate=when, validatecommand=(self.register(self._changed), "%P")
        )
        self.bind("<Return>", lambda event: self._changed(self.get()))

    def _changed(self, text):
        """Updates validity state on tkinter callback when contents change"""
        self._valid = self._is_valid(text)
        self.config(fg="black" if self._valid else "red")
        if self._callback is not None:
            self._callback()
        return True

    def is_valid(self):
        """True if the entry is facially valid"""
        return self._valid

    def _is_valid(self, text):
        """Checks that the provided text satisfies the spec at creation"""
        entry = text.strip()
        if len(entry) == 0:
            return self._optional
        try:
            return self._test(entry)
        except ValueError:
            return False
