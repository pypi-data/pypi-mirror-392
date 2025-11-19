import time
import sys

def benchmark_import():
    """Measure import time"""
    
    # vargula
    start = time.time()
    import vargula
    vg_time = (time.time() - start) * 1000
    
    # Rich
    start = time.time()
    from rich.console import Console
    rich_time = (time.time() - start) * 1000
    
    # colorama
    start = time.time()
    import colorama
    colorama_time = (time.time() - start) * 1000
    
    print(f"Import Time Comparison:")
    print(f"  vargula: {vg_time:.2f}ms")
    print(f"  Rich:      {rich_time:.2f}ms ({rich_time/vg_time:.1f}x slower)")
    print(f"  colorama:  {colorama_time:.2f}ms")

def benchmark_styling():
    """Measure styling performance"""
    import vargula as vg
    from rich.console import Console
    
    iterations = 10000
    
    # vargula
    start = time.time()
    for _ in range(iterations):
        vg.style("Hello World", color="red", look="bold")
    vg_time = (time.time() - start) * 1000
    
    # Rich
    console = Console()
    start = time.time()
    for _ in range(iterations):
        console.render_str("[red bold]Hello World[/]")
    rich_time = (time.time() - start) * 1000
    
    print(f"\nStyling Performance ({iterations} iterations):")
    print(f"  vargula: {vg_time:.2f}ms")
    print(f"  Rich:      {rich_time:.2f}ms ({rich_time/vg_time:.1f}x slower)")

if __name__ == "__main__":
    benchmark_import()
    benchmark_styling()