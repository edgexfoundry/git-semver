// Copyright (c) 2020 Intel Corporation
//
// SPDX-License-Identifier: Apache-2.0

package scope

import (
	"errors"
	"fmt"
	"github.com/blang/semver"
	"os"
	"strconv"
	"testing"
)

const maxuint64 = ^uint64(0)

var (
	makeOptError  = errors.New("MakeOpt Error")
)

func TestBumpMajor(t *testing.T) {
	tests := []struct {
		name string
		want interface{}
	}{
		{name: "0.0.1-test.1", want: "1.0.0"},
		{name: "0.1.0-test.1", want: "1.0.0"},
		{name: "1.0.0-test.1", want: "2.0.0"},
		{name: "1.2.3-test.4", want: Version{Major: 2}},
		{name: fmt.Sprintf("%s.0.0", strconv.FormatUint(maxuint64, 10)), want: ErrBumpMajorOverflow},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ver, err := MakeVersion(tt.name, BumpMajor())
			switch exp := tt.want.(type) {
			case error:
				if err != exp {
					t.Errorf("BumpMajor() = %v, want %v", err, tt.want)
				}
			case string:
				if tt.want != ver.String() {
					t.Errorf("BumpMajor() = %v, want %v", ver, tt.want)
				} else {
					t.Logf("%v", ver)
				}
			case Version:
				if !ver.Equals(exp) {
					t.Errorf("BumpMajor() = %v, want %v", ver, tt.want)
				} else {
					t.Logf("%v", ver)
				}
			default:
				t.Errorf("BumpMajor() = %T, want %T", ver, tt.want)
			}
		})
	}
}

func TestBumpMinor(t *testing.T) {
	tests := []struct {
		name string
		want interface{}
	}{
		{name: "0.0.1-test.1", want: "0.1.0"},
		{name: "0.1.0-test.1", want: "0.2.0"},
		{name: "1.0.0-test.1", want: "1.1.0"},
		{name: "1.2.3-test.4", want: Version{Major: 1, Minor: 3}},
		{name: fmt.Sprintf("0.%s.0", strconv.FormatUint(maxuint64, 10)), want: ErrBumpMinorOverflow},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ver, err := MakeVersion(tt.name, BumpMinor())
			switch exp := tt.want.(type) {
			case error:
				if err != exp {
					t.Errorf("BumpMinor() = %v, want %v", err, tt.want)
				}
			case string:
				if tt.want != ver.String() {
					t.Errorf("BumpMinor() = %v, want %v", ver, tt.want)
				} else {
					t.Logf("%v", ver)
				}
			case Version:
				if !ver.Equals(exp) {
					t.Errorf("BumpMinor() = %v, want %v", ver, tt.want)
				} else {
					t.Logf("%v", ver)
				}
			default:
				t.Errorf("BumpMinor() = %T, want %T", ver, tt.want)
			}
		})
	}
}

func TestBumpPatch(t *testing.T) {
	tests := []struct {
		name string
		want interface{}
	}{
		{name: "0.0.1-test.1", want: "0.0.2"},
		{name: "0.1.0-test.1", want: "0.1.1"},
		{name: "1.0.0-test.1", want: "1.0.1"},
		{name: "1.2.3-test.4", want: Version{Major: 1, Minor: 2, Patch: 4}},
		{name: fmt.Sprintf("0.0.%s", strconv.FormatUint(maxuint64, 10)), want: ErrBumpPatchOverflow},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ver, err := MakeVersion(tt.name, BumpPatch())
			switch exp := tt.want.(type) {
			case error:
				if err != exp {
					t.Errorf("BumpPatch() = %v, want %v", err, tt.want)
				}
			case string:
				if tt.want != ver.String() {
					t.Errorf("BumpPatch() = %v, want %v", ver, tt.want)
				} else {
					t.Logf("%v", ver)
				}
			case Version:
				if !ver.Equals(exp) {
					t.Errorf("BumpPatch() = %v, want %v", ver, tt.want)
				} else {
					t.Logf("%v", ver)
				}
			default:
				t.Errorf("BumpPatch() = %T, want %T", ver, tt.want)
			}
		})
	}
}

func TestBumpPre(t *testing.T) {
	tests := []struct {
		name string
		want interface{}
	}{
		{name: "0.0.1-test.1", want: "0.0.1-test.2"},
		{name: "0.1.0-test.1", want: "0.1.0-test.2"},
		{name: "1.0.0-test.1", want: "1.0.0-test.2"},
		{name: "0.0.0-dev.1", want: Version{Pre: []semver.PRVersion{{VersionStr: "test"}, {VersionNum: 1, IsNum: true}}}},
		{name: fmt.Sprintf("0.0.0-test.%s", strconv.FormatUint(maxuint64, 10)), want: ErrBumpPRVerOverflow},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ver, err := MakeVersion(tt.name, BumpPre("test"))
			switch exp := tt.want.(type) {
			case error:
				if err != exp {
					t.Errorf("BumpPre(\"test\") = %v, want %v", err, tt.want)
				}
			case string:
				if tt.want != ver.String() {
					t.Errorf("BumpPre(\"test\") = %v, want %v", ver, tt.want)
				} else {
					t.Logf("%v", ver)
				}
			case Version:
				if !ver.Equals(exp) {
					t.Errorf("BumpPre(\"test\") = %v, want %v", ver, tt.want)
				} else {
					t.Logf("%v", ver)
				}
			default:
				t.Errorf("BumpPre(\"test\") = %T, want %T", ver, tt.want)
			}
		})
	}
}

func TestPrivateMakeVersion_Error(t *testing.T) {
	// makeVersion Should return expected When MakeOpt function returns an error
	wantVersion, _ := semver.Parse("0.0.1-test.1")
	var makeOptMock MakeOpt = func(version *Version) error {
		return makeOptError
	}

	gotVersion, gotError := makeVersion(wantVersion, makeOptMock)
	if gotVersion.Compare(wantVersion) != 0 {
		t.Errorf("Failed to return expected version")
	}
	if gotError != makeOptError {
		t.Errorf("Failed to return expected error")
	}
}

func TestPrivateMakeVersion(t *testing.T) {
	// makeVersion Should return expected When MakeOpt function has no error
	wantVersion, _ := semver.Parse("0.0.1-test.1")
	var makeOptMock MakeOpt = func(version *Version) error {
		return nil
	}

	gotVersion, gotError := makeVersion(wantVersion, makeOptMock)
	if gotVersion.Compare(wantVersion) != 0 {
		t.Errorf("Failed to return expected version")
	}
	if gotError != nil {
		t.Errorf("Failed returned error not expected")
	}
}

func TestMakeVersion(t *testing.T) {
	// MakeVersion Should return expected When version is prefixed with v
	versionStr := "v0.0.1-test.1"
	var makeOptMock MakeOpt = func(version *Version) error {
		return nil
	}

	gotVersion, gotError := MakeVersion(versionStr, makeOptMock)
	wantVersion, _ := semver.Parse("0.0.1-test.1")
	if gotVersion.Compare(wantVersion) != 0 {
		t.Errorf("Failed to return expected version")
	}
	if gotError != nil {
		t.Errorf("Failed returned error not expected")
	}
}

func TestGetEnv_Default(t *testing.T) {
	os.Unsetenv("KEY1")
	gotKey := GetEnv("KEY1", "DEFAULT")
	wantKey := "DEFAULT"
	if gotKey != wantKey {
		t.Errorf("Failed did not return default value")
	}
}

func TestGetEnv(t *testing.T) {
	defer os.Unsetenv("KEY1")
	gotError := os.Setenv("KEY1", "VALUE1")
	if gotError != nil {
		t.Errorf("Failed setting environment variable")
	}
	gotValue := GetEnv("KEY1", "DEFAULT")
	wantValue := "VALUE1"
	if gotValue != wantValue {
		t.Errorf("Failed did not return expected value")
	}
}
