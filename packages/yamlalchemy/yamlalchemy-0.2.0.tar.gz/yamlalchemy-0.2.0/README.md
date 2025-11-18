# YAMLAlchemy

[![Build Status](https://app.travis-ci.com/ahmetonol/yamlalchemy.svg?branch=master)](https://travis-ci.org/ahmetonol/yamlalchemy)
[![PyPI](https://img.shields.io/pypi/v/yamlalchemy.svg)](https://pypi.python.org/pypi/yamlalchemy)
[![PyPI](https://img.shields.io/pypi/pyversions/yamlalchemy.svg)](https://pypi.python.org/pypi/yamlalchemy)

YAMLAlchemy is a Python-based library to convert YAML string to SQLAlchemy read-only queries.

## Installation

Installation via PyPI:

```shell
 pip install yamlalchemy
```

## Usage

```python
from yamlalchemy import parse
from sqlalchemy.engine import URL
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import pandas as pd


uri = URL.create(**{
    'drivername': "mysql+pymysql",
    "username": "guest",
    "host": "relational.fit.cvut.cz",
    "port": "3306",
    "password": "relational",
    "database": "AdventureWorks2014"
})

engine = create_engine(uri)
engine.connect()

base = automap_base()

yaml_content = 
"""
$from: Product
$column:
  -
      $name: Color
      $alias: Color of Product
  -
      $name: ListPrice
      $alias: List Price of Product
      $func: avg
$where:
  -
  $name: Color
  $filter:
    $nis: null
  -
    $name: SellStartDate
    $filter:
      $gt: 2013-01-01
$group:
  -
      $name: Color
$order:
  -
    $name: Name
    $direction: asc
$limit: 10
$offset: 0
"""

base.prepare(engine, reflect=True)
session = Session(engine)
qs = parse(yaml_content, session, base).to_query()

df = pd.read_sql_query(qs.statement, session.connection())

```

## YAML Query Language Syntax

### FROM

Name of the table from which to select data. For now, YAMLAlchemy supports only one table.

| Identifier | Data Type |
|--|--|
| `$column` | String |

*Usage:*

```yaml
$from: Product
```

### COLUMNS

Field names of the table you want to select data from.

| Identifier | Data Type |
|--|--|
| `$column` | List |

*Column Definition:*

| Identifier | Description | Required |
|--|--|--|
| `$name` | Name of column | `True` |
| `$alias` | Alias of column | `False` |
| `$func` | Aggregate function of column. avg, sum, etc... | `False` |

*Usage:*

```yaml
$column:
  -
    $name: Color
    $alias: Color of Product
  -
    $name: ListPrice
    $alias: List Price of Product
    $func: avg
```

### GROUP

Field names of the table you want to group the same values into summary rows.

| Identifier | Data Type |
|--|--|
| `$group` | List |

*Column Definition:*

| Identifier | Description | Required |
|--|--|--|
| `$name` | Name of column | `True` |

*Usage:*  

```yaml
$group:
  -
    $name: Color
```

### ORDER

Field names of the table you want to sort result-set in ascending or descending order.

| Identifier | Data Type |
|--|--|
| `$order` | List |

*Column Definition:*

| Identifier | Description | Required | Defaults |
|--|--|--|--|
| `$name` | Name of column | `True` | -- |
| `$direction` | Ascending or descending order | `False` | `asc` or `desc` |

*Usage:*  

```yaml
$order:
  -
    $name: Name
    $direction: asc
```

### JOIN

Combine rows from two or more tables based on a related column between them.

| Identifier | Data Type |
|--|--|
| `$join` | List |

*JOIN Definition:*

| Identifier | Description | Required | Defaults |
|--|--|--|--|
| `$table` | Name of the table to join with | `True` | -- |
| `$on` | Join condition definition | `True` | -- |
| `$type` | Type of join (inner, left, right, outer) | `False` | `inner` |

*JOIN ON Definition:*

| Identifier | Description | Required |
|--|--|--|
| `$left` | Left column in format `Table.Column` | `True` |
| `$right` | Right column in format `Table.Column` | `True` |

*Usage:*

```yaml
$join:
  -
    $table: Category
    $on:
      $left: Product.CategoryID
      $right: Category.CategoryID
    $type: inner
  -
    $table: Supplier
    $on:
      $left: Product.ProductID
      $right: Supplier.ProductID
    $type: left
```

**Important Notes:**
- When selecting columns from joined tables, use the `Table.Column` format in `$column` definitions
- Multiple joins are supported
- Join types: `inner`, `left`, `right`, `outer`

### WHERE

Filtering records  to return.

| Identifier | Data Type |
|--|--|
| `$where` | List |

*Column Definition:*

| Identifier | Description | Required |
|--|--|--|
| `$name` | Name of column | `True` |
| `$filter` | List of filter definitions | `True` |

*Filter Definition:*

Filtering consists of the following two parts.

*Operator Definition:*

This part is optional.

| Identifier | Description |
|--|--|
| `$and` | Combines where statements with `AND` |
| `$or` | Combines where statements with `OR` |
| `$not` | Combines where statements with `NOT` |

*Comparator Definition:*

This part is required.

| Identifier | Description | SQL Part (MySQL) |
|--|--|--|
| `$eq` | Equal | `COLUMN = 'value'`  |
| `$gt` | Greator than |  `COLUMN > 'value'` |
| `$gte` | Greater than or equal  | `COLUMN >= 'value'`  |
|`$lt`| Less than |  `COLUMN > 'value'` |
| `$lte`| Less than or equal | `COLUMN <= 'value'`  |
| `$neq`| Not equal |  `COLUMN != 'value'` |
| `$like`| Like | `COLUMN LIKE '%value%'`  |
| `$ilike`| Case-insensitive like |  `COLUMN ILIKE '%value%'` |
| `$nlike`| Not like | `COLUMN NOT LIKE '%value%'` |
| `$nilike`| Case-insensitive not like | `COLUMN NOT ILIKE '%value%'`  |
| `$in`| In | `COLUMN IN ['value1', 'value2]`  |
| `$nin`| Not in | `COLUMN NOT IN ['value1', 'value2]`  |
| `$is (:null)`| is null |  `COLUMN IS NULL`  |
| `$nis (:null)`| Is not null | `COLUMN IS NOT NULL`  |
| `$contains`| Contains (Operand should contain 1 column) | `COLUMN LIKE '%value%'` |
| `$startswith`| Starts with | `COLUMN LIKE 'value%'`  |
| `$endswith` | Ends with | `COLUMN LIKE '%value'`  |

*Usage:*  

```yaml
$where:
  -
    $name: Class
    $filter:
      $is: null

  -
    $name: Color
    $filter:
      $nis: null
  -
    $name: SellStartDate
    $filter:
      $gt: 2013-01-01
  -
    $name: Style
    $filter:
      $or:
        $startswith:
          - U
          - M
```

### HAVING

Filtering with aggregate functions.

| Identifier | Data Type |
|--|--|
| `$having` | List |

*Column Definition:*

| Identifier | Description | Required |
|--|--|--|
| `$name` | Name of column | `True` |
| `$func` | Aggregate function name | `True` |
| `$filter` | Filtering part. Same sytntax with the filter part of WHERE statement. | `True` |

*Usage:*  

```yaml
$having:
  -
    $name: Review
    $func: avg
    $filter:
      $and:
        $lt: 1500
        $gt: 1000
  -
    $name: Stars
    $func: count
    $filter:
      $lt: 20
```

### LIMIT

Specifying the number of records to return.

| Identifier | Data Type |
|--|--|
| `$limit` | Integer |

*Usage:*  

```yaml
$limit: 10
```

### OFFSET

Specifying an offset from where to start returning data.

| Identifier | Data Type |
|--|--|
| `$offset` | Integer |

*Usage:*  

```yaml
$offset: 10
```

## Running tests

Run all tests:
```shell
python -m unittest discover tests -v
```

Run specific test files:
```shell
# Unit tests (33 tests)
python -m unittest tests/test_parser_unit.py -v

# SQL validation tests (12 tests)
python -m unittest tests/test_sql_validation.py -v
```

## Roadmap

- Sub Queries
- ~~JOIN support~~ ✅ Completed (v0.2.0)

## License

MIT License

Copyright (c) 2021 Ahmet Önol

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
