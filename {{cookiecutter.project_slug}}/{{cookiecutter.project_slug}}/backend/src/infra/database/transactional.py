from functools import wraps
from typing import Awaitable, Callable, ParamSpec

from src.infra.application.exception import AppError
from src.infra.application.result import Result
from src.infra.database.session import scoped_session


P = ParamSpec("P")


class transactional:  # noqa: N801
    def __call__(
        self,
        fun: Callable[P, Awaitable[Result]],
    ) -> Callable[P, Awaitable[Result]]:
        @wraps(fun)
        async def wrapped(*args: P.args, **kwargs: P.kwargs) -> Result:
            result = await fun(*args, **kwargs)

            match result:
                case Result(_, None):
                    try:
                        await scoped_session.commit()
                    except Exception as err:
                        await scoped_session.rollback()
                        return Result.fail(
                            AppError(str(err)),
                        )

            return result

        return wrapped
