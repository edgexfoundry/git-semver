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
	"io/ioutil"
	"os"
	"path/filepath"
	"time"

	"gopkg.in/src-d/go-git.v4"
	"gopkg.in/src-d/go-git.v4/plumbing/object"
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
