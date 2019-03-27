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
	"strings"
	"unicode"

	"github.com/blang/semver"
)

// MakeOpt is an option passed to MakeVersion
type MakeOpt func(*Version) error

func makeVersion(v Version, m ...MakeOpt) (Version, error) {
	for _, o := range m {
		if e := o(&v); e != nil {
			return v, e
		}
	}
	return v, nil
}

// MakeVersion parses the version string and applies the supplied options.
func MakeVersion(s string, m ...MakeOpt) (Version, error) {
	if len(s) > 1 && s[0] == 'v' && unicode.IsNumber(rune(s[1])) {
		s = s[1:]
	}
	v, e := semver.Parse(s)
	if e != nil {
		return v, e
	}
	return makeVersion(v, m...)
}

// BumpFinal will strip the pre-release suffix.
func BumpFinal() MakeOpt {
	return func(v *Version) error {
		v.Pre = nil
		return nil
	}
}

// BumpMajor will bump the major axis.
func BumpMajor() MakeOpt {
	return func(v *Version) error {
		v.Major++
		v.Minor = 0
		v.Patch = 0
		v.Pre = nil
		return nil
	}
}

// BumpMinor will bump the minor axis.
func BumpMinor() MakeOpt {
	return func(v *Version) error {
		v.Minor++
		v.Patch = 0
		v.Pre = nil
		return nil
	}
}

// BumpPatch will bump the patch axis.
func BumpPatch() MakeOpt {
	return func(v *Version) error {
		v.Patch++
		v.Pre = nil
		return nil
	}
}

// BumpPre will bump the pre-release suffix.
// Passing a different prefix than what is currently encoded will bump from zero with the new pre-release.
func BumpPre(pre string) MakeOpt {
	return func(v *Version) error {
		if v.Pre == nil || v.Pre[0].VersionStr != pre || len(v.Pre) <= 1 {
			v.Pre = []semver.PRVersion{
				{VersionStr: pre},
				{VersionNum: 1, IsNum: true},
			}
		} else {
			v.Pre = []semver.PRVersion{
				{VersionStr: pre},
				{VersionNum: v.Pre[1].VersionNum + 1, IsNum: true},
			}
		}
		return nil
	}
}

// WithPre does nothing for empty prefixes and works like BumpPre otherwise.
func WithPre(pre string) MakeOpt {
	if pre != "" {
		return BumpPre(pre)
	}
	return func(v *Version) error {
		return nil
	}
}

// WithBuild attaches build/metadata to the version string.
func WithBuild(s string) MakeOpt {
	return func(v *semver.Version) error {
		v.Build = strings.Split(s, ".")
		return nil
	}
}
