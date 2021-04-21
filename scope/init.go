// Copyright (c) 2019 Intel Corporation
//
// SPDX-License-Identifier: Apache-2.0

package scope

import (
	"fmt"
	"io/ioutil"
	"os"
	"path/filepath"

	"github.com/otiai10/copy"

	"github.com/blang/semver"

	"github.com/go-git/go-git/v5"
	"github.com/go-git/go-git/v5/config"
	"github.com/go-git/go-git/v5/plumbing"
)

// Init attempts to clone, but failing that will initialize, the semver orphan branch into .semver directory.
func Init(my *Extent, create bool, version string, force bool) (*Extent, error) {
	var (
		mydir = my.Store.Filesystem().Root()
		myurl = mydir
		mywkt = my.Tree.Filesystem.Root()
		svwkt = filepath.Join(mywkt, ".semver")
		svbrn = plumbing.NewBranchReferenceName("semver")
		svrrn = plumbing.NewRemoteReferenceName(RemoteName, "semver")
		err   error
		sv    *Extent
	)
	log.Printf("# $GIT_DIR = %s", mydir)
	log.Printf("# $GIT_WORK_TREE = %s", mywkt)
	log.Printf("# $SEMVER_REMOTE_NAME = %s", RemoteName)
	log.Printf("# $SEMVER_USER_EMAIL = %s", UserEmail)
	log.Printf("# $SEMVER_USER_NAME = %s", UserName)

	if b, ok := os.LookupEnv("SEMVER_BRANCH"); ok {
		if b != "" {
			my.Branch = b
		}
	} else if b, ok := os.LookupEnv("GIT_BRANCH"); ok {
		if b != "" {
			my.Branch = b
		}
	} else if b, ok := os.LookupEnv("BRANCH_NAME"); ok {
		if b != "" {
			my.Branch = b
		}
	}
	if my.Branch == "" {
		return nil, fmt.Errorf("unable to determine current branch")
	}
	log.Printf("# $SEMVER_BRANCH = %s", my.Branch)

	if myrem, err := my.Repo.Remote(RemoteName); err == nil {
		myurl = myrem.Config().URLs[0]
	}
	if sv, err = Open(svwkt); err != nil && !create {
		return nil, err
	} else if err == git.ErrRepositoryNotExists {
		sv = &Extent{}
		var (
			svtmp string
		)
		if svtmp, err = ioutil.TempDir(os.TempDir(), "semver-"); err != nil {
			return nil, err
		}
		log.Printf("# $SEMVER_TEMP = %s", svtmp)

		log.Printf("# git clone --branch semver %s $SEMVER_TEMP", myurl)
		sv.Repo, err = git.PlainClone(svtmp, false, &git.CloneOptions{
			URL:           myurl,
			SingleBranch:  true,
			ReferenceName: svbrn,
			RemoteName:    RemoteName,
		})
		if err != nil {
			log.Printf("# -> Clone(): %v", err)
			log.Printf("# git init %s", svtmp)
			if sv.Repo, err = git.PlainInit(svtmp, false); err != nil {
				return nil, err
			}
			if err = sv.Repo.Storer.SetReference(plumbing.NewSymbolicReference(plumbing.HEAD, svbrn)); err != nil {
				return nil, err
			}
			if sv.Tree, err = sv.Repo.Worktree(); err != nil {
				return nil, err
			}
			sv.Repo.DeleteRemote(RemoteName)
		}
		log.Printf("# '%s' -> '%s'", svtmp, svwkt)
		if err = os.Rename(svtmp, svwkt); err != nil {
			if err = copy.Copy(svtmp, svwkt); err != nil {
				return nil, err
			}
		}
		if err = ioutil.WriteFile(filepath.Join(mydir, "info", "exclude"), []byte(".semver"), 0644); err != nil {
			return nil, err
		}
		sv, err = Open(svwkt)
	}
	if err != nil {
		return nil, err
	}

	if create {
		log.Printf("# -> Force: %t", force)
		if _, err = ReadVersion(my, sv); err != nil || force {
			// set version if semantic version is not present or if force is set
			if err = setDefaultVersion(my, sv, version); err != nil {
				return nil, err
			}
		}
	}

	log.Printf("# $SEMVER_DIR = %s", sv.Tree.Filesystem.Root())
	if myo, mye := my.Repo.Remote(RemoteName); mye == nil && myo != nil {
		sv.Repo.CreateRemote(&config.RemoteConfig{
			Name: myo.Config().Name,
			URLs: myo.Config().URLs,
			Fetch: []config.RefSpec{
				config.RefSpec(fmt.Sprintf("+%s:%s", svbrn, svrrn)),
			},
		})
	}

	return sv, nil
}

func setDefaultVersion(my, sv *Extent, version string) error {
	initVersion, err := semver.Parse(version)
	if err != nil {
		return err
	}
	if err = WriteVersion(my, sv, initVersion); err != nil {
		return err
	}
	return nil
}
