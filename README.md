
# Web Scraping Examples

Collection of small web scraping examples in Go, Ruby, JavaScript, and Python.
The repository includes cached data from prior runs; the default Makefile
checks only compile and syntax so it does not crawl live websites.

Several examples were made to help a friend build an automotive database, and
one was for an interview test.

## Requirements

- Go 1.26.5 or newer for `591comtw`
- Node.js for JavaScript syntax checks and scripts
- Python 3 for Python syntax checks and scripts
- Ruby for Ruby syntax checks and scripts

## Verification

Run non-crawling sanity checks:

```sh
make test
```

Run Go dependency security checks:

```sh
make vulncheck
```

Run any one-off command through the Makefile:

```sh
make run CMD='node --check otomall/crawl.js'
```

## Maintenance Checklist

- [x] Update the Go crawler module runtime directive to Go 1.26.5.
- [x] Keep `golang.org/x/crypto` pinned to a fixed version in the selected module graph.
- [x] Add root Makefile targets for Go compile checks and Ruby, JavaScript, and Python syntax checks.
- [x] Add Go submodule Makefile targets for vulnerability checks and arbitrary commands.
- [x] Run `make test` without executing crawlers.
- [x] Run `make vulncheck`; no vulnerabilities were found.
