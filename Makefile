MAKE ?= make
NODE ?= node
PYTHON ?= python3
RUBY ?= ruby
CMD ?=

.PHONY: test go-test js-syntax python-syntax ruby-syntax vulncheck verify-dependency-security clean run

test: go-test js-syntax python-syntax ruby-syntax

go-test:
	$(MAKE) -C 591comtw test

js-syntax:
	$(NODE) --check otomall/crawl.js
	$(NODE) --check belimobilgue/scrap.js

python-syntax:
	$(PYTHON) -m py_compile onebrickio/old-gsmarena-toped.py onebrickio/tokped.py

ruby-syntax:
	$(RUBY) -c otomoto/scrap.rb
	$(RUBY) -c earlweb/shell.rb

vulncheck:
	$(MAKE) -C 591comtw verify-dependency-security
	$(MAKE) -C 591comtw vulncheck

verify-dependency-security: vulncheck

clean:
	rm -rf onebrickio/__pycache__

run:
	@test -n "$(CMD)" || (echo "usage: make run CMD='go test ./...'" >&2; exit 2)
	$(CMD)
