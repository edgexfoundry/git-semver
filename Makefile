.PHONY: build test

GO=CGO_ENABLED=0 go

VERSION=$(shell cat ./VERSION 2>/dev/null || echo 0.0.0)

GOFLAGS=-ldflags "-X github.com/edgexfoundry/git-semver.Version=$(VERSION)"

build:
	$(GO) build $(GOFLAGS) -o git-semver

test:
	$(GO) test ./... -coverprofile=coverage.out ./...
	$(GO) vet ./...
	gofmt -l .
	[ "`gofmt -l .`" = "" ]
