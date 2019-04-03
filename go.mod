module github.com/dweomer/git-semver

require (
	github.com/blang/semver v3.5.1+incompatible
	github.com/otiai10/copy v1.0.1
	gopkg.in/src-d/go-git.v4 v4.10.0
)

// UNCOMMENT BEFORE BUILDING TO MAKE src-d/go-git WORK FOR SSH URLS BEHIND A SOCKS PROXY
// replace gopkg.in/src-d/go-git.v4 v4.10.0 => github.com/dweomer/go-git v0.0.0-20190319204522-c7d3d2a65c77
