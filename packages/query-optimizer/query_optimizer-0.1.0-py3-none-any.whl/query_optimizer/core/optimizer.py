# src/query_optimizer/core/optimizer.py
import time
from typing import List, Tuple
from rich.console import Console

from .analyzer import DatabaseAdapter
from .models import IndexSuggestion

console = Console()

class Optimizer:
    """Orchestrates the query optimization process."""

    def __init__(self, adapter: DatabaseAdapter):
        self.adapter = adapter

    def get_optimizations(self, query: str, analyze: bool = True) -> Tuple[List[IndexSuggestion], float]:
        """
        Analyzes a query and returns optimization suggestions and the original cost.

        Returns:
            A tuple containing a list of IndexSuggestion objects and the original query cost.
        """
        console.print("[bold blue]Step 1: Validating query syntax...[/bold blue]")
        valid, error = self.adapter.validate_syntax(query)
        if not valid:
            raise ValueError(f"Invalid query syntax: {error}")
        console.print("[green]✓ Syntax is valid.[/green]\n")

        console.print(f"[bold blue]Step 2: Estimating original query cost...[/bold blue]")
        original_cost = self.adapter.estimate_query_cost(query)
        console.print(f"  [cyan]Estimated Cost:[/cyan] [yellow]{original_cost:.2f}[/yellow]\n")

        console.print(f"[bold blue]Step 3: Generating execution plan...[/bold blue]")
        plan = self.adapter.explain_query(query, analyze=analyze)
        console.print("[green]✓ Execution plan generated.[/green]\n")

        console.print("[bold blue]Step 4: Analyzing plan for optimization opportunities...[/bold blue]")
        suggestions = self.adapter.suggest_indexes(plan)
        if suggestions:
            console.print(f"[green]✓ Found {len(suggestions)} potential optimization(s).[/green]\n")
        else:
            console.print("[yellow]! No immediate index optimizations found.[/yellow]\n")
        
        return suggestions, original_cost

    def apply_optimizations(self, suggestions: List[IndexSuggestion]) -> List[str]:
        """
        Applies a list of index suggestions to the database.

        Args:
            suggestions: A list of IndexSuggestion objects.

        Returns:
            A list of messages confirming the applied changes.
        """
        if not suggestions:
            return ["No optimizations to apply."]

        applied_optimizations = []
        for suggestion in suggestions:
            console.print(f"[bold blue]Applying suggestion:[/bold blue] {suggestion.create_statement}")
            try:
                start_time = time.time()
                # Using execute_ddl as CREATE INDEX doesn't return rows
                self.adapter.execute_ddl(suggestion.create_statement)
                duration = time.time() - start_time
                
                message = f"Successfully created index on '{suggestion.table_name}' ({', '.join(suggestion.columns)}) in {duration:.2f}s."
                console.print(f"[green]✓ {message}[/green]\n")
                applied_optimizations.append(message)

            except Exception as e:
                error_message = f"Failed to create index on '{suggestion.table_name}': {e}"
                console.print(f"[red]✗ {error_message}[/red]\n")
                raise
                # Decide if we should stop or continue
                # For now, we continue with the next suggestion
        
        return applied_optimizations
