#!/usr/bin/env python
import asyncio
from argparse import ArgumentParser
from re import IGNORECASE, search
from subprocess import PIPE, Popen
from logging import Logger, basicConfig, getLevelName, getLogger

from i3ipc import Event
from i3ipc.aio import Connection


class Screenkey:
    """Singelton for controling screenkey process"""

    def __init__(self, command: list = ["screenkey"]) -> None:
        self.screenkey = None
        self.command = command

    def is_running(self) -> bool:
        # if there is not returncode from poll() the process is still running
        if isinstance(self.screenkey, Popen) and self.screenkey.poll() is None:
            return True
        return False

    def start(self) -> None:
        # check for old screenkey or if it returned with any returncode
        if not self.screenkey or isinstance(self.screenkey.poll(), int):
            self.screenkey = Popen(self.command, stdout=PIPE, stderr=PIPE)

    def stop(self) -> None:
        if isinstance(self.screenkey, Popen) and self.screenkey.poll() is None:
            self.screenkey.kill()


async def main(args, logger: Logger) -> None:
    def on_window(_, e):
        """Listen for window events and start/stop screenkey accordingly"""
        global SCREENKEY

        # log on level lower than DEBUG (-vvvv)
        logger.log(level=1, msg=e.ipc_data.get("container"))

        for unsafe_type in ("class", "instance", "title"):
            for unsafe_string in getattr(args, f"unsafe_{unsafe_type}_list"):
                logger.debug(f"{unsafe_type=} {unsafe_string=}")

                unsafe_attribute = (
                    e.ipc_data.get("container", {})
                    .get("window_properties", {})
                    .get(unsafe_type, "")
                )
                if search(unsafe_string, unsafe_attribute, IGNORECASE):
                    SCREENKEY.stop()
                    logger.info(
                        f"Screenkey paused due to {unsafe_type} match with {unsafe_string}"
                    )
                    return

        if not SCREENKEY.is_running():
            SCREENKEY.start()
            logger.info("Resumed Screenkey")
            return

    c = await Connection(auto_reconnect=True).connect()
    c.on(Event.WINDOW, on_window)
    global SCREENKEY
    SCREENKEY = Screenkey()
    await c.main()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "--unsafe-classes",
        metavar="CLASS",
        dest="unsafe_class_list",
        nargs="+",
        default=[],
        help=(
            "Provide a list of words that if matched in class "
            "disable screenkey (case-insensitive)"
        ),
    )
    parser.add_argument(
        "--unsafe-instances",
        metavar="INSTANCE",
        dest="unsafe_instance_list",
        nargs="+",
        default=[],
        help=(
            "Provide a list of words that if matched in instance "
            "disable screenkey (case-insensitive)"
        ),
    )
    parser.add_argument(
        "--unsafe-titles",
        metavar="TITLE",
        dest="unsafe_title_list",
        nargs="+",
        default=[],
        help=(
            "Provide a list of words that if matched in title "
            "disable screenkey (case-insensitive)"
        ),
    )
    parser.add_argument(
        "--verbose",
        "-v",
        dest="verbosity",
        action="count",
        default=0,
        help="Increase verbosity of output",
    )

    args = parser.parse_args()
    logger = getLogger("i3-autopause-screenkey")
    # FIXME: Simpler formatting of logs
    # FIXME: only set loglevel of the logger not everything (including asyncio)
    loglevel = 40 - 10 * args.verbosity
    basicConfig(level=loglevel)

    logger.debug(args)
    logger.debug(f"Loglevel: {loglevel} {getLevelName(loglevel)}")
    asyncio.get_event_loop().run_until_complete(main(args, logger))
