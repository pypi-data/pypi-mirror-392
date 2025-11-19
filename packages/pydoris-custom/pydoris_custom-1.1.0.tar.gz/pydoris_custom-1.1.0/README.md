# Apache Doris Python Client (Custom Build)

A Apache Doris client for the Python programming language.

This is a custom build with relaxed dependency constraints (sqlalchemy-utils removed as it's not actually used in the code).

Apache Doris is a high-performance, real-time analytical database based on MPP architecture, known for its extreme speed and ease of use. It only requires a sub-second response time to return query results under massive data and can support not only high-concurrent point query scenarios but also high-throughput complex analysis scenarios.

## Installation

```bash
pip install pydoris-custom
```

Or install from source:

```bash
pip install .
```

## SQLAlchemy Usage

To connect to doris using SQLAlchemy, use a connection string (URL) following this pattern:

- **User**: User Name
- **Password**: Password
- **Host**: doris FE Host
- **Port**: doris FE port
- **Catalog**: Catalog Name
- **Database**: Database Name

Here's what the connection string looks like:

```
doris://<User>:<Password>@<Host>:<Port>/<Database>
pydoris://<User>:<Password>@<Host>:<Port>/<Database>
```

```
doris://<User>:<Password>@<Host>:<Port>/<Catalog>.<Database>
pydoris://<User>:<Password>@<Host>:<Port>/<Catalog>.<Database>
```

## Example

It is recommended to use python 3.x to connect to the doris database, eg:

```python
from sqlalchemy import create_engine
from sqlalchemy.schema import Table, MetaData
from sqlalchemy.sql.expression import select, text

engine = create_engine('doris://root:xxx@localhost:9030/hive_catalog.hive_db')
connection = engine.connect()

rows = connection.execute(text("SELECT * FROM hive_table")).fetchall()
```

## Differences from Official Package

This custom build removes the `sqlalchemy-utils` dependency which is not actually used in the code.
