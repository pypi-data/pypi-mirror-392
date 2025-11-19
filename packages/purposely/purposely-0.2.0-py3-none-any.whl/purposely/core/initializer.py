"""
Project initialization logic.

This module handles the creation of:
- Configuration files (.purposely/config.json)
- Directory structure (docs/, .claude/)
- Template files (copying from package resources)
"""

import json
import shutil
from pathlib import Path
from typing import Optional
from importlib import resources
import click
from .. import __version__


class Initializer:
    """
    Handles Purposely project initialization.

    Responsibilities:
    1. Check for existing project
    2. Create configuration file
    3. Create directory structure
    4. Copy Claude Code folder (.claude/)
    5. Display next steps to user
    """

    def __init__(self, lang: str = 'en', force: bool = False):
        """
        Initialize the Initializer.

        Args:
            lang: Language code ('en' or 'ko')
            force: If True, overwrite existing project
        """
        self.lang = lang
        self.force = force
        self.project_root = Path.cwd()
        self.config_path = self.project_root / '.purposely' / 'config.json'
        self.docs_path = self.project_root / 'docs'
        self.claude_path = self.project_root / '.claude'

    def run(self):
        """
        Execute the initialization workflow.
        """
        click.echo("🚀 Initializing Purposely project...\n")

        # Step 1: Check existing
        self._check_existing()

        # Step 2: Create config
        self._create_config()

        # Step 3: Create directories
        self._create_directories()

        # Step 4: Copy .claude/ folder
        self._copy_claude_folder()

        # Step 5: Show next steps
        self._show_next_steps()

    def _check_existing(self):
        """
        Check if project already exists and handle force flag.
        """
        if self.config_path.exists():
            if not self.force:
                click.echo("⚠️  Purposely project already exists!")
                click.echo(f"   Config found: {self.config_path}")
                click.echo("\n💡 Use --force to reinitialize")
                raise click.Abort()
            else:
                click.echo("⚠️  Force mode: Overwriting existing project\n")

    def _create_config(self):
        """
        Create .purposely/config.json with language setting.
        """
        config_dir = self.config_path.parent
        config_dir.mkdir(parents=True, exist_ok=True)

        config = {
            "version": __version__,
            "language": self.lang,
            "current_phase": None
        }

        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        click.echo(f"✅ Created config: {self.config_path}")
        click.echo(f"   Language: {self.lang}\n")

    def _create_directories(self):
        """
        Create docs/ directory structure.
        """
        self.docs_path.mkdir(parents=True, exist_ok=True)
        click.echo(f"✅ Created directory: {self.docs_path}\n")

    def _copy_claude_folder(self):
        """
        Copy .claude/ folder from package resources to project.

        Uses importlib.resources to copy slash commands and instructions.
        """
        # Create .claude directory structure
        self.claude_path.mkdir(parents=True, exist_ok=True)
        commands_path = self.claude_path / 'commands'
        commands_path.mkdir(parents=True, exist_ok=True)

        # Get package resource path
        claude_template = resources.files('purposely') / 'templates' / '.claude'

        # Copy instructions.md
        instructions_src = claude_template / 'instructions.md'
        instructions_dst = self.claude_path / 'instructions.md'
        instructions_dst.write_text(instructions_src.read_text(encoding='utf-8'), encoding='utf-8')

        # Copy all slash command files
        commands_src = claude_template / 'commands'
        command_count = 0
        for cmd_file in commands_src.iterdir():
            if cmd_file.suffix == '.md':
                dst_file = commands_path / cmd_file.name
                dst_file.write_text(cmd_file.read_text(encoding='utf-8'), encoding='utf-8')
                command_count += 1

        click.echo(f"✅ Created .claude folder: {self.claude_path}")
        click.echo(f"   ├─ instructions.md")
        click.echo(f"   └─ commands/ ({command_count} slash commands)\n")

    def _show_next_steps(self):
        """
        Display next steps to the user.
        """
        click.echo("🎉 Purposely project initialized successfully!\n")
        click.echo("📝 Next steps:")
        click.echo("   1. Run '/purposely-init' to create GLOBAL_PURPOSE.md")
        click.echo("   2. Define your project's core purpose")
        click.echo("   3. Run '/purposely-phase' to start Phase 1\n")
        click.echo("💡 All slash commands are available in Claude Code")
        click.echo(f"   Commands location: {self.claude_path / 'commands'}\n")
