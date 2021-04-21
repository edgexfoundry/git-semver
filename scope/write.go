// Copyright (c) 2019 Intel Corporation
//
// SPDX-License-Identifier: Apache-2.0

package scope

import (
	"fmt"
	"io/ioutil"
	"os"
	"path/filepath"
	"time"

	"github.com/go-git/go-git/v5"
	"github.com/go-git/go-git/v5/plumbing/object"
)

// WriteVersion writes the version string value to a file named after the current branch.
func WriteVersion(my, sv *Extent, ver Version) error {
	vs := ver.String()
	vp := filepath.Join(sv.Tree.Filesystem.Root(), my.Branch)
	if err := os.MkdirAll(filepath.Dir(vp), 0755); err != nil {
		return err
	}
	if err := ioutil.WriteFile(vp, []byte(vs), 0644); err != nil {
		return err
	}
	if _, err := sv.Tree.Add(my.Branch); err != nil {
		return err
	}
	_, err := sv.Tree.Commit(fmt.Sprintf("semver(%s): %s", my.Branch, vs), &git.CommitOptions{
		Author: &object.Signature{
			Name:  UserName,
			Email: UserEmail,
			When:  time.Now(),
		},
	})
	return err
}
