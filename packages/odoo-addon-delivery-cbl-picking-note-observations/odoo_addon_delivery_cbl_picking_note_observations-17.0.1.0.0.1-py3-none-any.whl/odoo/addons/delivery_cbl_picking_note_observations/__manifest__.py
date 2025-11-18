# Copyright 2025 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Delivery Cbl Picking Note Observations",
    "summary": "Send Observations to CBL Picking Deliveries with customer_note field",
    "version": "17.0.1.0.0",
    "category": "Delivery",
    "website": "https://github.com/sygel-technology/sy-delivery-carrier",
    "author": "Sygel, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "delivery_cbl",
        "sale_stock_picking_note",
    ],
    "data": [
        "views/delivery_carrier_views.xml",
    ],
}
