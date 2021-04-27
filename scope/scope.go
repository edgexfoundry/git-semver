// Copyright (c) 2019 Intel Corporation
//
// SPDX-License-Identifier: Apache-2.0

// Package scope encapsulates ambit of the git-semver functionality.
package scope

import (
	"io/ioutil"
	golog "log"
	"os"
	"strconv"
	"strings"

	"github.com/blang/semver"

	"github.com/go-git/go-git/v5"
	"github.com/go-git/go-git/v5/storage/filesystem"
)

var (
	log = golog.New(ioutil.Discard, "", 0)
)

func init() {
	if s, ok := os.LookupEnv("SEMVER_DEBUG"); ok {
		if b, _ := strconv.ParseBool(s); b || strings.ToLower(s) == "on" {
			log.SetOutput(os.Stderr)
		}
	}
}

var (
	// RemoteName is the name of the remote that this tooling should work with.
	RemoteName = GetEnv("SEMVER_REMOTE_NAME", git.DefaultRemoteName)

	// PrePrefix is the default value for the pre-axis.
	PrePrefix = GetEnv("SEMVER_PRE_PREFIX", "pre")

	// UserEmail is the value for the git config user.email in the local semver repository.
	UserEmail = GetEnv("SEMVER_USER_EMAIL",
		GetEnv("GIT_AUTHOR_EMAIL",
			GetEnv("GIT_COMMITTER_EMAIL", "semver@semver.org"),
		),
	)

	// UserName is the value for the git config user.name in the local semver repository.
	UserName = GetEnv("SEMVER_USER_NAME",
		GetEnv("GIT_AUTHOR_NAME",
			GetEnv("GIT_COMMITTER_NAME", "semver"),
		),
	)
)

// Extent is an Open()'ed GIT repository.
type Extent struct {
	Store  *filesystem.Storage
	Repo   *git.Repository
	Tree   *git.Worktree
	Branch string
}

// Version type alias
type Version = semver.Version

// GetEnv attempt os.LookupEnv returning the default if the key is not found.
func GetEnv(key, def string) string {
	if val, ok := os.LookupEnv(key); ok {
		return val
	}
	return def
}
