# canacb - Adjusted cost base tracker for Canadian investors

Since 1972, Canadian tax law requires declaration of capital gains when you
dispose of a capital asset, so that capital gains taxes can be assessed.
It's usually simple to determine what you sold an asset for, but sometimes
not so easy to reconstruct what its cost (in tax terms, its "adjusted cost
base") is if you've bought and sold over many years.

Records get lost. Memories fade as time goes by. CAN-ACB can help.

## Features
- Cross platform pure Python3 application with an intuitive graphical user interface
- Multiple portfolios, multiple holdings
- Settlement date accounting, per Canadian rules
- Average cost accounting, per Canadian rules
- Handles purchases, sales, splits, and miscellaneous cost basis adjustments
- Accommodates transactions in foreign currencies via manual entry
- Superficial loss calculations, per Canadian rules (partial, as the rules are more complex than any software can handle)
- Displays full transaction history for a symbol, portfolio position as of a date, and Schedule 3 for a user specified year
- Local data storage - your data is YOUR data
- No internet access required; usable on an air gapped machine after installation

## Software prerequisites
- python >= 3.5
- tk/tcl >= 8.6.8

## Installation and usage
```bash
$ pip install canacb
$ canacb
