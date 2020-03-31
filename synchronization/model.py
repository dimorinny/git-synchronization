from git import Remote, RemoteReference


class RemoteReferenceWithRemote:
    def __init__(self, remote: Remote, reference: RemoteReference):
        self.remote = remote
        self.reference = reference
