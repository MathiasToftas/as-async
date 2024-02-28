# Unblock

Small python library to unblock sync functions and generators

## Installation

```sh
    pip install unblock
```

## Examples

basic usage

 ```python
    import time
    import asyncio
    from concurrent.futures import ThreadPoolExecutor

    from unblock import unblock

    @unblock()
    def long_running_function():
        time.sleep(5)
        return "Finished"

    async def main():
        result = await long_running_function()
        print(result)

    asyncio.run(main())
```

specify loop and or executor

```python
    import time
    import asyncio
    from concurrent.futures import ThreadPoolExecutor

    from unblock import unblock_generator

    @unblock_generator(loop=asyncio.get_event_loop(), executor=ThreadPoolExecutor(max_workers=5))
    def long_running_generator():
        for i in range(5):
            time.sleep(1)  # Simulate a long-running operation
            yield i

    async def main():
        async for value in long_running_generator():
            print(value)

    asyncio.run(main())
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
