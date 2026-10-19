from odoo import fields, models, api
from datetime import date
from dateutil.relativedelta import relativedelta

class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'Propiedad'

    name = fields.Char(string="Título", required=True)
    description = fields.Text(string="Descripción")
    postcode = fields.Char(string="Código Postal")
    date_availability = fields.Date(string="Fecha disponibilidad", copy=False, default=lambda self: date.today() + relativedelta(months=3))
    expected_price = fields.Float(string="Precio esperado")
    selling_price = fields.Float(string="Precio de venta", copy=False)
    bedrooms = fields.Integer(string="Habitaciones", default=2)
    living_area = fields.Integer(string="Superficie cubierta")
    facades = fields.Integer(string="Fachadas")
    garage = fields.Boolean(string="Garage")
    garden = fields.Boolean(string="Jardín")
    garden_orientation = fields.Selection(
        selection=[
            ("north", "Norte"),
            ("south", "Sur"),
            ("east", "Este"),
            ("west", "Oeste"),
        ],
        default="north",
        string="Orientación del jardín",
    )
    garden_area = fields.Integer(string="Superficie del jardín")
    state = fields.Selection(
        selection=[
            ("new", "Nuevo"),
            ("offer_received", "Oferta recibida"),
            ("offer_accepted", "Oferta aceptada"),
            ("sold", "Vendido"),
            ("canceled", "Cancelado"),
        ],
        default="new", string="Estado", copy=False, required=True
    )
    property_type_id = fields.Many2one(
        comodel_name="estate.property.type", string="Tipo de propiedad"
    )
    buyer_id = fields.Many2one(
        comodel_name="res.partner", string="Comprador"
    )

    salesman_id = fields.Many2one(
        comodel_name="res.users", string="Vendedor", copy=False, default=lambda self: self.env.user
    )

    tags_ids = fields.Many2many(
        comodel_name="estate.property.tag", string="Etiquetas"
    )

    offer_ids = fields.One2many(
        comodel_name="estate.property.offer",
        inverse_name="property_id",
        string="Ofertas"
    )

    # Unidad 2
    total_area = fields.Integer(string="Superficie total", compute="_compute_total_area", store=True)

    best_offer_price = fields.Float(string="Mejor oferta", compute="_compute_best_offer_price")


    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends("offer_ids.price")
    def _compute_best_offer_price(self):
        for record in self:
            if record.offer_ids:
                record.best_offer_price = max(record.offer_ids.mapped("price"))
            else:
                record.best_offer_price = 0.0

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "north"
        else:
            self.garden_area = 0
            self.garden_orientation = False

    @api.onchange("expected_price")
    def _onchange_expected_price(self):
        if self.expected_price and self.expected_price < 10000:
            return {
                "warning": {
                    "title": "Valor esperado negativo",
                    "message": "El valor esperado no puede ser negativo.",
                }
            }