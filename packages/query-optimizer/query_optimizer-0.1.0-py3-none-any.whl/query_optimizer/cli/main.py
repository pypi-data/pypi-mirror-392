# src/query_optimizer/cli/main.py
import click
import sys
import time
from urllib.parse import urlparse
from rich.console import Console
from rich.table import Table
from rich.live import Live
from dotenv import load_dotenv

from ..core.analyzer import DatabaseAdapter
from ..adapters.postgres import PostgresAdapter
from ..adapters.mysql import MySQLAdapter
from ..core.models import ExecutionPlan, IndexSuggestion, ScanType, DatabaseType
from ..core.optimizer import Optimizer

console = Console()

def get_adapter(connection_string: str) -> DatabaseAdapter:
    """Factory to create appropriate database adapter"""
    parsed = urlparse(connection_string)
    scheme = parsed.scheme.lower()
    
    adapters = {
        'postgresql': PostgresAdapter,
        'postgres': PostgresAdapter,
        'mysql': MySQLAdapter,
        'mysql+mysqlconnector': MySQLAdapter,
    }
    
    if scheme not in adapters:
        console.print(f"[red]Error:[/red] Unsupported database scheme: '{scheme}'. Supported: {', '.join(adapters.keys())}")
        sys.exit(1)
    
    return adapters[scheme](connection_string)

@click.group()
@click.version_option(version='0.1.0')
def cli():
    """Universal SQL Query Optimizer - Analyze, optimize, and monitor slow queries."""
    load_dotenv()

@cli.command()
@click.argument('query', type=str)
@click.option('--db', '-d', 'connection_string', envvar='DB_CONNECTION_STRING',
              required=True, help='Database connection string (or set DB_CONNECTION_STRING).')
@click.option('--analyze/--no-analyze', 'run_analyze', default=True,
              help='Run with actual execution stats (ANALYZE).')
def analyze(query, connection_string, run_analyze):
    """Analyze a SQL query and display the execution plan and suggestions."""
    adapter = None
    try:
        adapter = get_adapter(connection_string)
        adapter.connect()
        
        with console.status("[yellow]Analyzing query...[/yellow]"):
            plan = adapter.explain_query(query, analyze=run_analyze)
        
        display_plan(plan)
        
        suggestions = adapter.suggest_indexes(plan)
        if suggestions:
            display_suggestions(suggestions)
        else:
            console.print("\n[green]✓ No immediate index suggestions found.[/green]")
        
    except Exception as e:
        console.print(f"\n[red]An error occurred:[/red] {e}")
        sys.exit(1)
    finally:
        if adapter:
            adapter.close()

def display_plan(plan: ExecutionPlan):
    """Display execution plan in a rich table format."""
    console.print(f"\n[bold]Execution Plan Analysis ({plan.database_type.value})[/bold]")
    
    summary_table = Table(show_header=False, box=None)
    summary_table.add_row("Total Estimated Cost:", f"[yellow]{plan.total_cost:.2f}[/yellow]")
    if plan.total_time_ms > 0:
        summary_table.add_row("Actual Execution Time:", f"[yellow]{plan.total_time_ms:.2f} ms[/yellow]")
    console.print(summary_table)

    if plan.table_scans:
        table = Table(title="\nTable Access Patterns", expand=True)
        table.add_column("Table", style="cyan", no_wrap=True)
        table.add_column("Scan Type", style="magenta")
        table.add_column("Rows Examined", justify="right")
        table.add_column("Rows Returned", justify="right")
        table.add_column("Cost", justify="right")
        table.add_column("Filter", style="default")
        
        for scan in plan.table_scans:
            scan_style = "bold red" if scan.scan_type == ScanType.SEQUENTIAL else "green"
            table.add_row(
                scan.table_name,
                f"[{scan_style}]{scan.scan_type.value}[/{scan_style}]",
                f"{scan.rows_examined:,}",
                f"{scan.rows_returned:,}",
                f"{scan.cost:.2f}",
                (scan.filter_conditions[0] if scan.filter_conditions else "N/A")[:70]
            )
        console.print(table)
    
    if plan.warnings:
        console.print("\n[bold red]⚠️ Performance Warnings:[/bold red]")
        for warning in plan.warnings:
            console.print(f"  • {warning}")

def display_suggestions(suggestions: list[IndexSuggestion]):
    """Display optimization suggestions."""
    console.print("\n[bold green]✨ Optimization Suggestions[/bold green]")
    for i, suggestion in enumerate(suggestions, 1):
        table = Table(title=f"[cyan]Suggestion {i}: Add Index on '{suggestion.table_name}'[/cyan]", show_header=False, box=None)
        table.add_row("[bold]Columns:[/bold]", f"{', '.join(suggestion.columns)}")
        table.add_row("[bold]Rationale:[/bold]", suggestion.rationale)
        table.add_row("[bold]SQL:[/bold]", f"[yellow]{suggestion.create_statement}[/yellow]")
        console.print(table)

@cli.command()
@click.argument('query_file', type=click.Path(exists=True, readable=True))
@click.option('--db', '-d', 'connection_string', envvar='DB_CONNECTION_STRING',
              required=True, help='Database connection string.')
@click.option('--apply', is_flag=True, help='Apply suggested optimizations automatically.')
def optimize(query_file, connection_string, apply):
    """Analyze a query from a file and optionally apply optimizations."""
    with open(query_file) as f:
        query = f.read()
    
    console.print(f"[bold]Optimizing query from '{query_file}'...[/bold]\n")
    
    adapter = None
    try:
        adapter = get_adapter(connection_string)
        adapter.connect()
        optimizer = Optimizer(adapter)
        
        suggestions, _ = optimizer.get_optimizations(query)
        
        if not suggestions:
            console.print("[green]✓ Analysis complete. No optimizations to suggest.[/green]")
            return

        display_suggestions(suggestions)
        
        if apply:
            console.print("\n")
            if click.confirm(f"[bold yellow]Apply {len(suggestions)} optimization(s) to the database? This will execute CREATE INDEX statements.[/bold yellow]"):
                optimizer.apply_optimizations(suggestions)
                console.print("\n[bold green]✓ All optimizations applied.[/bold green]")
            else:
                console.print("\n[red]Optimization cancelled by user.[/red]")
        else:
            console.print("\nRun with the [bold]--apply[/bold] flag to execute these suggestions.")

    except Exception as e:
        console.print(f"\n[red]An error occurred:[/red] {e}")
        sys.exit(1)
    finally:
        if adapter:
            adapter.close()

@cli.command()
@click.option('--db', '-d', 'connection_string', envvar='DB_CONNECTION_STRING',
              required=True, help='Database connection string.')
@click.option('--threshold', default=10, help='Minimum mean execution time in ms to display.')
@click.option('--interval', default=5, help='Refresh interval in seconds.')
def monitor(connection_string, threshold, interval):
    """Monitor database for slow queries in real-time (PostgreSQL only)."""
    adapter = get_adapter(connection_string)
    if not isinstance(adapter, PostgresAdapter):
        console.print("[red]Error: Real-time monitoring is currently only supported for PostgreSQL.[/red]")
        sys.exit(1)

    console.print(f"[yellow]Monitoring for queries with mean execution time > {threshold}ms. Refreshing every {interval}s.[/yellow]")
    console.print("[dim]Press Ctrl+C to stop.[/dim]")

    try:
        adapter.connect()
        with Live(console=console, screen=False, auto_refresh=False) as live:
            while True:
                try:
                    slow_queries = adapter.get_slow_queries(min_mean_time_ms=threshold)
                    table = Table(title=f"Live Slow Query Monitor ({time.strftime('%X')})", expand=True)
                    table.add_column("Mean Time (ms)", style="red", justify="right")
                    table.add_column("Total Time (s)", style="yellow", justify="right")
                    table.add_column("Calls", style="cyan", justify="right")
                    table.add_column("Query", style="white")

                    for row in slow_queries:
                        query_text, calls, total_time, mean_time, _ = row
                        table.add_row(
                            f"{mean_time:.2f}",
                            f"{total_time/1000:.2f}",
                            f"{calls:,}",
                            query_text[:200].replace('\n', ' ') + ('...' if len(query_text) > 200 else '')
                        )
                    
                    live.update(table, refresh=True)
                    time.sleep(interval)

                except Exception as e:
                    console.print(f"[red]Monitor Error:[/red] {e}")
                    time.sleep(interval)

    except KeyboardInterrupt:
        console.print("\n[bold green]✓ Monitoring stopped.[/bold green]")
    except Exception as e:
        console.print(f"\n[red]An error occurred:[/red] {e}")
        sys.exit(1)
    finally:
        if adapter:
            adapter.close()

if __name__ == '__main__': 
    cli()