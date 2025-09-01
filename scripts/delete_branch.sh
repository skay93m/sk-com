#!/bin/bash

# Safe Branch Deletion Script
# Usage: ./delete_branch.sh <branch-name> "<reason>"

BRANCH_NAME=$1
REASON=$2
CURRENT_DATE=$(date +%Y-%m-%d)
CURRENT_USER=$(git config user.name)

if [ -z "$BRANCH_NAME" ] || [ -z "$REASON" ]; then
    echo "Usage: $0 <branch-name> '<reason for deletion>'"
    echo "Example: $0 feature/old-feature 'Feature completed and merged'"
    exit 1
fi

# Check if branch exists
if ! git show-ref --verify --quiet refs/heads/$BRANCH_NAME; then
    echo "Error: Branch '$BRANCH_NAME' does not exist locally"
    exit 1
fi

# Get last commit info
LAST_COMMIT=$(git log -1 --format="%h - %s" $BRANCH_NAME)

# Check if branch is merged
if git merge-base --is-ancestor $BRANCH_NAME HEAD; then
    STATUS="merged"
else
    STATUS="unmerged"
    echo "Warning: Branch '$BRANCH_NAME' is not merged into current branch"
    read -p "Are you sure you want to delete this unmerged branch? (y/N): " confirm
    if [[ $confirm != [yY] ]]; then
        echo "Deletion cancelled"
        exit 0
    fi
fi

# Log the deletion
echo "" >> docs/BRANCH_DELETION_LOG.md
echo "### $CURRENT_DATE" >> docs/BRANCH_DELETION_LOG.md
echo "" >> docs/BRANCH_DELETION_LOG.md
echo "Branch: $BRANCH_NAME" >> docs/BRANCH_DELETION_LOG.md
echo "Deleted by: $CURRENT_USER" >> docs/BRANCH_DELETION_LOG.md
echo "Reason: $REASON" >> docs/BRANCH_DELETION_LOG.md
echo "Last commit: $LAST_COMMIT" >> docs/BRANCH_DELETION_LOG.md
echo "Status: $STATUS" >> docs/BRANCH_DELETION_LOG.md
echo "" >> docs/BRANCH_DELETION_LOG.md

# Delete local branch
echo "Deleting local branch '$BRANCH_NAME'..."
if [ "$STATUS" = "merged" ]; then
    git branch -d $BRANCH_NAME
else
    git branch -D $BRANCH_NAME
fi

# Delete remote branch if it exists
if git show-ref --verify --quiet refs/remotes/origin/$BRANCH_NAME; then
    echo "Deleting remote branch 'origin/$BRANCH_NAME'..."
    git push origin --delete $BRANCH_NAME
fi

echo "Branch '$BRANCH_NAME' deleted successfully and logged."
echo "Reason: $REASON"
