#!/bin/bash

# Navigate to the directory where your git repository is located
# (uncomment the next line if needed to navigate to a specific directory)
# cd /path/to/your/git/repository

# Stage all changes (added, modified, deleted)
git add -A

# Commit with the specified message
git commit -m "Automated Commit By Centurion"

# Push the changes to the origin
git push origin

# Optionally, print a success message
echo "Changes have been committed and pushed successfully."
