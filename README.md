For making two-way repositories synchronization you should:

* Initialize git repository: `git init`
* Add remotes, that you're going to synchronize between each others:

```bash
git remote add origin git@bitbucket.org:merkurevd/synchronize.git
git remote add second git@bitbucket.org:merkurevd/second-synchronize.git
```

* Fetch remote branches: `git fetch --all`

* Synchronize all remotes branch into local ones using this package:
```bash
➜ git-synchronization sync --repository="<path-to-repo>"

===============================================================
Working dir: /home/dimorinny/Documents/Project/Python/git-synchronization/synchronize
origin: git@bitbucket.org:merkurevd/synchronize.git
second: git@bitbucket.org:merkurevd/second-synchronize.git
===============================================================

============================ master ============================
Rebase master <- origin/master
Current branch master is up to date.
Rebase master <- second/master
First, rewinding head to replay your work on top of it...
Applying: init
Applying: init
Applying: init
================================================================

============================ synchronize-common ============================
Rebase synchronize-common <- origin/synchronize-common
Current branch synchronize-common is up to date.
Rebase synchronize-common <- second/synchronize-common
First, rewinding head to replay your work on top of it...
Applying: init
Applying: init
============================================================================

============================ synchronize-specific ============================
Rebase synchronize-specific <- origin/synchronize-specific
Current branch synchronize-specific is up to date.
==============================================================================
```

* As a result, your local branches will be results of rebasing all remote branches with the same names.
Then you should just push it to remotes:
```bash
git push --all --force origin
git push --all --force second
```