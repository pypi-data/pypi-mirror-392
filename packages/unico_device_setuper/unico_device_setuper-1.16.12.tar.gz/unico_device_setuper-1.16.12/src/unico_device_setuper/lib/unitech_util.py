from unico_device_setuper.lib import cnsl, unitech


async def get_device_name(device_id: str, client: unitech.Client):
    device_name = next(
        (
            d.name
            for d in await unitech.get_device_all_devices.request(client) or []
            if d.id_device == device_id
        ),
        None,
    )
    if device_name is None:
        cnsl.print_red(f"Impossible de trouver le nom de l'appereil {device_id}")
        return None
    return device_name
