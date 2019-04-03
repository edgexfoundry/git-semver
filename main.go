// Copyright (c) 2019 Intel Corporation
//
// SPDX-License-Identifier: Apache-2.0

package main

import (
	"flag"
	"fmt"
	"log"
	"os"
	"strings"

	"github.com/dweomer/git-semver/scope"
)

var (
	dir   string
	cli   = flag.NewFlagSet("git-semver", flag.ExitOnError)
	_init = flag.NewFlagSet("git-semver-init", flag.ExitOnError)
	_bump = flag.NewFlagSet("git-semver-bump", flag.ExitOnError)
	_tag  = flag.NewFlagSet("git-semver-tag", flag.ExitOnError)
	_push = flag.NewFlagSet("git-semver-push", flag.ExitOnError)
	pre   string
)

func init() {
	log.SetFlags(0)
	if gd, ok := os.LookupEnv("GIT_DIR"); ok {
		dir = gd
	} else {
		if wd, err := os.Getwd(); err != nil {
			log.Fatalf("%s: %v", cli.Name(), err)
		} else {
			dir = wd
		}
	}

	cli.Usage = func() {
		fmt.Fprintf(cli.Output(), "Usage:  %s [flags] [commands] (default: write current value to stdout)", cli.Name())
		fmt.Fprintln(cli.Output())
		cli.PrintDefaults()
		for _, sub := range []*flag.FlagSet{_init, _bump, _tag, _push} {
			nam := strings.Split(sub.Name(), "-")[2]
			out := sub.Output()
			fmt.Fprintln(out)
			switch nam {
			case "init":
				fmt.Fprintf(out, "  %s\t(initialize the worktree location)", nam)
			case "bump":
				fmt.Fprintf(out, "  %s\tmajor|minor|patch|pre|final", nam)
			case "tag":
				fmt.Fprintf(out, "  %s\t(apply semver tag)", nam)
			case "push":
				fmt.Fprintf(out, "  %s\t(push semver branch to the remote)", nam)
			}
		}
		fmt.Fprintln(cli.Output())
	}

	_bump.StringVar(&pre, "pre", "", "the pre-release prefix (defaults to 'pre' if not specified when bumping 'pre')")

	if err := cli.Parse(os.Args[1:]); err != nil {
		fail(err, cli.Usage)
	}

	if cli.NArg() > 0 {
		switch sub := fmt.Sprintf("%s-%s", cli.Name(), cli.Arg(0)); sub {
		case _init.Name():
			if err := _init.Parse(cli.Args()[1:]); err != nil {
				fail(err, _init.Usage)
			}
		case _bump.Name():
			if err := _bump.Parse(cli.Args()[1:]); err != nil {
				fail(err, _bump.Usage)
			}
		case _tag.Name():
			if err := _tag.Parse(cli.Args()[1:]); err != nil {
				fail(err, _tag.Usage)
			}
		case _push.Name():
			if err := _push.Parse(cli.Args()[1:]); err != nil {
				fail(err, _push.Usage)
			}
		default:
			fail(fmt.Errorf("%s: %q is not a recognized command", cli.Name(), cli.Arg(0)), cli.Usage)
		}
	}
}

func main() {
	var (
		cmd = cli.Name()
		err error
		my  *scope.Extent
		sv  *scope.Extent
	)

	if my, err = scope.Open(dir); err != nil {
		log.Fatalf("%s: %v", cmd, err)
	}
	if sv, err = scope.Init(my, _init.Parsed()); err != nil {
		log.Fatalf("%s: %v", cmd, err)
	}

	switch {
	case _bump.Parsed():
		// do 'git-semver bump'
		cmd = _bump.Name()

		if _bump.NArg() != 1 {
			log.Fatalf("%s: %v", cmd, fmt.Errorf("axis is required"))
		}
		if err = scope.Bump(my, sv, _bump.Args()[0], pre); err != nil {
			log.Fatalf("%s: %v", cmd, err)
		}
	case _tag.Parsed():
		// do 'git-semver tag'
		cmd = _tag.Name()

		if err = scope.Tag(my, sv); err != nil {
			log.Fatalf("%s: %v", cmd, err)
		}
		// do 'git-semver push'
	case _push.Parsed():
		if err = scope.Push(my, sv); err != nil {
			log.Fatalf("%s: %v", cmd, fmt.Errorf("failed to push: %v", err))
		}
	default:
		if ver, err := scope.ReadVersion(my, sv); err != nil {
			log.Fatalf("%s: %v", cmd, err)
		} else {
			fmt.Fprintln(os.Stdout, ver)
		}
	}
}

func fail(err error, usage func()) {
	fmt.Fprintln(os.Stderr, err)
	if usage != nil {
		usage()
	}
	os.Exit(1)
}
