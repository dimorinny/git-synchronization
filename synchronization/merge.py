from typing import List

from git import Repo, RemoteReference

from .model import RemoteReferenceWithRemote


class Merger:

    def __init__(self, repository: Repo):
        self._git_repository = repository

    def merge(self, local_branch_name: str, references: List[RemoteReferenceWithRemote], fetch: bool):
        Merger._print_header(local_branch_name, references)

        if fetch:
            Merger._fetch_references(local_branch_name, references)

        if self._is_local_branch_identical_to_all_remote_references(
                local_branch_name=local_branch_name,
                references=references
        ):
            branch = self._get_local_branch_by_name(local_branch_name)

            if branch is None:
                reference_postfix = ''
            else:
                reference_postfix = f': {branch.commit}'

            print(f'Branch: {local_branch_name} has the same state in every remote and locally{reference_postfix}')
            Merger._print_footer(local_branch_name)
            return

        self._clear_current_branch()

        try:
            result_branch = self._create_local_branch_from_remote_reference(
                local_branch_name=local_branch_name,
                reference=references[0].reference
            )

            for reference in references:
                print(f'Rebase {result_branch} <- {reference.reference}')
                output = self._git_repository.git.rebase(reference.reference)
                print(output)
        finally:
            self._clear_current_branch()
            Merger._print_footer(local_branch_name)

    def _is_local_branch_identical_to_all_remote_references(
            self,
            local_branch_name: str,
            references: List[RemoteReferenceWithRemote]
    ) -> bool:
        references_to_compare = [reference.reference for reference in references]

        local_branch_reference = self._get_local_branch_by_name(local_branch_name)
        if local_branch_reference is None:
            return False

        references_to_compare.append(local_branch_reference)

        return len(set([reference.commit for reference in references_to_compare])) == 1

    def _get_local_branch_by_name(self, name):
        heads = self._git_repository.heads

        if name not in heads:
            return None

        return self._git_repository.heads[name]

    def _create_local_branch_from_remote_reference(self, local_branch_name: str, reference: RemoteReference):
        result_branch = self._git_repository.create_head(path=local_branch_name, commit=reference, force=True)
        result_branch.checkout(force=True)
        self._clear_current_branch()

        return result_branch

    # noinspection PyBroadException
    def _clear_current_branch(self):
        try:
            self._git_repository.git.rebase(abort=True)
        except Exception:
            pass

        try:
            self._git_repository.git.reset(hard=True)
        except Exception:
            pass

    # noinspection PyBroadException
    @staticmethod
    def _fetch_references(branch_name: str, references: List[RemoteReferenceWithRemote]):
        if len(references) > 0:
            print(f'Fetching remote references for branch: {branch_name}')

        for reference in references:
            remote = reference.remote
            try:
                for info in remote.fetch(refspec=branch_name):
                    print(f'Updating reference: {branch_name} for remote: {remote.name} info: {info}')
            except Exception as e:
                print(f'Failed to prefetch reference from remote: {remote.name} branch: {branch_name}. Error: {e}')

        print()

    @staticmethod
    def _print_header(local_branch_name: str, references: List[RemoteReferenceWithRemote]):
        joined_references = ', '.join([f'{reference.reference.name}' for reference in references])
        print(Merger._get_header(local_branch_name))
        print(f'References to merge: {joined_references}')
        print()

    @staticmethod
    def _print_footer(local_branch_name: str):
        print('=' * len(Merger._get_header(local_branch_name)))
        print()

    @staticmethod
    def _get_header(local_branch_name: str) -> str:
        return f'============================ {local_branch_name} ============================'
