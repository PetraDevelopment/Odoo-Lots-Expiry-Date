from datetime import datetime
import logging

from odoo.exceptions import ValidationError
from odoo.fields import first
from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta


import logging
_logger = logging.getLogger(__name__)


class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    use_date = fields.Datetime(
        string='Best Before Date', store=True)
    alert_date = fields.Datetime(
        string='Alert Date', store=True)
    end_life_date = fields.Datetime(
        string='End of Life Date',  store=True)
    removal_date = fields.Datetime(
        string='Removal Date', store=True)

    assigned_to = fields.Char()

    product_expiry_alert = fields.Boolean(
        compute='_compute_product_expiry_alert', help="The Expiration Date has been reached.")
    product_expiry_reminded = fields.Boolean(string="Expiry has been reminded")

    @api.depends('end_life_date')
    def _compute_product_expiry_alert(self):
        current_date = fields.Datetime.now()
        for lot in self:
            if lot.end_life_date:
                lot.product_expiry_alert = lot.end_life_date <= current_date
            else:
                lot.product_expiry_alert = False

    # How to get old value of a field in a fucntion - Odoo12

    # @api.model
    # def write(self, vals):
    #     if 'assigned_to' in vals:
    #         new_value = vals['assigned_to']
    #         # To get the old value, you need to access it from the 'vals' dictionary
    #         old_value = self._origin.assigned_to  # Use '_origin' to access old values
    #         print(new_value, old_value)
    #     res = super(ProductionLot, self).write(vals)
    #     return res

    # date = fields.Datetime('Date', default=fields.Datetime.now)

    message = fields.Char()
    now_time = fields.Datetime(default=lambda self: datetime.now())
    timestamp = fields.Datetime(default=lambda self: datetime.now())
    expiration_date_out = fields.Integer(
        string='Expiration Date after days ', compute='_compute_expiry')
    # expiration_date_out = fields.Datetime(
    #     string='expiration_date_out', compute='_compute_expiry')

    def _compute_expiry(self):
        for lot in self:
            if lot.end_life_date and lot.now_time:
                # 'lot.end_life_date', '<=', fields.Datetime.now()
                delta = (lot.end_life_date - lot.now_time).days
                if delta <= 0:
                    lot.message = f'Product {lot.product_id.name} with lot {lot.name} has expired '
                    lot.expiration_date_out = delta

                    # Here you can add any custom logic or trigger an event if the product of the lot is expired
                    _logger.info(
                        "Product with lot %s has expired lot.expiration_date_out=  %s  --.  %s has expired", lot.name, lot.expiration_date_out, delta)
                else:
                    lot.expiration_date_out = delta
            else:
                lot.expiration_date_out = 0
            _logger.info("Computed field_based_on_group: %s  ",
                         lot.expiration_date_out)


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    test = fields.Char(string='test')

    # Define computed fields to access the dates from the lot
    computed_best_before_date = fields.Datetime(
        string='Best Before Date', store=True)
    computed_alert_date = fields.Datetime(
        string='Alert Date', store=True)
    computed_end_life_date = fields.Datetime(
        string='End of Life Date', store=True)
    computed_removal_date = fields.Datetime(
        string='Removal Date', store=True)

    picking_id = fields.Many2one(
        'stock.picking', 'Transfer', auto_join=True,
        check_company=True,
        index=True,
        help='The stock operation where the packing has been made')

    picking_type_code = fields.Selection(
        related='picking_id.picking_type_code',
        string='Picking Type Code',
        store=True,
        readonly=True
    )

    @api.model
    def _get_value_production_lot(self):
        self.ensure_one()
        # Add your custom logic here
        # For example, log a message

        # Call the original method to maintain its functionality

        # Modify the result if needed
        # For example, add additional fields to the dictionary
        res = super(StockMoveLine, self)._get_value_production_lot()
        res.update({
            'use_date': self.computed_best_before_date,
            'alert_date': self.computed_alert_date,
            'removal_date': self.computed_removal_date,
            'end_life_date': self.computed_end_life_date,
        })
        _logger.info(
            "Retrieved self.computed_best_before_date in orgin %s  best_before_date ", self.computed_best_before_date)

        return res

    partner_name = fields.Char(string='user')

    #     _logger.info(
    #         "Retrieved .items.name : %s  best_before_date ", lot.product_id.id, lot.best_before_date)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    expired_lots_message = fields.Text(
        string="Expired Lots Message", readonly=True, store=False)

    def button_validate(self):
        # Check for expired lots and set the message
        expired_lots = self.env['stock.production.lot'].search([
            ('end_life_date', '<=', fields.Datetime.now())
        ])
        print("okay validate product_name %s lot_name %s",
              expired_lots)

        # Collect the products and lots to be validated
        # Collect the products and lots to be validated
        products_to_validate = {}
        expired_lots_to_validate = []
        for picking in self:
            for move_line in picking.move_line_ids:
                product_name = move_line.product_id.name
                lot_name = move_line.lot_id.name
                lot_id = move_line.lot_id.id
                if product_name not in products_to_validate:
                    products_to_validate[product_name] = []
                if lot_name:
                    if lot_id in expired_lots.ids:
                        products_to_validate[product_name].append(
                            (lot_name, lot_id))
                        expired_lots_to_validate.append(
                            (product_name, lot_name, lot_id))

        # Construct the validation error message
        validation_error_message = ""
        has_expired_lots = False
        for product_name, lots in products_to_validate.items():
            validation_error_message += f"Product: {product_name}\n"
            if lots:
                validation_error_message += "  Lots:\n"
                for lot_name, lot_id in lots:
                    validation_error_message += f"    - Lot: {lot_name} (ID: {lot_id})\n"
            else:
                validation_error_message += "  No expire lots found for this product.\n"

        # Append all expired lots to the message
        if expired_lots_to_validate:
            validation_error_message += "\nExpired Lots:\n"
            print("okay validate product_name %s lot_name %s",
                  product_name, lot_name)
            for product_name, lot_name, lot_id in expired_lots_to_validate:
                validation_error_message += f"  Product: {product_name}, Lot: {lot_name} (ID: {lot_id})\n"
            has_expired_lots = True

        # If there are expired lots, raise a validation error
        if has_expired_lots:
            raise ValidationError(
                _("Some products in this picking have expired lots. Please record new end of life dates before proceeding.\n\n%s" % (
                    validation_error_message))
            )
        else:
            print("okay validate")

        # Call the super method to perform the standard validation
        res = super(StockPicking, self).button_validate()

        return res
