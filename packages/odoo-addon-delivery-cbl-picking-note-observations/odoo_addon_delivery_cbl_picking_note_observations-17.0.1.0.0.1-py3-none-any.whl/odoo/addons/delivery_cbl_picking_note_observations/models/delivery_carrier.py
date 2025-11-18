# Copyright 2025 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    cbl_observations_size = fields.Integer(default=33, required=True)

    _sql_constraints = [
        (
            "cbl_observations_size",
            "CHECK (cbl_observations_size > 0)",
            "CBL Observatios Size should be positive!",
        ),
    ]
