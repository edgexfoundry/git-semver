// Copyright (c) 2020 Intel Corporation
//
// SPDX-License-Identifier: Apache-2.0

package scope

import (
	"fmt"
	"errors"
	"github.com/blang/semver"
	"testing"
)

var (
	bumpReadError  = errors.New("Read Error")
	__ReadVersion  = _ReadVersion
	__WriteVersion = _WriteVersion
)

func TestBump_ReadVersionError(t *testing.T) {
	// Bump Should return error When ReadVersion error
	myExtentMock := &Extent{}
	svExtentMock := &Extent{}
	defer func() {
		_ReadVersion = __ReadVersion
	}()
	_ReadVersion = func(my, sv *Extent) (Version, error) {
		return Version{}, bumpReadError
	}
	gotError := Bump(myExtentMock, svExtentMock, "major", "")
	if gotError != bumpReadError {
		t.Errorf("Failed to return expected error")
	}
}

func TestBump_Major(t *testing.T) {
	// Bump Should return WriteVersion result When bumping major axis
	myExtentMock := &Extent{}
	svExtentMock := &Extent{}
	defer func() {
		_ReadVersion = __ReadVersion
	}()
	_ReadVersion = ReadVersionMock("1.2.3-dev.4")
	defer func() {
		_WriteVersion = __WriteVersion
	}()
	_WriteVersion = WriteVersionMock
	gotError := Bump(myExtentMock, svExtentMock, "major", "")
	if gotError.Error() != "WriteVersion 2.0.0" {
		t.Errorf("Failed WriteVersion did not receive expected arguments")
	}
}

func TestBump_Minor(t *testing.T) {
	// Bump Should return WriteVersion result When bumping minor axis
	myExtentMock := &Extent{}
	svExtentMock := &Extent{}
	defer func() {
		_ReadVersion = __ReadVersion
	}()
	_ReadVersion = ReadVersionMock("1.2.3-dev.4")
	defer func() {
		_WriteVersion = __WriteVersion
	}()
	_WriteVersion = WriteVersionMock
	gotError := Bump(myExtentMock, svExtentMock, "minor", "")
	if gotError.Error() != "WriteVersion 1.3.0" {
		t.Errorf("Failed WriteVersion did not receive expected arguments")
	}
}

func TestBump_Patch(t *testing.T) {
	// Bump Should return WriteVersion result When bumping patch axis
	myExtentMock := &Extent{}
	svExtentMock := &Extent{}
	defer func() {
		_ReadVersion = __ReadVersion
	}()
	_ReadVersion = ReadVersionMock("1.2.3-dev.4")
	defer func() {
		_WriteVersion = __WriteVersion
	}()
	_WriteVersion = WriteVersionMock
	gotError := Bump(myExtentMock, svExtentMock, "patch", "")
	if gotError.Error() != "WriteVersion 1.2.4" {
		t.Errorf("Failed WriteVersion did not receive expected arguments")
	}
}

func TestBump_Final(t *testing.T) {
	// Bump Should return WriteVersion result When bumping final axis
	myExtentMock := &Extent{}
	svExtentMock := &Extent{}
	defer func() {
		_ReadVersion = __ReadVersion
	}()
	_ReadVersion = ReadVersionMock("1.2.3-dev.4")
	defer func() {
		_WriteVersion = __WriteVersion
	}()
	_WriteVersion = WriteVersionMock
	gotError := Bump(myExtentMock, svExtentMock, "final", "")
	if gotError.Error() != "WriteVersion 1.2.3" {
		t.Errorf("Failed WriteVersion did not receive expected arguments")
	}
}

func TestBump_PreDev(t *testing.T) {
	// Bump Should return WriteVersion result When bumping pre axis with pre override with same name
	myExtentMock := &Extent{}
	svExtentMock := &Extent{}
	defer func() {
		_ReadVersion = __ReadVersion
	}()
	_ReadVersion = ReadVersionMock("1.2.3-dev.4")
	defer func() {
		_WriteVersion = __WriteVersion
	}()
	_WriteVersion = WriteVersionMock
	gotError := Bump(myExtentMock, svExtentMock, "pre", "dev")
	if gotError.Error() != "WriteVersion 1.2.3-dev.5" {
		t.Errorf("Failed WriteVersion did not receive expected arguments")
	}
}

func TestBump_PreOverride(t *testing.T) {
	// Bump Should return WriteVersion result When bumping pre axis with pre override with different name
	myExtentMock := &Extent{}
	svExtentMock := &Extent{}
	defer func() {
		_ReadVersion = __ReadVersion
	}()
	_ReadVersion = ReadVersionMock("1.2.3-dev.4")
	defer func() {
		_WriteVersion = __WriteVersion
	}()
	_WriteVersion = WriteVersionMock
	gotError := Bump(myExtentMock, svExtentMock, "pre", "pre")
	if gotError.Error() != "WriteVersion 1.2.3-pre.1" {
		t.Errorf("Failed WriteVersion did not receive expected arguments")
	}
}

func TestBump_PreNoPre(t *testing.T) {
	// Bump Should return WriteVersion result When bumping pre axis with no pre
	myExtentMock := &Extent{}
	svExtentMock := &Extent{}
	defer func() {
		_ReadVersion = __ReadVersion
	}()
	_ReadVersion = ReadVersionMock("1.2.3")
	defer func() {
		_WriteVersion = __WriteVersion
	}()
	_WriteVersion = WriteVersionMock
	gotError := Bump(myExtentMock, svExtentMock, "pre", "")
	if gotError.Error() != "WriteVersion 1.2.4-pre.1" {
		t.Errorf("Failed WriteVersion did not receive expected arguments")
	}
}

func TestBump_PrePre(t *testing.T) {
	// Bump Should return WriteVersion result When bumping pre axis with pre no override
	myExtentMock := &Extent{}
	svExtentMock := &Extent{}
	defer func() {
		_ReadVersion = __ReadVersion
	}()
	_ReadVersion = ReadVersionMock("1.2.3-dev.1")
	defer func() {
		_WriteVersion = __WriteVersion
	}()
	_WriteVersion = WriteVersionMock
	gotError := Bump(myExtentMock, svExtentMock, "pre", "")
	fmt.Printf("%v\n", gotError)
	if gotError.Error() != "WriteVersion 1.2.3-dev.2" {
		t.Errorf("Failed WriteVersion did not receive expected arguments")
	}
}

func TestBump_PreBug(t *testing.T) {
	// Bump Should return WriteVersion result When bumping pre axis with no pre and override
	myExtentMock := &Extent{}
	svExtentMock := &Extent{}
	defer func() {
		_ReadVersion = __ReadVersion
	}()
	_ReadVersion = ReadVersionMock("1.2.3")
	defer func() {
		_WriteVersion = __WriteVersion
	}()
	_WriteVersion = WriteVersionMock
	gotError := Bump(myExtentMock, svExtentMock, "pre", "bug")
	if gotError.Error() != "WriteVersion 1.2.4-bug.1" {
		t.Errorf("Failed WriteVersion did not receive expected arguments")
	}
}

func TestBump_NotSupported(t *testing.T) {
	// Bump Should return error When bumping unsupported axis
	myExtentMock := &Extent{}
	svExtentMock := &Extent{}
	defer func() {
		_ReadVersion = __ReadVersion
	}()
	_ReadVersion = ReadVersionMock("1.2.3-dev.4")
	defer func() {
		_WriteVersion = __WriteVersion
	}()
	_WriteVersion = WriteVersionMock
	gotError := Bump(myExtentMock, svExtentMock, "notsupported", "")
	if gotError == nil {
		t.Errorf("Failed to return expected error")
	}
}

func TestBump(t *testing.T) {
	// Table-Driven tests for Bump containing most of the test cases above
	myExtentMock := &Extent{}
	svExtentMock := &Extent{}
	tests := []struct {
		name       	string
		versionStr	string
		axis		string
		pre			string
		wantError	string
	}{
		{
			name: "Bump Should return WriteVersion result When bumping major axis",
			versionStr: "1.2.3-dev.4",
			axis: "major",
			pre: "",
			wantError: "WriteVersion 2.0.0",
		}, {
			name: "Bump Should return WriteVersion result When bumping minor axis",
			versionStr: "1.2.3-dev.4",
			axis: "minor",
			pre: "",
			wantError: "WriteVersion 1.3.0",
		}, {
			name: "Bump Should return WriteVersion result When bumping patch axis",
			versionStr: "1.2.3-dev.4",
			axis: "patch",
			pre: "",
			wantError: "WriteVersion 1.2.4",
		}, {
			name: "Bump Should return WriteVersion result When bumping final axis",
			versionStr: "1.2.3-dev.4",
			axis: "final",
			pre: "",
			wantError: "WriteVersion 1.2.3",
		}, {
			name: "Bump Should return WriteVersion result When bumping pre axis with pre override with same name",
			versionStr: "1.2.3-dev.4",
			axis: "pre",
			pre: "dev",
			wantError: "WriteVersion 1.2.3-dev.5",
		}, {
			name: "Bump Should return WriteVersion result When bumping pre axis with pre override with different name",
			versionStr: "1.2.3-dev.4",
			axis: "pre",
			pre: "pre",
			wantError: "WriteVersion 1.2.3-pre.1",
		}, {
			name: "Bump Should return WriteVersion result When bumping pre axis with no pre",
			versionStr: "1.2.3",
			axis: "pre",
			pre: "",
			wantError: "WriteVersion 1.2.4-pre.1",
		}, {
			name: "Bump Should return WriteVersion result When bumping pre axis with pre no override",
			versionStr: "1.2.3-dev.1",
			axis: "pre",
			pre: "",
			wantError: "WriteVersion 1.2.3-dev.2",
		}, {
			name: "Bump Should return WriteVersion result When bumping pre axis with no pre and override",
			versionStr: "1.2.3",
			axis: "pre",
			pre: "bug",
			wantError: "WriteVersion 1.2.4-bug.1",
		},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			defer func() {
				_ReadVersion = __ReadVersion
			}()
			_ReadVersion = ReadVersionMock(test.versionStr)
			defer func() {
				_WriteVersion = __WriteVersion
			}()
			_WriteVersion = WriteVersionMock
			gotError := Bump(myExtentMock, svExtentMock, test.axis, test.pre)
			if gotError.Error() != test.wantError {
				t.Errorf("Failed WriteVersion did not receive expected arguments")
			}
		})
	}
}

func ReadVersionMock(versionStr string) func(my, sv *Extent) (Version, error) {
	f := func(my, sv *Extent) (Version, error) {
		version, _ := semver.Parse(versionStr)
		return version, nil
	}
	return f
}

func WriteVersionMock(my, sv *Extent, ver Version) error {
	return errors.New(
		fmt.Sprintf("WriteVersion %v", ver))
}