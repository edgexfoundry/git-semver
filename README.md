
# `git semver`

[![Go Report Card](https://goreportcard.com/badge/github.com/edgexfoundry/git-semver)](https://goreportcard.com/report/github.com/edgexfoundry/git-semver)
[![Go Doc](https://godoc.org/github.com/edgexfoundry/git-semver?status.svg)](https://godoc.org/github.com/edgexfoundry/git-semver)

Create and manage a `.semver` directory right next to your `.git` directory, for all of your [Semantic Versioning][semver-web] needs.

## Installation

### Go

If you're using Go (1.11.4+):

```bash
go get github.com/edgexfoundry/git-semver
```

Assuming that your `$GOPATH/bin` is in your path, that's it.

## Usage

NOTE: As of yet, authentication is the default provided by [src-d/go-git](https://github.com/src-d/go-git), i.e. ssh-agent auth for SSH URLs.

### `git semver init`

Prepare the repository (and the current branch) for Semantic Versioning:

```bash
# git [init|clone] ...
git semver init
```

This will:

- create an orphaned branch named `semver`.
- create and commit a single file named after your current branch, i.e. `master`, with the content of `0.0.0`.
- move this new checkout to `.semver` in your current repository
- - modify the `.git/info/exclude` to ignore `.semver`
- push the `semver` branch to your current `.git` repository directory as if it were a remote.

This invocation is idempotent-ish in that it will inspect your current repository and make modifications to the `semver` configuration accordingly. It will also attempt to clone (or checkout) the `semver` branch if it already exists instead of creating it anew.

### `git semver`

Write to STDOUT the current version for the current branch.

### `git semver bump [-pre=<prefix>] major|minor|patch|final|pre`

This will bump the specified axis and commit the change to the semver branch. `final` lops off any pre-release semver suffix whereas `pre` appends it. The default pre-release prefix is "pre" when bumping the `pre` axis but can be overridden by specifying the `-pre=prefix` flag to `bump`. Additionally, specifying the `-pre=prefix` flag to `major`, `minor`, or `patch` will initialize the pre-release semver suffix after bumping the specified axis.

For example, if currently on the `master` branch and the value returned by `git semver` is `1.0.0` invoking `git semver bump -pre=rc patch` will result in `1.0.1-rc.1` written to `$PWD/.semver/master` and commited, the written to STDOUT.

### `git semver tag`

Attempt to tag the current HEAD with a tag that is effectively `v$(git semver)`. This will fail if `git-semver` detects a tag on the current HEAD that can be parsed as a Semantic Version.

### `git semver push`

Push `semver` branch commits to the remote. Also push tags _from the current repo_ that match the ref-spec `refs/tags/v*:refs/tags/v*`.

### Environment Variables

From [scope/scope.go](scope/scope.go), these values have default values that can be over-ridden:

- `SEMVER_ORIGIN_NAME = origin`
- `SEMVER_PRE_PREFIX  = pre`
- `SEMVER_USER_EMAIL  = semver@semver.org`
- `SEMVER_USER_NAME   = semver`

Additionally, `$SEMVER_BRANCH` (then `$GIT_BRANCH` if empty, then `$BRANCH_NAME`) will be dereferenced if `git-semver` is unable to detect the current branch (common with the default clone/checkout in Jenkins).

As described below, there is also `SEMVER_DEBUG` which interprets as per [strconv.ParseBool()](https://golang.org/pkg/strconv/#ParseBool) with the caveat that "on", "On, or "ON" are are treated as `true`.

### When Things Go Wrong

If this darn tool just isn't behaving the way you expect, consider invoking it with the `SEMVER_DEBUG=on` to log a bit more detail to STDERR, e.g.

```bash
export SEMVER_DEBUG=on
git semver init
# $GIT_DIR = /tmp/test/.git
# $GIT_WORK_TREE = /tmp/test
# $SEMVER_ORIGIN_NAME = origin
# $SEMVER_USER_EMAIL = semver@semver.org
# $SEMVER_USER_NAME = semver
# $SEMVER_BRANCH = master
# $SEMVER_TEMP = /var/folders/7s/bwc8hz3n5498r68fw4gq6cxr0000gq/T/semver-546746833
# git clone --branch semver /tmp/test/.git $SEMVER_TEMP
# -> Clone(): remote repository is empty
# git init /var/folders/7s/bwc8hz3n5498r68fw4gq6cxr0000gq/T/semver-546746833
# git push /tmp/test/.git semver
# '/var/folders/7s/bwc8hz3n5498r68fw4gq6cxr0000gq/T/semver-546746833' -> '/tmp/test/.semver'
# $SEMVER_DIR = /tmp/test/.semver
git semver
# $GIT_DIR = /tmp/test/.git
# $GIT_WORK_TREE = /tmp/test
# $SEMVER_ORIGIN_NAME = origin
# $SEMVER_USER_EMAIL = semver@semver.org
# $SEMVER_USER_NAME = semver
# $SEMVER_BRANCH = master
# $SEMVER_DIR = /tmp/test/.semver
0.0.0
```

Submitting such output with your [bug reports](https://github.com/edgexfoundry/git-semver/issues) will be helpful!

---

[semver-web]: https://semver.org/ "Semantic Versioning"
[concourse-semver]: https://github.com/concourse/semver-resource "Concourse SemVer Resource"
