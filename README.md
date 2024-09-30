# Temporal Logic Parser

[![PyPI](https://img.shields.io/pypi/v/tlparser.svg)](https://pypi.org/project/tlparser/)
[![Changelog](https://img.shields.io/github/v/release/RomanBoegli/tlparser?include_prereleases&label=changelog)](https://github.com/RomanBoegli/tlparser/releases)
[![Test](https://github.com/RomanBoegli/tlparser/actions/workflows/test.yml/badge.svg)](https://github.com/RomanBoegli/tlparser/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/RomanBoegli/tlparser/blob/master/LICENSE)

The Temporal Logic Parser or `tlparser` takes something like this as input:

```
G((x and (u == 9) and (i < 3)) --> G(not y or x))
```

And returns some statistics about it:

```json
{
    "ap": [
        "u_eq_9",
        "x",
        "y",
        "i_lt_3"
    ],
    "asth": 5,
    "cops": {
        "eq": 1,
        "geq": 0,
        "gt": 0,
        "leq": 0,
        "lt": 1,
        "neq": 0
    },
    "lops": {
        "and": 2,
        "impl": 1,
        "not": 1,
        "or": 1
    },
    "tops": {
        "A": 0,
        "E": 0,
        "F": 0,
        "G": 2,
        "R": 0,
        "U": 0,
        "X": 0
    },
    "agg": {
        "aps": 4,
        "cops": 2,
        "lops": 5,
        "tops": 2
    }
}
```

## How to use

To contribute to this tool, first `git clone` this repository and `cd` into the folder.

> [!NOTE]  
> This tool requires **Python 3.10 or later**. Ensure you have the correct version [installed](https://www.python.org/downloads/).

Next, create a new virtual environment using the following commands:

```bash
python3 -m venv venv && source venv/bin/activate
```

Install and test the dependencies:

```bash
pip3 install --upgrade pip && pip3 install -e '.[test]' && python3 -m pytest
```

Now you are ready to start the `tlparser`.
Test it by printing the `help` message.

```bash
tlparser --help
```

<details>
<summary>Read and plot test data (optional)</summary>

First, digest the test data file to create an Excel file.

```bash
tlparser digest ../tlparser/tests/data/test.json
```

The Excel file will serve as basis for generating the plots.
It contains the following columns:

| Column                 | Meaning                                                                                                                                               |
|------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------|
| id                     | Unique requirement identifier                                                                                                                         |
| text                   | Requirement in human language                                                                                                                         |
| type                   | Temporal logic (supported are `INV`, `LTL`, `MTLb`, `MITL`, `TPTL`, `CTLS`, `STL`)                                                                    |
| reasoning              | Thought decisive for formalizing the requirement in this logic                                                                                        |
| casting                | Specified whether the requirement can theoretically be formalized in (*casted to*) another logic (possible values are `self`, `yes`, `no`, `unknown`) |
| castclass              | Category name derived by concatenating first letters of all casting answers per requirement                                                           |
| stats.formula_raw      | Formalization with comparison operators (e.g. `G((x <= 7) --> (not (y)))`)                                                                            |
| stats.formula_parsable | Formalization without comparison operators (e.g. `G((x_leq_7) --> (not (y)))`)                                                                        |
| stats.formula_parsed   | Interpreted formalization using [`pyModelChecking`](https://github.com/albertocasagrande/pyModelChecking) (e.g. `G((x_leq_7 --> not y))`)             |
| stats.asth             | Height (or *depth* or *nesting*) of the abstract syntax tree                                                                                          |
| stats.ap               | Set of all atomic propositions                                                                                                                        |
| stats.cops.eq          | Number of `==` (equals) comparisons                                                                                                                   |
| stats.cops.ge          | Number of `>=` (greater-or-equal-than) comparisons                                                                                                    |
| stats.cops.gt          | Number of `>` (greater-than) comparisons                                                                                                              |
| stats.cops.leq         | Number of `<=`less-or-equal-than comparisons                                                                                                          |
| stats.cops.lt          | Number of `<` (less-than) comparisons                                                                                                                 |
| stats.cops.ne          | Number of `!=` (not-equals) comparisons                                                                                                               |
| stats.lops.and         | Number of `∧` (and) operators                                                                                                                         |
| stats.lops.imp         | Number of `-->` (implies) operators                                                                                                                   |
| stats.lops.not         | Number of `¬` (not) operators                                                                                                                         |
| stats.lops.or          | Number of `∨` (or) operators                                                                                                                          |
| stats.tops.A           | Number of `for all paths` operators                                                                                                                   |
| stats.tops.E           | Number of `there exists a path` operators                                                                                                             |
| stats.tops.F           | Number of `eventually` (diamond symbol) operators                                                                                                     |
| stats.tops.G           | Number of `globally` (square symbol) operators                                                                                                        |
| stats.tops.R           | Number of `release` operators                                                                                                                         |
| stats.tops.U           | Number of `until` operators                                                                                                                           |
| stats.tops.X           | Number of `next` operators                                                                                                                            |
| stats.agg.aps          | Total number of atomic propositions                                                                                                                   |
| stats.agg.cops         | Total number of comparison operators (`==`, `!=`, `<`, `>`, `=>`, `<=`)                                                                               |
| stats.agg.lops         | Total number of logical operators (`∧`, `∨`, `-->`, `¬`)                                                                                              |
| stats.agg.tops         | Total number of temporal operators (`A`, `E`, `F`, `G`, `R`, `U`, `X`)                                                                                |

To generate all plots of the latest Excel file execute the following command:

```bash
tlparser visualize -l -p all
```

</details>
</br>

You can parse the `spacewire` requirements using the following command:

```bash
tlparser digest ../tlparser/data/spacewire.json
```

The resulting Excel file serves as basis for generating the plots.

```bash
tlparser visualize -l -p all
```

Exit the virtual environment again using this command:

```bash
deactivate
```

To activate it again, simply execute this command in the root folder of the repository:

```bash
source venv/bin/activate
```
