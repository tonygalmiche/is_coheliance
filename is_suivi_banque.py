# -*- coding: utf-8 -*-
from openerp import models,fields,api
from openerp.tools.translate import _
import datetime
import codecs
import unicodedata
import base64


def _date_creation():
    now  = datetime.date.today()
    return now.strftime('%Y-%m-%d')



class IsSuiviBanque(models.Model):
    _name='is.suivi.banque'
    _order='import_banque_id desc,ligne, id'


    def _compute_solde(self):
        cr, uid, context = self.env.args
        for obj in self:
            cr.execute("select sum(credit-debit) from is_suivi_banque where date<='"+str(obj.date)+"' and ligne>="+str(obj.ligne)+" ")
            obj.solde=cr.fetchone()[0] or 0.0

            #x1 = cr.fetchone()[0] or 0.0
            #cr.execute("select sum(value) from kmn_account_move where account2_id="+str(obj.id))
            #x2 = cr.fetchone()[0] or 0.0
            #obj.bal_solde=x2-x1




    import_banque_id = fields.Many2one('is.import.banque', 'Import Banque', required=True, ondelete='cascade')
    ligne            = fields.Integer("Ligne", select=True)
    date             = fields.Date("Date"   , required=True, select=True)
    libelle          = fields.Char("Libellé", required=True)
    invoice_id       = fields.Many2one('account.invoice', u'Facture')
    debit            = fields.Float("Débit" , digits=(14,2))
    credit           = fields.Float("Crédit", digits=(14,2))
    solde            = fields.Float("Solde", compute=_compute_solde)
    commentaire      = fields.Char("Commentaire")


class IsImportBanque(models.Model):
    _name='is.import.banque'
    _order='name desc'

    name               = fields.Date(u"Date de création", default=lambda *a: _date_creation())
    file_operation_ids = fields.Many2many('ir.attachment', 'is_import_banque_operation_attachment_rel', 'doc_id', 'file_id', 'Opérations à importer')
    file_cb_ids        = fields.Many2many('ir.attachment', 'is_import_banque_cb_attachment_rel'       , 'doc_id', 'file_id', 'Détail CB à importer')
    ligne_ids          = fields.One2many('is.suivi.banque', 'import_banque_id', u'Lignes')


    @api.multi
    def action_importer_fichier(self):
        for obj in self:
            obj.ligne_ids.unlink()
            for attachment in obj.file_operation_ids:
                attachment=base64.decodestring(attachment.datas)
                attachment=attachment.decode('iso-8859-1').encode('utf8')
                csvfile=attachment.split("\n")
                tab=[]
                ct=0

                nb_lignes=len(csvfile)


                for row in csvfile:
                    ct=ct+1
                    if ct>1:
                        lig=row.split(";")
                        if len(lig)>5:
                            print lig
                            date    = lig[1]
                            libelle = lig[3]
                            montant = lig[6].replace(',', '.')
                            try:
                                montant = float(montant)
                            except ValueError:
                                montant=0
                            debit=0
                            credit=0
                            if montant<0:
                                debit=-montant
                            else:
                                credit=montant
                            vals={
                                'import_banque_id'  : obj.id,
                                'ligne'             : (ct-1),
                                'date'              : date,
                                'libelle'           : libelle,
                                'debit'             : debit,
                                'credit'            : credit,
                            }
                            self.env['is.suivi.banque'].create(vals)
            return {
                'name': u'Suivi banque '+obj.name,
                'view_mode': 'tree,form',
                'view_type': 'form',
                'res_model': 'is.suivi.banque',
                'domain': [
                    ('import_banque_id','=',obj.id),
                ],
                'context':{
                    'default_import_banque_id': obj.id,
                },
                'type': 'ir.actions.act_window',
            }









