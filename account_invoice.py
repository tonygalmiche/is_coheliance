# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import time
from openerp import pooler
from openerp.osv import fields, osv
from openerp.tools.translate import _

class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    
    _columns = {
        'order_id': fields.many2one('sale.order', 'Commande', readonly=False),
    }

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

