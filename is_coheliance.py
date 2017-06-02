# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import time
from openerp import pooler
from openerp.osv import fields, osv
from openerp.tools.translate import _

from datetime import datetime, timedelta

class is_affaire(osv.osv):
    _name = 'is.affaire'
    _description = u"Affaire"
    _order='name desc'

    def _ecart_budget(self, cr, uid, ids, field_name, arg, context=None):
        res={}
        for obj in self.browse(cr, uid, ids, dict(context, active_test=False)):
            total=0
            for intervenant in obj.intervenant_ids:
                total=total+intervenant.budget_prevu
            res[obj.id] = obj.budget_propose-total
        return res

    _columns = {
        'name': fields.char(u"Code de l'affaire"),
        'version': fields.char(u"Version", required=True, size=4),
        'date_creation': fields.date(u"Date de création"),
        'date_signature': fields.date(u"Date de signature"),
        'date_relance': fields.date(u"Date de relance"),
        'createur_id': fields.many2one('res.users', u'Créateur'),
        'interlocutrice_id': fields.many2one('res.users', u'Interlocutrice administrative'),
        'pilote_id': fields.many2one('res.users', u'Pilote', required=True),
        'client_id': fields.many2one('res.partner', u'Client', required=True),
        'contact_client_id': fields.many2one('res.partner', u'Contact client', required=False),
        'article_id': fields.many2one('product.template', u'Article', required=True),


        'intitule': fields.text(u"Intitulé", required=True),
        'objectif': fields.text(u"Objectifs", required=False, help="Pour les conventions de formations"),
        'descriptif': fields.text(u"Descriptif / Programme", required=True),
        'methode_pedagogique': fields.text(u"Méthodes et supports pédagogiques", required=False, help="Pour les conventions de formations"),
        'personnes_concernees': fields.text(u"Personnes concernées", required=False),
        'lieu_intervention': fields.char(u"Lieu d'intervention"),
        'date_debut': fields.char(u"Date de début"),
        'date_fin': fields.char(u"Date de fin"),
        'duree_prestation': fields.text(u"Durée de la prestation"),
        'budget_bas': fields.float(u"Budget bas"),
        'budget_haut': fields.float(u"Budget haut"),
        'budget_propose': fields.float(u"Budget proposé "),
        'budget_propose_annee': fields.float(u"Budget année en cours", help="Il faudra modifier cette valeur au début de l'année si l'affaire n'est pas clôturée pour le suivi des tableaux de bords"),
        'ecart_budget': fields.function(_ecart_budget, type='float', string="Ecart budget", help="Ecart entre le budget prévu par intervenant et le budget proposé", store=True, ),
        'modalite_paiement': fields.text(u"Modalités de paiement"),
        'frais_a_refacturer': fields.text(u"Frais à refacturer"),
        'intervenant_ids': fields.one2many('is.affaire.intervenant', 'affaire_id', u'Intervenants'),
        'date_validation': fields.date(u"Date de validation"),
        'date_solde': fields.date(u"Date annulé ou soldé"),
        'order_id': fields.many2one('sale.order', 'Commande', readonly=False),
        'intervention_ids': fields.one2many('is.affaire.intervention', 'affaire_id', u'Interventions'),
        'frais_ids': fields.one2many('is.frais', 'affaire_id', u'Frais'),
        'vente_ids': fields.one2many('is.affaire.vente', 'affaire_id', u'Ventes'),
        'acompte_ids': fields.one2many('is.acompte', 'affaire_id', u'Acomptes'),
        'state': fields.selection([('en_attente', u'En attente'),
                                  ('valide', u'Validé'),
                                  ('annule', u'Annulé'),
                                  ('solde', u'Soldé')], u"État", readonly=True, select=True),
    }
    
    _defaults = {
        'name': '',
        'intitule': '',
        'descriptif': 'Descriptif précis de la mission, des compétences et moyens mis en œuvre ainsi que des résultats attendus ou modalités de réalisation : voir document annexe.',
        'version': '1',
        'createur_id': lambda obj, cr, uid, context: uid,
        'interlocutrice_id': lambda obj, cr, uid, context: uid,
        'pilote_id': lambda obj, cr, uid, context: uid,
        'date_creation': fields.datetime.now,
        'date_relance':   (datetime.now() + timedelta(30)).strftime('%Y-%m-%d'),
        'unite_temps': 'jour',
        'state': 'en_attente',
    }


    def prepare_commande(self, cr, uid, ids, obj, context=None):
        order_line_obj = self.pool.get('sale.order.line')
        sale_obj = self.pool.get('sale.order')
        
        quotation={}
        lines = []
        order_line_obj= self.pool.get('sale.order.line')
        quotation_line = order_line_obj.product_id_change(cr, uid, ids, obj.client_id.property_product_pricelist.id, 
                                                          obj.article_id.id, 0, False, 0, False, '', obj.client_id.id, 
                                                         False, True, False, False, False, False, context=context)['value']
        quotation_line.update({'product_id':obj.article_id.id, 'product_uom_qty': 1})
        if 'tax_id' in quotation_line:
            quotation_line.update({'tax_id': [[6, False, quotation_line['tax_id']]]})

        #Descriptif de la commande
        intitule=u"Intitulé :\n"+obj.intitule+"\n\n"
        intitule=intitule+u"Descriptif :\n"+obj.descriptif+"\n\n"
        if obj.personnes_concernees:
            intitule=intitule+u"Personnes Concernées :\n"+obj.personnes_concernees+"\n\n"
        if obj.lieu_intervention:
            intitule=intitule+u"Lieu d'intervention :\n"+obj.lieu_intervention+"\n\n"
        if obj.date_debut:
            intitule=intitule+u"Date de début :\n"+obj.date_debut+"\n\n"
        if obj.date_fin:
            intitule=intitule+u"Date de fin :\n"+obj.date_fin+"\n\n"
        if obj.duree_prestation:
            intitule=intitule+u"Durée de la prestation :\n"+obj.duree_prestation+"\n\n"

        intitule=intitule+"Intervenants :"
        for intervenant in obj.intervenant_ids:
            name=""
            if intervenant.associe_id:
                name=intervenant.associe_id.name
            if intervenant.sous_traitant_id:
                name=intervenant.sous_traitant_id.name
                if intervenant.sous_traitant_id.is_prenom:
                    name=intervenant.sous_traitant_id.is_prenom+' '+intervenant.sous_traitant_id.name
            intitule=intitule+"\n- "+name

        quotation_line.update({'name': intitule})
        quotation_line.update({'price_unit': obj.budget_propose})
        lines.append([0,False,quotation_line]) 
        quotation_values = {
            'name': '/',
            'partner_id': obj.client_id.id,
            'origin': obj.name,
            'order_line': lines,
            'picking_policy': 'direct',
            'order_policy': 'manual',
            'invoice_quantity': 'order',
            'affaire_id': obj.id,
        }
        quotation.update(quotation_values)
        return quotation


    def action_generer_commande(self, cr, uid, ids, context=None):
        order_obj = self.pool.get('sale.order')
        res={}
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.order_id :
                if obj.order_id.state in ('draft', 'sent', 'cancel'):
                    order_obj.unlink(cr, uid, [obj.order_id.id], context=context)
                else:
                    raise osv.except_osv(_('Avertissement'), _(u"Vous ne pouvez pas créer une autre commande, car celle-ci est déjà confirmée"))
            vals = self.prepare_commande(cr, uid, ids, obj, context=context)
            new_id = order_obj.create(cr, uid, vals, context=context)
            res = self.write(cr, uid, obj.id, {'order_id': new_id}, context=context)
        return res  


    def action_detail_frais(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context=context):
            return {
                'name': "Détail des frais",
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'is.frais.ligne',
                'type': 'ir.actions.act_window',
                'domain': [('affaire_id','=',obj.id)],
            }


    def create(self, cr, uid, vals, context=None):
        data_obj = self.pool.get('ir.model.data')
        sequence_ids = data_obj.search(cr, uid, [('name','=','is_affaire_seq')], context=context)
        if sequence_ids:
            sequence_id = data_obj.browse(cr, uid, sequence_ids[0], context).res_id
            vals['name'] = self.pool.get('ir.sequence').get_id(cr, uid, sequence_id, 'id', context=context)
        new_id = super(is_affaire, self).create(cr, uid, vals, context=context)
        return new_id


    def write(self, cr, uid, ids, vals, context=None):
        if 'state' in vals:
            vals["date_validation"]=False
            vals["date_solde"]=False
            if vals["state"]=='valide':
                vals["date_validation"]=datetime.now().strftime('%Y-%m-%d')
            if vals["state"]=='solde' or vals["state"]=='annule':
                vals["date_solde"]=datetime.now().strftime('%Y-%m-%d')


        res = super(is_affaire, self).write(cr, uid, ids, vals, context=context)
        return res


    def copy(self, cr, uid, id, default=None, context=None):
        if not context:
            context = {}
        default.update({
            'order_id'     : False,
        })
        return super(is_affaire, self).copy(cr, uid, id, default=default, context=context)


class is_affaire_intervenant(osv.osv):
    _name = 'is.affaire.intervenant'
    _description = u"Intervenants"
    
    _columns = {
        'affaire_id': fields.many2one('is.affaire', 'Affaire', required=True),
        'associe_id': fields.many2one('res.users', u'Associé'),
        'sous_traitant_id': fields.many2one('res.partner', u'Sous-Traitant'),

        'duree_mission': fields.char(u"Durée mission Sous-Traitant"),
        'condition_financiere': fields.char(u"Conditions financières Sous-Traitant"),

        'budget_prevu': fields.float(u"Budget prévu", help="Budget prévu pour cette personne", required=True),

        'taux1': fields.float(u"Taux horaire"),
        'taux2': fields.float(u"Taux demi-journée"),
        'taux3': fields.float(u"Taux journée"),

    }

    def print_convention_st(self, cr, uid, ids, context=None):
        return self.pool['report'].get_action(cr, uid, ids, 'is_coheliance.report_convention_st', context=context)


class is_affaire_intervention(osv.osv):
    _name = 'is.affaire.intervention'
    _description = u"Interventions"

    def _montant_facture(self, cr, uid, ids, field_name, arg, context=None):
        res={}



        for obj in self.browse(cr, uid, ids, dict(context, active_test=False)):
            print obj


            intervenant_ids = obj.affaire_id.intervenant_ids

            trouve=False
            for intervenant in intervenant_ids:
                if(obj.associe_id and intervenant.associe_id.id==obj.associe_id.id):
                    trouve=intervenant
                if(obj.sous_traitant_id and intervenant.sous_traitant_id.id==obj.sous_traitant_id.id):
                    trouve=intervenant

            taux=0
            if trouve:
                if obj.unite_temps=="heure":
                    taux=trouve.taux1
                if obj.unite_temps=="demi-jour":
                    taux=trouve.taux2
                if obj.unite_temps=="jour":
                    taux=trouve.taux3

            res[obj.id] = taux*obj.temps_passe
        return res

    _columns = {
        'affaire_id': fields.many2one('is.affaire', 'Affaire', required=True),
        'date': fields.date(u"Date", required=True),
        'associe_id': fields.many2one('res.users', u'Associé'),
        'sous_traitant_id': fields.many2one('res.partner', u'Sous-Traitant'),
        'temps_passe': fields.float(u"Temps passé", required=True),
        'unite_temps': fields.selection([('heure','Heure'),('demi-jour','Demi-journée'),('jour','Jour')], u"Unité de temps", required=True),
        'montant_facture': fields.function(_montant_facture, type='float', string="Montant à facturer", store=True, ),
        'commentaire': fields.text(u"Commentaire"),
    }

    _defaults = {
        'associe_id': lambda obj, cr, uid, context: uid,
        'date': fields.datetime.now,
        'unite_temps': 'heure',
    }


    def write(self, cr, uid, ids, vals, context=None):
        intervention = self.browse(cr, uid, ids[0], context=context)
        new_vals={}
        new_vals["associe_id"]       = intervention.associe_id.id or 0
        new_vals["sous_traitant_id"] = intervention.sous_traitant_id.id or 0
        if "associe_id" in vals:
            new_vals["associe_id"]       = vals["associe_id"] or 0
        if "sous_traitant_id" in vals:
            new_vals["sous_traitant_id"] = vals["sous_traitant_id"] or 0
        err=False
        print "new_vals=",new_vals
        if new_vals["associe_id"]>0  and new_vals["sous_traitant_id"]>0:
            err=True
        if err:
            raise osv.except_osv(_('Avertissement'), _(u"Dans les interventions, il faut choisir entre l'associé et le sous-traitant "))
        res = super(is_affaire_intervention, self).write(cr, uid, ids, vals, context=context)
        return res



#class is_frais(osv.osv):
#    _name = 'is.frais'
#    _description = u"Fiche de frais"

#    _columns = {
#        'name': fields.char(u"Numéro"),
#        'date_creation': fields.date(u"Date de création"),
#        'affaire_id': fields.many2one('is.affaire', 'Affaire', required=True),
#        'intervenant_id': fields.many2one('res.users', u'Intervenant', required=True),
#        'taux_km': fields.float(u"Taux indemnité kilométrique"),
#        'ligne_ids': fields.one2many('is.frais.ligne', 'frais_id', u'Lignes'),
#    }

#    _defaults = {
#        'name': '',
#        'intervenant_id': lambda obj, cr, uid, context: uid,
#        'date_creation': fields.datetime.now,
#    }

#    def create(self, cr, uid, vals, context=None):

#        company_obj = self.pool.get('res.company')
#        taux_km = company_obj.browse(cr, uid, 1, context).taux_km
#        vals["taux_km"]=taux_km

#        data_obj = self.pool.get('ir.model.data')
#        sequence_ids = data_obj.search(cr, uid, [('name','=','is_frais_seq')], context=context)
#        if sequence_ids:
#            sequence_id = data_obj.browse(cr, uid, sequence_ids[0], context).res_id
#            vals['name'] = self.pool.get('ir.sequence').get_id(cr, uid, sequence_id, 'id', context=context)
#        new_id = super(is_frais, self).create(cr, uid, vals, context=context)
#        return new_id



#class is_frais_ligne(osv.osv):
#    _name = 'is.frais.ligne'
#    _description = u"Lignes des fiches de frais"


#    def _montant_ttc(self, cr, uid, ids, field_name, arg, context=None):
#        res={}
#        for obj in self.browse(cr, uid, ids, dict(context, active_test=False)):
#            tva=0
#            if obj.type_frais_id:
#                if obj.type_frais_id.taxes_id:
#                    for taxe in obj.type_frais_id.taxes_id:
#                        tva=taxe.amount
#            res[obj.id] = obj.montant_ht*(1+tva)
#        return res



#    _columns = {
#        'frais_id': fields.many2one('is.frais', 'Frais', required=True),
#        'date': fields.date(u"Date"),
#        'type_frais_id': fields.many2one('product.template', u'Type de frais'),
#        'refacturable': fields.selection([('oui','Oui'),('non','Non')], u"Refacturable"),
#        'km': fields.integer(u"Km"),
#        'montant_ht': fields.float(u"Montant HT"),
#        'montant_ttc': fields.function(_montant_ttc, type='float', string="Montant TTC", store=True, ),
#        'refacture': fields.boolean(u"Frais refacturé au client"),
#    }

#    _defaults = {
#        'date': fields.datetime.now,
#        'refacturable': 'oui',
#        'refacture': False,
#    }


#    def create(self, cr, uid, vals, context=None):
#        if 'km' in vals:
#            company_obj = self.pool.get('res.company')
#            taux_km = company_obj.browse(cr, uid, 1, context).taux_km
#            vals['montant_ht']=vals['km']*taux_km
#        res = super(is_frais_ligne, self).create(cr, uid, vals, context=context)



#    def write(self, cr, uid, ids, vals, context=None):
#        if 'km' in vals:
#            company_obj = self.pool.get('res.company')
#            taux_km = company_obj.browse(cr, uid, 1, context).taux_km
#            vals['montant_ht']=vals['km']*taux_km
#        res = super(is_frais_ligne, self).write(cr, uid, ids, vals, context=context)




class is_acompte(osv.osv):
    _name = 'is.acompte'
    _description = u"Gestion acomptes"
    _order='date_acompte'
    _columns = {
        'affaire_id': fields.many2one('is.affaire', 'Affaire', required=True),
        'date_acompte': fields.date(u"Date acompte"),
        'montant_acompte': fields.float(u"Montant acompte"),
        'commentaire': fields.text(u"Commentaire"),
        'account_id': fields.many2one('account.invoice', u"Facture d'acompte"),
    }

    _defaults = {
    }




