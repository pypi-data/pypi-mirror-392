import inspect
import logging

import twisted
from twisted.internet import reactor
from twisted.internet.defer import (
    maybeDeferred,
    Deferred,
    inlineCallbacks,
    ensureDeferred,
)
from twisted.internet.threads import deferToThread

logger = logging.getLogger(__name__)


def callMethodLater(func):
    def wrapper(*args, **kwargs):
        return reactor.callLater(0, func, *args, **kwargs)

    return wrapper


def nonConcurrentMethod(method):
    def call(*args, **kwargs):
        if call.running:
            return
        call.running = True
        try:
            return method(*args, **kwargs)
        finally:
            call.running = False

    call.running = False

    return call


def maybeDeferredWrap(funcToWrap):
    """Maybe Deferred Wrap

    A decorator that ensures a function will return a deferred.

    """

    def func(*args, **kwargs):
        return maybeDeferred(funcToWrap, *args, **kwargs)

    return func


def ensureDeferredWrap(funcToWrap):
    """Ensured Deferred Wrap

    A decorator that converts asyncio functions to ones that
     return Twisted Deferred instead.

    This keeps all the async processing in Twisteds reactive design while providing
     support of the await/async syntax (and asyncio processing)


    """

    def func(*args, **kwargs):
        return ensureDeferred(funcToWrap(*args, **kwargs))

    return func


def vortexLogFailure(failure, loggerArg, consumeError=False, successValue=True):
    """
    Log a Twisted Failure instance using the provided logger.

    Args:
        failure: Twisted Failure instance to log
        loggerArg: Logger instance to use for logging
        consumeError: If True, returns successValue instead of the failure
        successValue: Value to return if consumeError is True

    Returns:
        The original failure or successValue depending on consumeError
    """
    try:
        if not hasattr(failure, "_vortexFailureLogged"):
            exc_info = (
                failure.type,
                failure.value,
                failure.getTracebackObject(),
            )

            # Log with full exception info for better tracebacks
            loggerArg.exception(str(failure.value), exc_info=exc_info)

            # Mark as logged to prevent duplicate logging
            failure._vortexFailureLogged = True

        return successValue if consumeError else failure

    except Exception as e:
        # If something goes wrong in our logging logic, log that error
        loggerArg.exception("Error while logging failure: %s", str(e))
        return failure


def vortexLogAndConsumeFailure(failure, loggerArg, successValue=True):
    return vortexLogFailure(
        failure, loggerArg, consumeError=True, successValue=successValue
    )


printFailure = vortexLogFailure


def vortexInlineCallbacksLogAndConsumeFailure(loggerArg):
    """Vortex InlineCallbacks Log and Consume Failure

    This is exactly the same as @inlineCallbacks decorator, except it will log
    and consume any deferred failures that are thrown.
    """

    def wrapper(funcToWrap):
        funcIcb = inlineCallbacks(funcToWrap)

        def called(*args, **kwargs):
            d = funcIcb(*args, **kwargs)
            d.addErrback(vortexLogAndConsumeFailure, loggerArg)
            return d

        return called

    return wrapper


class YieldInDeferToThreadException(Exception):
    pass


def deferToThreadWrapWithLogger(
    logger, consumeError=False, checkMainThread=True
):
    """Defer To Thread Wrap With Logger

    This method is a decorator used to send blocking methods to threads easily.

    :param logger: An instance from logging.getLogger(..)
    :param consumeError: Should errors occuring in the thread be consumed or errback'd
    :param checkMainThread: Don't use this parameter, it's only needed during reactor
                startup when the reactors thread isn't properly set and the check
                fails.

    :return: A deferred.

    Usage: ::

            import logging
            logger = logging.getLogger(__name__)
            @deferToThreadWrapWithLogger(logger)
            def myFunction(arg1, kw=True):
                pass


    """
    assert isinstance(
        logger, logging.Logger
    ), """Usage:
    import logging
    logger = logging.getLogger(__name__)
    @deferToThreadWrapWithLogger(logger)
    def myFunction(arg1, kw=True):
        pass
    """

    def wrapper(funcToWrap) -> Deferred:
        def checkForInlineCallbackYield(result):
            if inspect.isgenerator(result):
                logger.error(
                    "Module Name %s, Class Name %s, Function Name %s"
                    " has a yield in it. IT SHOULD NOT.",
                    funcToWrap.__module__,
                    funcToWrap.__class__.__name__,
                    funcToWrap.__name__,
                )
                raise YieldInDeferToThreadException()
            return result

        def func(*args, **kwargs):
            if not twisted.python.threadable.isInIOThread() and checkMainThread:
                logger.error(
                    "Module Name %s, Class Name %s, Function Name %s"
                    " is being deferred from a thread. IT SHOULD NOT.",
                    funcToWrap.__module__,
                    funcToWrap.__class__.__name__,
                    funcToWrap.__name__,
                )
                raise Exception(
                    "Deferring to a thread can only be done from the main thread"
                )

            d = deferToThread(funcToWrap, *args, **kwargs)
            d.addCallback(checkForInlineCallbackYield)
            d.addErrback(vortexLogFailure, logger, consumeError=consumeError)
            return d

        return func

    return wrapper


def isMainThread():
    return twisted.python.threadable.isInIOThread()


def noMainThread():
    if isMainThread():
        raise Exception(
            "Blocking operations shouldn't occur in the reactors thread."
        )


def yesMainThread():
    if not isMainThread():
        raise Exception(
            "Async operations must occur in the reactors main thread."
        )
