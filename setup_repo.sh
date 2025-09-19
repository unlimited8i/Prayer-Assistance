#!/bin/bash

# Navigate to the project directory
cd /Users/lmd8/Downloads/Prayer_Assistance

# Initialize Git repository
git init

# Add all files
git add .

# Make initial commit
git commit -m "Initial commit: Prayer Assistance Application

- Computer vision-based prayer tracking using MediaPipe
- Automatic prayer time fetching from Aladhan API
- Excel-based prayer logging system
- Pose detection for Rakah and Sajdah counting
- Manual completion fallback for camera issues
- Comprehensive error handling and user guidance"

echo "✅ Git repository initialized successfully!"
echo "📁 Repository location: $(pwd)"
echo "📋 Next steps:"
echo "1. Create a repository on GitHub/GitLab"
echo "2. Add remote origin: git remote add origin <your-repo-url>"
echo "3. Push to remote: git push -u origin main"
