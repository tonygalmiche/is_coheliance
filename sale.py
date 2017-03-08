# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import time
from openerp import pooler
from openerp.osv import fields, osv
from openerp.tools.translate import _

class sale_order(osv.osv):
    _inherit = 'sale.order'
    
    _columns = {
        'affaire_id': fields.many2one('is.affaire', 'Affaire', readonly=True),
    }
