/*******************************************************************************
 * Copyright (c) 2019 Intel Corporation
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
 * in compliance with the License. You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software distributed under the License
 * is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
 * or implied. See the License for the specific language governing permissions and limitations under
 * the License.
 *******************************************************************************/
package scope

import (
	"io/ioutil"
	golog "log"
	"os"
	"strconv"
	"strings"

	"github.com/blang/semver"

	"gopkg.in/src-d/go-git.v4"
	"gopkg.in/src-d/go-git.v4/storage/filesystem"
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
	UserEmail = GetEnv("SEMVER_USER_EMAIL", "semver@semver.org")

	// UserName is the value for the git config user.name in the local semver repository.
	UserName = GetEnv("SEMVER_USER_NAME", "semver")
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
