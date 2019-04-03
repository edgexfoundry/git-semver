// Copyright (c) 2019 Intel Corporation
//
// SPDX-License-Identifier: Apache-2.0

package scope

import (
	"fmt"
	"time"

	"gopkg.in/src-d/go-git.v4"
	"gopkg.in/src-d/go-git.v4/plumbing"
	"gopkg.in/src-d/go-git.v4/plumbing/object"
)

// Tag the current HEAD with the current semver version.
func Tag(my, sv *Extent) error {
	tip, err := my.Repo.Head()
	if err != nil {
		return err
	}
	log.Printf("# %s", tip)
	tag, err := resolveTag(my, tip)
	if err != nil {
		return err
	}
	if tag != nil {
		log.Printf("# %s", tag)
		return fmt.Errorf("%s is already tagged: %s", tip.Hash().String()[:7], tag.Name().Short())
	}
	ver, err := ReadVersion(my, sv)
	if err != nil {
		return err
	}
	tag, err = my.Repo.CreateTag(fmt.Sprintf("v%s", ver), tip.Hash(), &git.CreateTagOptions{
		Message: fmt.Sprintf("semver(tag): %s", ver),
		Tagger: &object.Signature{
			Name:  UserName,
			Email: UserEmail,
			When:  time.Now(),
		},
	})
	log.Printf("# %s", tag)
	return err
}

func resolveTag(my *Extent, tip *plumbing.Reference) (*plumbing.Reference, error) {
	tags, err := my.Repo.TagObjects()
	if err != nil {
		return nil, err
	}
	defer tags.Close()
	var (
		tagref *plumbing.Reference
	)
	tags.ForEach(func(tag *object.Tag) error {
		if th := tip.Hash(); th == tag.Hash || th == tag.Target {
			log.Printf("# tagobj: %s %s %s", tag.Hash, tag.Target, tag.Name)
			refs, err := my.Repo.Tags()
			if err != nil {
				return err
			}
			defer refs.Close()
			refs.ForEach(func(ref *plumbing.Reference) error {
				// this is inefficient but it seems to work
				log.Printf("# tagref: %s %s", ref.Hash(), ref.Name())
				if rh := ref.Hash(); rh == tag.Hash || rh == tag.Target {
					if _, e := MakeVersion(tag.Name); e == nil {
						tagref = ref
					}
				} else if ref.Hash() == tip.Hash() {
					if _, e := MakeVersion(ref.Name().Short()); e == nil {
						tagref = ref
					}
				}
				return nil
			})
		}
		return nil
	})
	return tagref, nil
}
