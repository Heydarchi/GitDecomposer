"""
Example of how to use the new class-based plotting interface.
"""
from .base import BasePlotter
from .commit import CommitPlotter
from .contributor import ContributorPlotter
from .file import FilePlotter
from .technical_debt import TechnicalDebtPlotter


class PlotterFactory:
    """
    Factory class to create plotters with a consistent interface.
    """
    
    @staticmethod
    def create_all_plotters(metrics_coordinator):
        """
        Create all available plotters.
        
        Args:
            metrics_coordinator: GitMetrics instance for data access.
            
        Returns:
            dict: Dictionary of plotter name to plotter instance
        """
        return {
            'commit': CommitPlotter(metrics_coordinator),
            'contributor': ContributorPlotter(metrics_coordinator),
            'file': FilePlotter(metrics_coordinator),
            'technical_debt': TechnicalDebtPlotter(metrics_coordinator),
        }
    
    @staticmethod
    def get_plotter_info(plotter: BasePlotter):
        """
        Get information about a plotter.
        
        Args:
            plotter: An instance of BasePlotter
            
        Returns:
            dict: Plotter information
        """
        return {
            'title': plotter.title,
            'description': plotter.description,
            'class_name': plotter.__class__.__name__
        }


def generate_all_reports_with_new_interface(metrics_coordinator, output_dir: str):
    """
    Example function showing how to use the new class-based interface.
    
    Args:
        metrics_coordinator: GitMetrics instance
        output_dir (str): Directory to save reports
    """
    from pathlib import Path
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Create all plotters
    plotters = PlotterFactory.create_all_plotters(metrics_coordinator)
    
    # Generate reports
    report_info = {}
    for name, plotter in plotters.items():
        try:
            # Generate the report
            save_path = output_path / f"{name}_analysis.html"
            fig = plotter.create_visualization(str(save_path))
            
            # Store report information
            report_info[name] = {
                'title': plotter.title,
                'description': plotter.description,
                'file_path': str(save_path),
                'success': True
            }
            print(f"✓ Generated {plotter.title}: {save_path}")
            
        except Exception as e:
            report_info[name] = {
                'title': plotter.title,
                'description': plotter.description,
                'error': str(e),
                'success': False
            }
            print(f"✗ Failed to generate {plotter.title}: {e}")
    
    return report_info
