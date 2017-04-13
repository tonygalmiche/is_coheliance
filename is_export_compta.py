# -*- coding: utf-8 -*-
from openerp import models,fields,api
from openerp.tools.translate import _
import datetime
from openerp.exceptions import Warning


class is_export_compta(models.Model):
    _name='is.export.compta'
    _order='name desc'

    name               = fields.Char("N°Folio"      , readonly=True)
    type_interface     = fields.Selection([('ventes', u'Ventes'),('achats', u'Achats')], "Interface", required=True)
    date_debut         = fields.Date("Date de début")
    date_fin           = fields.Date("Date de fin")
    num_debut          = fields.Char("N° facture début")
    num_fin            = fields.Char("N° facture fin")

    ligne_ids          = fields.One2many('is.export.compta.ligne', 'export_compta_id', u'Lignes')


    _defaults = {
        'type_interface':  'ventes',
    }


    @api.model
    def create(self, vals):
        data_obj = self.env['ir.model.data']
        sequence_ids = data_obj.search([('name','=','is_export_compta_seq')])
        if sequence_ids:
            sequence_id = data_obj.browse(sequence_ids[0].id).res_id
            vals['name'] = self.env['ir.sequence'].get_id(sequence_id, 'id')
        res = super(is_export_compta, self).create(vals)
        return res


    @api.multi
    def action_export_compta(self):
        cr=self._cr
        for obj in self:
            obj.ligne_ids.unlink()
            if obj.type_interface=='ventes':
                type_facture=['out_invoice', 'out_refund']
                journal='VTE'
            else:
                type_facture=['in_invoice', 'in_refund']
                journal='AC'
            filter=[
                ('state'       , 'in' , ['open','paid']),
                ('type'        , 'in' , type_facture)
            ]
            if obj.date_debut:
                filter.append(('date_invoice', '>=', obj.date_debut))
            if obj.date_fin:
                filter.append(('date_invoice', '<=', obj.date_fin))
            if obj.num_debut:
                filter.append(('number', '>=', obj.num_debut))
            if obj.num_fin:
                filter.append(('number', '<=', obj.num_fin))
            invoices = self.env['account.invoice'].search(filter, order="date_invoice,id")
            if len(invoices)==0:
                raise Warning('Aucune facture à traiter')
            for invoice in invoices:
                sql="""
                    SELECT  
                        ai.date_invoice,
                        aa.code, 
                        ai.number, 
                        rp.name, 
                        aml.name,
                        ai.type, 
                        rp.is_code_fournisseur,
                        ai.is_nom_fournisseur,
                        sum(aml.debit), 
                        sum(aml.credit)

                    FROM account_move_line aml inner join account_invoice ai             on aml.move_id=ai.move_id
                                               inner join account_account aa             on aml.account_id=aa.id
                                               inner join res_partner rp                 on ai.partner_id=rp.id
                    WHERE ai.id="""+str(invoice.id)+"""
                    GROUP BY ai.date_invoice, ai.number, rp.name, aml.name, aa.code, ai.type, ai.date_due, rp.supplier,rp.is_code_fournisseur,ai.is_nom_fournisseur
                    ORDER BY ai.date_invoice, ai.number, rp.name, aml.name, aa.code, ai.type, ai.date_due, rp.supplier,rp.is_code_fournisseur,ai.is_nom_fournisseur
                """
                cr.execute(sql)
                for row in cr.fetchall():
                    nom_fournisseur=str(row[7])
                    if nom_fournisseur=='None':
                        nom_fournisseur=row[3]
                    libelle=nom_fournisseur+u' - '+row[4]
                    compte=str(row[1])
                    if obj.type_interface=='achats' and compte=='401100':
                        compte=str(row[6])
                    vals={
                        'export_compta_id'  : obj.id,
                        'date_facture'      : row[0],
                        'journal'           : journal,
                        'compte'            : compte,
                        'libelle'           : libelle,
                        'debit'             : row[8],
                        'credit'            : row[9],
                        'devise'            : 'E',
                        'piece'             : row[2],
                        'commentaire'       : False,
                    }
                    self.env['is.export.compta.ligne'].create(vals)


class is_export_compta_ligne(models.Model):
    _name = 'is.export.compta.ligne'
    _description = u"Lignes d'export en compta"
    _order='date_facture'

    export_compta_id = fields.Many2one('is.export.compta', 'Export Compta', required=True)
    date_facture     = fields.Date("Date")
    journal          = fields.Char("Journal")
    compte           = fields.Char("N°Compte")
    piece            = fields.Char("Pièce")
    libelle          = fields.Char("Libellé")
    debit            = fields.Float("Débit")
    credit           = fields.Float("Crédit")
    devise           = fields.Char("Devise")
    commentaire      = fields.Char("Commentaire")


    _defaults = {
        'journal': 'VTE',
        'devise' : 'E',
    }







