from datetime import timedelta

from odoo import models, fields, api

class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Oferta sobre propiedad'

    price = fields.Float(string="Precio", required=True)
    status = fields.Selection(
        selection=[
            ("accepted", "Aceptada"),
            ("refused", "Rechazada"),
        ],
        string="Estado",
        required=True,
    )
    validity = fields.Integer(string="Validez (días)", default=7)
    date_deadline = fields.Date(string="Fecha límite", compute="_compute_date_deadline", inverse="_inverse_date_deadline", store=True)

    partner_id = fields.Many2one(
        comodel_name="res.partner", string="Ofertante", required=True
    )
    property_id = fields.Many2one(
        comodel_name="estate.property", string="Propiedad", required=True
    )

    property_type = fields.Char(related="property_id.property_type_id.name", string="Tipo de propiedad", store=True, readonly=True)

    @api.depends("create_date", "validity")
    def _compute_date_deadline(self):
        for record in self:
            if record.create_date and record.validity:
                record.date_deadline = record.create_date + timedelta(days=record.validity)
            else:
                record.date_deadline = False

    def _inverse_date_deadline(self):
        for record in self:
            if record.date_deadline:
                record.validity = (record.date_deadline - record.create_date).days
            else:
                record.validity = 0