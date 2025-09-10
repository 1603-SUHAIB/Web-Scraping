import typer
from rich.console import Console
from pathlib import Path
import time

from scraper import WebScraper

app = typer.Typer(
    name="SiteScraper",
    help="A powerful CLI to scrape text and navigation data from a website.",
    add_completion=False,
)
console = Console()

@app.command()
def run(
    url: str = typer.Argument(..., help="The starting URL to crawl."),
    depth: int = typer.Option(2, "--depth", "-d", help="Maximum link depth to follow."),
    threads: int = typer.Option(5, "--threads", "-t", help="Number of concurrent threads to use."),
    delay: float = typer.Option(1.0, "--delay", help="Seconds to wait between requests per thread."),
    output_dir: Path = typer.Option(
        "output",
        "--output-dir",
        "-o",
        help="Directory to save the output files.",
        writable=True,
        file_okay=False,
    ),
    vectorize: bool = typer.Option(
        False,
        "--vectorize",
        "-v",
        help="Enable to generate sentence embeddings for text chunks.",
    ),
    user_agent: str = typer.Option("EnhancedScraper/1.0 (CLI)", "--user-agent", "-ua", help="Custom User-Agent."),
):
    """
    Scrape a website starting from the given URL.
    """
    console.rule("[bold cyan]SiteScraper CLI[/bold cyan]")
    console.print(f"▶️  [bold]URL:[/bold] {url}")
    console.print(f"🔎 [bold]Depth:[/bold] {depth}")
    console.print(f"🧵 [bold]Threads:[/bold] {threads}")
    console.print(f"⏳ [bold]Delay:[/bold] {delay}s")
    console.print(f"📁 [bold]Output Dir:[/bold] {output_dir}")
    console.print(f"🧠 [bold]Vectorize:[/bold] {'Enabled' if vectorize else 'Disabled'}")
    console.print("-" * 30)

    output_dir.mkdir(exist_ok=True)

    def rich_logger(message):
        console.log(message)

    try:
        start_time = time.time()
        
        with console.status("[bold green]Scraping in progress...", spinner="dots") as status:
            scraper = WebScraper(
                base_url=url,
                depth_limit=depth,
                threads=threads,
                delay=delay,
                user_agent=user_agent,
                vectorize=vectorize,
                logger=rich_logger
            )
            scraper.crawl()
            
            status.update("[bold green]Scraping complete! Saving results...")
            
            json_result, log_result = scraper.get_results()
            json_file = output_dir / "scraped_data.json"
            log_file = output_dir / "scraped_log.txt"
            
            with open(json_file, 'w', encoding='utf-8') as f:
                f.write(json_result)
            
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(log_result)

        end_time = time.time()
        duration = end_time - start_time
        
        console.print("\n[bold green]✅ Success! Scraping finished.[/bold green]")
        console.print(f"Total time: [yellow]{duration:.2f} seconds[/yellow]")
        console.print(f"Scraped data saved to [cyan]{json_file}[/cyan]")
        console.print(f"Navigation log saved to [cyan]{log_file}[/cyan]")

    except Exception as e:
        console.print(f"\n[bold red]❌ An error occurred: {e}[/bold red]")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()