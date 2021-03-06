# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import time
from openerp import pooler
from openerp import models,fields,api
from openerp.tools.translate import _


class account_invoice(models.Model):
    _inherit = 'account.invoice'


    @api.depends('date_invoice','amount_total','partner_id')
    def _compute(self):
        for obj in self:
            filter=[
                ('date_invoice', '=' , obj.date_invoice),
                ('amount_total', '=' , obj.amount_total),
                ('partner_id'  , '=' , obj.partner_id.id),
            ]
            invoices = self.env['account.invoice'].search(filter)
            msg=False
            if len(invoices)>1:
                msg='Attention : Il existe une autre facture du même montant à cette même date et pour ce même fournisseur'
            obj.is_msg_err=msg


    order_id                 = fields.Many2one('sale.order', 'Commande', readonly=False)
    is_affaire_id            = fields.Many2one('is.affaire', 'Affaire')
    is_refacturable          = fields.Selection([('oui','Oui'),('non','Non')], u"Refacturable")
    is_nom_fournisseur       = fields.Char('Nom du fournisseur')
    is_personne_concernee_id = fields.Many2one('res.users', u'Personne concernée')
    is_msg_err               = fields.Char('Message', compute='_compute', readonly=True)


    def create(self, cr, uid, vals, context=None):
        new_id = super(account_invoice, self).create(cr, uid, vals, context=context)
        origin = self.browse(cr, uid, new_id, context).origin
        if origin:
            sql="select id,affaire_id from sale_order where name= '"+origin+"' order by id desc limit 1"
            cr.execute(sql)
            res=cr.fetchone()
            if res:
                order_id      = res[0] or False
                is_affaire_id = res[1] or False
                if order_id:
                    vals={
                        'order_id'     : order_id,
                        'is_affaire_id': is_affaire_id,
                    }
                    self.write(cr, uid, new_id, vals, context=context)
        return new_id



    @api.multi
    def actualiser_affaire_sur_facture_action(self):
        for obj in self:
            if obj.order_id and not obj.is_affaire_id:
                obj.is_affaire_id = obj.order_id.affaire_id


    @api.multi
    def actualiser_affaire_sur_ligne_action(self):
        for obj in self:
            if obj.is_affaire_id:
                for line in obj.invoice_line:
                    if not line.is_affaire_id:
                        line.is_affaire_id = obj.is_affaire_id.id


    @api.multi
    def voir_facture_fournisseur(self):
        for obj in self:
            res= {
                'name': 'Facture',
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'account.invoice',
                'res_id': obj.id,
                'type': 'ir.actions.act_window',
            }
            return res


    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if name:
            filtre=['|',('name','ilike', name),('internal_number','ilike', name)]
            ids = self.search(cr, user, filtre, limit=limit, context=context)
        else:
            ids = self.search(cr, user, args, limit=limit, context=context)


        result = self.name_get(cr, user, ids, context=context)
        return result


class account_invoice_line(models.Model):
    _inherit = "account.invoice.line"

    is_affaire_id = fields.Many2one('is.affaire', u'Affaire')

    @api.multi
    def product_id_change(self, product, uom_id, qty=0, name='', type='out_invoice',
            partner_id=False, fposition_id=False, price_unit=False, currency_id=False,
            company_id=None, is_affaire_id=False):
        res = super(account_invoice_line, self).product_id_change(product, uom_id, qty=qty, name=name, type=type,
            partner_id=partner_id, fposition_id=fposition_id, price_unit=price_unit, currency_id=currency_id,
            company_id=company_id)
        if 'value' in res:
            if 'name' in res['value']:
                res['value']['name']=False
            if is_affaire_id:
                res['value']['is_affaire_id']=is_affaire_id
        return res



