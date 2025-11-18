# Copyright 2025 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.delivery_cbl.models.cbl_request import CBLRequest

original_generate_shipping_json = CBLRequest._generate_shipping_json


def new_generate_shipping_json(self, picking, daily_token):
    vals = original_generate_shipping_json(self, picking, daily_token)
    if picking.customer_note:
        limit1 = picking.carrier_id.cbl_observations_size
        limit2 = limit1 * 2
        observations1 = picking.customer_note[:limit1]
        observations2 = picking.customer_note[limit1:limit2]
        vals.update({"observations1": observations1, "observations2": observations2})
    return vals


CBLRequest._generate_shipping_json = new_generate_shipping_json
