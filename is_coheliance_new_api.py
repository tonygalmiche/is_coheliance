# -*- coding: utf-8 -*-


import time
from openerp import pooler
from openerp import models,fields,api
from openerp.tools.translate import _
import datetime




def _date_creation():
    now  = datetime.date.today()
    return now.strftime('%Y-%m-%d')


class is_affaire_vente(models.Model):
    _name  = 'is.affaire.vente'
    _order = 'date'


    @api.depends('quantite','prix_achat','prix_vente')
    def _compute(self):
        for obj in self:
            obj.total_achat=obj.quantite*obj.prix_achat
            obj.total_vente=obj.quantite*obj.prix_vente


    affaire_id  = fields.Many2one('is.affaire', 'Affaire', required=True)
    date        = fields.Date(u"Date", required=True)
    product_id  = fields.Many2one('product.product', u'Article', required=True)
    quantite    = fields.Float(u"Quantité")
    prix_achat  = fields.Float(u"Prix d'achat")
    prix_vente  = fields.Float(u"Prix de vente")
    total_achat = fields.Float(u"Total des achats", compute='_compute', readonly=True, store=True)
    total_vente = fields.Float(u"Total des ventes", compute='_compute', readonly=True, store=True)
    commentaire = fields.Char(u"Commentaire")


class is_frais(models.Model):
    _name = 'is.frais'
    _description = u"Fiche de frais"
    _order='name desc'

    name           = fields.Char(u"Numéro")
    date_creation  = fields.Date(u"Date de création")
    affaire_id     = fields.Many2one('is.affaire', 'Affaire', required=True)
    intervenant_id = fields.Many2one('res.users', u'Intervenant', required=True)
    taux_km        = fields.Float(u"Taux indemnité kilométrique")
    ligne_ids      = fields.One2many('is.frais.ligne', 'frais_id', u'Lignes')


    def _taux_km(self,cr):
        sql="select taux_km from res_company limit 1";
        cr.execute(sql)
        taux_km=0
        for row in cr.fetchall():
            taux_km=row[0]
        return taux_km


    _defaults = {
        'name': '',
        'intervenant_id': lambda obj, cr, uid, context: uid,
        'date_creation': lambda *a: _date_creation(),
        'taux_km': lambda self, cr, uid, context: self._taux_km(cr),
    }


    @api.model
    def create(self, vals):
        data_obj = self.env['ir.model.data']
        sequence_ids = data_obj.search([('name','=','is_frais_seq')])
        if sequence_ids:
            sequence_id = data_obj.browse(sequence_ids[0].id).res_id
            vals['name'] = self.env['ir.sequence'].get_id(sequence_id, 'id')
        res = super(is_frais, self).create(vals)
        return res


    @api.multi
    def write(self, vals):
        for obj in self:
            if 'taux_km' in vals:
                taux_km=vals['taux_km']
                for lig in obj.ligne_ids:
                    if lig.km:
                        lig.montant_ht=lig.km*taux_km
        res = super(is_frais, self).write(vals)
        return res

    @api.multi
    def print_fiche_frais(self):
        cr, uid, context = self.env.args
        for obj in self:
            return self.pool['report'].get_action(cr, uid, obj.id, 'is_coheliance.report_frais', context=context)



class is_frais_ligne(models.Model):
    _name = 'is.frais.ligne'
    _description = u"Lignes des fiches de frais"
    _order='date desc'

    @api.depends('type_frais_id','montant_ht')
    def _montant_ttc(self):
        res={}
        for obj in self:
            tva=0
            if obj.type_frais_id:
                if obj.type_frais_id.taxes_id:
                    for taxe in obj.type_frais_id.taxes_id:
                        tva=taxe.amount
            obj.montant_ttc=obj.montant_ht*(1+tva)


    frais_id       = fields.Many2one('is.frais', 'Frais', required=True)
    affaire_id     = fields.Many2one('is.affaire', 'Affaire', related='frais_id.affaire_id', readonly=True)
    intervenant_id = fields.Many2one('res.users', u'Intervenant', related='frais_id.intervenant_id', readonly=True)
    date           = fields.Date(u"Date")
    type_frais_id  = fields.Many2one('product.template', u'Type de frais')
    refacturable   = fields.Selection([('oui','Oui'),('non','Non')], u"Refacturable")
    km             = fields.Integer(u"Km")
    montant_ht     = fields.Float(u"Montant HT", digits=(14,2))
    montant_ttc    = fields.Float('Montant TTC', digits=(14,2), compute='_montant_ttc', readonly=True, store=True)
    refacture      = fields.Boolean(u"Frais refacturé au client")

    _defaults = {
        'date': lambda *a: _date_creation(),
        'refacturable': 'oui',
        'refacture': False,
    }


    @api.model
    def create(self,vals):
        obj = super(is_frais_ligne, self).create(vals)
        if 'km' in vals:
            if vals['km']!=0:
                taux_km=obj.frais_id.taux_km
                obj.montant_ht=vals['km']*taux_km
        return obj


    @api.multi
    def write(self, vals):
        for obj in self:
            if 'km' in vals:
                taux_km=obj.frais_id.taux_km
                vals['montant_ht']=vals['km']*taux_km
        res = super(is_frais_ligne, self).write(vals)
        return res





#TODO, j'ai voulu rendre modifiable le compte des lignes des factures validées et payées, mais ce n'est pas possible
#class account_invoice_line(models.Model):
#    _inherit = 'account.invoice.line'
#    
#    is_number = fields.Char('N°Facture', related='invoice_id.number', readonly=True)





