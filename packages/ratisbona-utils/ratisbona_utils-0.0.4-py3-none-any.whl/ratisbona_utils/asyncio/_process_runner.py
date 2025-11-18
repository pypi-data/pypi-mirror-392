import asyncio


async def run_command(command, stdout_callback, stderr_callback, **kwds):
    """
    Runs a shell command asynchronously and uses callbacks for stdout and stderr.

    Args:
        command (str): The shell command to run.
        stdout_callback (callable): Function to handle stdout text. Should accept two arguments:
                                    the process instance and the line of output.
        stderr_callback (callable): Function to handle stderr text. Should accept two arguments:
                                    the process instance and the line of output.
    """
    process = await asyncio.create_subprocess_shell(
        command,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        **kwds
    )

    async def handle_stream(stream, callback):
        """Handle the stream (stdout or stderr) by calling the provided callback."""
        while True:
            line = await stream.readline()
            if not line:
                break
            await callback(process, line.decode().strip())

    # Create tasks to read from stdout and stderr
    stdout_task = asyncio.create_task(handle_stream(process.stdout, stdout_callback))
    stderr_task = asyncio.create_task(handle_stream(process.stderr, stderr_callback))

    # Wait for the process to complete
    await process.wait()

    # Ensure all tasks are completed
    await stdout_task
    await stderr_task
    return process.returncode


async def simple_run_command(command, **kwds):
    """
    Run a shell command asynchronously and print the output to stdout.

    Args:
        command (str): The shell command to run.
    """
    stdout = ""
    stderr = ""

    async def stdout_callback(process, line):
        nonlocal stdout
        stdout += line + "\n"

    async def stderr_callback(process, line):
        nonlocal stderr
        stderr += line + "\n"

    retval = await run_command(command, stdout_callback, stderr_callback, **kwds)

    return retval, stdout, stderr


