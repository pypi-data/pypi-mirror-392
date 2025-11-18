import contextlib
import dataclasses
import pathlib
import typing

import httpx

from unico_device_setuper.lib import auth, cnsl, env, sygic, unitech, unitech_util, util


def get_unitech_env(unitech_env: env.UnitechEnv | None) -> env.UnitechEnv:
    if unitech_env is not None:
        return unitech_env
    return env.UnitechEnv.get_default()


def get_sygic_env(sygic_env: env.SygicEnv | None) -> env.SygicEnv:
    if sygic_env is not None:
        return sygic_env
    return env.SygicEnv.get_default()


@contextlib.asynccontextmanager
async def create_unitech_client(
    unitech_env: env.UnitechEnv, client_name: str | None
) -> typing.AsyncIterator[unitech.Client | None]:
    async with unitech.Client(base_url=str(unitech_env.api_base_url)) as unitech_client:
        headers = unitech_client.get_async_httpx_client().headers
        auth_header_name = 'Authorization'
        auth_token = await auth.get_unitech_auth_token(
            unitech_env,
            auth.PickWithName(client_name) if client_name is not None else auth.PICK_INTERACTIVE,
        )
        if auth_token is None:
            yield None
        else:
            headers[auth_header_name] = f'Bearer {auth_token}'
            yield unitech_client


@contextlib.asynccontextmanager
async def create_sygic_client(sygic_env: env.SygicEnv) -> typing.AsyncIterator[sygic.Client]:
    async with httpx.AsyncClient() as http_client:
        yield sygic.Client(
            base_url=sygic_env.api_base_url,
            http_client=http_client,
            api_key=await auth.get_sygic_api_key(sygic_env, http_client),
        )


def validate_device_id(s: str) -> str | None:
    s = s.strip()
    if not s:
        return None

    if util.parse_hex(s) is not None and len(s) == 16:
        return s

    cnsl.warn(f"L'identifiant {s!r} est invalide et sera donc ignoré")
    return None


def get_device_ids(device_id_path: pathlib.Path) -> list[str]:
    return [
        device_id
        for line in device_id_path.read_text().splitlines()
        if (device_id := validate_device_id(line)) is not None
    ]


@dataclasses.dataclass
class Device:
    id: str
    name: str


async def get_device(id: str, client: unitech.Client) -> None | Device:
    name = await unitech_util.get_device_name(id, client)
    if name is None:
        cnsl.warn(f"L'appreil {id} sera donc ignoré")
        return None
    return Device(id, name)


async def get_devices(device_id_path: pathlib.Path, client: unitech.Client) -> list[Device]:
    return [
        device
        for id in get_device_ids(device_id_path)
        if (device := await get_device(id, client)) is not None
    ]


@dataclasses.dataclass
class Params:
    device_id_path: pathlib.Path
    client_name: str | None = None
    unitech_env: env.UnitechEnv | None = None
    sygic_env: env.SygicEnv | None = None
    sygic_products_names: list[str] | None = None


async def register(params: Params) -> int:
    unitech_env = get_unitech_env(params.unitech_env)
    sygic_env = get_sygic_env(params.sygic_env)

    cnsl.print_gray(f'Environement Unitech: {unitech_env.value}')
    cnsl.print_gray(f'Environement Sygic: {sygic_env.value}')

    async with create_unitech_client(unitech_env, params.client_name) as unitech_client:
        if unitech_client is None:
            cnsl.print_red('Impossible de se connecter à Unitech')
            return 1

        devices = await get_devices(params.device_id_path, unitech_client)
        async with create_sygic_client(sygic_env) as sygic_client:
            license_products = await sygic.choose_license_products(
                params.sygic_products_names, sygic_client, unitech_env
            )
            if license_products is None:
                cnsl.print_red("Impossible d'obtenir les licenses Sygic")
                return 1

            for device in devices:
                success = await sygic.setup(
                    license_products=license_products,
                    device_id=device.id,
                    device_name=device.name,
                    client=sygic_client,
                    unitech_env=unitech_env,
                )
                if not success:
                    return 1
    return 0
