cwtoken Technical Reference
===========================

cwtoken simplifies working with PostgREST APIs by:

- Automatically handling **access token generation**
- Provides a query constructor for URL generation
- Making authenticated **GET requests** to PostgREST endpoints
- Create and manage a lightweight backend that can schedule queries, refresh data on intervals, and expose custom API endpoints.
- Providing a **CLI** for quick testing and usage
- Including a user-friendly **GUI** for building and running queries without code

---

CWClient -- API Client
----------------------

Represents an authenticated connection to the PostgREST API. All queries are created via this object.

Constructor:

    client = CWClient(
        api_token: str,
        clubcode: str = None,
        access_token: str = None,
        base_url: str = "https://atukpostgrest.clubwise.com/"
    )

Attributes:

- client.access_token — automatically fetched if not provided
- client.headers — dict of headers including Authorization
- client.clubcode — club code used

Methods:

- client.table(endpoint: str) -> Query  
  Returns a query constructor object for building endpoint queries. Supports method chaining.

- client.raw_query(full_query: str) -> RawQuery  
  Returns a raw query object for executing a fully specified URL.

- client.get_endpoints() -> list[str]  
  Fetches available API endpoints from the PostgREST spec.

- client.last_response() -> dict | str | None  
  Returns the raw JSON or text of the last HTTP response made by the client.

---

Query -- Table-based Query Constructor
--------------------------------------

- Created via client.table(endpoint)
- Supports chained methods:

    q = client.table("member") \
              .select("member_no", "first_name") \
              .filters("date_of_birth=gt.1980-01-01") \
              .order("first_name", desc=True) \
              .limit(10)

Methods:

- .select(*columns) — adds columns to select
- .filters(*filters) — raw PostgREST filter strings
- .order(*columns, desc=False) — orders results
- .limit(n) — limits results
- .fetch(to_df=True)  -> pandas.DataFrame
- .fetch(to_df=False) -> dict — executes query
- .clear_filters(), .clear_orders(), .clear_params(), .clear_select(), .clear_limit() — reset parts of the query

Utility methods:

- .compose_url() -> str  
  Builds the full query string (with filters, ordering, and parameters).  
  Does not send the request — only constructs the final URL.

- .get_columns() -> list[str]  
  Fetches one row (with `?limit=1`) and returns the list of available column names for that endpoint.

- .last_response() -> dict | str | None  
  Returns the most recent response payload (JSON if possible, else raw text).

---

RawQuery -- Direct URL Query
----------------------------

- Created via client.raw_query(full_query)
- Used for fully constructed query strings without method chaining.

Example:

    df = client.raw_query("member?select=first_name&limit=10").fetch()

Methods:

- .fetch(to_df=False) -> dict | list  
  Executes the raw URL request. Returns JSON by default, or pandas.DataFrame if `to_df=True`.

- .get_columns() -> list[str]  
  Fetches one row (with `?limit=1`) and extracts available column names.

- .last_response() -> dict | str | None  
  Returns the JSON or raw text of the last executed request.

---

CWBackend -- Backend API
------------------------

- Created via CWBackend(client, **kwargs)
- Each kwarg defines an endpoint: name=(function, interval_seconds)
- Functions are executed on schedule, results cached and served via backend

Example:

    def example_function(client):
        query = client.table("example_table")
        data = query.fetch()
        return data

    backend = CWBackend(
        client,
        example_endpoint=(example_function, 300)
    )
    backend.run()

Endpoints:

- /example_endpoint  -> returns output of example_function
- /overview          -> returns a combined JSON of all endpoints

---

CLI Functions
-------------

### test_connection()
Pings the API server to check if it's reachable.  
Run from CLI:

    cwtoken test

### cwtoken gui
Launches the graphical interface for building and executing queries.  
Run from CLI:

    cwtoken gui

---

Notes on Usage
--------------

- Queries are always linked to a client.
- Method chaining is supported for the query object.
- Both Query and RawQuery store the **last response** in `.response`, accessible via `.last_response()`.
- `.get_endpoints()` discovers all available PostgREST tables.
- `.get_columns()` checks an endpoint for available column names.
- `.compose_url()` lets you debug or log the full query string before execution.
- Both Query and RawQuery can return results as pandas.DataFrame for analysis or dict/JSON for raw usage.
