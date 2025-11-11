#!/bin/bash
# Quick deployment script for HuggingFace Space

set -e

echo "🚀 LEMM HuggingFace Space Deployment"
echo "===================================="

# Check if Space name is provided
if [ -z "$1" ]; then
    echo "Usage: ./deploy_space.sh YOUR_USERNAME/space-name"
    echo "Example: ./deploy_space.sh john-doe/lemm-music-generator"
    exit 1
fi

SPACE_REPO="$1"
SPACE_URL="https://huggingface.co/spaces/$SPACE_REPO"

echo ""
echo "📦 Preparing files for Space: $SPACE_REPO"

# Create temporary directory
TEMP_DIR=$(mktemp -d)
echo "Using temp directory: $TEMP_DIR"

# Copy necessary files
echo "Copying files..."
cp app.py "$TEMP_DIR/"
cp requirements_space.txt "$TEMP_DIR/requirements.txt"
cp README_SPACE.md "$TEMP_DIR/README.md"
cp -r config "$TEMP_DIR/"
cp -r src "$TEMP_DIR/"

# Create .gitignore
cat > "$TEMP_DIR/.gitignore" << 'EOL'
__pycache__/
*.pyc
logs/
output/
models/ACE-Step-HF/
*.log
EOL

echo "✅ Files prepared"

# Clone or update Space repository
echo ""
echo "📥 Cloning Space repository..."
if [ -d "huggingface_space" ]; then
    echo "Removing existing huggingface_space directory..."
    rm -rf huggingface_space
fi

git clone "$SPACE_URL" huggingface_space || {
    echo "❌ Failed to clone Space. Make sure it exists and you have access."
    echo "Create it at: https://huggingface.co/new-space"
    exit 1
}

# Copy files to Space repo
echo ""
echo "📋 Copying files to Space repository..."
cp -r "$TEMP_DIR/"* huggingface_space/

# Commit and push
cd huggingface_space

echo ""
echo "📤 Committing and pushing to HuggingFace..."
git add .
git commit -m "Deploy LEMM v0.1.0" || echo "No changes to commit"
git push

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🌐 Your Space: $SPACE_URL"
echo ""
echo "⏳ Building... This may take 10-15 minutes."
echo "   Monitor progress at: $SPACE_URL"
echo ""
echo "📝 Next steps:"
echo "   1. Wait for build to complete"
echo "   2. Test the Space"
echo "   3. Upgrade to GPU if needed (Settings -> Hardware)"
echo ""

# Cleanup
cd ..
rm -rf "$TEMP_DIR"
