---
source_id: KB-GIT-001
title: Git Version Control and Collaborative Workflow
skill: git
topic: Developer Tools & Version Control
difficulty: Beginner to Intermediate
prerequisites: Basic command-line usage
keywords: [git, github, version control, branching, merge, rebase, pull request, commit]
---

# Git Version Control and Collaborative Workflow

## Overview
Git is a distributed version control system tracking changes in source code during software development. It enables non-linear workflows through branching, distributed repositories, and cryptographic integrity verification.

## Core Concepts
- **Repository Lifecycle & States**: Working directory, Staging Area (index), and Git repository (`.git`); file states (untracked, modified, staged, committed).
- **Core Commands**: `git init`, `git status`, `git add`, `git commit -m`, `git diff`, and `git log --oneline --graph`.
- **Branching Strategies**: Creating branches (`git branch`, `git checkout -b`, `git switch -c`), feature branch workflows, and trunk-based development.
- **Integrating Changes**: `git merge` (fast-forward vs 3-way merge commits) vs `git rebase` (linear commit history); understanding when to rebase vs merge.
- **Resolving Merge Conflicts**: Identifying conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`), editing resolution files, and staging resolved states.
- **Remote Collaboration**: Remote repositories (`origin`), `git clone`, `git fetch`, `git pull`, `git push`, tracking upstream branches, and Pull Request (PR) review conventions.
- **Undoing Mistakes**: `git restore` for discarded changes, `git reset` (soft vs hard), and `git revert` for safe history-preserving rollback.

## Learning Objectives
1. Manage local code changes across working, staging, and commit areas with atomic commits.
2. Execute feature branch workflows, resolve merge conflicts methodically, and produce clean commit histories.
3. Collaborate with remote team repositories using pull requests, code reviews, and remote branch tracking.
4. Safely revert faulty commits without corrupting shared history.

## Practice Projects
- **Team Simulation Repository**: Initialize a Git repository, create multiple feature branches making conflicting edits to a single file, and resolve the merge conflict cleanly while keeping a clear commit history.
- **Git History Hygiene**: Set up an interactive rebase (`git rebase -i`) to squash small typo commits, reword commit messages to adhere to Conventional Commits standards, and push to a remote repository.
