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
)

// Bump the specified semver axis with prefix, invoking WriteVersion on the result.
func Bump(my, sv *Extent, axis, pre string) error {
	ver, err := ReadVersion(my, sv)
	if err != nil {
		return err
	}
	switch axis {
	case "major":
		ver, err = makeVersion(ver, BumpMajor(), WithPre(pre))
	case "minor":
		ver, err = makeVersion(ver, BumpMinor(), WithPre(pre))
	case "patch":
		ver, err = makeVersion(ver, BumpPatch(), WithPre(pre))
	case "final":
		ver, err = makeVersion(ver, BumpFinal())
	case "pre":
		if pre == "" {
			pre = PrePrefix
		}
		ver, err = makeVersion(ver, BumpPre(pre))
	default:
		err = fmt.Errorf("bump axis not supported: %s", axis)
	}
	if err != nil {
		return err
	}
	return WriteVersion(my, sv, ver)
}
