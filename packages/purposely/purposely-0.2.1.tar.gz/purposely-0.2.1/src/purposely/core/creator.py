"""
Document creator for Purposely.

This module handles the creation of documents from templates.
"""

import json
from pathlib import Path
import click
from .renderer import TemplateRenderer


class DocumentCreator:
    """
    Creates documents from templates.

    Reads configuration from .purposely/config.json and creates
    documents in the docs/ directory using the appropriate language.
    """

    def __init__(self, project_root: Path = None):
        """
        Initialize DocumentCreator.

        Args:
            project_root: Root directory of the project (default: current directory)
        """
        self.project_root = project_root or Path.cwd()
        self.config_path = self.project_root / '.purposely' / 'config.json'
        self.docs_path = self.project_root / 'docs'
        self.scripts_path = self.project_root / 'scripts'

        # Load configuration
        if not self.config_path.exists():
            raise click.ClickException(
                "Not a Purposely project. Run 'purposely init' first."
            )

        with open(self.config_path) as f:
            self.config = json.load(f)

        self.lang = self.config.get('language', 'en')
        self.renderer = TemplateRenderer(self.lang)

    def create_rules(self, force: bool = False) -> Path:
        """
        Create RULES.md in .purposely/ directory.

        Args:
            force: Overwrite if file already exists

        Returns:
            Path to created file
        """
        output_path = self.config_path.parent / 'RULES.md'

        if output_path.exists() and not force:
            raise click.ClickException(
                f"File already exists: {output_path}\n"
                f"Use --force to overwrite."
            )

        # Render template (language-agnostic, rules are technical)
        content = self.renderer.render('RULES.md')

        # Write file
        output_path.write_text(content, encoding='utf-8')

        return output_path

    def create_global_purpose(self, force: bool = False) -> Path:
        """
        Create GLOBAL_PURPOSE.md in docs/ directory.

        Args:
            force: Overwrite if file already exists

        Returns:
            Path to created file
        """
        output_path = self.docs_path / 'GLOBAL_PURPOSE.md'

        if output_path.exists() and not force:
            raise click.ClickException(
                f"File already exists: {output_path}\n"
                f"Use --force to overwrite."
            )

        # Render template
        content = self.renderer.render('GLOBAL_PURPOSE.md')

        # Write file
        output_path.write_text(content, encoding='utf-8')

        return output_path

    def create_spec(self, phase: str, force: bool = False) -> Path:
        """
        Create 00_SPEC.md for a phase.

        Args:
            phase: Phase number (e.g., '01', '02')
            force: Overwrite if file already exists

        Returns:
            Path to created file
        """
        phase_dir = self.docs_path / f'phase-{phase}'
        phase_dir.mkdir(parents=True, exist_ok=True)

        # Also create corresponding scripts directory for this phase
        scripts_phase_dir = self.scripts_path / f'phase-{phase}'
        scripts_phase_dir.mkdir(parents=True, exist_ok=True)

        output_path = phase_dir / '00_SPEC.md'

        if output_path.exists() and not force:
            raise click.ClickException(
                f"File already exists: {output_path}\n"
                f"Use --force to overwrite."
            )

        # Render template with phase context
        content = self.renderer.render(
            '00_SPEC.md',
            phase=phase,
            phase_number=phase,
            phase_name=''  # Will be filled by user
        )

        # Write file
        output_path.write_text(content, encoding='utf-8')

        # Update current phase in config
        self.config['current_phase'] = phase
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

        return output_path

    def create_research_overview(self, phase: str, force: bool = False) -> Path:
        """
        Create research overview document (01_00_RESEARCH_OVERVIEW.md).

        Args:
            phase: Phase number (e.g., '01', '02')
            force: Overwrite if file already exists

        Returns:
            Path to created file
        """
        phase_dir = self.docs_path / f'phase-{phase}'

        if not phase_dir.exists():
            raise click.ClickException(
                f"Phase directory does not exist: {phase_dir}\n"
                f"Create SPEC first with 'purposely create spec {phase}'"
            )

        output_path = phase_dir / '01_00_RESEARCH_OVERVIEW.md'

        if output_path.exists() and not force:
            raise click.ClickException(
                f"File already exists: {output_path}\n"
                f"Use --force to overwrite."
            )

        # Render template
        content = self.renderer.render(
            '01_RESEARCH_OVERVIEW.md',
            phase=phase,
            phase_number=phase
        )

        # Write file
        output_path.write_text(content, encoding='utf-8')

        return output_path

    def create_research(self, phase: str, number: str, title: str, force: bool = False) -> Path:
        """
        Create research document (01_XX_RESEARCH_*.md).

        Args:
            phase: Phase number (e.g., '01', '02')
            number: Research document number (e.g., '01', '02')
            title: Title/topic of research
            force: Overwrite if file already exists

        Returns:
            Path to created file
        """
        phase_dir = self.docs_path / f'phase-{phase}'

        if not phase_dir.exists():
            raise click.ClickException(
                f"Phase directory does not exist: {phase_dir}\n"
                f"Create SPEC first with 'purposely create spec {phase}'"
            )

        # Create filename with title
        safe_title = title.replace(' ', '_').replace('/', '_')
        output_path = phase_dir / f'01_{number}_RESEARCH_{safe_title}.md'

        if output_path.exists() and not force:
            raise click.ClickException(
                f"File already exists: {output_path}\n"
                f"Use --force to overwrite."
            )

        # Render template
        content = self.renderer.render(
            '01_RESEARCH.md',
            phase=phase,
            phase_number=phase,
            topic=title
        )

        # Write file
        output_path.write_text(content, encoding='utf-8')

        return output_path

    def create_design_overview(self, phase: str, force: bool = False) -> Path:
        """
        Create design overview document (02_00_DESIGN_OVERVIEW.md).

        Args:
            phase: Phase number (e.g., '01', '02')
            force: Overwrite if file already exists

        Returns:
            Path to created file
        """
        phase_dir = self.docs_path / f'phase-{phase}'

        if not phase_dir.exists():
            raise click.ClickException(
                f"Phase directory does not exist: {phase_dir}\n"
                f"Create SPEC first with 'purposely create spec {phase}'"
            )

        output_path = phase_dir / '02_00_DESIGN_OVERVIEW.md'

        if output_path.exists() and not force:
            raise click.ClickException(
                f"File already exists: {output_path}\n"
                f"Use --force to overwrite."
            )

        # Render template
        content = self.renderer.render(
            '02_DESIGN_OVERVIEW.md',
            phase=phase,
            phase_number=phase
        )

        # Write file
        output_path.write_text(content, encoding='utf-8')

        return output_path

    def create_design_detail(self, phase: str, number: str, title: str, force: bool = False) -> Path:
        """
        Create detailed design document (02_XX_DESIGN_*.md).

        Args:
            phase: Phase number (e.g., '01', '02')
            number: Design document number (e.g., '01', '02')
            title: Title/component name
            force: Overwrite if file already exists

        Returns:
            Path to created file
        """
        phase_dir = self.docs_path / f'phase-{phase}'

        if not phase_dir.exists():
            raise click.ClickException(
                f"Phase directory does not exist: {phase_dir}\n"
                f"Create SPEC first with 'purposely create spec {phase}'"
            )

        # Create filename with title
        safe_title = title.replace(' ', '_').replace('/', '_')
        output_path = phase_dir / f'02_{number}_DESIGN_{safe_title}.md'

        if output_path.exists() and not force:
            raise click.ClickException(
                f"File already exists: {output_path}\n"
                f"Use --force to overwrite."
            )

        # Render template
        content = self.renderer.render(
            '0X_DESIGN_DETAIL.md',
            phase=phase,
            phase_number=phase,
            component_name=title
        )

        # Write file
        output_path.write_text(content, encoding='utf-8')

        return output_path

    def create_plan(self, phase: str, force: bool = False) -> Path:
        """
        Create implementation plan (03_PLAN.md).

        Args:
            phase: Phase number (e.g., '01', '02')
            force: Overwrite if file already exists

        Returns:
            Path to created file
        """
        phase_dir = self.docs_path / f'phase-{phase}'

        if not phase_dir.exists():
            raise click.ClickException(
                f"Phase directory does not exist: {phase_dir}\n"
                f"Create SPEC first with 'purposely create spec {phase}'"
            )

        output_path = phase_dir / '03_PLAN.md'

        if output_path.exists() and not force:
            raise click.ClickException(
                f"File already exists: {output_path}\n"
                f"Use --force to overwrite."
            )

        # Render template
        content = self.renderer.render(
            '03_PLAN.md',
            phase=phase,
            phase_number=phase
        )

        # Write file
        output_path.write_text(content, encoding='utf-8')

        return output_path

    def create_implementation(self, phase: str, force: bool = False) -> Path:
        """
        Create implementation log (04_IMPLEMENTATION.md).

        Args:
            phase: Phase number (e.g., '01', '02')
            force: Overwrite if file already exists

        Returns:
            Path to created file
        """
        phase_dir = self.docs_path / f'phase-{phase}'

        if not phase_dir.exists():
            raise click.ClickException(
                f"Phase directory does not exist: {phase_dir}\n"
                f"Create SPEC first with 'purposely create spec {phase}'"
            )

        output_path = phase_dir / '04_IMPLEMENTATION.md'

        if output_path.exists() and not force:
            raise click.ClickException(
                f"File already exists: {output_path}\n"
                f"Use --force to overwrite."
            )

        # Render template
        content = self.renderer.render(
            '04_IMPLEMENTATION.md',
            phase=phase,
            phase_number=phase
        )

        # Write file
        output_path.write_text(content, encoding='utf-8')

        return output_path
