"""Project automation tasks."""

from invoke import task


@task
def pipeline(context):
    """Create and display the artifact structure without running analysis."""
    context.run("python -m regime_anomaly.pipeline", echo=True)


@task
def app(context):
    """Launch the Streamlit result application."""
    context.run("streamlit run src/app.py", echo=True)


@task(
    help={
        "build": "Generate the static site instead of starting the development server.",
        "strict": "Fail the static build when MkDocs emits a warning.",
        "address": "Address used by the development server.",
        "port": "Port used by the development server.",
    }
)
def docs(
    context,
    build=False,
    strict=False,
    address="127.0.0.1",
    port=8000,
):
    """Serve or build the MkDocs documentation."""
    if build:
        command = "mkdocs build"
        if strict:
            command += " --strict"
    else:
        command = f"mkdocs serve --dev-addr {address}:{port}"

    context.run(command, echo=True)
