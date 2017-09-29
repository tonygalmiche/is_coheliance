# -*- coding: utf-8 -*-
from openerp import models,fields,api
from openerp.tools.translate import _
import datetime


#TODO : Faire les calculs et mettre en production


class is_bilan_pedagogique(models.Model):
    _name='is.bilan.pedagogique'
    _order='name desc'
    _sql_constraints = [('name_uniq','UNIQUE(name)', u'Cette année existe déjà')]

    name               = fields.Integer("Année", required=True, select=True)
    financier_ids      = fields.One2many('is.bilan.pedagogique.financier', 'bilan_id', string='C - Bilan financier par origine du financement')
    vente_outil        = fields.Integer("C - Produits résultant de la vente d'outils pédagogique")
    sous_traitance     = fields.Integer("D - Honoraires de sous-traitance")
    heure_formation    = fields.Integer("E - Nombre d'heure de formation associés")
    heure_formation_st = fields.Integer("E - Nombre d'heures de formation des sous-traitant")
    typologie_ids      = fields.One2many('is.bilan.pedagogique.typologie', 'bilan_id', string="F - Nombre de stagiaires et d'heures par typologie")


    @api.multi
    def action_calculer(self):
        cr=self._cr
        for obj in self:

            # C - Bilan financier par origine du financement *******************
            obj.financier_ids.unlink()
            financements=self.env['is.origine.financement'].search([])
            for financement in financements:
                sql="""
                    select sum(iai.montant_facture)
                    from is_affaire_intervention iai inner join is_affaire ia on iai.affaire_id=ia.id
                    where iai.date>='"""+str(obj.name)+"""-01-01' and 
                          iai.date<='"""+str(obj.name)+"""-12-31' and
                          ia.origine_financement_id="""+str(financement.id)+"""
                """
                cr.execute(sql)
                bilan_financier=0
                for row in cr.fetchall():
                    if row[0]:
                        bilan_financier=row[0]
                vals={
                    'bilan_id'               : obj.id,
                    'origine_financement_id' : financement.id,
                    'bilan_financier'        : bilan_financier,
                }
                self.env['is.bilan.pedagogique.financier'].create(vals)

            # C - Produits résultant de la vente d'outils pédagogique **********
            sql="""
                select sum(iav.total_vente)
                from is_affaire_vente iav inner join is_affaire ia on iav.affaire_id=ia.id
                where iav.date>='"""+str(obj.name)+"""-01-01' and 
                      iav.date<='"""+str(obj.name)+"""-12-31' and
                      iav.product_id is not null 
            """
            cr.execute(sql)
            vente_outil=0
            for row in cr.fetchall():
                if row[0]:
                    vente_outil=row[0]
            obj.vente_outil=vente_outil

            # D - Honoraires de sous-traitance *********************************
            sql="""
                select sum(ail.quantity*price_unit)
                from account_invoice_line ail inner join account_invoice ai on ail.invoice_id=ai.id
                                              inner join product_product pp on ail.product_id=pp.id
                where ai.date_invoice>='"""+str(obj.name)+"""-01-01' and 
                      ai.date_invoice<='"""+str(obj.name)+"""-12-31' and
                      pp.name_template='HONORAIRES FORMATEURS' 
            """
            cr.execute(sql)
            sous_traitance=0
            for row in cr.fetchall():
                if row[0]:
                    sous_traitance=row[0]
            obj.sous_traitance=sous_traitance

            # E - Nombre d'heure de formation associés *************************
            sql="""
                select sum(iai.temps_formation)
                from is_affaire_intervention iai inner join is_affaire ia on iai.affaire_id=ia.id
                where iai.date>='"""+str(obj.name)+"""-01-01' and 
                      iai.date<='"""+str(obj.name)+"""-12-31' and
                      iai.associe_id is not null
            """
            cr.execute(sql)
            heure_formation=0
            for row in cr.fetchall():
                if row[0]:
                    heure_formation=row[0]
            obj.heure_formation=heure_formation


            # E - Nombre d'heures de formation des sous-traitant ***************
            sql="""
                select sum(iai.temps_formation)
                from is_affaire_intervention iai inner join is_affaire ia on iai.affaire_id=ia.id
                where iai.date>='"""+str(obj.name)+"""-01-01' and 
                      iai.date<='"""+str(obj.name)+"""-12-31' and
                      iai.associe_id is null and iai.sous_traitant_id is not null
            """
            cr.execute(sql)
            heure_formation_st=0
            for row in cr.fetchall():
                if row[0]:
                    heure_formation_st=row[0]
            obj.heure_formation_st=heure_formation_st


            # F - Nombre de stagiaires et d'heures par typologie ***************
            obj.typologie_ids.unlink()
            typologies=self.env['is.typologie.stagiaire'].search([])
            for typologie in typologies:
                # nb_stagiaire
                sql="""
                    select ia.id, max(ia.nb_stagiaire)
                    from is_affaire_intervention iai inner join is_affaire ia on iai.affaire_id=ia.id
                    where iai.date>='"""+str(obj.name)+"""-01-01' and 
                          iai.date<='"""+str(obj.name)+"""-12-31' and
                          ia.typologie_stagiaire_id="""+str(typologie.id)+"""
                    group by ia.id
                """
                cr.execute(sql)
                nb_stagiaire=0
                for row in cr.fetchall():
                    if row[1]:
                        nb_stagiaire=nb_stagiaire+row[1]

                # nb_heure
                sql="""
                    select sum(iai.temps_formation)
                    from is_affaire_intervention iai inner join is_affaire ia on iai.affaire_id=ia.id
                    where iai.date>='"""+str(obj.name)+"""-01-01' and 
                          iai.date<='"""+str(obj.name)+"""-12-31' and
                          ia.typologie_stagiaire_id="""+str(typologie.id)+"""
                """
                cr.execute(sql)
                nb_heure=0
                for row in cr.fetchall():
                    if row[0]:
                        nb_heure     = row[0]
                vals={
                    'bilan_id'     : obj.id,
                    'typologie_id' : typologie.id,
                    'nb_stagiaire' : nb_stagiaire ,
                    'nb_heure'     : nb_heure,
                }
                self.env['is.bilan.pedagogique.typologie'].create(vals)




class is_bilan_pedagogique_financier(models.Model):
    _name='is.bilan.pedagogique.financier'
    _order='origine_financement_id'

    bilan_id               = fields.Many2one('is.bilan.pedagogique', string='Bilan Pédagogique')
    origine_financement_id = fields.Many2one('is.origine.financement', string='Origine du financement')
    bilan_financier        = fields.Float("Bilan Financier")


class is_bilan_pedagogique_typologie(models.Model):
    _name='is.bilan.pedagogique.typologie'
    _order='typologie_id'

    bilan_id     = fields.Many2one('is.bilan.pedagogique', string='Bilan Pédagogique')
    typologie_id = fields.Many2one('is.typologie.stagiaire', string='Typologie Stagiaire')
    nb_stagiaire = fields.Float("Nombre de stagiaires")
    nb_heure     = fields.Float("Nombre d'heures")


class is_origine_financement(models.Model):
    _name = 'is.origine.financement'
    _order='name'

    name         = fields.Char('Origine financement', required=True)


class is_typologie_stagiaire(models.Model):
    _name = 'is.typologie.stagiaire'
    _order='name'

    name         = fields.Char('Typologie du stagiaire', required=True)






