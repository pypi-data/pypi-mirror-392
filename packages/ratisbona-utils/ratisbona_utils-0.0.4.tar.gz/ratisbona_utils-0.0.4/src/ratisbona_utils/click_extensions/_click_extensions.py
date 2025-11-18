from click import Group


class DefaultGroup(Group):
    """
        A Click Group subclass that supports a default command.

        Fields:
            default_cmd: The name of the default command to execute if no command is provided.
        Usage:
        ```python
            @click.group(cls=DefaultGroup, default_cmd='start')
            def cli():
                pass

            @cli.command()
            def start():
                click.echo("Starting...")

            @cli.command()
            def stop():
                click.echo("Stopping...")
        ```
    """
    def __init__(self, *args, default_cmd=None, **kwargs):
        self.default_cmd = default_cmd
        super().__init__(*args, **kwargs)

    def parse_args(self, ctx, args):
        if args and args[0] not in self.commands and not args[0].startswith('-'):
            if self.default_cmd:
                args.insert(0, self.default_cmd)
        return super().parse_args(ctx, args)
