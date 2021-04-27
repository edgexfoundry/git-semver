// Copyright (c) 2019 Intel Corporation
//
// SPDX-License-Identifier: Apache-2.0

package scope

import (
	"fmt"

	"github.com/go-git/go-git/v5"
	"github.com/go-git/go-git/v5/plumbing"
	"github.com/go-git/go-git/v5/plumbing/storer"
	"github.com/go-git/go-git/v5/storage/filesystem"
)

// Open the GIT "extent" located at path.
func Open(path string) (*Extent, error) {
	var (
		err error
		ext Extent
	)

	if ext.Repo, err = git.PlainOpen(path); err != nil {
		return nil, err
	}

	if cfg, err := ext.Repo.Config(); err != nil {
		return nil, err
	} else if cfg.Core.IsBare {
		return nil, fmt.Errorf("repository is bare")
	}
	switch t := ext.Repo.Storer.(type) {
	case *filesystem.Storage:
		ext.Store = t
	default:
		return nil, fmt.Errorf("repository storage not supported: %T", t)
	}
	if err = ext.resolveBranch(); err != nil {
		log.Printf("# -> Open(): %v", err)
	}
	if ext.Tree, err = ext.Repo.Worktree(); err != nil {
		return nil, err
	}
	return &ext, nil
}

func (x *Extent) resolveBranch() error {
	var (
		refname  plumbing.ReferenceName
		branches storer.ReferenceIter
	)
	if head, err := x.Repo.Reference(plumbing.HEAD, false); err != nil {
		return err
	} else if head.Name().IsBranch() {
		refname = head.Name()
	} else if head.Target().IsBranch() {
		refname = head.Target()
	} else if branches, err = x.Repo.Branches(); err != nil {
		return err
	} else {
		defer branches.Close()
		branches.ForEach(func(ref *plumbing.Reference) error {
			if ref.Hash() == head.Hash() {
				refname = ref.Name()
			}
			return nil
		})
	}
	if !refname.IsBranch() {
		return fmt.Errorf("unable to determine branch for HEAD")
	}
	x.Branch = refname.Short()
	return nil
}
