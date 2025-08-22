"""
Command Line Interface for GitDecomposer.
"""

import argparse
import os
import sys
from pathlib import Path
import warnings

# Suppress FutureWarning from plotly
warnings.filterwarnings("ignore", category=FutureWarning)

# Add the package to Python path for development
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.rule import Rule
from rich.traceback import install as rich_traceback_install

# Install rich traceback handler
rich_traceback_install()

from gitdecomposer import GitMetrics, GitRepository


class CLI:
    """A class to encapsulate the command-line interface logic."""

    def __init__(self, args):
        """
        Initialize the CLI object.

        Args:
            args: Parsed command-line arguments.
        """
        self.args = args
        self.console = Console()
        self.repo_path = None
        self.output_dir = None
        self.git_repo = None
        self.metrics = None

    def run(self):
        """Execute the main analysis workflow."""
        try:
            self._setup_and_validate_paths()
            self._run_analysis()
        except Exception as e:
            self.console.print(f"[bold red]An unexpected error occurred: {e}[/bold red]")
            sys.exit(1)
        finally:
            if self.git_repo:
                self.git_repo.close()

    def _setup_and_validate_paths(self):
        """Validate repository path and set up output directory."""
        self.repo_path = Path(self.args.repository).resolve()
        if not self.repo_path.exists():
            self.console.print(f"[bold red]Error: Repository path '{self.repo_path}' does not exist[/bold red]")
            sys.exit(1)

        if not (self.repo_path / ".git").exists():
            self.console.print(f"[bold red]Error: '{self.repo_path}' is not a Git repository[/bold red]")
            sys.exit(1)

        self.output_dir = Path(self.args.output)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        if self.args.verbose:
            self.console.print(f"Output directory: {self.output_dir.resolve()}")

    def _run_analysis(self):
        """Run the core analysis and generate outputs."""
        if self.args.verbose:
            self.console.print(f"Initializing repository: {self.repo_path}")

        with self.console.status("[bold green]Analyzing repository...[/bold green]") as status:
            self.git_repo = GitRepository(str(self.repo_path))
            self.metrics = GitMetrics(self.git_repo)

            status.update("Generating repository summary...")
            summary = self.metrics.generate_repository_summary()
            if self.args.verbose:
                self.console.print(f"Summary result type: {type(summary)}, value: {summary}")

            if not summary or "error" in summary:
                error_msg = summary.get("error", "Unknown error") if summary else "Summary generation failed"
                self.console.print(f"[bold red]Error generating repository summary: {error_msg}[/bold red]")
                return

            self._display_summary(summary)

            if self.args.format in ["csv", "both"]:
                status.update("Exporting CSV files...")
                self._export_csv()

            if self.args.format in ["html", "both"] and not self.args.no_visualizations:
                self._create_visualizations()

            self._display_recommendations(summary)

            self.console.print(f"\n[bold green]Analysis complete! Results saved to: {self.output_dir.resolve()}[/bold green]")

    def _display_summary(self, summary):
        """Display the repository summary in a panel."""
        self.console.print(Rule("[bold]Repository Analysis Summary[/bold]"))
        
        repo_info = summary.get("repository_info", {})
        commits_info = summary.get("commits", {})
        contributors_info = summary.get("contributors", {})
        branches_info = summary.get("branches", {})

        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column(style="cyan")
        table.add_column()
        table.add_row("Repository:", str(repo_info.get('path', 'Unknown')))
        table.add_row("Active Branch:", repo_info.get('active_branch', 'Unknown'))
        table.add_row("Total Commits:", str(commits_info.get('total_commits', 0)))
        table.add_row("Contributors:", str(contributors_info.get('total_contributors', 0)))
        table.add_row("Branches:", str(branches_info.get('total_branches', 0)))
        table.add_row("Branching Model:", branches_info.get('branching_model', 'Unknown'))
        
        self.console.print(Panel(table, expand=False))

    def _export_csv(self):
        """Export metrics to CSV files."""
        csv_files = self.metrics.export_metrics_to_csv(str(self.output_dir))
        self.console.print(f"✓ Exported {len(csv_files)} CSV files")

    def _create_visualizations(self):
        """Create and save HTML visualizations."""
        self.console.print(Rule("[bold]Visualizations[/bold]"))
        
        visualizations_to_create = {
            "Commit Activity": (self.metrics.create_commit_activity_dashboard, "commit_activity.html"),
            "Contributor Analysis": (self.metrics.create_contributor_analysis_charts, "contributor_analysis.html"),
            "File Analysis": (self.metrics.create_file_analysis_visualization, "file_analysis.html"),
            "Enhanced File Analysis": (self.metrics.create_enhanced_file_analysis_dashboard, "enhanced_file_analysis.html"),
            "Executive Summary": (self.metrics.create_executive_summary_report, "executive_summary.html"),
        }

        with Progress(
            SpinnerColumn(),
            BarColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            task = progress.add_task("Creating visualizations...", total=len(visualizations_to_create))
            for name, (func, filename) in visualizations_to_create.items():
                progress.update(task, description=f"Creating {name}...")
                try:
                    path = self.output_dir / filename
                    func(str(path))
                    self.console.print(f"  ✓ Created: [link=file://{path.resolve()}]{path}[/link]")
                except Exception as e:
                    self.console.print(f"  ✗ Failed to create {name}: [red]{e}[/red]")
                progress.update(task, advance=1)
        
        # Generate the index page that links to all reports
        try:
            self.metrics.create_index_page_only(str(self.output_dir))
            index_path = self.output_dir / "index.html"
            self.console.print(f"  ✓ Created: [link=file://{index_path.resolve()}]index.html[/link] (Main Dashboard)")
        except Exception as e:
            self.console.print(f"  ✗ Failed to create index page: [red]{e}[/red]")

    def _display_recommendations(self, summary):
        """Display branching model recommendations."""
        branches_info = summary.get("branches", {})
        recommendations = branches_info.get("recommendations", [])
        if recommendations:
            self.console.print(Rule("[bold]Recommendations[/bold]"))
            for i, rec in enumerate(recommendations, 1):
                self.console.print(f"  {i}. {rec}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="GitDecomposer - Analyze Git repositories",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  gitdecomposer /path/to/repo
  gitdecomposer . --output ./analysis
  gitdecomposer /path/to/repo --format csv
        """,
    )

    parser.add_argument("repository", help="Path to the Git repository to analyze")

    parser.add_argument(
        "-o",
        "--output",
        default="./gitdecomposer_output",
        help="Output directory for analysis results (default: ./gitdecomposer_output)",
    )

    parser.add_argument(
        "--format",
        choices=["html", "csv", "both"],
        default="both",
        help="Output format (default: both)",
    )

    parser.add_argument(
        "--no-visualizations",
        action="store_true",
        help="Skip creating visualization files (faster analysis)",
    )

    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()
    cli_app = CLI(args)
    cli_app.run()


if __name__ == "__main__":
    main()
