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
	"strings"
)

// ReadVersion reads the semver version for the current branch.
func ReadVersion(my, sv *Extent) (Version, error) {
	file, err := sv.Tree.Filesystem.Open(my.Branch)
	if err != nil {
		return Version{}, err
	}
	defer file.Close()
	var buf []byte
	if buf, err = ioutil.ReadAll(file); err != nil {
		return Version{}, err
	}
	ver := strings.TrimRight(string(buf), "\n\r")
	return MakeVersion(ver)
}
