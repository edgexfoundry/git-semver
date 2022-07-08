## Functional Tests

| Command | Test |
| --- | --- |
| init | SHOULD set version WHEN no version set and version specified |
| init | SHOULD set default version 0.0.0 WHEN no version set and no version specified |
| init | SHOULD do nothing WHEN version set and version specified |
| init | SHOULD set version WHEN version set and version and force specified |
| init | SHOULD fail WHEN invalid version is specified |
| init | SHOULD set remote version WHEN branch does not exist |
| init | SHOULD do nothing WHEN setting same version |
| bump | SHOULD bump major WHEN bump major |
| bump | SHOULD bump minor WHEN bump minor |
| bump | SHOULD bump patch WHEN bump patch |
| bump | SHOULD bump pre WHEN bump pre |
| bump | SHOULD bump pre with prefix WHEN bump pre prefix |
| bump | SHOULD bump final WHEN bump final |
| tag | SHOULD tag head with version WHEN head is not tagged |
| tag | SHOULD fail WHEN head is already tagged |
| tag | SHOULD tag head with version WHEN head is already tagged and force |
| push | SHOULD push semver and tags WHEN push |
| base | SHOULD display version WHEN version set |
| base | SHOULD fail WHEN version not set |
| all | SHOULD work WHEN using SSH proxy |
| all | SHOULD work WHEN using no SSH proxy |

## Execution
```
chown root:root /root/.ssh/config
eval `ssh-agent`
ssh-add
ssh -T git@github.com

export SEMVER_PRE_PREFIX=dev

cd /repo

git semver
ERROR: the semver branch does not exist

git semver init
0.0.0

git semver init --version=1.0.0-dev.1 --force
1.0.0-dev.1

git semver
1.0.0-dev.1

git semver push
1.0.0-dev.1

rm -rf .semver

git semver
ERROR: the semver branch does not exist

git semver init
1.0.0-dev.1

git semver
1.0.0-dev.1

git semver tag
1.0.0-dev.1

git semver bump pre
1.0.0-dev.2

git semver push
1.0.0-dev.2

git semver tag
ERROR: head fd394b046cc5e5223f04d5a42dc951bed3f47850 is already tagged with v1.0.0-dev.1

git semver tag --force
1.0.0-dev.2

git semver bump pre
1.0.0-dev.3

git semver push
1.0.0-dev.3

rm -rf .semver

git semver
ERROR: the semver branch does not exist

git semver init
1.0.0-dev.3

git semver
1.0.0-dev.3

git semver bump pre
1.0.0-dev.4

git semver bump pre --prefix=rc
ERROR: mismatch between current prerelease dev and bump rc - use init to set version with different prerelease

git semver bump patch
1.0.1

git semver bump minor
1.1.0

git semver bump major
2.0.0

git semver bump pre --prefix=tst
2.0.0-tst.1

git semver bump pre
ERROR: mismatch between current prerelease tst and bump dev - use init to set version with different prerelease

export SEMVER_PRE_PREFIX=tst

git semver bump pre
2.0.0-tst.2

git semver bump final
2.0.0
```