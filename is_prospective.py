# -*- coding: utf-8 -*-
from openerp import models,fields,api
from openerp.tools.translate import _
import datetime


def _annee_creation():
    now=datetime.date.today()
    return now.strftime('%Y')


class is_prospective(models.Model):
    _name='is.prospective'
    _order='name desc'
    _sql_constraints = [('name_uniq','UNIQUE(name)', u'Cette année existe deja')]

    name     = fields.Integer("Année", required=True)
    state    = fields.Selection([('en_cours', u'En cours'),('termine', u'Terminé')], u"État", readonly=True, select=True)
    line_ids = fields.One2many('is.prospective.line', 'prospective_id', u'Lignes')


    _defaults = {
        'name' : lambda *a: _annee_creation(),
        'state': 'en_cours',
    }


    @api.multi
    def action_recalculer(self):
        cr      = self._cr
        for obj in self:
            sql="""
                select 
                    ia.id,
                    ia.date_creation,
                    ia.pilote_id,
                    ia.client_id,
                    ia.article_id,
                    ia.intitule,
                    ia.duree_prestation,
                    ia.budget_bas,
                    ia.budget_haut,
                    ia.budget_propose,
                    ia.budget_propose_annee,
                    ia.date_validation,
                    ia.date_solde,
                    ia.state
                from is_affaire ia
                where state<>'annule' 
            """
            line_obj = self.env['is.prospective.line']
            obj.line_ids.unlink()
            cr.execute(sql)
            for row in cr.fetchall():
                affaire_id      = str(row[0])
                date_creation   = str(row[1])
                date_solde      = str(row[12])
                if (date_solde=='None' or date_solde[:4]==str(obj.name)) and date_creation[:4]<=str(obj.name):
                    associe01     = self.get_montant_intervenant(str(obj.name), affaire_id, 8)      # Olivier
                    associe02     = self.get_montant_intervenant(str(obj.name), affaire_id, 6)      # JP
                    associe03     = self.get_montant_intervenant(str(obj.name), affaire_id, 7)      # Patrice
                    associe04     = self.get_montant_intervenant(str(obj.name), affaire_id, 10)     # Frédérique
                    associe05     = self.get_montant_intervenant(str(obj.name), affaire_id, 9)      # Isabelle
                    sous_traitant = self.get_montant_intervenant(str(obj.name), affaire_id, 0)      # Sous-traitance
                    total=associe01+associe02+associe03+associe04+associe05+sous_traitant
                    vals={
                        'prospective_id'      : obj.id,
                        'name'                : row[0],
                        'date_creation'       : row[1],
                        'pilote_id'           : row[2],
                        'client_id'           : row[3],
                        'article_id'          : row[4],
                        'intitule'            : row[5],
                        'duree_prestation'    : row[6],
                        'budget_bas'          : row[7],
                        'budget_haut'         : row[8],
                        'budget_propose'      : row[9],
                        'budget_propose_annee': row[10],
                        'date_validation'     : row[11],
                        'date_solde'          : row[12],
                        'state'               : row[13],
                        'associe01'           : associe01,
                        'associe02'           : associe02,
                        'associe03'           : associe03,
                        'associe04'           : associe04,
                        'associe05'           : associe05,
                        'sous_traitant'       : sous_traitant,
                        'total'               : total,
                    }
                    line_obj.create(vals)
            return self.action_detail_lignes()


    @api.multi
    def action_detail_lignes(self):
        for obj in self:
            return {
                'name': "Lignes de prospective",
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'is.prospective.line',
                'type': 'ir.actions.act_window',
                'limit': 200,
                'domain': [('prospective_id','=',obj.id)],
            }


    @api.multi
    def get_montant_intervenant(self,annee, affaire_id, associe_id):
        cr      = self._cr
        sql="""
            SELECT sum(budget_prevu)
            FROM is_affaire_intervenant
            WHERE 
                annee="""+annee+""" and
                affaire_id="""+str(affaire_id)+""" 
        """
        if associe_id>0:
            sql=sql+" and associe_id="+str(associe_id)
        else:
            sql=sql+" and sous_traitant_id is not null"
        cr.execute(sql)
        montant=0
        for row in cr.fetchall():
            montant=row[0]
        if str(montant)=='None':
            montant=0
        return montant


class is_prospective_line(models.Model):
    _name='is.prospective.line'
    _order='name desc'

    prospective_id       = fields.Many2one('is.prospective', 'Année', required=True, ondelete='cascade')
    name                 = fields.Many2one('is.affaire', u'Affaire')
    date_creation        = fields.Date(u"Date de création")
    pilote_id            = fields.Many2one('res.users', u'Pilote')
    client_id            = fields.Many2one('res.partner', u'Client')
    article_id           = fields.Many2one('product.template', u'Article')
    intitule             = fields.Text(u"Intitulé")
    duree_prestation     = fields.Text(u"Durée de la prestation")
    budget_bas           = fields.Float(u"Budget bas")
    budget_haut          = fields.Float(u"Budget haut")
    budget_propose       = fields.Float(u"Budget proposé ")
    budget_propose_annee = fields.Float(u"Budget année en cours")
    date_validation      = fields.Date(u"Date de validation")
    date_solde           = fields.Date(u"Date annulé ou soldé")
    state                = fields.Selection([
                                ('en_attente', u'En attente'),
                                ('valide', u'Validé'),
                                ('annule', u'Annulé'),
                                ('solde', u'Soldé')], u"État", readonly=True, select=True)
    associe01            = fields.Integer(u"Olivier")
    associe02            = fields.Integer(u"JP")
    associe03            = fields.Integer(u"Patrice")
    associe04            = fields.Integer(u"Frédérique")
    associe05            = fields.Integer(u"Isabelle")
    sous_traitant        = fields.Integer(u"Sous traitance")
    total                = fields.Integer(u"Total")


