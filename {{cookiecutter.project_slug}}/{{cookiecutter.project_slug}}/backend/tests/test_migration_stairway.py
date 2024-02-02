"""
Test can find forgotten downgrade methods, undeleted data types in downgrade
methods, typos and many other errors.

Does not require any maintenance: you just add it once to check the most of
generic typos and mistakes in migrations forever.
"""
from dataclasses import dataclass

import alembic.command
import alembic.config
from alembic.script import ScriptDirectory, Script

from tests.base import get_test_alembic_config, get_test_app_config


_previous_revision_ident: str = "-1"


@dataclass(frozen=True)
class Revision:
    revision: str
    down_revision: str
    docu: str


def get_alembic_revisions_from_config(
    *,
    alembic_config: alembic.config.Config,
) -> list[Revision]:
    revision_dir = ScriptDirectory.from_config(alembic_config)

    revisions: list[Script] = list(revision_dir.walk_revisions())
    revisions.reverse()

    return _linearize_down_alembic_revisions(revisions)


def _linearize_down_alembic_revisions(
    revisions: list[Script],
) -> list[Revision]:
    """
    In case of merged heads we need to linearize revisions to properly perform
    downgrade migrations for them.
    """
    return_value = []
    for rev in revisions:
        if not rev.down_revision:
            return_value.append(
                Revision(
                    revision=rev.revision,
                    down_revision=_previous_revision_ident,
                    docu=rev.doc,
                )
            )

        elif isinstance(rev.down_revision, (list, tuple)):
            for down_revision in rev.down_revision:
                return_value.append(
                    Revision(
                        revision=rev.revision,
                        down_revision=down_revision,
                        docu=rev.doc,
                    )
                )

        else:
            return_value.append(
                Revision(
                    revision=rev.revision,
                    down_revision=rev.down_revision,
                    docu=rev.doc,
                )
            )

    return return_value


def pytest_generate_tests(metafunc):
    test_app_config = get_test_app_config()
    test_alembic_config = get_test_alembic_config(test_app_config)

    alembic_revisions = get_alembic_revisions_from_config(
        alembic_config=test_alembic_config
    )
    argvalues = [
        (
            test_alembic_config,
            revision,
        )
        for revision in alembic_revisions
    ]
    idlist = [
        f"{revision.revision}: {revision.docu.lower()}"
        for revision in alembic_revisions
    ]

    metafunc.parametrize(
        ["test_alembic_config", "revision"],
        argvalues,
        ids=idlist,
        scope="session",
    )


def test_migration_stairway(
    test_alembic_config: alembic.config.Config,
    revision: Revision,
):
    alembic.command.upgrade(test_alembic_config, revision.revision)
    alembic.command.downgrade(test_alembic_config, revision.down_revision)
    alembic.command.upgrade(test_alembic_config, revision.revision)
