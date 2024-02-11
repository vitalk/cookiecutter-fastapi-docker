from src.infra.application.exception import BadRequestError, NotFoundError


class UserNotFoundError(NotFoundError):
    ...


class EmailTakenError(BadRequestError):
    ...
