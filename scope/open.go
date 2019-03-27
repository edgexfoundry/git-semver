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
	"fmt"

	"gopkg.in/src-d/go-git.v4"
	"gopkg.in/src-d/go-git.v4/plumbing"
	"gopkg.in/src-d/go-git.v4/plumbing/storer"
	"gopkg.in/src-d/go-git.v4/storage/filesystem"
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
