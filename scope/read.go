// Copyright (c) 2019 Intel Corporation
//
// SPDX-License-Identifier: Apache-2.0

package scope

import (
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
	if buf, err = ioutilReadAll(file); err != nil {
		return Version{}, err
	}
	ver := strings.TrimRight(string(buf), "\n\r")
	return MakeVersion(ver)
}
