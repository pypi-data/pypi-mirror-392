#!/usr/bin/env python3
import asyncio
import logging
import time

from pyoverkiz.client import OverkizClient
from pyoverkiz.const import SUPPORTED_SERVERS
from pyoverkiz.enums import Server

from overkiz_runner import printer, dwh
from overkiz_runner.configuration import conf

logger = logging.getLogger(__name__)


async def show_states():
    for creds in conf.credentials:
        server = SUPPORTED_SERVERS[Server[creds.servertype]]
        async with OverkizClient(
            creds.username, creds.password, server=server
        ) as client:
            try:
                await client.login()
            except Exception:  # pylint: disable=broad-except
                logger.exception(
                    "Something went wrong while connecting to %s (login=%r)",
                    server,
                    creds.username,
                )
                return
            printer.print_device_states(await client.get_devices())


async def listen_events(index):
    username = conf.credentials[index].username
    password = conf.credentials[index].password
    server = SUPPORTED_SERVERS[Server[conf.credentials[index].servertype]]

    async with OverkizClient(username, password, server=server) as client:
        try:
            await client.login()
        except Exception:  # pylint: disable=broad-except
            logger.exception(
                "Something went wrong while connecting to %s (login=%r)",
                server,
                username,
            )
            return
        logger.warning(
            "Connected with %s to %r, listening...",
            username,
            server.name,
        )
        while True:
            for event in await client.fetch_events():
                printer.print_event(event)
            yield


async def listen_all_events():
    listerners = [
        listen_events(index) for index in range(len(conf.credentials))
    ]
    while True:
        for listerner in listerners:
            async for _ in listerner:
                time.sleep(conf.watch.interval)


async def execute() -> None:
    for creds in conf.credentials:
        server = SUPPORTED_SERVERS[Server[creds.servertype]]
        async with OverkizClient(
            creds.username, creds.password, server=server
        ) as client:
            try:
                await client.login()
            except Exception:  # pylint: disable=broad-except
                logger.exception(
                    "Something went wrong while connecting to %s (login=%r)",
                    server,
                    creds.username,
                )
                return

            for device in await client.get_devices():
                if device.id == conf.appliance:
                    if device.widget == "DomesticHotWaterProduction":
                        await dwh.execute(client, device, conf.command)
                    else:
                        logger.error(
                            "Don't know how to deal with %s (%s)",
                            device.id,
                            device.widget,
                        )


async def main():
    if conf.command == "listen-events":
        await listen_all_events()
    elif conf.command == "show-states":
        await show_states()
    else:
        await execute()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("CTRL+C: EXITING")
