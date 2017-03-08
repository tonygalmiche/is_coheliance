# -*- coding: utf-8 -*-

from openerp import tools
from openerp import models,fields,api
from openerp.tools.translate import _


class is_suivi_facture(models.Model):
    _name='is.suivi.facture'
    _order='num_facture desc'
    _auto = False

    num_facture   = fields.Char('N°facture')
    date_facture  = fields.Date('Date facture')
    partner_id    = fields.Many2one('res.partner', u'Client')
    total_ht      = fields.Float('Total HT')
    total_ttc     = fields.Float('Total TTC')
    reste_a_payer = fields.Float('Reste à payer')

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'is_suivi_facture')
        cr.execute("""

            CREATE OR REPLACE FUNCTION fsens(t text) RETURNS integer AS $$
                    BEGIN

                        IF t = ANY (ARRAY['out_refund'::character varying::text, 'in_invoice'::character varying::text]) THEN
                            RETURN -1;
                        ELSE
                            RETURN 1;
                        END IF;

                    END;
            $$ LANGUAGE plpgsql;


            CREATE OR REPLACE view is_suivi_facture AS (
                SELECT 
                    ai.id             as id,
                    ai.date_invoice   as date_facture,
                    ai.number         as num_facture,
                    ai.partner_id     as partner_id,
                    fsens(ai.type)*ai.amount_untaxed as total_ht,
                    fsens(ai.type)*ai.amount_total   as total_ttc,
                    fsens(ai.type)*ai.residual       as reste_a_payer
                FROM account_invoice ai
                WHERE ai.state in ('open', 'paid') and ai.type in ('out_invoice', 'out_refund')
                      and ai.date_invoice>='2016-06-01' 
            )
        """)




# id  | create_uid | product_code |        create_date         | name | sequence | product_name | company_id | write_uid | delay |         
#write_date         | min_qty |  qty   | product_tmpl_id 
#plastigray=# select * from product_supplierinfo;

#Ajouter dans le menu « Comptabilité » un sous-menu « Suivi » avec ces rapports : 
#Suivi des factures
#1 ligne par client
#1 colonne par mois
#Total TTC et Total HT
