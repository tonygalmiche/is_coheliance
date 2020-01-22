# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import time
from openerp import pooler
from openerp import models,fields,api
from openerp.tools.translate import _


class account_bank_statement(models.Model):
    _inherit = 'account.bank.statement'


    @api.multi
    def export_compta_banque_action(self):
        for obj in self:
            print obj

            vals={
                'type_interface': 'banque',
            }
            export = self.env['is.export.compta'].create(vals)



            for line in obj.line_ids:
                print line

                debit  = 0
                credit = 0
                if line.amount<0:
                    debit = abs(line.amount)
                else:
                    credit = line.amount

                vals={
                    'export_compta_id'  : export.id,
                    'date_facture'      : line.date,
                    'journal'           : 'BANQUE',
                    'compte'            : line.partner_id.is_code_fournisseur or False,
                    'libelle'           : line.name,
#                    'affaire'           : affaire,
                    'debit'             : debit,
                    'credit'            : credit,
                    'devise'            : 'E',
                    'piece'             : line.ref,
#                    'commentaire'       : False,
                }
                self.env['is.export.compta.ligne'].create(vals)


            return {
                'name': u'Export banque',
                'view_mode': 'tree',
                'view_type': 'form',
                'res_model': 'is.export.compta.ligne',
                'domain': [
                    ('export_compta_id','=',export.id),
                ],
                'type': 'ir.actions.act_window',
                'limit': 1000,
            }





