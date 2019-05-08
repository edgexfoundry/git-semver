module github.com/edgexfoundry/git-semver

require (
	github.com/blang/semver v3.5.1+incompatible
	github.com/otiai10/copy v1.0.1
	github.com/otiai10/curr v0.0.0-20150429015615-9b4961190c95 // indirect
	gopkg.in/src-d/go-git.v4 v4.10.0
)

// UNCOMMENT BEFORE BUILDING TO MAKE src-d/go-git WORK FOR SSH URLS BEHIND A SOCKS PROXY
// replace gopkg.in/src-d/go-git.v4 => github.com/src-d/go-git v0.0.0-20190502205309-e17ee112ca6c
