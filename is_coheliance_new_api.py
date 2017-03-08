# -*- coding: utf-8 -*-


import time
from openerp import pooler
from openerp import models,fields,api
from openerp.tools.translate import _

from datetime import datetime, timedelta


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

    _defaults = {
        'name': '',
        'intervenant_id': lambda obj, cr, uid, context: uid,
        'date_creation': datetime.today().strftime('%Y-%m-%d'),
    }


    @api.model
    def create(self, vals):
        company_obj = self.env['res.company']
        taux_km = company_obj.browse(1).taux_km
        vals["taux_km"]=taux_km

        data_obj = self.env['ir.model.data']
        sequence_ids = data_obj.search([('name','=','is_frais_seq')])
        if sequence_ids:
            sequence_id = data_obj.browse(sequence_ids[0].id).res_id
            vals['name'] = self.env['ir.sequence'].get_id(sequence_id, 'id')
        res = super(is_frais, self).create(vals)
        return res



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
        'date': datetime.today().strftime('%Y-%m-%d'),
        'refacturable': 'oui',
        'refacture': False,
    }


    @api.model
    def create(self,vals):
        if 'km' in vals:
            if vals['km']!=0:
                company_obj = self.env['res.company']
                taux_km = company_obj.browse(1).taux_km
                vals['montant_ht']=vals['km']*taux_km
        res = super(is_frais_ligne, self).create(vals)
        return res


    @api.multi
    def write(self, vals):
        if 'km' in vals:
            company_obj = self.env['res.company']
            taux_km = company_obj.browse(1).taux_km
            vals['montant_ht']=vals['km']*taux_km
        res = super(is_frais_ligne, self).write(vals)
        return res



