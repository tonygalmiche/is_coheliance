# -*- coding: utf-8 -*-


from openerp import models,fields,api
from openerp.tools.translate import _


class product_template(models.Model):
    _inherit = 'product.template'

    is_type_frais         = fields.Boolean('Type de frais'        , help=u'Cocher cette case pour afficher cet article dans les fiches de frais')
    is_type_frais_hors_km = fields.Boolean('Type de frais hors km', help=u'Cocher cette case pour afficher cet article dans le tableau de refacturation total des frais')


