// Copyright (c) 2019 Intel Corporation
//
// SPDX-License-Identifier: Apache-2.0

package scope

import (
	"fmt"
)

// Bump the specified semver axis with prefix, invoking WriteVersion on the result.
func Bump(my, sv *Extent, axis, pre string) error {
	ver, err := _ReadVersion(my, sv)
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
		if len(ver.Pre) == 0 {
			ver, err = makeVersion(ver, BumpPatch())
		} else if pre == "" {
			pre = ver.Pre[0].String()
		}
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
	return _WriteVersion(my, sv, ver)
}
