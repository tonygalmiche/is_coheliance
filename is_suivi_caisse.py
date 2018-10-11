# -*- coding: utf-8 -*-
from openerp import models,fields,api
from openerp.tools.translate import _
import datetime


class IsSuiviCaisse(models.Model):
    _name='is.suivi.caisse'
    _order='id desc'

    date        = fields.Date("Date"   , required=True, select=True)
    libelle     = fields.Char("Libellé", required=True)
    invoice_id  = fields.Many2one('account.invoice', u'Facture')
    debit       = fields.Float("Débit" , digits=(14,2))
    credit      = fields.Float("Crédit", digits=(14,2))
    commentaire = fields.Char("Commentaire")

