# from nautobot.extras.plugins import PluginMenuButton, PluginMenuItem, PluginMenu
from nautobot.core.apps import NavMenuItem, NavMenuTab, NavMenuGroup
# from nautobot.core.choices import ButtonColorChoices


# imported_device_buttons = [
#     PluginMenuButton(
#         link='plugins:slurpit_nautobot:import',
#         title='Import',
#         icon_class='mdi mdi-sync',
#         color=ButtonColorChoices.ORANGE,
#     )
# ]

menu_items = (
    NavMenuTab(
        name='Slurp`it',
        groups=(
            NavMenuGroup(
                name='Slurp`it', 
                items = (
                    NavMenuItem(
                        link='plugins:slurpit_nautobot:settings',
                        name='Settings',
                        permissions=["slurpit_nautobot.view_slurpitsetting"]
                    ),
                    NavMenuItem(
                        link='plugins:slurpit_nautobot:slurpitimporteddevice_list',
                        name='Onboard devices',
                        # buttons=imported_device_buttons,
                        permissions=[
                            "slurpit_nautobot.view_slurpitstageddevice",
                            "slurpit_nautobot.view_slurpitimporteddevice"
                        ]
                    ),
                    NavMenuItem(
                        link='plugins:slurpit_nautobot:data_mapping_list',
                        name='Data mapping',
                        permissions=[
                            "slurpit_nautobot.view_slurpitmapping",
                            "slurpit_nautobot.view_slurpitprefix",
                            "slurpit_nautobot.view_slurpitipaddress",
                            "slurpit_nautobot.view_slurpitinterface"
                        ]
                    ),
                    NavMenuItem(
                        link='plugins:slurpit_nautobot:reconcile_list',
                        name='Reconcile',
                        permissions=[
                            "slurpit_nautobot.view_slurpitmapping",
                            "slurpit_nautobot.view_slurpitprefix",
                            "slurpit_nautobot.view_slurpitipaddress",
                            "slurpit_nautobot.view_slurpitinterface"
                        ]
                    )
                )
            ),
        ),
        # icon_class='mdi mdi-swap-horizontal'
    ),
)
