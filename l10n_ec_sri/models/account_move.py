# -*- coding: utf-8 -*-
from odoo import api,fields, models
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    tax_form_ids = fields.Many2many(
        'l10n_ec_sri.tax.form', 'move_tax_form_rel', 'tax_form_ids',
        'move_ids', string="Tax form", )
    r_invoice_ids = fields.One2many(
        'account.move',
        'r_move_id',
        string='Facturas a las que retiene',
        )
    move_name = fields.Char(string='Number', related='invoice_line_ids.move_name', store=True)
    invoice_date = fields.Date(string='Invoice/Bill Date', readonly=True, index=True, copy=False,
        states={'draft': [('readonly', False)]},
        default=datetime.today())
    
    
    
"""
class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # Necesitamos saber si el asiento es parte de una retención o si fué creado
    # como un pago, para el outstanding payments widget.
    r_invoice_id = fields.Many2one('account.move', string='Retención de la factura', )
"""
