# -*- coding: utf-8 -*-
from openerp import models,fields,api
from openerp.tools.translate import _
import datetime


class IsSuiviCaisse(models.Model):
    _name='is.suivi.caisse'
    _order='date desc, id desc'


    def _compute_solde(self):
        cr, uid, context = self.env.args
        for obj in self:
            cr.execute("select sum(credit-debit) from is_suivi_caisse where date<='"+str(obj.date)+"' and id>="+str(obj.id)+" ")
            obj.solde=cr.fetchone()[0] or 0.0


    date        = fields.Date("Date"   , required=True, select=True)
    libelle     = fields.Char("Libellé", required=True)
    invoice_id  = fields.Many2one('account.invoice', u'Facture')
    debit       = fields.Float("Débit" , digits=(14,2))
    credit      = fields.Float("Crédit", digits=(14,2))
    solde       = fields.Float("Solde", compute=_compute_solde)
    commentaire = fields.Char("Commentaire")

