# -*- coding: utf-8 -*-

{
  "name" : "InfoSaône - Module Odoo pour Coheliance",
  "version" : "0.1",
  "author" : "InfoSaône / Tony Galmiche",
  "category" : "InfoSaône",
  'description': """
InfoSaône - Module Odoo pour Coheliance
===================================================

InfoSaône - Module Odoo pour Coheliance
""",
  'maintainer': 'InfoSaône',
  'website': 'http://www.infosaone.com',

  "depends" : [
    "base",
    "mail",
    "calendar",               # Agenda
    "crm",                    # CRM
    "account_voucher",        # eFacturation & Règlements
    "account_accountant",     # Comptabilité et finance
    "sale",                   # Gestion des ventes
    "purchase",               # Gestion des achats
    "sale_order_dates",       # Ajout de champs dates dans les commandes clients (date demandée)
    "project",                # Gestin de projets
    "hr",                     # Répertoire des employés
    "hr_timesheet_sheet",     # Feuilles de temps
    "report",
  ], # Liste des dépendances (autres modules nececessaire au fonctionnement de celui-ci)
     # -> Il peut être interessant de créer un module dont la seule fonction est d'installer une liste d'autres modules
     # Remarque : La desinstallation du module n'entrainera pas la desinstallation de ses dépendances (ex : mail)

  "init_xml" : [],             # Liste des fichiers XML à installer uniquement lors de l'installation du module
  "demo_xml" : [],             # Liste des fichiers XML à installer pour charger les données de démonstration
  "data" : [
    "assets.xml",              # Permet d'ajouter des css et des js
    "product_view.xml", 
    "res_partner_view.xml", 
    "sale_view.xml",
    "account_invoice_view.xml",    
    "is_coheliance_view.xml",
    "is_coheliance_sequence.xml",
    "is_suivi_tresorerie_view.xml",
    "is_export_compta.xml",
    "is_coheliance_report.xml",
    "is_prospective_view.xml",
    "views/layouts.xml",
    "views/layouts-convention.xml",
    "views/report_affaire.xml",
    "views/report_convention.xml",
    "views/report_convention_st.xml",
    "views/report_contrat_formation.xml",
    "views/report_invoice.xml",
    "views/report_frais.xml",
    "report/is_suivi_facture.xml",
    "report/is_suivi_refacturation_associe.xml",
    "report/is_suivi_intervention.xml",
    "menu.xml",
    "security/ir.model.access.csv",
  ],                           # Liste des fichiers XML à installer lors d'une mise à jour du module (ou lord de l'installation)
  "installable": True,         # Si False, ce module sera visible mais non installable (intéret ?)
  "active": False,             # Si True, ce module sera installé automatiquement dés la création de la base de données d'OpenERP
  "application": True,
}

