# -*- coding: utf-8 -*-

from openerp import models, api, _
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import SUPERUSER_ID

class res_partner(osv.osv):
    _name = "res.partner"
    _inherit = 'res.partner'

    @api.multi
    def open_partner_form_view(self):
        dummy, view_id = self.env['ir.model.data'].get_object_reference('base', 'view_partner_form')
        for partner in self:
            return {
            'name':_("Contacts"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'res.partner',
            'type': 'ir.actions.act_window',
            'res_id': partner.id,
            'domain': '[]',
        }


    def _affaire_count(self, cr, uid, ids, field_name, arg, context=None):
        Affaire = self.pool['is.affaire']
        return {
            client_id: Affaire.search_count(cr,uid, [('client_id', '=', client_id)], context=context)
            for client_id in ids
        }


    _columns = {  
        'is_prenom'              : fields.char("Prénom"),
        'is_code_fournisseur'    : fields.char("Code comptable fournisseur"),
        'is_siret'               : fields.char("SIRET"),
        'is_num_declaration_activite' : fields.char("N° déclaration activité", help=u"N° de déclaration d'activité obligatoire pour les sous-traitants"),
        'is_ape'                 : fields.char("APE"),
        'is_secteur_activite_id' : fields.many2one('is.secteur.activite', "Secteur d'activité", required=False),
        'is_typologie_id'        : fields.many2one('is.typologie', "Typologie"),
        'is_region_id'           : fields.many2one('is.region', 'Région', required=False),
        'is_classification_id'   : fields.many2one('is.classification', 'Classification', required=False),
        'is_bp'                  : fields.char("Boite postale"),
        'is_liste_diffusion'     : fields.char("Liste de diffusion"),
        'is_email_perso'         : fields.char("Courriel personnel"),
        'is_responsable'         : fields.boolean("Responsable structure", help="Est le responsable légal de la structure"),
        'affaire_count'          : fields.function(_affaire_count, string='# Affaires', type='integer'),
    }


    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name=record.name
            if record.is_prenom:
                name = record.is_prenom  + ' ' +record.name
            if record.parent_id and not record.is_company:
                name = "%s, %s" % (record.parent_name, name)
            if context.get('show_address_only'):
                name = self._display_address(cr, uid, record, without_company=True, context=context)
            if context.get('show_address'):
                name = name + "\n" + self._display_address(cr, uid, record, without_company=True, context=context)
            name = name.replace('\n\n','\n')
            name = name.replace('\n\n','\n')
            if context.get('show_email') and record.email:
                name = "%s <%s>" % (name, record.email)
            res.append((record.id, name))
        return res




class res_company(osv.osv):
    _name = "res.company"
    _inherit = 'res.company'

    _columns = {  
        'taux_km': fields.float(u"Taux indemnité kilométrique ", required=False),
    }


class is_region(osv.osv):
    _name = 'is.region'
    _description = u"Région"
    _columns = {
        'name': fields.char("Région", required=True),
    }

class is_secteur_activite(osv.osv):
    _name = 'is.secteur.activite'
    _description = u"Secteur d'activité"
    _columns = {
        'name': fields.char("Secteur d'activité", required=True),
    }

class is_typologie(osv.osv):
    _name = 'is.typologie'
    _description = u"Typologie"
    _columns = {
        'name': fields.char("Typologie", required=True),
    }

class is_classification(osv.osv):
    _name = 'is.classification'
    _description = u"Classification"
    _columns = {
        'name': fields.char("Classification", required=True),
    }

class is_base_documentaire(osv.osv):
    _name = 'is.base.documentaire'
    _description = "Base documentaire"
    _columns = {
        'name': fields.char("Nom du document", required=True),
    }






