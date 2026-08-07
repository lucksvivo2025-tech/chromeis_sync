from chromeis_sync.sync_engine.framework.upsert.result import (
    UpsertResult,
)


class BaseUpsert:
    """
    Base class for all ERP upsert implementations.

    Child classes will implement:

        • create()
        • update()

    The common execution flow lives here.
    """

    @classmethod
    def execute(cls, identity_result, builder):

        if identity_result.found:

            return cls.update(
                identity_result,
                builder,
            )

        return cls.create(
            identity_result,
            builder,
        )

    @classmethod
    def create(cls, identity_result, builder):

        raise NotImplementedError

    @classmethod
    def update(cls, identity_result, builder):

        raise NotImplementedError

    @staticmethod
    def success(action, doctype, document_name, message=""):

        return UpsertResult(
            success=True,
            action=action,
            doctype=doctype,
            document_name=document_name,
            message=message,
        )

    @staticmethod
    def failure(action, doctype, message):

        return UpsertResult(
            success=False,
            action=action,
            doctype=doctype,
            message=message,
        )
