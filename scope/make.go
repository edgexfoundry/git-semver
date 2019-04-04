// Copyright (c) 2019 Intel Corporation
//
// SPDX-License-Identifier: Apache-2.0

package scope

import (
	"errors"
	"strings"
	"unicode"

	"github.com/blang/semver"
)

var (
	// ErrBumpMajorOverflow when the major axis resets to zero
	ErrBumpMajorOverflow = errors.New("bump overflow: major")

	// ErrBumpMinorOverflow when the minor axis resets to zero
	ErrBumpMinorOverflow = errors.New("bump overflow: minor")

	// ErrBumpPatchOverflow when the patch axis resets to zero
	ErrBumpPatchOverflow = errors.New("bump overflow: patch")

	// ErrBumpPRVerOverflow when the pre-release version resets to zero
	ErrBumpPRVerOverflow = errors.New("bump overflow: pre-release version")
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
		x := v.Major + 1
		if x == 0 {
			return ErrBumpMajorOverflow
		}
		v.Major = x
		v.Minor = 0
		v.Patch = 0
		v.Pre = nil
		return nil
	}
}

// BumpMinor will bump the minor axis.
func BumpMinor() MakeOpt {
	return func(v *Version) error {
		x := v.Minor + 1
		if x == 0 {
			return ErrBumpMinorOverflow
		}
		v.Minor = x
		v.Patch = 0
		v.Pre = nil
		return nil
	}
}

// BumpPatch will bump the patch axis.
func BumpPatch() MakeOpt {
	return func(v *Version) error {
		x := v.Patch + 1
		if x == 0 {
			return ErrBumpPatchOverflow
		}
		v.Patch = x
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
		} else if x := v.Pre[1].VersionNum + 1; x == 0 {
			return ErrBumpPRVerOverflow
		} else {
			v.Pre = []semver.PRVersion{
				{VersionStr: pre},
				{VersionNum: x, IsNum: true},
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
