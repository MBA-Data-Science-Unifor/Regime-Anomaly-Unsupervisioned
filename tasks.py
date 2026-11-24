"""Project automation tasks."""

from invoke import task

NOTEBOOKS = (
    "01_EDA",
    "02_preprocessing",
    "03_Modeling",
    "04_Review",
    "05_Transition_Filter",
)


@task
def pipeline(context):
    """Check published artifacts against the manifest without running analysis."""
    context.run("python -m regime_anomaly.pipeline", echo=True)


@task(help={"start": "First notebook to run, e.g. 03_Modeling (earlier ones are skipped)."})
def notebooks(context, start=NOTEBOOKS[0]):
    """Execute the analysis notebooks in order, in place, regenerating every artifact."""
    if start not in NOTEBOOKS:
        raise ValueError(f"Unknown notebook {start!r}; choose one of {', '.join(NOTEBOOKS)}")
    for name in NOTEBOOKS[NOTEBOOKS.index(start) :]:
        context.run(
            "jupyter nbconvert --to notebook --execute --inplace "
            f"--ExecutePreprocessor.timeout=1800 artifacts/notebooks/{name}.ipynb",
            echo=True,
        )


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
