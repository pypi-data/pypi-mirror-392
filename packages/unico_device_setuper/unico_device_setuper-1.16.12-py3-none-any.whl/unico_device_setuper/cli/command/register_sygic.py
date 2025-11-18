from unico_device_setuper.cli import stp
from unico_device_setuper.cli.command import register_unitech
from unico_device_setuper.lib import cnsl, sygic, unitech_util


@cnsl.command("Enregistrement de l'appareil sur Sygic", 'Appareil enregistré sur Sygic')
async def register_sygic(setup: stp.Setup):
    device_id = await register_unitech.get_id_device(setup)
    if device_id is None:
        return False

    unitech_client = await setup.get_unitech_client()
    if unitech_client is None:
        return False

    device_name = await unitech_util.get_device_name(device_id, unitech_client)
    if device_name is None:
        return False

    license_products = await setup.get_sygic_license_products()
    if license_products is None:
        return False

    return await sygic.setup(
        license_products,
        device_id=device_id,
        device_name=device_name,
        client=await setup.get_sygic_client(),
        unitech_env=setup.unitech_env,
    )
