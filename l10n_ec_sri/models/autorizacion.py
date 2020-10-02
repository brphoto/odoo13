# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.osv import expression
import logging

_logger = logging.getLogger(__name__)

class Autorizacion(models.Model):
    _name = 'l10n_ec_sri.autorizacion'
    _description = "Autorizaciones"

    name = fields.Char(string="Autorizacion",)
    autorizacion = fields.Char('Nro. de autorizacion', related="name", )
    establecimiento = fields.Char(
        'Establecimiento',
        size=3,
        required=True,
    )
    puntoemision = fields.Char(
        'Punto de impresion',
        size=3,
        required=True,
    )
    fechaemision = fields.Date('Fecha de emision', )
    fechavencimiento = fields.Date('Fecha de vencimiento', )
    secuencia_inicial = fields.Integer('Secuencia inicial', )
    secuencia_final = fields.Integer('Secuencia final', )
    secuencia_actual = fields.Integer(
        string='Último secuencial utilizado',
    )
    comprobante_id = fields.Many2one(
        'l10n_ec_sri.comprobante',
        string="Comprobante",
        required=True,
        domain=[('requiere_autorizacion', '=', True)],)
    c_invoice_ids = fields.One2many(
        'account.move', inverse_name='autorizacion_id', ondelete='restrict',
        string="Facturas", )
    r_invoice_ids = fields.One2many(
        'account.move', inverse_name='r_autorizacion_id', ondelete='restrict',
        string="Retenciones", )
    comprobantesanulados_ids = fields.One2many('l10n_ec_sri.comprobantesanulados', inverse_name='autorizacion_id',
                                               ondelete='restrict', string="Comprobantes anulados", )
    revisar = fields.Char(string="Comprobantes no registrados",
                          compute="_compute_c_ids", )

    
    @api.onchange('establecimiento')
    def _onchange_establecimiento(self):
        
        for r in self:
            if not r.establecimiento:
                return
            if r.establecimiento.isdigit():
                r.establecimiento = r.establecimiento.zfill(3)
            else:
                r.establecimiento = ''

    
    @api.onchange('puntoemision')
    def _onchange_puntoemision(self):
        
        for r in self:
            if not r.puntoemision:
                return
            if r.puntoemision.isdigit():
                r.puntoemision = r.puntoemision.zfill(3)
            else:
                r.puntoemision = ''

    # tipoEm se usa en el ATS.
    tipoem = fields.Selection(
        [
            ('F', 'Facturación física'),
            ('E', 'Facturación electrónica'),
        ],
        required=True,
        string='Tipo de emisión',
        defaut='F', )  # Default F es importante para que las facturas actuales sean todas físicas.

    # Facturación electrónica.
    direstablecimiento = fields.Char('Dirección del establecimiento', )

    
    def name_get(self):
        
        res = []
        for r in self:
            name = '-'.join([
                r.comprobante_id.name or '',
                r.establecimiento or '',
                r.puntoemision or '',
                r.autorizacion or '',
            ])
            res.append((r.id, name))
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        
        args = args or []
        domain = []
        if name:
            domain = ['|', ('establecimiento', '=ilike', name + '%'),
                      '|', ('puntoemision', '=ilike', name + '%'),
                      ('autorizacion', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&'] + domain
        autorizaciones = self.search(domain + args, limit=limit)
        return autorizaciones.name_get()

    
    @api.depends('secuencia_inicial', 'secuencia_actual', 'c_invoice_ids', 'comprobantesanulados_ids')
    def _compute_c_ids(self):
        for r in self:
            
            revisar = ''
            if r.tipoem != 'E' and r.secuencia_inicial != 0:
                anulados = list()
                revisar = ''
                for a in r.comprobantesanulados_ids:
                    _logger.warning('Primer')
                    for i in range(a.secuencialinicio, (a.secuencialfin + 1), 1):
                        anulados.append(i)
                
                if r.secuencia_inicial < (r.secuencia_actual + 1):
                    for n in range(r.secuencia_inicial, (r.secuencia_actual + 1), 1):
                        
                        if any(inv.secuencial == n for inv in r.c_invoice_ids) \
                            or any(inv.secuencial == n for inv in r.r_invoice_ids):
                            continue
                        else:
                            if n not in anulados:
                                revisar += str(n) + ', '
                            r.revisar = revisar
                else: 
                    r.revisar = revisar
            else:
                r.revisar=''

    @api.onchange('autorizacion')
    def _onchange_autorizacion(self):
        
        if self.autorizacion:
            self.name = self.autorizacion
        else:
            self.name=''
        

