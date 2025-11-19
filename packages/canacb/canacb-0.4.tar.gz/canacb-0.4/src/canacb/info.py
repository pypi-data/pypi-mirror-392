#!/usr/bin/env python3

"""Canadian ACB calculator - user interface information windows"""


import tkinter as tk
from tkinter import ttk, font as tkFont

from . import cfg


class About(tk.Toplevel):
    """Little popup with bare bones identifying information"""

    def __init__(self, parent):
        """Lays out the popup and hides it"""

        super().__init__(parent)
        self.withdraw()
        self.title("About {}".format(cfg.APP_NAME))
        self.protocol("WM_DELETE_WINDOW", self.withdraw)
        self.bind("<Escape>", lambda event: self.withdraw())

        bold_font = tkFont.nametofont("TkTextFont").copy()
        bold_font["weight"] = "bold"

        tk.Label(
            self,
            text="Adjusted cost base tracker for Canadian investors",
            font=bold_font,
        ).grid(row=0, column=0, padx=20, pady=20)
        tk.Label(self, text="Version: {}".format(cfg.APP_VERSION)).grid(
            row=10, column=0, padx=10, pady=0, sticky="w"
        )
        tk.Label(self, text="Author(s): {}".format(cfg.APP_AUTHORS)).grid(
            row=11, column=0, padx=10, pady=0, sticky="w"
        )
        tk.Label(self, text="License: {}".format(cfg.APP_LICENSE)).grid(
            row=12, column=0, padx=10, pady=0, sticky="w"
        )
        tk.Label(self, text="Data file: {}".format(cfg.DATA_FILE)).grid(
            row=13, column=0, padx=10, pady=0, sticky="w"
        )

        tk.Button(self, text="Close", command=self.withdraw).grid(
            row=20, column=0, padx=10, pady=10, sticky="e"
        )


class FAQ(tk.Toplevel):
    """Window to display frequently asked questions"""

    _FAQ = (
        (
            "Why might I need this software?",
            "Since 1972, "
            "Canadian tax law requires declaration of capital gains when you "
            "dispose of a capital asset, so that capital gains taxes can be "
            "assessed.\n\n"
            "It's usually simple to determine what you sold an asset "
            "for, but sometimes not so easy to reconstruct what its cost (in "
            'tax terms, its "adjusted cost base") is if you\'ve bought and '
            "sold over many years.\n\n"
            "Records get lost and memories fade as time goes by. "
            "CAN-ACB can help.",
        ),
        (
            "My investments are all in my RRSP and TFSA. Do I need this?",
            "You don't.\n\n"
            "Adjusted cost base only needs to be tracked for assets "
            "held in taxable accounts and subject to capital gains tax.",
        ),
        (
            "What do I need to record?",
            "Record any transaction that changes the share count of what you "
            "own, as they happen or when you see a change on a statement ...\n"
            "  - Purchases of new shares\n"
            "  - A reinvestment of an income distribution that buys shares\n"
            "  - Inheriting shares from Grandma ... record a purchase at "
            "current market value\n"
            "  - A sale of shares\n"
            "  - A split or consolidation which changes the share count\n\n"
            "There are a few more unusual cases where you should record an "
            '"Adjustment"\n'
            '  - An amount reported in Box 42 of a T3 tax slip is "return '
            'of capital", which reduces ACB. Record these!\n'
            '  - ETFs can pay "phantom dividends", capital gains '
            "dividends which are reinvested but do not change share count. "
            "These increase ACB and should be recorded.",
        ),
        (
            'Why "adjusted" cost base?',
            'For tax purposes, the "cost base" of an asset is what you paid '
            "to acquire it. (In some cases, e.g. for a gift, the cost base is "
            "the fair market value at the time.)\n\n"
            "Things can happen during ownership that change the asset's cost. "
            "Among securities, REITs and ETFs often pay "
            'distributions that are part or all "return of capital".\n\n'
            "Return of capital isn't taxable immediately, but it reduces the "
            '"adjusted" cost base of the asset. '
            "Then, when the asset is sold, the capital "
            "gain will be larger and tax will eventually be collected.",
        ),
        (
            "Won't my broker keep track of this for me?",
            "You wish! Brokers are pretty good these days at keeping track of "
            "purchase cost, but mixed distributions and really ancient "
            "holdings will throw them for a loop.\n\n"
            "In addition, Canadian tax law "
            "says that identical property held in different accounts forms "
            "a single pool with an overall cost. Suppose you hold 200 XYZ at "
            "Broker A that cost you $30 each in 2008 and another 100 XYZ at "
            "Broker B that cost you $90 each in 2019. Today you want to sell "
            "100 for $80.\n\n"
            "Broker A will say you realized a $5000 gain. "
            "Broker B would say it was a $1000 loss.\n\n"
            "CRA insists you use average cost - $50/share - "
            "so your capital gain is $3000 for tax purposes.",
        ),
        (
            "Will this work for property other than securities?",
            "It will, but it's cumbersome and likely overkill for most things."
            "\n\n"
            "You need this kind of recordkeeping where you have multiple "
            "purchases and sales of the same kind of property, at different "
            "time and prices. Anything where you need to know "
            '"how many" at the same time as "how much did they cost," '
            "in order to satisfy tax authorities.\n\n"
            "So stocks. Or bonds. Or Krugerrands.\n\n"
            "Pairs of socks if you like (and are OCD), as long as you invent "
            '"ticker symbols" to distinguish white from black, or Nike from '
            "Gold Toe.",
        ),
        (
            "Do I have to use average cost?",
            "For securities in Canada, yes. It's the law.",
        ),
        (
            "I need FIFO for my US taxes. Will CAN-ACB handle that?",
            "It will not.\n\n"
            "FIFO is more complex to deal with than average cost "
            "and the added option of specific ID for US taxpayers "
            "complicates cost accounting under US tax law even more.\n\n",
        ),
        (
            "Does this track foreign assets?",
            "When asset transactions are priced in a foreign currency, you "
            "should enter the price or amount in the foreign currency and "
            "also record the exchange rate to Canadian dollars on the "
            "transaction date. That's the way to keep an accurate record.\n\n"
            "A note: If you're recording an F/X rate, there is a good "
            "argument for recording the rate as of the TRADE date, not the "
            "SETTLED date that you have for the transaction. "
            "It's your choice. Pick a method and "
            "stick with it for everything, and you will be fine with CRA.",
        ),
        (
            'Dates are labelled "settled". What\'s that about?',
            "If you sell Royal Bank shares on the TSX "
            "today, the trade settles on the next business day.  If today is "
            'Friday Dec 29th, you "sell" the shares today but '
            'you "own" them through Tuesday Jan 2nd.\n\n'
            "Canadian tax law says that the sale occurred after New Years. "
            "That is the date you have to record.",
        ),
        (
            "Any tips or recommendations for using the software?",
            "Keep your life simple. "
            "Use one portfolio per individual taxpayer, not per financial "
            "account.\n\n"
            "Open another portfolio only for another taxpayer, like a "
            "spouse, child, or personal corporation.\n\n"
            "A few user interface tips ...\n"
            "  Ctrl-S is a keyboard shortcut to save all data\n"
            "  Ctrl-Q/Alt-F4 are keyboard shortcuts to exit the application\n"
            "  CAN-ACB will auto-save changes after 10 minutes of inactivity\n"
            "  No edits of transactions in this version ... add a "
            "corrected copy and delete the bad one\n"
            "  You can delete a transaction by selecting it in the history "
            "and pressing Delete",
        ),
        (
            "Where is my data stored?",
            'This version stores all data in a file named "canacb.json". '
            "The default directory in which this file is located varies "
            "depending on the computer and operating system that you use, "
            "but it is ALWAYS on your local file system. NO future version "
            "of this software will ever move this file to a remote machine "
            'or to the "cloud".\n\n'
            'To find exact placement, use the "About" menu item.',
        ),
        (
            "This is sensitive financial info. Do you encrypt my data?",
            "We are not encryption wizards. "
            "The data is with the software. "
            "If some villain has physical access to your device, all bets are "
            "off.\n\n"
            "The next q&a offers a security tip if you're worried.",
        ),
        (
            "I share a computer with others. How about a password to get in?",
            "If you can't "
            "trust others that have access to the computer, then you probably "
            "don't keep sensitive/confidential data anywhere on the device. "
            "\n\n"
            "In such a case, consider putting this program on a thumb "
            "drive, keep the data with the program, plug the thumb drive into "
            "the computer when you want to use it, save your work (it will be "
            "on the thumb drive), and always take the thumb drive with you."
            "\n\n"
            "Of course, if you lend that thumb drive to someone ...\n"
            "Or lose the thumb drive ...\n"
            "Or it dies of old age ...\n\n"
            "Somewhat related ... Do you backup all your files regularly?",
        ),
        (
            "Can I be sure my financial info won't end up in Kazakhstan?",
            "Improbable but not impossible. "
            "The software operates entirely locally. It doesn't use a network "
            "connection. It will run on a computer that is never connected to "
            "the internet, as long as there is a reasonably current version "
            "of Python3 installed.\n\n"
            "But if the data file is on a secure computer or a thumb drive "
            "and then you attach it to an email sent to your girlfriend in "
            "Kazakhstan (or your husband sitting four feet away at the "
            "kitchen table, because that email can be routed via Kazakhstan), "
            "it's a possibility.",
        ),
        (
            "What does this software cost?",
            "Nothing. It's absolutely free for you to use.\n\n"
            "No purchase price. No annoying ads. No subscription required. "
            "No monthly fees. No salesman will call.",
        ),
        (
            "Do I need to register / sign up?",
            "The software and its authors don't know who you are, don't want "
            "your name, address, email, or credit card details.\n\n"
            "This is not facebook or google or the cable company.\n\n"
            "We have no interest in monetizing you or your habits.",
        ),
        (
            "What platforms can I run this software on?",
            "CAN-ACB is written in Python and uses a cross-platform GUI named "
            "Tcl/Tk. You will need at least version 3.5 of Python and version "
            "8.6.8 of Tcl/Tk installed on your computer to run this software."
            "\n\n"
            "Testing has been done on a limited number of hardware/software "
            "combinations, under Windows, MacOS and Linux.\n\n"
            "The oldest hardware/software success to date was a 2007 "
            "vintage laptop running a 2017 Linux/python/tcl software stack.",
        ),
        (
            "Can I sue if something goes wrong?",
            "This is free software, really just a calculator with a good "
            "memory and a very specific use.\n\n"
            "No warranty of merchantability or fitness is provided.",
        ),
        (
            "How do I report bugs or problems?",
            "By email to canacb@libra-investments.com.",
        ),
    )
    _ANSWER_PADX = 15
    _WRAP_LENGTH = 600

    def __init__(self, parent):
        """Lays out the FAQ window."""

        super().__init__(parent)
        self.iconify()

        self._answer = tk.StringVar()
        self._answer.set("What's your question?")

        self.title("{} FAQ (v{})".format(cfg.APP_NAME, cfg.APP_VERSION))
        self.protocol("WM_DELETE_WINDOW", self.iconify)
        self.bind("<Escape>", lambda event: self.iconify())

        self.columnconfigure(0, weight=1)
        self.rowconfigure(10, weight=1)

        answer_font = tkFont.nametofont("TkTextFont").copy()
        answer_font["size"] = 11

        self._questions = ttk.Combobox(
            self,
            values=tuple(item[0] for item in self._FAQ),
            width=50,
            state="readonly",
        )
        self._questions.grid(row=0, column=0, padx=10, pady=10)
        self._questions.bind("<<ComboboxSelected>>", self._question_chosen)

        answers = tk.Label(
            self,
            anchor="nw",
            font=answer_font,
            height=13,
            justify="left",
            textvariable=self._answer,
            width=self._WRAP_LENGTH // 8,  # divisor is a decent guess
            wraplength=self._WRAP_LENGTH,
        )
        answers.grid(row=10, column=0, padx=self._ANSWER_PADX, sticky="nsew")

        button_frame = tk.Frame(self)
        button_frame.grid(row=20, column=0, padx=15, pady=10)
        self._next = tk.Button(
            button_frame, text="Next", command=self._on_next
        )
        self._next.grid(row=0, column=10, padx=10)
        self._enable_disable_next()
        close = tk.Button(button_frame, text="Close", command=self.iconify)
        close.grid(row=0, column=20, padx=10)

        min_width = max(
            self.winfo_reqwidth(), self._WRAP_LENGTH + 2 * self._ANSWER_PADX
        )
        self.geometry(
            "+{}+{}".format(self.winfo_screenwidth() - min_width - 50, 50)
        )
        self.deiconify()

    def _question_chosen(self, _event=None):
        """Answers the question chosen by the user."""
        self._answer.set(self._FAQ[self._questions.current()][1])
        self._questions.select_clear()
        self._enable_disable_next()

    def _on_next(self):
        """Advances to the next question and answer."""
        self._questions.current(
            min(self._questions.current() + 1, len(self._FAQ) - 1)
        )
        self._questions.select_clear()
        self._answer.set(self._FAQ[self._questions.current()][1])
        self._enable_disable_next()

    def _enable_disable_next(self):
        """Enables/disables the Next button depending on list placement."""
        current = self._questions.current()
        self._next.config(
            state="normal" if current < len(self._FAQ) - 1 else "disabled"
        )


class Welcome(tk.Toplevel):
    """Welcome popup on first run"""

    _HEADING = "Welcome to {}!".format(cfg.APP_NAME)
    _TEXT = (
        "Canada's tax rules require you to keep track of the adjusted cost "
        "base of your security holdings. This software helps you with that. "
        "Record transactions on screen, starting with a single portfolio. All "
        "data is stored locally, keeping your financial information secure."
    )
    _WRAP_LENGTH = 540

    def __init__(self, parent, faq, carry_on):
        """Lays out the welcome window.

        Arguments:
            parent - the Tk/Tcl interpreter that we inform when done
            carry_on - a list to which we append one element if signaling
                that the user is interested in proceeding (tkinter trick)
        """
        super().__init__(parent)

        self.iconify()
        self.layout_externals(parent.quit)
        self.layout_internals(carry_on, parent.quit, faq)
        self.deiconify()

    def layout_externals(self, tk_quit):
        """Sets up the outer window frame and binds a few controls."""
        self.title("")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", tk_quit)
        self.bind("<Escape>", lambda event: tk_quit())

    def layout_internals(self, carry_on, tk_quit, faq):
        """Lays out widgets inside the window frame."""
        title_font = tkFont.nametofont("TkTextFont").copy()
        title_font["size"] = 18
        body_font = tkFont.nametofont("TkTextFont").copy()
        body_font["size"] = 11

        tk.Label(self, text=self._HEADING, font=title_font).grid(
            row=0, column=0, pady=10
        )
        tk.Label(
            self,
            text=self._TEXT,
            justify="left",
            font=body_font,
            wraplength=self._WRAP_LENGTH,
        ).grid(row=10, column=0, padx=15, pady=10)

        button_frame = tk.Frame(self)
        button_frame.grid(row=20, column=0, padx=15, pady=20)
        tk.Button(
            button_frame,
            text="No thanks",
            command=tk_quit,
        ).grid(row=0, column=0, padx=10)
        tk.Button(
            button_frame,
            text="Review FAQ",
            command=faq,
        ).grid(row=0, column=1, padx=10)
        tk.Button(
            button_frame,
            text="Let's go",
            command=lambda: carry_on.append(True) or tk_quit(),
        ).grid(row=0, column=2, padx=10)
