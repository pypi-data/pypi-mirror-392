#!/usr/bin/env python3

"""Canadian ACB calculator - portfolio management

A hierarchy of classes that manage assets within portfolios.

PortfolioManager, a collection of ...
    Portfolio, itself a collection of ...
        Holding, a thin cover for a ...
            History, a chronologically ordered collection of ...
                Transactions (Buy, Sell, Split, or Adjust), coupled with
                State to record (shares, cost, gain) after application

Most users should instantiate a single Portfolio, or a PortfolioManager if
using multiple portfolios, and avoid dealing directly with other classes.
"""


import datetime

from .tools import fromisoformat, checked_float, pretty_float


# -------------  "Protected" classes  ----------------
# -- ordered to avoid forward reference problems


class State(tuple):
    """A 4-tuple for recording the state of a Holding after a series of
    Transactions are applied.
    """

    __slots__ = ()

    def __new__(cls, shares=0.0, cost=0.0, gain=None, superficial=None):
        """Manufactures the object"""
        return super().__new__(cls, (shares, cost, gain, superficial))

    @property
    def shares(self):
        """Number of shares"""
        return self[0]

    @property
    def cost(self):
        """Total cost"""
        return self[1]

    @property
    def average_cost(self):
        """Average per share cost"""
        return None if self.shares == 0.0 else self.cost / self.shares

    @property
    def gain(self):
        """Gain/loss recorded when this state was created"""
        return self[2]

    @property
    def superficial(self):
        """Superficial loss recorded when this state was created"""
        return self[3]

    def __str__(self):
        if self.shares == 0.0:
            return "N/A"

        if self.gain is None or self.gain == 0.0:
            gain = ""
        elif self.superficial is not None and self.superficial < 0.0:
            gain = " [Loss of {} ({} denied as superficial)".format(
                pretty_float(-(self.gain + self.superficial)),
                pretty_float(-self.superficial),
            )
        elif self.gain > 0.0:
            gain = " [Gain of {}]".format(pretty_float(self.gain))
        else:
            gain = " [Loss of {}]".format(pretty_float(-self.gain))

        return "Position: {} shares with cost {} ({}/share){}".format(
            pretty_float(self.shares, min_decimals=0, max_decimals=4),
            pretty_float(self.cost, blank_if_zero=False),
            pretty_float(self.average_cost, blank_if_zero=False),
            gain,
        )


class Transaction:
    """Base class for various transaction types"""

    def __init__(self, settled, details):
        """Creates a skeleton transaction.

        Settle date gets checked here, details by subclasses,
        perhaps raising ValueError if things go wrong.
        """
        self._settled = fromisoformat(settled).isoformat()
        self._details = self._checked_details(details)

    @property
    def settled(self):
        """Settled date of the transaction"""
        return self._settled

    def _checked_details(self, _details):
        """Stub"""
        return NotImplemented

    def __str__(self):
        """Returns a dated string suitable for display to user"""
        return "{} {}".format(self.settled, self.description())

    def description(self):
        """Stub"""
        return NotImplemented

    def serializable(self):
        """Returns a representation suitable for serialization"""
        return [self._settled, self.__class__.__name__, *self._details]

    def apply(self, _state):
        """Stub"""
        return NotImplemented


class Trade(Transaction):
    """Common methods for Buy and Sell transactions"""

    @property
    def shares(self):
        """Number of shares bought/sold"""
        return self._details[0]

    @property
    def price(self):
        """Price per share"""
        return self._details[1]

    @property
    def fee(self):
        """Commission/fee"""
        return self._details[2]

    @property
    def amount(self):
        """Trade amount"""
        return self._details[3]

    @property
    def fx(self):
        """FX rate"""
        return self._details[4]

    def _checked_details(self, details):
        """Sanity checks the buy/sell details.

        Returns argument if checks are ok, otherwise raises ValueError.
        """
        try:
            if len(details) == 5:
                shares, price, fee, amount, fx = details
            else:
                # accommodates earlier version that didn't have amount
                shares, price, fee, fx = details
                amount = None
        except ValueError as exc:
            raise ValueError(
                "Expecting (shares, price, fee, amount, fx)"
            ) from exc

        shares = checked_float(
            shares, lambda f: f > 0.0, "Share count must be positive"
        )
        if price is None:
            if amount is None:
                raise ValueError("Must have at least one of price and amount")
            amount = checked_float(
                amount, lambda f: f > 0.0, "Amount must be positive"
            )
        else:
            if amount is None:
                price = checked_float(
                    price, lambda f: f > 0.0, "Price must be positive"
                )
            else:
                price = None  # price yields to amount if both provided
        if fee is None:
            fee = 0.0
        else:
            fee = checked_float(
                fee, lambda f: f >= 0.0, "Fee must be non-negative"
            )
        if fx is None:
            fx = 1.0
        else:
            fx = checked_float(fx, lambda f: f >= 0.0, "FX must be positive")

        return (shares, price, fee, amount, fx)

    def _ui_description(self, verb, fee_sign):
        return "{} {} {} {}{}{}".format(
            verb,
            pretty_float(self.shares, min_decimals=0, max_decimals=4),
            "@" if self.amount is None else "for",
            pretty_float(self.price if self.amount is None else self.amount),
            (
                ""
                if self.fee == 0.0
                else " {}{} fee".format(
                    "with " if self.amount is None else fee_sign,
                    pretty_float(self.fee),
                )
            ),
            (
                ""
                if self.fx == 1.0
                else " @FX {}".format(
                    pretty_float(self.fx, min_decimals=4, max_decimals=4)
                )
            ),
        )


class Buy(Trade):
    """Buy transaction"""

    def description(self):
        """Returns a string suitable for display to user"""
        return self._ui_description("Bought", "including ")

    def apply(self, state):
        """Returns the effect on share count and ACB"""
        if self.amount is None:
            cost = self.fx * (self.shares * self.price + self.fee)
        else:
            cost = self.amount
        return State(state.shares + self.shares, state.cost + cost)


class Sell(Trade):
    """Sell transaction"""

    def description(self):
        """Returns a string suitable for display to user"""
        return self._ui_description("Sold", "net of ")

    def apply(self, state):
        """Returns the effect on share count and ACB"""
        if self.shares > state.shares:
            raise ValueError("Cannot sell more shares than are held")

        if self.amount is None:
            proceeds = self.fx * (self.shares * self.price - self.fee)
        else:
            proceeds = self.amount
        cost = self.shares * state.average_cost
        new_shares = state.shares - self.shares
        new_cost = state.cost - cost
        if abs(new_shares) < 0.0000005:
            new_shares = 0.0
            new_cost = 0.0
        elif abs(new_cost) < 0.005:
            new_cost = 0.0
        gain = proceeds - cost
        if abs(gain) < 0.005:
            gain = 0.0
        return State(new_shares, new_cost, gain)


class Split(Transaction):
    """Split transaction"""

    @property
    def multiplier(self):
        """Numerator of the split ratio"""
        return self._details[0]

    @property
    def divisor(self):
        """Denominator of the split ratio"""
        return self._details[1]

    def _checked_details(self, details):
        """Sanity checks the split details.

        Returns argument if checks are ok, otherwise raises ValueError.
        """
        try:
            multiplier, divisor = details
        except ValueError as exc:
            raise ValueError("Expecting (multiplier, divisor)") from exc

        multiplier = checked_float(
            multiplier, lambda f: f > 0.0, "New share count must be positive"
        )
        divisor = checked_float(
            divisor, lambda f: f > 0.0, "Old share count must be positive"
        )

        return (multiplier, divisor)

    def description(self):
        """Returns a string suitable for display to user"""
        return "Split {} for {}".format(
            pretty_float(self.multiplier, min_decimals=0),
            pretty_float(self.divisor, min_decimals=0),
        )

    def apply(self, state):
        """Returns the effect on share count and ACB"""
        if state.shares == 0.0:
            raise ValueError("Cannot split shares when none are held")
        return State(
            state.shares * (self.multiplier / self.divisor), state.cost
        )


class Adjust(Transaction):
    """Adjustment transaction"""

    @property
    def amount(self):
        """Adjustment amount"""
        return self._details[0]

    @property
    def fx(self):
        """FX rate"""
        return self._details[1]

    @property
    def memo(self):
        """Memo"""
        return self._details[2]

    def _checked_details(self, details):
        """Sanity checks the adjustment details.

        Returns argument if checks are ok, otherwise raises ValueError.
        """
        try:
            amount, fx, memo = details
        except ValueError as exc:
            raise ValueError("Expecting (amount, fx, memo)") from exc

        amount = checked_float(
            amount, lambda f: True, "Amount must be numeric"
        )
        if fx is None:
            fx = 1.0
        else:
            fx = checked_float(
                fx, lambda f: f >= 0.0, "FX must be a positive number"
            )

        return (amount, fx, memo)

    def description(self):
        """Returns a string suitable for display to user"""
        return "{} cost base{} by {}{}".format(
            "Reduced" if self.amount < 0.0 else "Increased",
            "" if self.memo is None else " ({})".format(self.memo),
            pretty_float(abs(self.amount)),
            (
                ""
                if self.fx == 1.0
                else " @FX {}".format(
                    pretty_float(self.fx, min_decimals=4, max_decimals=4)
                )
            ),
        )

    def apply(self, state):
        """Returns the effect on share count and ACB"""
        if state.shares == 0.0:
            raise ValueError("Cannot adjust cost of shares when none are held")
        expected_cost = state.cost + self.fx * self.amount
        if abs(expected_cost) < 0.005:
            expected_cost = 0.0
        if expected_cost >= 0.0:
            return State(state.shares, expected_cost)
        return State(state.shares, 0.0, -expected_cost)


class TransactionFactory:
    """A factory to generate Transactions"""

    _DISPATCH = {cls.__name__: cls for cls in (Buy, Sell, Split, Adjust)}

    @classmethod
    def create(cls, action, settled, details):
        """Returns a Transaction of appropriate type,
        or raises a NameError if type is unknown.
        """
        return cls._DISPATCH[action](settled, details)

    @classmethod
    def from_serializable(cls, serializable):
        """Returns a Transaction corresponding to the list provided"""
        return cls.create(serializable[1], serializable[0], serializable[2:])


class History(list):
    """A chronological list of (Transaction, State) tuples.

    A completely miserable class due to Canada's superficial loss rules.
    """

    _THIRTY_DAYS = datetime.timedelta(days=30)

    def __init__(self, transactions):
        """Instantiates from transaction list"""
        super().__init__()
        state = State()
        for transaction in sorted(transactions, key=lambda t: t.settled):
            state = transaction.apply(state)
            self.append((transaction, state))
        self._revise_for_superficial_losses(self.transactions)

    @property
    def last_transaction_date(self):
        """Date of last transaction, or None if no transactions"""
        return None if len(self) == 0 else self[-1][0].settled

    @property
    def last_state(self):
        """Final state in the history"""
        return State() if len(self) == 0 else self[-1][1]

    @property
    def transactions(self):
        """Transaction list from the history"""
        return [entry[0] for entry in self]

    @property
    def states(self):
        """State list from the history"""
        return [entry[1] for entry in self]

    def _lookup(self, as_of=None):
        """Returns the index of the last element in ourselves with a
        settled date no greater than the argument.

        If no as of date, returns the list length less one.

        A naive backwards scan through the history, not a big deal for
        typical usage which is almost always "last state of play."
        """
        index = len(self) - 1
        if as_of is not None:
            while index >= 0 and self[index][0].settled > as_of:
                index -= 1
        return index

    def total_shares(self, as_of=None):
        """Share count as of a given date or, if no as of date, last date
        in the history.
        """
        index = self._lookup(as_of)
        return 0.0 if index < 0 else self[index][1].shares

    def total_cost(self, as_of=None):
        """Total cost as of a given date or, if no as of date, last date
        in the history.
        """
        index = self._lookup(as_of)
        return 0.0 if index < 0 else self[index][1].cost

    def average_cost(self, as_of=None):
        """Average cost as of a given date or, if no as of date, last date
        in the history, but None if no shares held.
        """
        index = self._lookup(as_of)
        shares = 0.0 if index < 0 else self[index][1].shares
        return None if index < 0 else self[index][1].cost / shares

    def _revise_for_superficial_losses(self, transactions):
        """Inserts superficial loss adjustments and revises states"""
        state = State()
        new_history = []
        for transaction in transactions:
            state = transaction.apply(state)
            if isinstance(transaction, Sell) and state.gain < 0.0:
                fraction = self._superficial_loss_fraction(transaction)
                if fraction > 0.0:
                    denied_loss = fraction * state.gain
                    state = State(
                        state.shares,
                        state.cost - denied_loss,
                        state.gain - denied_loss,
                        denied_loss,
                    )
            new_history.append((transaction, state))
        self.clear()
        self.extend(new_history)

    def _superficial_loss_fraction(self, transaction):
        """Returns the CRA approved superficial fraction of a capital loss."""
        settled_d = fromisoformat(transaction.settled)
        window_end = (settled_d + self._THIRTY_DAYS).isoformat()
        window_end_shares = self.total_shares(window_end)
        if window_end_shares == 0.0:
            return 0.0
        window_start = (settled_d - self._THIRTY_DAYS).isoformat()
        window_purchases = self._purchases_between(window_start, window_end)
        return (
            min(transaction.shares, window_end_shares, window_purchases)
            / transaction.shares
        )

    def _purchases_between(self, start, end):
        """Returns the total purchases between the start and end dates."""
        total = 0.0
        for transaction in self.transactions:
            if transaction.settled < start:
                continue
            if transaction.settled > end:
                break
            if isinstance(transaction, Buy):
                total += transaction.shares
        return total

    def after_adding(self, transaction):
        """Returns a new History with a transaction added.

        One might think that adding a transaction in chronological
        sequence could be optimized because "how could this transaction
        affect the past?"  Welcome to Canada's superficial loss rules!

        Raises a ValueError if a History can't be created.
        """
        return History(self.transactions + [transaction])

    def after_cancelling(self, cancel_list):
        """Returns a new History with the numbered transactions omitted.

        Raises a ValueError if a History can't be created.
        """
        cancel_list = set(cancel_list)
        for index in cancel_list:
            if index < 0 or index > len(self):
                raise ValueError("Trying to cancel non-existent transaction")

        transactions = []
        for index, entry in enumerate(self):
            if index not in cancel_list:
                transactions.append(entry[0])
        return History(transactions)


class Holding:
    """A collection of ACB altering transactions"""

    def __init__(self, serializable=None):
        """Creates a holding"""
        transactions = []
        if serializable is not None:
            for item in serializable:
                transactions.append(TransactionFactory.from_serializable(item))
        self._history = History(transactions)

    @property
    def transactions(self):
        """Transactions recorded in the history"""
        return self._history.transactions

    @property
    def last_transaction_date(self):
        """Date of last transaction, or None if no transactions"""
        return self._history.last_transaction_date

    @property
    def last_state(self):
        """Final state in the history"""
        return self._history.last_state

    def total_shares(self, as_of=None):
        """Share count as of a given date, or final shares if no as of"""
        return self._history.total_shares(as_of)

    def total_cost(self, as_of=None):
        """Running cost, or 0.0 if no transactions"""
        return self._history.total_cost(as_of)

    def average_cost(self, as_of=None):
        """Average cost as of a given date, or final average if no as of"""
        return self._history.average_cost(as_of)

    def cancel_transactions(self, expected_length, cancel_list):
        """Attempts to cancel a list of transactions.

        Returns None if cancellation goes fine, an error message if not.
        """
        if len(cancel_list) == 0:
            return None
        if expected_length != len(self._history):
            raise RuntimeError("sanity check failure on cancellation")
        try:
            self._history = self._history.after_cancelling(cancel_list)
            return None
        except ValueError:
            return "history rebuild failed after transaction cancellation"

    def display_transactions(self):
        """Quick and dirty transaction/state display suitable for printing"""
        result = ""
        for entry in self._history:
            result += "{} -> {}\n".format(str(entry[0]), str(entry[1]))
        return result

    def view_transactions(self):
        """Transaction/state info suitable for a treeview"""
        result = []
        for transaction, state in self._history:
            description = transaction.description()
            if state.superficial is not None and state.superficial <= 0.0:
                if state.gain == 0.0:
                    description += (
                        " [{} superficial loss added to ACB]".format(
                            pretty_float(-state.superficial)
                        )
                    )
                else:
                    total_loss = -(state.gain + state.superficial)
                    description += (
                        " [{} of {} loss is superficial; added to ACB]".format(
                            pretty_float(-state.superficial),
                            pretty_float(total_loss),
                        )
                    )

            result.append(
                (
                    transaction.settled,
                    description,
                    pretty_float(state.shares, min_decimals=0, max_decimals=6),
                    pretty_float(state.cost),
                    (
                        ""
                        if state.average_cost is None
                        else pretty_float(state.average_cost)
                    ),
                    "" if state.gain is None else pretty_float(state.gain),
                )
            )
        return result

    def _update_history_with(self, transaction):
        """Updates the holding history with a transaction.

        Returns None if successful, an error message on failure.
        """
        try:
            self._history = self._history.after_adding(transaction)
            return None
        except ValueError as failure:
            return str(failure)

    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def buy(self, settled, shares, price, fee, amount, fx):
        """Creates a transaction and applies it to the history"""
        return self._update_history_with(
            Buy(settled, (shares, price, fee, amount, fx))
        )

    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def sell(self, settled, shares, price, fee, amount, fx):
        """Creates a transaction and applies it to the history"""
        return self._update_history_with(
            Sell(settled, (shares, price, fee, amount, fx))
        )

    def split(self, settled, multiplier, divisor):
        """Creates a transaction and applies it to the history"""
        return self._update_history_with(Split(settled, (multiplier, divisor)))

    def adjust(self, settled, amount, fx=None, memo=None):
        """Creates a transaction and applies it to the history"""
        return self._update_history_with(Adjust(settled, (amount, fx, memo)))

    def serializable(self):
        """Returns a representation suitable for serialization"""
        result = []
        for transaction in self._history.transactions:
            serializable = transaction.serializable()
            if serializable is not None:
                result.append(serializable)
        return {"transactions": result}

    def s3_record(self, year):
        """Returns a 6-tuple (shares, acquired, proceeds, acb, outlays, gain)
        suitable for a Schedule 3 line for the given year.
        """
        earliest_acquisition = None
        latest_acquisition = None
        total_shares = 0.0
        total_proceeds = 0.0
        total_acb = 0.0
        total_outlays = 0.0
        total_gain = 0.0
        for transaction, state in self._history:
            if transaction.settled[0:4] > year:
                break
            if isinstance(transaction, Buy):
                if earliest_acquisition is None:
                    earliest_acquisition = transaction.settled[0:4]
                latest_acquisition = transaction.settled[0:4]
            if transaction.settled < year:
                if state.shares == 0.0:
                    earliest_acquisition = None
                    latest_acquisition = None
                continue
            if not isinstance(transaction, Sell):
                continue
            if transaction.amount is None:
                proceeds = transaction.fx * (
                    transaction.shares * transaction.price
                )
            else:
                proceeds = transaction.fx * (
                    transaction.amount + transaction.fee
                )
            outlays = transaction.fx * transaction.fee
            acb = proceeds - outlays - state.gain
            total_shares += transaction.shares
            total_proceeds += proceeds
            total_acb += acb
            total_outlays += outlays
            total_gain += state.gain

        years = earliest_acquisition
        if earliest_acquisition != latest_acquisition:
            years += "-" + latest_acquisition
        return (
            total_shares,
            years,
            total_proceeds,
            total_acb,
            total_outlays,
            total_gain,
        )


# -------------  Public classes  -----------------


class PortfolioManager(dict):
    """A collection of Portfolios, with a few minor additions to
    the standard complement of dict methods to accommodate this app.
    """

    def __init__(self, saved_pfos=None):
        """Builds a dictionary of Portfolios created from the argument"""
        super().__init__()
        if saved_pfos is not None:
            for name, data in saved_pfos.items():
                self[name] = Portfolio(data)

    def __setitem__(self, key, value):
        """A protective __setitem__

        Raises:
            KeyError on duplicate key
            TypeError if value isn't a Portfolio
            ValueError on no/blank key
        """
        if not isinstance(value, Portfolio):
            raise TypeError("Portfolio Manager only holds Portfolios")
        if isinstance(key, str):
            key = key.strip()
            if len(key) > 0:
                if key in self:
                    raise KeyError("duplicate portfolio name '{}'".format(key))
                super().__setitem__(key, value)
                return
        raise ValueError("portfolio name must be provided")

    def __delitem__(self, key):
        """A protection against element deletion"""
        raise TypeError("PortfolioManager doesn't support Portfolio deletion")

    @property
    def pfo_names(self):
        """Returns a sorted list of portfolio names"""
        return sorted(list(self.keys()))

    def is_dirty(self):
        """Returns True if any Portfolio is dirty"""
        for pfo in self.values():
            if pfo.is_dirty():
                return True
        return False

    def mark_clean(self):
        """Marks every Portfolio clean, e.g. after a successful save."""
        for pfo in self.values():
            pfo.mark_clean()

    def serializable(self):
        """Returns a representation suitable for serialization"""
        return {name: pfo.serializable() for name, pfo in self.items()}


class Portfolio:
    """A collection of Holdings"""

    def __init__(self, holdings=None):
        """Creates a portfolio, a collection of Holdings.

        If data regarding existing holdings is passed as an argument,
        Holdings will be created and added to the collection.

        Raises:
            TypeError if the holdings argument isn't a dictionary
            + whatever Holding creation throws
        """

        self._holdings = {}
        self._dirty = True

        if holdings is None:
            return
        if not isinstance(holdings, dict):
            raise TypeError("expecting a dict for existing holdings")

        for symbol, data in holdings.items():
            self.add_holding(symbol, data["transactions"])

    @property
    def holding_names(self):
        """Returns a sorted list of holding symbols"""
        return sorted(list(self._holdings.keys()))

    def __contains__(self, symbol):
        """Returns True if there is a Holding for the given symbol"""
        return symbol.strip() in self._holdings

    def add_holding(self, symbol, transactions=None):
        """Adds a Holding with the given symbol to the portfolio.

        Raises ValueError on no/blank symbol, KeyError on duplicate.
        """
        if isinstance(symbol, str):
            symbol = symbol.strip()
            if len(symbol) > 0:
                if symbol in self._holdings:
                    raise KeyError("duplicate symbol '{}'".format(symbol))
                self._holdings[symbol] = Holding(transactions)
                self._dirty = True
                return
        raise ValueError("symbol must be provided")

    def change_symbol(self, old, new):
        """Changes the symbol on an existing holding"""
        if isinstance(new, str) and isinstance(old, str):
            old = old.strip()
            new = new.upper().strip()
            if len(new) > 0:
                if new in self._holdings:
                    raise KeyError("duplicate symbol '{}'".format(new))
                if old not in self._holdings:
                    raise KeyError("symbol '{}' unknown".format(old))
                self._holdings[new] = self._holdings.pop(old)
                return
        raise ValueError("new symbol must be provided")

    def is_dirty(self):
        """Returns True if the portfolio has been altered"""
        return self._dirty

    def mark_clean(self):
        """Marks the portfolio clean, e.g. after saving to a file."""
        self._dirty = False

    def serializable(self):
        """Returns a representation suitable for serialization"""
        result = {}
        for symbol, holding in self._holdings.items():
            result[symbol] = holding.serializable()
        return result

    def buy(self, symbol, *args):
        """Forwards a buy to the specified holding"""
        failure = self._holdings[symbol.strip()].buy(*args)
        if failure is None:
            self._dirty = True
        return failure

    def sell(self, symbol, *args):
        """Forwards a sell to the specified holding"""
        failure = self._holdings[symbol.strip()].sell(*args)
        if failure is None:
            self._dirty = True
        return failure

    def split(self, symbol, *args):
        """Forwards a split to the specified holding"""
        failure = self._holdings[symbol.strip()].split(*args)
        if failure is None:
            self._dirty = True
        return failure

    def adjust(self, symbol, *args):
        """Forwards a cost adjustment to the specified holding"""
        failure = self._holdings[symbol.strip()].adjust(*args)
        if failure is None:
            self._dirty = True
        return failure

    def cancel_transactions(self, symbol, *args):
        """Forwards a transaction cancel request to the specified holding"""
        failure = self._holdings[symbol.strip()].cancel_transactions(*args)
        if failure is None:
            self._dirty = True
        return failure

    def last_transaction_date_for(self, symbol):
        """Returns the final transaction date for a holding, or None."""
        return self._holdings[symbol.strip()].last_transaction_date

    def transactions_for(self, symbol):
        """Returns the transactions recorded for a holding."""
        return self._holdings[symbol.strip()].transactions

    def display_transactions(self, symbol):
        """Forwards a transaction display request to the specified holding"""
        return self._holdings[symbol.strip()].display_transactions()

    def view_holdings(self, as_of):
        """Returns the current holdings as of a date,
        suitable for a ttk.Treeview to display.
        """
        result = []
        for symbol, holding in sorted(self._holdings.items()):
            shares = holding.total_shares(as_of)
            if shares > 0.0:
                result.append(
                    [
                        symbol,
                        pretty_float(shares, min_decimals=0, max_decimals=4),
                        pretty_float(holding.total_cost(as_of)),
                        pretty_float(holding.average_cost(as_of)),
                    ]
                )
        return result

    def view_transactions(self, symbol):
        """Forwards a transaction view request to the specified Holding"""
        return self._holdings[symbol.strip()].view_transactions()

    def s3_for(self, year):
        """Returns the portfolio's Schedule 3 for the given year,
        suitable for a ttk.Treeview to display.
        """
        if not (len(year) == 4 and year.isnumeric()):
            raise ValueError("Sch3: bad year '{}'".format(year))

        result = []
        total_proceeds = 0.0
        total_gain = 0.0
        for symbol, holding in sorted(self._holdings.items()):
            shares, acquired, proceeds, acb, outlays, gain = holding.s3_record(
                year
            )
            if abs(shares) < 0.0000005:
                continue
            result.append(
                [
                    pretty_float(shares, min_decimals=0, max_decimals=4),
                    symbol,
                    acquired,
                    pretty_float(proceeds),
                    pretty_float(acb),
                    pretty_float(outlays),
                    pretty_float(gain),
                ]
            )
            total_proceeds += proceeds
            total_gain += gain

        result.append(["", "", "", "", "", "", ""])
        result.append(
            [
                "Totals",
                "",
                "",
                pretty_float(total_proceeds, blank_if_zero=False),
                "",
                "",
                pretty_float(total_gain, blank_if_zero=False),
            ]
        )
        return result
