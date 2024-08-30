from invoke.tasks import task

poetry = ["poetry", "run"]


@task
def precommit(c):
    poetry.append("pre-commit")
    c.run(" ".join(poetry) + " run --all-files")
