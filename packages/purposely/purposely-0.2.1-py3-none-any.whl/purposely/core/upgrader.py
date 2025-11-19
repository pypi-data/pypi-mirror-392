"""
Project upgrade logic.

This module handles upgrading existing Purposely projects to new versions:
- Updates .claude/ folder (slash commands and instructions)
- Updates config.json with new version
- Preserves user's documents and settings
"""

import json
from pathlib import Path
from importlib import resources
import click
from .. import __version__


class Upgrader:
    """
    Handles Purposely project upgrades.

    Responsibilities:
    1. Check if project exists
    2. Compare versions
    3. Update .claude/ folder with new templates
    4. Update config version
    5. Show what was updated
    """

    def __init__(self, force: bool = False):
        """
        Initialize the Upgrader.

        Args:
            force: If True, upgrade even if already at latest version
        """
        self.force = force
        self.project_root = Path.cwd()
        self.config_path = self.project_root / '.purposely' / 'config.json'
        self.docs_path = self.project_root / 'docs'
        self.claude_path = self.project_root / '.claude'

    def run(self):
        """
        Execute the upgrade workflow.
        """
        click.echo("🔄 Checking for Purposely updates...\n")

        # Step 1: Check if project exists
        if not self._check_project_exists():
            return

        # Step 2: Load current version
        current_version = self._get_current_version()

        # Step 3: Check if upgrade needed
        if not self._needs_upgrade(current_version):
            return

        # Step 4: Update .claude/ folder
        self._update_claude_folder()

        # Step 5: Update config version
        self._update_config_version()

        # Step 6: Show summary
        self._show_summary(current_version)

    def _check_project_exists(self) -> bool:
        """
        Check if this is a Purposely project.
        """
        if not self.config_path.exists():
            click.echo("❌ Not a Purposely project!")
            click.echo("   Run 'purposely init' first\n")
            return False
        return True

    def _get_current_version(self) -> str:
        """
        Get current version from config.json.
        """
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config.get('version', '0.0.0')

    def _needs_upgrade(self, current_version: str) -> bool:
        """
        Check if upgrade is needed.
        """
        if current_version == __version__ and not self.force:
            click.echo(f"✅ Already at latest version: {__version__}")
            click.echo("   Nothing to update!\n")
            click.echo("💡 Use --force to reinstall templates\n")
            return False

        if self.force:
            click.echo(f"⚠️  Force mode: Reinstalling templates\n")
        else:
            click.echo(f"📦 Upgrade available:")
            click.echo(f"   Current: {current_version}")
            click.echo(f"   Latest:  {__version__}\n")

        return True

    def _update_claude_folder(self):
        """
        Update .claude/ folder with new slash commands and instructions.

        Preserves user's documents but updates templates.
        """
        # Create backup
        backup_path = self.claude_path.parent / '.claude.backup'
        if self.claude_path.exists() and not backup_path.exists():
            import shutil
            shutil.copytree(self.claude_path, backup_path)
            click.echo(f"💾 Backup created: {backup_path}")

        # Create .claude directory structure
        self.claude_path.mkdir(parents=True, exist_ok=True)
        commands_path = self.claude_path / 'commands'
        commands_path.mkdir(parents=True, exist_ok=True)

        # Get package resource path
        claude_template = resources.files('purposely') / 'templates' / '.claude'

        # Update instructions.md
        instructions_src = claude_template / 'instructions.md'
        instructions_dst = self.claude_path / 'instructions.md'
        instructions_dst.write_text(instructions_src.read_text(encoding='utf-8'), encoding='utf-8')

        # Update all slash command files
        commands_src = claude_template / 'commands'
        command_count = 0
        updated_commands = []
        for cmd_file in commands_src.iterdir():
            if cmd_file.suffix == '.md':
                dst_file = commands_path / cmd_file.name
                dst_file.write_text(cmd_file.read_text(encoding='utf-8'), encoding='utf-8')
                command_count += 1
                updated_commands.append(cmd_file.stem)

        click.echo(f"\n✅ Updated .claude folder:")
        click.echo(f"   ├─ instructions.md")
        click.echo(f"   └─ commands/ ({command_count} slash commands)")

        # Show which commands were updated
        if updated_commands:
            click.echo(f"\n📝 Updated commands:")
            for cmd in sorted(updated_commands):
                click.echo(f"   - /{cmd}")

    def _update_config_version(self):
        """
        Update version in config.json while preserving other settings.
        """
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        config['version'] = __version__

        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        click.echo(f"\n✅ Updated config version to {__version__}")

    def _show_summary(self, old_version: str):
        """
        Show upgrade summary.
        """
        click.echo(f"\n🎉 Upgrade complete!")
        click.echo(f"   {old_version} → {__version__}\n")
        click.echo("📌 What was updated:")
        click.echo("   ✓ Slash commands (.claude/commands/)")
        click.echo("   ✓ Instructions (.claude/instructions.md)")
        click.echo("   ✓ Config version (.purposely/config.json)\n")
        click.echo("📝 Your documents were preserved:")
        click.echo("   ✓ docs/GLOBAL_PURPOSE.md")
        click.echo("   ✓ docs/phase-*/\n")
        click.echo("💡 New features are now available in Claude Code!")
