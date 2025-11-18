from unittest import TestCase

import asyncio
from ratisbona_utils.asyncio._process_runner import simple_run_command


class TestProcessRunner(TestCase):

    def test_simple_run_process(self):
        cmd = 'echo "Hello, World!"; echo "Hollas!" >&2'

        result, stdout, stderr = asyncio.run(simple_run_command(cmd))

        self.assertEqual(result, 0)
        self.assertEqual(stdout, 'Hello, World!\n')
        self.assertEqual(stderr, 'Hollas!\n')
