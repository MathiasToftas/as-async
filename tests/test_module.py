import time

import pytest

from as_async import as_async, as_async_generator


@pytest.mark.asyncio
async def test_as_async():
    tmp = []

    @as_async()
    def buz():
        """my cool function that blocks the event loop for 0.1 seconds."""
        time.sleep(0.1)
        tmp.append("buz")

    b = buz()
    tmp.append("foo")
    await b

    assert tmp == ["foo", "buz"]


@pytest.mark.asyncio
async def test_as_async_generator():
    tmp = []

    @as_async_generator()
    def buz():
        """my cool generator that blocks the event loop for 0.1 seconds.

        Yields:
            str: "buz"
        """
        time.sleep(0.1)
        tmp.append("buz")
        yield "buz"

    a_gen = buz()
    tmp.append("foo")
    async for _ in a_gen:
        pass

    assert tmp == ["foo", "buz"]
