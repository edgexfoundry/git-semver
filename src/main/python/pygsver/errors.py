

class GitSemverError(Exception):
    """ base class for all package exceptions
    """
    pass


class PrereleaseMismatchError(GitSemverError):
    """ thrown if mismatch between current prerelease version and bump prefix
    """
    pass


class InvalidPathError(GitSemverError):
    """ thrown if semver path is not a directory
    """


class InvalidBranchError(GitSemverError):
    """ thrown if semver branch is invalid
    """
    pass


class InvalidRepoError(GitSemverError):
    """ thrown if semver path is not a git repo
    """
    pass


class HeadTaggedError(GitSemverError):
    """ thrown if head is already tagged with a semantic version
    """
    pass


class BranchDoesNotExistError(GitSemverError):
    """ thrown if semver branch does not exist
    """
    pass


class EmptyVersionError(GitSemverError):
    """ thrown if version file in semver branch is empty
    """
    pass
