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
	"gopkg.in/src-d/go-git.v4"
	"gopkg.in/src-d/go-git.v4/config"
)

// Push the semver branch and any tags to the remote.
func Push(my, sv *Extent) error {
	err := sv.Repo.Push(&git.PushOptions{
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
