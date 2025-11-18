class GitSnapError(Exception):
    """Base exception for gitsnap errors."""
    pass

class GitRepositoryError(GitSnapError):
    """Raised when there is an error with the git repository."""
    pass

class NoChangesError(GitSnapError):
    """Raised when there are no changes to snapshot."""
    pass

class RepositoryNotInitializedError(GitSnapError):
    """Raised when the directory is not a git repository."""
    pass
