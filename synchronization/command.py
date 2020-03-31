import re
from typing import Dict, List

from git import Repo, RemoteReference, Remote

from .merge import Merger
from .model import RemoteReferenceWithRemote


class Command:
    HEAD = 'HEAD'

    def __init__(self, repository: str, fetch: bool = False, **filters):
        self._git_repository = Repo(repository)
        self._fetch = fetch
        self._git_merger = Merger(self._git_repository)

        # Origin name -> branch name to sync pattern
        self._branch_filters = {}

        for origin, pattern in filters.items():
            self._branch_filters[origin] = re.compile(pattern)

    def sync(self):
        if self._git_repository.bare:
            raise Exception(f'Bare repository isn\'t supported. Repository: {self._git_repository}')

        self._log_remotes()

        # Branch name -> All related remote branches to sync
        remotes: Dict[str, List[RemoteReferenceWithRemote]] = {}

        def add_remote(remote_reference: RemoteReferenceWithRemote, reference_name: str):
            if reference_name not in remotes:
                remotes[reference_name] = []

            remotes[reference_name].append(remote_reference)

        for remote in self._git_repository.remotes:
            for reference in remote.refs:
                reference_branch_name = self._get_local_branch_name_from_reference(
                    remote=remote.name,
                    reference=reference
                )

                if reference_branch_name == Command.HEAD:
                    continue

                if not self._synchronize_branch_for_remote(
                        branch_name=reference_branch_name,
                        remote=remote
                ):
                    continue

                add_remote(
                    remote_reference=RemoteReferenceWithRemote(
                        remote=remote,
                        reference=reference
                    ),
                    reference_name=reference_branch_name
                )

        for branch_name, references in remotes.items():
            self._git_merger.merge(
                local_branch_name=branch_name,
                references=references,
                fetch=self._fetch
            )

    def _log_remotes(self):
        print('===============================================================')
        print(f'Working dir: {self._git_repository.working_tree_dir}')
        for remote in self._git_repository.remotes:
            print(f'{remote}: {remote.url}')
        print('===============================================================')
        print()

    def _synchronize_branch_for_remote(self, branch_name: str, remote: Remote) -> bool:
        remote_pattern = self._branch_filters.get(remote.name, None)

        if remote_pattern is None:
            return True

        return remote_pattern.match(branch_name) is not None

    @staticmethod
    def _get_local_branch_name_from_reference(remote: str, reference: RemoteReference):
        remote_branch_prefix = f'{remote}/'

        if not reference.name.startswith(remote_branch_prefix):
            raise Exception(f'Failed to get local branch name from reference: {reference.name}')

        return reference.name[len(remote_branch_prefix):]
