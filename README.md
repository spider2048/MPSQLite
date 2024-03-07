# MPSQLite

A fine, interprocess caching system

Using `twisted` and `reactor` and `SQLite`

## Usage

* Usable with multiple processes (or) threads
* Access your database using a token

### Packet structure

* Obtain a token

```json
# Request
{
  "create": "true"
}

# Response
{
  "status": "OK",
  "token": ... # token
}
```

* Request data
```json
# Request
{
  "token": ..., # token
  "query": {
       "statement": ..., # SQL statement
       "parameters": [...], # SQL parameters
   }
}

# Response
{
  "status": "OK",
  "result": ... # base64 encoded pickle
}
```

Handles ~10,000+ requests/second across multiple processes and databases.
