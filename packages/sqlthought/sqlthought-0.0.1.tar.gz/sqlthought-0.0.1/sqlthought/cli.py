import click
from .nlq.conversion import to_sql


@click.group()
def cli():
    """SQLThought CLI — NLQ → SQL with Groq backend."""


@cli.command()
@click.argument("question")
@click.argument("db")
def query(question, db):
    """Run NLQ → SQL conversion."""
    result = to_sql(question, db)

    print("\n=== SQLThought Result ===")
    print("SQL:", result.get("sql"))
    print("Success:", result.get("success"))
    print("Result:", result.get("result"))


@cli.command()
def config():
    """Reconfigure Groq API key / model."""
    from .nlq.conversion import CONFIG_PATH, _ensure_config

    if click.confirm("Reset configuration?", default=True):
        import os
        if os.path.exists(CONFIG_PATH):
            os.remove(CONFIG_PATH)
    _ensure_config()
    print("Configuration updated.")


@cli.command()
def version():
    print("sqlthought 0.0.1")
