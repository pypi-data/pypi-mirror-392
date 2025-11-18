"""
FinOps Dashboard HTML Exporter

Captures Rich CLI dashboard output to standalone HTML for:
- Playwright screenshot generation
- Executive presentation materials
- Archived dashboard snapshots
- Web-based sharing

Author: CloudOps-Runbooks
Version: 1.1.20
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from rich.console import Console


class DashboardHTMLExporter:
    """Export FinOps dashboard output to standalone HTML."""

    def __init__(self, output_dir: str = "artifacts/screenshots"):
        """
        Initialize HTML exporter.

        Args:
            output_dir: Directory for HTML exports (default: artifacts/screenshots)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Rich console with recording enabled
        self.console = Console(
            record=True,
            width=120,  # Standard terminal width for readability
            force_terminal=True,  # Preserve Rich formatting
            color_system="truecolor"  # Full color support
        )

    def get_recording_console(self) -> Console:
        """
        Get the recording console for dashboard rendering.

        Returns:
            Console instance with recording enabled
        """
        return self.console

    def export_html(
        self,
        profile: str,
        include_timestamp: bool = True,
        custom_filename: Optional[str] = None
    ) -> Path:
        """
        Export captured console output to HTML.

        Args:
            profile: AWS profile name for filename
            include_timestamp: Include timestamp in filename (default: True)
            custom_filename: Optional custom filename (overrides default naming)

        Returns:
            Path to exported HTML file

        Example:
            >>> exporter = DashboardHTMLExporter()
            >>> console = exporter.get_recording_console()
            >>> # ... render dashboard to console ...
            >>> html_path = exporter.export_html(profile="prod")
            >>> print(f"HTML exported to: {html_path}")
        """
        # Generate filename
        if custom_filename:
            filename = custom_filename
        else:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S") if include_timestamp else ""
            filename = f"finops-dashboard-{profile}"
            if timestamp:
                filename += f"-{timestamp}"
            filename += ".html"

        html_path = self.output_dir / filename

        # Export HTML with inline styles for portability
        html_content = self.console.export_html(
            theme=None,  # Use default Rich theme
            clear=False,  # Keep recording for multiple exports
            inline_styles=True,  # Embed CSS for standalone HTML
            code_format="<pre style=\"font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace\">{code}</pre>"
        )

        # Add executive dashboard metadata
        html_with_metadata = self._add_metadata(html_content, profile)

        # Write HTML file
        html_path.write_text(html_with_metadata, encoding='utf-8')

        return html_path

    def _add_metadata(self, html_content: str, profile: str) -> str:
        """
        Add metadata to HTML export for better executive presentation.

        Args:
            html_content: Original HTML from Rich console
            profile: AWS profile name

        Returns:
            HTML with enhanced metadata
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Inject metadata header
        metadata_header = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="FinOps Dashboard - AWS Profile: {profile}">
    <meta name="generated" content="{timestamp}">
    <title>FinOps Dashboard - {profile} - {timestamp}</title>
    <style>
        body {{
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', 'source-code-pro', monospace;
            background-color: #0c0c0c;
            color: #cccccc;
            padding: 20px;
            margin: 0;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 20px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
            font-weight: 600;
        }}
        .header p {{
            margin: 5px 0 0 0;
            opacity: 0.9;
            font-size: 14px;
        }}
        .dashboard-content {{
            background-color: #1e1e1e;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }}
        pre {{
            margin: 0;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🏢 FinOps Executive Dashboard</h1>
        <p>AWS Profile: <strong>{profile}</strong> | Generated: {timestamp}</p>
    </div>
    <div class="dashboard-content">
"""

        footer = """
    </div>
</body>
</html>
"""

        # Extract body content from Rich HTML (remove Rich's default wrapper)
        if "<body" in html_content:
            # Extract content between <body> tags
            start = html_content.find("<body")
            start = html_content.find(">", start) + 1
            end = html_content.rfind("</body>")
            body_content = html_content[start:end]
        else:
            body_content = html_content

        return metadata_header + body_content + footer

    def clear_recording(self):
        """Clear console recording buffer (useful for multiple exports in same session)."""
        # Create new console to reset recording
        self.console = Console(
            record=True,
            width=120,
            force_terminal=True,
            color_system="truecolor"
        )


def export_dashboard_html(
    console: Console,
    profile: str,
    output_dir: str = "artifacts/screenshots"
) -> Path:
    """
    Convenience function to export dashboard HTML from existing console.

    Args:
        console: Rich Console instance with recorded output
        profile: AWS profile name
        output_dir: Output directory for HTML file

    Returns:
        Path to exported HTML file

    Example:
        >>> from rich.console import Console
        >>> console = Console(record=True)
        >>> console.print("[bold]Dashboard Output[/bold]")
        >>> html_path = export_dashboard_html(console, profile="prod")
    """
    output_dir_path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"finops-dashboard-{profile}-{timestamp}.html"
    html_path = output_dir_path / filename

    # Export HTML
    html_content = console.export_html(
        theme=None,
        clear=False,
        inline_styles=True
    )

    # Add metadata wrapper
    exporter = DashboardHTMLExporter(output_dir=output_dir)
    html_with_metadata = exporter._add_metadata(html_content, profile)

    # Write file
    html_path.write_text(html_with_metadata, encoding='utf-8')

    return html_path
