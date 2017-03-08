# -*- coding: utf-8 -*-

from openerp import tools
from openerp import models,fields,api
from openerp.tools.translate import _


class is_suivi_refacturation_associe(models.Model):
    _name='is.suivi.refacturation.associe'
    _order='date desc'
    _auto = False

    type_donnee   = fields.Char('Type de donnée')
    affaire_id    = fields.Many2one('is.affaire', u'Affaire')
    associe_id    = fields.Many2one('res.users', u'Associé')
    type_frais    = fields.Char(u'Type de frais')
    type_frais_km = fields.Char(u'Frais Km ou autres frais')
    montant       = fields.Float('Montant')
    date          = fields.Date('Date')
    commentaire   = fields.Char('Commentaire')


    def init(self, cr):
        tools.drop_view_if_exists(cr, 'is_suivi_refacturation_associe')
        cr.execute("""

            CREATE OR REPLACE FUNCTION is_frais_km(frais text) RETURNS text AS $$
                    BEGIN
                        IF frais ='' THEN
                            RETURN '';
                        END IF;
                        IF frais ='FRAIS DEPLACEMENT KM' THEN
                            RETURN 'FRAIS DEPLACEMENT KM';
                        ELSE
                            IF frais ='FRAIS DEPLACEMENT KM SANS TVA' THEN
                                RETURN 'FRAIS DEPLACEMENT KM';
                            ELSE
                                RETURN 'AUTRES FRAIS';
                            END IF;
                        END IF;
                    END;
            $$ LANGUAGE plpgsql;

            CREATE OR REPLACE view is_suivi_refacturation_associe AS (
                select 
                    id+1000000 as id, 
                    'intervention' as type_donnee, 
                    affaire_id, 
                    associe_id, 
                    '' as type_frais, 
                    '' as type_frais_km, 
                    date, 
                    montant_facture as montant, 
                    commentaire as commentaire
                from is_affaire_intervention 
                where associe_id is not null and montant_facture!=0 

                Union

                select 
                    ifl.id+2000000 as id, 
                    'frais' as type_donnee, 
                    if.affaire_id, 
                    if.intervenant_id as associe_id, 
                    pt.name as type_frais, 
                    is_frais_km(pt.name) as type_frais_km, 
                    ifl.date, 
                    ifl.montant_ht  as montant, 
                    '' as commentaire
                from is_frais if inner join is_frais_ligne ifl on if.id=ifl.frais_id 
                                 left outer join product_template pt on ifl.type_frais_id=pt.id
            )
        """)





