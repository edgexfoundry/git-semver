package scope_test

import (
	"fmt"

	"github.com/edgexfoundry/git-semver/scope"
)

func ExampleBumpFinal() {
	ver, err := scope.MakeVersion("1.2.3-dev.4", scope.BumpFinal())
	if err != nil {
		fmt.Printf("%s", err)
	} else {
		fmt.Printf("%s", ver)
	}
	// Output: 1.2.3
}

func ExampleBumpMajor() {
	ver, err := scope.MakeVersion("1.2.3-dev.4", scope.BumpMajor())
	if err != nil {
		fmt.Printf("%s", err)
	} else {
		fmt.Printf("%s", ver)
	}
	// Output: 2.0.0
}

func ExampleBumpMinor() {
	ver, err := scope.MakeVersion("1.2.3-dev.4", scope.BumpMinor())
	if err != nil {
		fmt.Printf("%s", err)
	} else {
		fmt.Printf("%s", ver)
	}
	// Output: 1.3.0
}

func ExampleBumpPatch() {
	ver, err := scope.MakeVersion("1.2.3-dev.4", scope.BumpPatch())
	if err != nil {
		fmt.Printf("%s", err)
	} else {
		fmt.Printf("%s", ver)
	}
	// Output: 1.2.4
}
func ExampleBumpPre_dev() {
	ver, err := scope.MakeVersion("1.2.3-dev.4", scope.BumpPre("dev"))
	if err != nil {
		fmt.Printf("%s", err)
	} else {
		fmt.Printf("%s", ver)
	}
	// Output: 1.2.3-dev.5
}

func ExampleBumpPre_pre() {
	ver, err := scope.MakeVersion("1.2.3-dev.4", scope.BumpPre("pre"))
	if err != nil {
		fmt.Printf("%s", err)
	} else {
		fmt.Printf("%s", ver)
	}
	// Output: 1.2.3-pre.1
}
