// Copyright (c) 2020 Intel Corporation
//
// SPDX-License-Identifier: Apache-2.0

package scope

import (
	"io"
	"errors"
	"github.com/blang/semver"
	"gopkg.in/src-d/go-billy.v4/memfs"
	"gopkg.in/src-d/go-git.v4"
	"testing"
)

var (
	readError  = errors.New("Read Error")
	__ioutilReadAll = ioutilReadAll
)

func TestReadVersion_OpenError(t *testing.T) {
	// ReadVersion Should return expected When Open returns an error
	myExtentMock := &Extent{
		Branch: "testbranch",
	}
	svExtentMock := &Extent{
		Tree: &git.Worktree{
			Filesystem: memfs.New(),
		},
	}

	gotVersion, gotError := ReadVersion(myExtentMock, svExtentMock)
	if gotVersion.Compare(Version{}) != 0 {
		t.Errorf("Failed to return expected version")
	}
	if gotError.Error() != "file does not exist" {
		t.Errorf("Failed to return expected error")
	}
}

func TestReadVersion_ReadAllError(t *testing.T) {
	// ReadVersion Should return expected When ReadAll returns an error
	myExtentMock := &Extent{
		Branch: "testbranch",
	}
	memFs := memfs.New()
	svExtentMock := &Extent{
		Tree: &git.Worktree{
			Filesystem: memFs,
		},
	}
	memFs.Create("testbranch")
	defer func() {
		ioutilReadAll = __ioutilReadAll
	}()
	ioutilReadAll = func(r io.Reader) ([]byte, error) {
		return nil, readError
	}
	gotVersion, gotError := ReadVersion(myExtentMock, svExtentMock)
	if gotVersion.Compare(Version{}) != 0 {
		t.Errorf("Failed to return expected version")
	}
	if gotError != readError {
		t.Errorf("Failed to return expected error")
	}
}

func TestReadVersion(t *testing.T) {
	// ReadVersion Should return expected When no error
	myExtentMock := &Extent{
		Branch: "testbranch",
	}
	memFs := memfs.New()
	svExtentMock := &Extent{
		Tree: &git.Worktree{
			Filesystem: memFs,
		},
	}
	file, _ := memFs.Create("testbranch")
	data := []byte("0.0.1-test.1")
	file.Write(data)
	file.Close()
	gotVersion, gotError := ReadVersion(myExtentMock, svExtentMock)
	wantVersion, _ := semver.Parse("0.0.1-test.1")
	if gotVersion.Compare(wantVersion) != 0 {
		t.Errorf("Failed to return expected version")
	}
	if gotError != nil {
		t.Errorf("Failed returned error not expected")
	}
}
