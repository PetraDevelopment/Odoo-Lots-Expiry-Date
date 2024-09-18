
# from odoo.tools import Command
from datetime import datetime
from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)

# expiry_date_of_end_life_date = fields.Char(
#     string="Expiry")


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    lot_account_move = fields.Char(related='sale_line_ids.lot_sale_order_line')

    expiry_date_of_end_life_date = fields.Date(
        string="Expiry Date",
        compute='get_lot_date',
        store=True
    )
    lot_ids = fields.Many2many(
        'stock.production.lot', string='Serial Numbers', compute='get_lot_date', store=True)

    @api.depends('lot_ids', 'sale_line_ids.move_ids.lot_ids', 'purchase_line_id.move_ids.lot_ids')
    def get_lot_date(self):
        for rec in self:
            lots = rec.sale_line_ids.move_ids.lot_ids or rec.purchase_line_id.move_ids.lot_ids
            date_list = []
            if lots:
                rec.lot_ids = lots
                for lot in lots:
                    print("okay validate 'ir.actions.lot lot', %s", lot)
                    if lot.end_life_date:
                        print("okay validate lot.end_life_date,",
                              lot.end_life_date)
                        date_list.append(
                            lot.end_life_date.strftime("%Y-%m-%d %H:%M:%S"))  # Modified format string
                        print("22okay validate lot.end_life_date, %s", date_list)
                rec.expiry_date_of_end_life_date = max(
                    date_list) if date_list else False


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    lot_sale_order_line = fields.Char(
        compute='_compute_lot_sale', string='Lot')
    lot_ids = fields.Many2many(
        'stock.production.lot', string="Serial Numbers", compute='_compute_lot_sale', store=True)

    @api.depends('qty_delivered')
    def _compute_lot_sale(self):
        for line in self:
            move_ids = self.env['stock.move'].search([
                ('sale_line_id', '=', line.id)
            ])
            if move_ids:
                line.lot_ids = move_ids.lot_ids
                line.lot_sale_order_line = ''
            else:
                line.lot_sale_order_line = ''
