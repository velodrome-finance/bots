import nox
import tempfile

locations = ["bots", "tests", "noxfile.py"]
nox.options.sessions = "lint", "safety", "tests"


@nox.session(python=["3.10"])
def tests(session):
    session.run("poetry", "install", external=True)
    session.run("pytest")


@nox.session(python=["3.10"])
def lint(session):
    args = session.posargs or locations
    session.install("flake8", "flake8-bandit", "flake8-black", "flake8-bugbear")
    session.run("flake8", *args)


@nox.session(python="3.10")
def black(session):
    args = session.posargs or locations
    session.install("black")
    session.run("black", *args)


@nox.session(python="3.10")
def safety(session):
    with tempfile.NamedTemporaryFile() as requirements:
        session.run(
            "poetry",
            "export",
            "--dev",
            "--format=requirements.txt",
            "--without-hashes",
            f"--output={requirements.name}",
            external=True,
        )
        session.install("safety")
        session.run("safety", "check", f"--file={requirements.name}", "--full-report")
