// Copyright (c) 2019 Intel Corporation
//
// SPDX-License-Identifier: Apache-2.0

package scope

import (
	"github.com/go-git/go-git/v5"
	"github.com/go-git/go-git/v5/config"
)

// Push the semver branch and any tags to the remote.
func Push(my, sv *Extent) error {
	var err = sv.Repo.Push(&git.PushOptions{
		RemoteName: RemoteName,
		RefSpecs: []config.RefSpec{
			config.RefSpec("refs/heads/semver:refs/heads/semver"),
		},
	})
	if err == git.NoErrAlreadyUpToDate {
		err = nil
	}
	if err != nil {
		return err
	}
	err = my.Repo.Push(&git.PushOptions{
		RemoteName: RemoteName,
		RefSpecs: []config.RefSpec{
			config.DefaultPushRefSpec,
			config.RefSpec("refs/tags/v*:refs/tags/v*"),
		},
	})
	if err == git.NoErrAlreadyUpToDate {
		err = nil
	}
	return err
}
