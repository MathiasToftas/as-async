import asyncio
import functools
from concurrent.futures import Executor
from typing import Any, AsyncGenerator, Callable, Coroutine, Generator, cast


def to_async[**P, T](
    func: Callable[P, T],
    loop: asyncio.AbstractEventLoop | None = None,
    executor: Executor | None = None,
) -> Callable[P, Coroutine[None, None, T]]:
    """
    The `to_async` function is used to convert a synchronous function into an asynchronous
    one by running it in a separate thread, effectively making it non-blocking. This is
    useful when you have a CPU-bound or I/O-bound function that you don't want to block
    the event loop, and which would be difficult to reimplement as async.

    Args:
        func (Callable): The synchronous function to convert to asynchronous.
        loop (asyncio.AbstractEventLoop, optional): The event loop to run the blocking function on.
        Defaults to `asyncio.get_event_loop()`.
        executor (Executor, optional): The executor to run the blocking function on.
        This can affect performance, check asyncio docs for info. Defaults to None.

    Returns:
        Callable: The new asynchronous function.

    Example:
    ```python
    import time
    import asyncio
    from concurrent.futures import ThreadPoolExecutor

    def long_running_function():
        time.sleep(5)
        return "Finished"


    async def main():
        async_func = to_async(long_running_function)
        result = await async_func()
        print(result)

    asyncio.run(main())
    ```
    """

    @functools.wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        _loop = loop or asyncio.get_event_loop()
        return await _loop.run_in_executor(
            executor, functools.partial(func, *args, **kwargs)
        )

    return wrapper


def as_async[**P, T](
    loop: asyncio.AbstractEventLoop | None = None, executor: Executor | None = None
) -> Callable[[Callable[P, T]], Callable[P, Coroutine[None, None, T]]]:
    """
    The `as_async` decorator is used to run a synchronous function in a separate thread,
    effectively making it non-blocking. This is useful when you have a CPU-bound or I/O-bound
    function that you don't want to block the event loop, and which would be difficult to
    reimplement as async.

    Args:
        loop (asyncio.AbstractEventLoop, optional): The event loop to run the blocking function on.
        Defaults to `asyncio.get_event_loop()`.
        executor (Executor, optional): The executor to run the blocking function on.
        This can affect performance, check asyncio docs for info. Defaults to None.

    Example:
    ```python
    import time
    import asyncio
    from concurrent.futures import ThreadPoolExecutor

    @as_async(loop=asyncio.get_event_loop(), executor=ThreadPoolExecutor(max_workers=5))
    def long_running_function():
        time.sleep(5)
        return "Finished"

    async def main():
        result = await long_running_function()
        print(result)

    asyncio.run(main())
    ```
    """

    def decorator(func: Callable[P, T]) -> Callable[P, Coroutine[None, None, T]]:
        return to_async(func, loop=loop, executor=executor)

    return decorator


def to_async_generator[**P, T](
    func: Callable[P, Generator[T, Any, None]],
    loop: asyncio.AbstractEventLoop | None = None,
    executor: Executor | None = None,
) -> Callable[P, AsyncGenerator[T, Any]]:
    """
    The `to_async_generator` function is used to convert a synchronous generator into an
    asynchronous one by running it in a separate thread, effectively making it non-blocking.
    This is useful when you have a CPU-bound or I/O-bound generator that you don't want to
    block the event loop, and which would be difficult to reimplement as async.

    Args:
        func (Callable): The synchronous generator to convert to asynchronous.
        loop (asyncio.AbstractEventLoop, optional): The event loop to run the blocking generator on.
        Defaults to `asyncio.get_event_loop()`.
        executor (Executor, optional): The executor to run the blocking generator on.
        This can affect performance, check asyncio docs for info. Defaults to None.

    Returns:
        Callable: The new asynchronous generator.

    Example:
    ```python
    import time
    import asyncio
    from concurrent.futures import ThreadPoolExecutor

    def long_running_generator():
        for i in range(5):
            time.sleep(1)  # Simulate a long-running operation
            yield i


    async def main():
        async_gen = to_async_generator(long_running_generator)
        async for value in async_gen():
            print(value)

    asyncio.run(main())
    ```
    """

    @functools.wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> AsyncGenerator[T, Any]:
        blocking = func(*args, **kwargs)
        _loop = loop or asyncio.get_event_loop()
        done = object()

        def get_next():
            try:
                return blocking.__next__()
            except StopIteration:
                return done

        while True:
            obj = await _loop.run_in_executor(executor, get_next)
            if obj is done:
                break
            yield cast(T, obj)

    return wrapper


def as_async_generator[**P, T](
    loop: asyncio.AbstractEventLoop | None = None, executor: Executor | None = None
) -> Callable[
    [Callable[P, Generator[T, Any, None]]], Callable[P, AsyncGenerator[T, Any]]
]:
    """
    The `as_async_generator` decorator is used to run a synchronous generator in a separate thread,
    effectively making it non-blocking. This is useful when you have a CPU-bound or I/O-bound
    generator that you don't want to block the event loop, and which would be difficult to
    reimplement as async.

    Args:
        loop (asyncio.AbstractEventLoop, optional): The event loop to run the blocking generator on.
        Defaults to `asyncio.get_event_loop()`.
        executor (Executor, optional): The executor to run the blocking generator on.
        This can affect performance, check asyncio docs for info. Defaults to None.

    Example:
    ```python
    import time
    import asyncio
    from concurrent.futures import ThreadPoolExecutor

    @as_async_generator(loop=asyncio.get_event_loop(), executor=ThreadPoolExecutor(max_workers=5))
    def long_running_generator():
        for i in range(5):
            time.sleep(1)  # Simulate a long-running operation
            yield i

    async def main():
        async for value in long_running_generator():
            print(value)

    asyncio.run(main())
    ```
    """

    def decorator(
        func: Callable[P, Generator[T, Any, None]],
    ) -> Callable[P, AsyncGenerator[T, Any]]:
        return to_async_generator(func, loop=loop, executor=executor)

    return decorator
