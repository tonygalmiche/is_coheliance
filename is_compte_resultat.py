# -*- coding: utf-8 -*-
from openerp import models,fields,api
from openerp.tools.translate import _
import datetime

import re


class is_compte_resultat_annee(models.Model):
    _name='is.compte.resultat.annee'
    _order='name desc'
    _sql_constraints = [('name_uniq','UNIQUE(name)', u'Cette année existe déjà')]

    name     = fields.Integer("Année", required=True, select=True)
    line_ids = fields.One2many('is.compte.resultat', 'compte_resultat_id', u'Lignes')

    @api.multi
    def action_calculer(self):
        for obj in self:
            print obj


            cr_obj=self.env['is.compte.resultat']

            

            rows=cr_obj.search([
                ('annee','=',0),
            ])
            for i in [0,1,2]:
                annee=obj.name-i
                for row in rows:
                    vals={
                        'compte_resultat_id' : obj.id,
                        'annee'              : annee,
                        'ordre'              : row.ordre,
                        'intitule'           : str(row.ordre)+u' '+row.intitule,
                        'type_champ'         : row.type_champ,
                        'associe_id'         : row.associe_id.id,
                        'article_achat_id'   : row.article_achat_id.id,
                        'article_vente_id'   : row.article_vente_id.id,
                        'formule'            : row.formule,
                        'couleur'            : row.couleur,
                        'objectif'           : row.objectif,
                    }
                    res=cr_obj.search([
                        ('annee','=',annee),
                        ('ordre','=',row.ordre),
                    ])
                    if len(res)>0:
                        res.update(vals)
                    else:
                        res=cr_obj.create(vals)
                    res.action_calculer()


            return {
                'name': "Compte de résultat "+str(obj.name),
                'view_type': 'form',
                'view_mode': 'graph,tree,form',
                'res_model': 'is.compte.resultat',
                'type': 'ir.actions.act_window',
                'domain': [('compte_resultat_id','=',obj.id)],
            }







class is_compte_resultat(models.Model):
    _name='is.compte.resultat'
    _order='ordre,annee'
    _sql_constraints = [('ordre_uniq','UNIQUE(annee,ordre)', u'Cet ordre existe déjà')]


    @api.multi
    def name_get(self):
        res=[]
        for obj in self:
            name=str(obj.annee)+u'-'+str(obj.ordre)
            res.append((obj.id, name))
        return res


    @api.depends('montant_calcule','montant_force')
    def _compute(self):
        for obj in self:
            now   = datetime.date.today()
            annee = int(now.strftime('%Y'))
            jour  = int(now.strftime('%j'))
            if jour>365:
                jour=365
            montant=obj.montant_calcule
            if obj.montant_force>0:
                montant=obj.montant_force
            if obj.type_champ=='saisie_manuelle' and obj.annee==annee:
                montant=obj.montant_force*jour/365
            obj.montant=montant


    @api.depends('article_achat_id','article_vente_id','type_champ')
    def _compute_code_comptable(self):
        for obj in self:
            code_comptable=''
            if obj.type_champ=='achat':
                if obj.article_achat_id:
                    code_comptable=obj.article_achat_id.property_account_expense.code
            if obj.type_champ=='vente':
                if obj.article_vente_id:
                    code_comptable=obj.article_vente_id.property_account_income.code
            obj.code_comptable=code_comptable


    compte_resultat_id = fields.Many2one('is.compte.resultat.annee', 'Compte de résultat', ondelete='cascade')
    annee      = fields.Integer("Année", select=True)
    intitule   = fields.Char("Intitulé", required=True, select=True)
    ordre      = fields.Integer("Ordre", required=True, select=True)
    type_champ = fields.Selection([
            ('saisie_manuelle', u'Saisie manuelle'),
            ('budget_prevu'   , u'Total budget prévu'),
            ('intervention'   , u'Interventions réalisées'),
            ('intervention_st', u'Interventions réalisées en sous-traitance'),
            ('vente'          , u'Ventes'),
            ('frais'          , u'Frais à refacturer'),
            ('achat'          , u'Achats'),
            ('calcul'         , u'Calcul'),
        ], u"Type de champ", select=True)
    associe_id       = fields.Many2one('res.users', u'Associé')
    article_achat_id = fields.Many2one('product.product', u'Article achat')
    article_vente_id = fields.Many2one('product.product', u'Article vente')
    code_comptable   = fields.Char("Code comptable", compute='_compute_code_comptable', readonly=True, store=True)
    formule          = fields.Char("Formule")
    couleur = fields.Selection([
        ('#FF0000','rouge'),
        ('#FFA500','orange'),
        ('#0000FF','bleu'),
        ('#008000','vert'),
        ('#FFFF00','jaune'),
        ('#FFC0CB','rose'),
        ('#FF00FF','fuchsia'),
        ('#800000','marron'),
        ('#000000','noir'),
        ('#FFFFFF','blanc'),
    ], "Code Couleur")
    montant_calcule  = fields.Float("Montant calculé", readonly=True)
    montant_force    = fields.Float("Montant forcé")
    montant          = fields.Float("Montant", compute='_compute', readonly=True, store=True)
    objectif         = fields.Float("Objectif année en cours")

    @api.multi
    def action_calculer(self):
        cr=self._cr

        for obj in self:
            montant=0
            if obj.type_champ=='budget_prevu':
                sql="""
                    SELECT sum(budget_prevu)
                    FROM is_affaire_intervenant
                    WHERE 
                        annee="""+str(obj.annee)+""" 
                """
                cr.execute(sql)
                for row in cr.fetchall():
                    montant=row[0]

            if obj.type_champ=='intervention' and obj.annee and obj.associe_id:
                sql="""
                    SELECT sum(iai.montant_facture)
                    FROM is_affaire_intervention iai
                    WHERE 
                        iai.associe_id="""+str(obj.associe_id.id)+""" and 
                        iai.date>='"""+str(obj.annee)+"""-01-01' and 
                        iai.date<='"""+str(obj.annee)+"""-12-31'
                """
                cr.execute(sql)
                for row in cr.fetchall():
                    montant=row[0]


            if obj.type_champ=='vente' and obj.annee and obj.article_vente_id:
                sql="""
                    SELECT sum(total_vente)
                    FROM is_affaire_vente
                    WHERE 
                        product_id="""+str(obj.article_vente_id.id)+""" and 
                        date>='"""+str(obj.annee)+"""-01-01' and 
                        date<='"""+str(obj.annee)+"""-12-31'
                """
                cr.execute(sql)
                for row in cr.fetchall():
                    montant=row[0]


            if obj.type_champ=='frais':
                sql="""
                    SELECT sum(montant_ht)
                    FROM is_frais_ligne
                    WHERE 
                        refacturable='oui' and
                        date>='"""+str(obj.annee)+"""-01-01' and 
                        date<='"""+str(obj.annee)+"""-12-31'
                """
                cr.execute(sql)
                for row in cr.fetchall():
                    montant=row[0]


            if obj.type_champ=='achat':
                if obj.article_achat_id.id:
                    sql="""
                        SELECT sum(ail.price_subtotal)
                        FROM account_invoice ai inner join account_invoice_line ail on ai.id=ail.invoice_id
                        WHERE
                            ai.type='in_invoice' and
                            ai.date_invoice>='"""+str(obj.annee)+"""-01-01' and 
                            ai.date_invoice<='"""+str(obj.annee)+"""-12-31' and 
                            ail.product_id="""+str(obj.article_achat_id.id)+""" 

                    """
                    cr.execute(sql)
                    for row in cr.fetchall():
                        montant=row[0]


            if obj.type_champ=='calcul':
                cr_obj = self.env['is.compte.resultat']
                formule=obj.formule
                p = re.compile('\[\d+\]')
                res=p.findall(formule)
                for r in res:
                    p = re.compile('\d+')
                    ordres=p.findall(r)
                    for ordre in ordres:
                        rows=cr_obj.search([
                            ('annee','=',obj.annee),
                            ('ordre','=',eval(ordre)),
                        ])
                        for row in rows:
                            formule=formule.replace(r, str(row.montant))
                montant=eval(formule)


            if str(montant)=='None':
                montant=0
            if type(montant) is list:
                montant=0
            obj.montant_calcule=montant





