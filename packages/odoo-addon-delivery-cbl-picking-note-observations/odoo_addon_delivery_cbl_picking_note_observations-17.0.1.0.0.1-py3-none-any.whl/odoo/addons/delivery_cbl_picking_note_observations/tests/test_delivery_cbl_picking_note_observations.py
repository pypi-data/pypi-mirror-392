# Copyright 2025 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.delivery_cbl.tests.test_delivery_cbl import TestCBLRequest


class TestCBLNoteObservations(TestCBLRequest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
                "country_id": cls.env.ref("base.es").id,
                "state_id": cls.env["res.country.state"].search([], limit=1).id,
            }
        )

    def test_note_observations(self):
        self.picking.carrier_id = self.carrier
        self.picking.company_id = self.env.company
        self.picking.partner_id = self.partner

        notes = "Custom Customer Notes"
        self.picking.customer_note = notes

        daily_token = "dummy_token"
        json_data = self.cbl_request._generate_shipping_json(self.picking, daily_token)

        self.assertIn("observations1", json_data)
        self.assertIn("observations2", json_data)
        self.assertIn(notes, json_data.get("observations1"))
