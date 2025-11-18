# GQLBridge

This package allows you to write GraphQL-style queries against a PostgreSQL database and automatically converts them into SQL queries that return nested JSON results.

### It is especially useful for:

* **Organizations** that want to query relational data sources (PostgreSQL) using GraphQL-like queries, without needing to set up a full GraphQL server.
* **Developers & data engineers** who work with analytics pipelines, ETL processes, or APIs and want an easy way to express complex relational queries in a GraphQL-like syntax.
* **Teams** that want **GraphQL as a query interface** for their data warehouse but keep execution in **SQL (PostgreSQL)** for performance and compatibility.


### Key Features

* **GraphQL-style input**: Accepts GraphQL query strings directly as input.
* **Automatic SQL generation**: Converts nested selections, filters, joins, and lists into PostgreSQL SQL queries.
* **JSON output**: Returns query results as nested JSON objects for direct consumption in APIs or applications.
* **Join handling**: Supports `LEFT`, `RIGHT`, `INNER`, `FULL`, and `CROSS` joins defined via GraphQL arguments.
* **Filter support**: Handles comparison operators (`eq`, `ne`, `lt`, `gt`, `le`, `ge`) and list-based filters.
* **Pagination**: Supports **pagination** with `first`, `after`, and `orderBy`.
* **Date handling**: Automatically parses and casts date strings into `TIMESTAMP`.
* **Alias mapping**: Supports **table and column aliasing** via YAML mappings—GraphQL uses alias names, while SQL queries use actual database names, with unmapped fields falling back to real names.
* **Integration ready**: Returns results as Python dictionaries (via Pandas + JSON), suitable for APIs, ETL, or downstream analytics.

### Installation

```
pip install gqlbridge
```

### Environment Variables

Before running queries, configure your PostgreSQL connection using environment variables:

```
export DB_HOST=your-db-host
export DB_PORT=your-db-port
export DB_NAME=your-database
export DB_USER=your-username
export DB_PASSWORD=your-password
```
### Running GraphQL Queries

After installing the package, you can run any GraphQL query using:
```
gqlbridge.run_graphql_query(queryStr, alias_file_path="alias-test.yml")
```
**Notes:** Just pass the GraphQL query string and an optional alias-mapping YAML file. If no alias file is provided, the query runs using the original database schema.

### How Queries Work

Queries are written in GraphQL style, but instead of hitting a GraphQL API, this package translates them into PostgreSQL and executes them against PostgreSQL.

General Structure query

``` graphql
query {
  project(path: {eq:"demo_project"}) {
    id
    name
    description
  }
}
```

* `project` → **Outer table** (the main table you are selecting from).
* `path: {eq:"demo_project"}` → **Filter condition** (`WHERE path = 'demo_project'`).
* `id, name, description` → **Columns** to select.

#### Schema

Represent the schema of different tables using schema attribute in arguments


#### Example with Schema

``` graphql
query {
  project(path: {eq:"demo_project"}, schema: "public") {
    id
    name
    description
  }
}
```

#### Explanation:

1. **schema**
   * `public` represents the schema of table **project**.

#### Joins

This package supports joins between tables using GraphQL arguments.

#### Example with Joins

``` graphql
query {
  project(path: {eq:"demo_project"}) {
    id
    name
    description

    join_table1(left: {id: "eq-project_id"}, title: {eq:"Bug Fix"}) {
      id
      title
    }

    join_table2(left: {id: "eq-project_id"}) {
      id
      project_id
    }
  }
}
```

#### Explanation:

1. **Outer Table**
   * `project` is the **main table**.
   * The filter `path: {eq:"demo_project"}"` applies as a SQL `WHERE` clause.
2. **Join Tables**
   * `join_table1` and `join_table2` represent tables joined with `project`.
   * `left` specifies the **join type** (`LEFT JOIN`).
   * Supported join types: `left`, `right`, `inner`, `full`, `cross`.
3. **Join Condition (`id: "eq-project_id"`)**
   * This means:
     * `id` belongs to the **main table** (`project`).
     * `project_id` belongs to the **join table** (`join_table1` or `join_table2`).
   * Interpreted as:

     `project.id = join_table1.project_id
     `
4. **Filters on Join Table**
   * `title: {eq:"Bug Fix"}` applies as a `WHERE` filter inside the join.

---

#### JSON Fields

If a column in the database stores **JSON data**, you can request nested fields using GraphQL notation.

#### Example: Extracting JSON

``` graphql
query {
  project(path: {eq:"demo_project"}) {
    id
    metadata {
      name
      version
    }
  }
}
```

This extracts `metadata.name` and `metadata.version` from the `metadata` JSON column.

---

#### JSON Lists (`list_items`)

When a JSON field contains a **list (array)**, you must use `list_items` to expand it.

#### Example: JSON Array

``` graphql
query {
  project(path: {eq:"demo_project"}) {
    id
    metadata {
      name
      tags {
        list_items {
          key
          value
        }
      }
    }
  }
}
```

* `metadata.tags` is a **list field**.
* `list_items` tells the query engine to expand the array elements.
* Equivalent SQL logic uses `jsonb_array_elements`.

---

#### Pagination

With pagination, you can easily control how many rows to fetch, where to start, and the order of results — all directly in your GraphQL-style query.

#### Example: Pagination
``` graphql
query {
  project(first: 3, after: 2, orderBy: "id") {
    id
    name
    fullPath
    description
  }
}
```

* first: 3 → limit results to 3 rows
* after: 2 → offset (skip) the first page - first 3 rows
* orderBy: "id" → order results by column id

---

### Alias File (YAML) Support

GQLBridge allows you to **rename tables and columns** using an external YAML alias file.\
This is useful when:

* Database table/column names are inconsistent
* You want cleaner or domain-specific names in GraphQL queries
* You are migrating schemas but want to preserve a stable query interface
* Teams want to expose simplified field names to users while keeping internal DB names unchanged

### How It Works

When you pass an `alias_file_path` to the `main()` function:

`main(queryStr, alias_file_path="alias.yml")
`

GQLBridge loads the YAML file and uses the aliases to:

* interpret GraphQL field names
* translate them into real PostgreSQL table / column names
* output final JSON using the **GraphQL names**, not DB names

> **If an alias is not provided, the original table/column name is used.**

---

### Alias YAML Structure

```yaml
tables: 
  public:                 # schema name
    epics:                # original table name
      table_name: epic    # alias table name → actual table is "epics"
      yml_file: yaml      # old column : new column
      epic_id: id         # old column : new column

    project:              # original table name
      id: ids             # alias column name
      table_name: projects
      weburl: web_url
```

### Rules

1. **table_name**\
   Defines the alias → actual internal DB table name.\
   Example:\
   _GraphQL uses:_ `epic`\
   _Actual DB table:_ `epics`
2. **Column aliases**\
   Every mapping inside a table is:

   `old_column_name : new_column_name
   `

   GraphQL uses the **new column name**,\
   SQL uses the **old column name**.
3. **No alias defined?**\
   → GQLBridge keeps the **same** name.

---

### Example: Using Aliases in GraphQL Query

#### Input Query (GraphQL)

```graphql
query {
  epic(id1: {eq: 10}) {      # Uses alias "epic" for table "epics"
    id1                     # Maps to DB column "id"
    yaml                    # Maps to DB column "1_test_str1"

    projects(left: {ids: "eq-epic_id"}) {   # "projects" is alias for table "project"
      ids                                   # Maps to DB column "id"
      web_url                               # Maps to DB column "weburl"
    }
  }
}
```

---

### How Aliases Translate Internally

#### Table Mapping

| GraphQL Name | Actual DB Table |
|--------------|-----------------|
| `epic` | `epics` |
| `projects` | `project` |

#### Column Mapping (Example: `epics` table)

| GraphQL Column | Actual DB Column |
|----------------|------------------|
| `id` | `epic_id` |
| `yaml` | `yml_file` |

#### Column Mapping (Example: `project` table)

| GraphQL Column | Actual DB Column |
|----------------|------------------|
| `ids` | `id` |
| `web_url` | `weburl` |

---

## Summary

* The alias YAML file provides a flexible way to **rename tables and columns**.
* GraphQL queries use **alias names**, but SQL runs against **real DB names**.
* If a mapping is missing, original names are preserved.

This aliasing allows organizations to create a **clean public query interface** without modifying internal database schema.

### End-to-End Example

#### Input Query

``` graphql
query {
  project(path: {eq:"demo_project"}) {
    id
    name
    description

    join_table1(left: {id: "eq-project_id"}, title: {eq:"Bug Fix"}) {
      id
      title
    }

    join_table2(left: {id: "eq-project_id"}) {
      id
      project_id
    }

    metadata {
      name
      tags {
        list_items {
          key
          value
        }
      }
    }
  }
}
```

#### Output JSON

``` json
{
  "Query1": [
    {
      "id": 1,
      "name": "Demo Project",
      "description": "A test project",
      "join_table1": [
        { "id": 101, "title": "Bug Fix" }
      ],
      "join_table2": [
        { "id": 201, "project_id": 1 }
      ],
      "metadata": {
        "name": "Project Metadata",
        "tags": [
          { "key": "priority", "value": "high" },
          { "key": "status", "value": "active" }
        ]
      }
    }
  ]
}
```

### Supported Features

* ✅ GraphQL-style query input (string-based).
* ✅ Automatic translati# Alias File (YAML) Support

GQLBridge allows you to **rename tables and columns** using an external YAML alias file.\
This is useful when:

* Database table/column names are inconsistent
* You want cleaner or domain-specific names in GraphQL queries
* You are migrating schemas but want to preserve a stable query interface
* Teams want to expose simplified field names to users while keeping internal DB names unchanged

### How It Works

When you pass an `alias_file_path` to the `main()` function:

`main(queryStr, alias_file_path="alias.yml")
`

GQLBridge loads the YAML file and uses the aliases to:

* interpret GraphQL field names
* translate them into real PostgreSQL table / column names
* output final JSON using the **GraphQL names**, not DB names

> **If an alias is not provided, the original table/column name is used.**

---

## Alias YAML Structure

```yaml
tables: 
  public:                 # schema name
    epics:                # original table name
      table_name: epic    # alias table name → actual table is "epics"
      yml_file: yaml      # old column : new column
      epic_id: id         # old column : new column

    project:              # original table name
      id: ids             # alias column name
      table_name: projects
      weburl: web_url
```

### Rules

1. **table_name**\
   Defines the alias → actual internal DB table name.\
   Example:\
   _GraphQL uses:_ `epic`\
   _Actual DB table:_ `epics`
2. **Column aliases**\
   Every mapping inside a table is:

   `old_column_name : new_column_name
   `

   GraphQL uses the **new column name**,\
   SQL uses the **old column name**.
3. **No alias defined?**\
   → GQLBridge keeps the **same** name.

---

## Example: Using Aliases in GraphQL Query

### Input Query (GraphQL)

```graphql
query {
  epic(id1: {eq: 10}) {      # Uses alias "epic" for table "epics"
    id1                     # Maps to DB column "id"
    yaml                    # Maps to DB column "1_test_str1"

    projects(left: {ids: "eq-epic_id"}) {   # "projects" is alias for table "project"
      ids                                   # Maps to DB column "id"
      web_url                               # Maps to DB column "weburl"
    }
  }
}
```

---

## How Aliases Translate Internally

### Table Mapping

| GraphQL Name | Actual DB Table |
|--------------|-----------------|
| `epic` | `epics` |
| `projects` | `project` |

### Column Mapping (Example: `epics` table)

| GraphQL Column | Actual DB Column |
|----------------|------------------|
| `id` | `epic_id` |
| `yaml` | `yml_file` |

### Column Mapping (Example: `project` table)

| GraphQL Column | Actual DB Column |
|----------------|------------------|
| `ids` | `id` |
| `web_url` | `weburl` |

---

### Alias Summary

* The alias YAML file provides a flexible way to **rename tables and columns**.
* GraphQL queries use **alias names**, but SQL runs against **real DB names**.
* If a mapping is missing, original names are preserved.

This aliasing allows organizations to create a **clean public query interface** without modifying internal database schema.on to PostgreSQL SQL.


* ✅ Supports **joins** (`LEFT`, `RIGHT`, `INNER`, `FULL`, `CROSS`).
* ✅ Supports **comparison operators** (`eq`, `ne`, `lt`, `le`, `gt`, `ge`).
* ✅ Handles **string, numeric, and timestamp filters**.
* ✅ Extracts and structures **JSON and JSON arrays** with `list_items`.
* ✅ Returns results as **nested JSON** matching the GraphQL query shape.

### Audience

* **Data engineers**: Simplify ETL pipelines with GraphQL queries on SQL data.
* **Backend developers**: Expose data without writing raw SQL.
* **Organizations**: Provide a query interface for PostgreSQL that feels like GraphQL.
* **Analysts**: Explore relational data using GraphQL syntax.

### License

MIT License.
