
import os
import shutil
import tempfile
from datetime import datetime

def create_project_archive():
    """Create a simple archive of all project files"""
    
    # Files to include in the download
    important_files = [
        "main.py",
        "dashboard.py", 
        "admin_dashboard.py",
        "setup.py",
        "achievements.py",
        "customization.py",
        "test_system.py",
        "utils.py",
        "data.py",
        "bracket.py",
        "team_builder.py",
        "live_match.py",
        "pyproject.toml",
        ".replit",
        "README.md"
    ]
    
    # Data files to include
    data_files = [
        "stats.json",
        "matches.json",
        "tournaments.json",
        "queue.json",
        "match_history.json",
        "mvp_votes.json",
        "teams.json",
        "player_profiles.json",
        "admin_settings.json"
    ]
    
    # Create a temporary directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = f"octanecore_bot_{timestamp}"
    
    print(f"📦 Creating project archive: {archive_name}")
    print("=" * 50)
    
    # Create directory structure
    os.makedirs(archive_name, exist_ok=True)
    os.makedirs(f"{archive_name}/data", exist_ok=True)
    
    copied_files = 0
    
    # Copy main files
    for file in important_files:
        if os.path.exists(file):
            try:
                shutil.copy2(file, archive_name)
                print(f"✅ Copied: {file}")
                copied_files += 1
            except Exception as e:
                print(f"❌ Failed to copy {file}: {e}")
        else:
            print(f"⚠️  File not found: {file}")
    
    # Copy data files
    for file in data_files:
        if os.path.exists(file):
            try:
                shutil.copy2(file, f"{archive_name}/data/")
                print(f"✅ Copied data: {file}")
                copied_files += 1
            except Exception as e:
                print(f"❌ Failed to copy data {file}: {e}")
        else:
            print(f"⚠️  Data file not found: {file}")
    
    # Create a simple README for the archive
    readme_content = f"""# OctaneCore Bot Archive
Created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Files Included
- Main bot files: {len([f for f in important_files if os.path.exists(f)])}
- Data files: {len([f for f in data_files if os.path.exists(f)])}
- Total files: {copied_files}

## Setup Instructions
1. Install Python 3.11+
2. Install dependencies: pip install discord.py flask pillow python-dotenv
3. Set up your bot token in environment variables
4. Run: python main.py

## File Structure
- main.py - Main bot file
- dashboard.py - Interactive dashboards
- admin_dashboard.py - Admin controls
- setup.py - Server setup automation
- data/ - All bot data files

## Notes
- Remember to configure your bot token
- Set up LOG_CHANNEL_ID for logging
- Admin permissions required for setup commands
"""
    
    with open(f"{archive_name}/README.md", "w") as f:
        f.write(readme_content)
    
    print("=" * 50)
    print(f"✅ Archive created: {archive_name}/")
    print(f"📁 Total files copied: {copied_files}")
    print(f"📖 README created with setup instructions")
    print("\n💡 You can now copy this folder to your local machine!")
    print("💡 All files are in plain text format for easy transfer")
    
    return archive_name

if __name__ == "__main__":
    create_project_archive()
