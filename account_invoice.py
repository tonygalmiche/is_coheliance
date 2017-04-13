# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import time
from openerp import pooler
from openerp import models,fields,api
from openerp.tools.translate import _


class account_invoice(models.Model):
    _inherit = 'account.invoice'
    
    order_id                 = fields.Many2one('sale.order', 'Commande', readonly=False)
    is_nom_fournisseur       = fields.Char('Nom du fournisseur')
    is_personne_concernee_id = fields.Many2one('res.users', u'Personne concernée')


    def create(self, cr, uid, vals, context=None):
        new_id = super(account_invoice, self).create(cr, uid, vals, context=context)
        origin = self.browse(cr, uid, new_id, context).origin
        if origin:
            print origin
            sql="select id from sale_order where name= '"+origin+"' order by id desc limit 1"
            cr.execute(sql)
            print sql
            res=cr.fetchone()
            print res
            if res:
                order_id=res[0] or False
                print order_id
                if order_id:
                    self.write(cr, uid, new_id, {'order_id': order_id}, context=context)
        return new_id

