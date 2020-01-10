from typing import Dict, List

from git import Repo, RemoteReference


class Command:
    HEAD = 'HEAD'

    def __init__(self, repository: str):
        self._git_repository = Repo(repository)

    def sync(self):
        if self._git_repository.bare:
            raise Exception(f'Bare repository isn\'t supported. Repository: {self._git_repository}')

        self._log_remotes()

        # Branch name -> All references with that branch name
        remotes: Dict[str, List[RemoteReference]] = {}

        def add_remote(remote_reference: RemoteReference, reference_name: str):
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

                add_remote(
                    remote_reference=reference,
                    reference_name=reference_branch_name
                )

        for branch_name, references in remotes.items():
            self._rebase_remotes_branches_to_local(
                branch_name=branch_name,
                references=references
            )

    def _rebase_remotes_branches_to_local(self, branch_name: str, references: List[RemoteReference]):
        header = f'============================ {branch_name} ============================'
        footer = '=' * len(header)

        print(header)
        first_reference = references[0]

        self._clear_current_branch()

        try:
            result_branch = self._git_repository.create_head(path=branch_name, commit=first_reference, force=True)
            result_branch.checkout(force=True)
            self._clear_current_branch()

            for reference in references:
                print(f'Rebase {result_branch} <- {reference}')
                output = self._git_repository.git.rebase(reference)
                print(output)
        finally:
            self._clear_current_branch()

            print(footer)
            print('')

    def _log_remotes(self):
        print('===============================================================')
        print(f'Working dir: {self._git_repository.working_tree_dir}')
        for remote in self._git_repository.remotes:
            print(f'{remote}: {remote.url}')
        print('===============================================================')
        print()

    # noinspection PyBroadException
    def _clear_current_branch(self):
        try:
            self._git_repository.git.rebase(abort=True)
        except Exception:
            pass

        try:
            self._git_repository.git.reset(abort=True)
        except Exception:
            pass

    @staticmethod
    def _get_local_branch_name_from_reference(remote: str, reference: RemoteReference):
        remote_branch_prefix = f'{remote}/'

        if not reference.name.startswith(remote_branch_prefix):
            raise Exception(f'Failed to get local branch name from reference: {reference.name}')

        return reference.name[len(remote_branch_prefix):]
