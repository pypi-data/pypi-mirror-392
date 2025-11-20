# src/query_optimizer/core/optimizer.py
import time
from typing import List, Tuple
from rich.console import Console
import pandas as pd

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
    
    
    
    def analyze(self, query):
        """New method that returns OptimizerResult object"""
        suggestions, cost = self.get_optimizations(query)
        return OptimizerResult(query, suggestions, cost, self.adapter)
    
    def benchmark(self, query, apply_optimization=True):
        """Direct benchmark method for backwards compatibility"""
        result = self.analyze(query)
        return result.benchmark(apply_optimization=apply_optimization)

class OptimizerResult:
    def __init__(self, query, suggestions, cost, adapter):
        self.query = query
        self.suggestions = suggestions
        self.cost = cost
        self.adapter = adapter
        self.total_improvement = sum(s.estimated_improvement for s in suggestions)
    
    def info(self):
        """Show optimization summary"""
        print(f"Query: {self.query[:50]}...")
        print(f"Suggestions: {len(self.suggestions)}")
        print(f"Estimated improvement: {self.total_improvement}%")
    
    def get_suggestions(self):
        """Return suggestions as DataFrame"""
        if not self.suggestions:
            return pd.DataFrame()
        return pd.DataFrame([{
            'table': s.table_name,
            'columns': ', '.join(s.columns),
            'improvement': f"{s.estimated_improvement}%",
            'sql': s.create_statement
        } for s in self.suggestions])
    
    def apply(self, index=0):
        """Apply specific optimization"""
        if index < len(self.suggestions):
            self.adapter._connection.execute(self.suggestions[index].create_statement)
            self.adapter._connection.commit()
            print(f"✓ Applied: {self.suggestions[index].create_statement}")
    
    def benchmark(self, apply_optimization=True):
        """Compare before/after performance"""
        # BEFORE
        start = time.time()
        self.adapter._connection.execute(self.query).fetchall()
        before = time.time() - start
        
        if apply_optimization and self.suggestions:
            self.apply(0)
            
            # AFTER
            start = time.time()
            self.adapter._connection.execute(self.query).fetchall()
            after = time.time() - start
            
            print(f"\n🚀 Optimization Results:")
            print(f"BEFORE: {before:.3f}s")
            print(f"AFTER: {after:.3f}s")
            print(f"Improvement: {before/after:.1f}x faster!")
            return before, after
        else:
            print(f"Query time: {before:.3f}s")
            return before, None

