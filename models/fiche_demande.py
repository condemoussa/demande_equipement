# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class FicheDemande(models.Model):
    _name = "fiche.demande"
    _description = "Fiche de Demande cogitech"
    _rec_name = "name"
    _description="Demande de materiel"

    @api.model
    def create(self, vals):
        record = super(FicheDemande, self).create(vals)
        if record:
            record['name'] = "DMD-N°" + "00" + str(record.id)
        return record

    def action_soumis(self):
        self.update({"state": "submitted"})
        users = self.env["res.users"].search([('type_groups', '=','type4')])
        # Création de l'e-mail pour chaque utilisateur
        for user in users:
            mail_values = {
                "subject": "Nouvelle demande de sortie",
                "body_html": f"""
                            <p>Bonjour M. {user.name},</p>
                            <p>Une nouvelle demande à été crée :</p>
                            <p><strong>{self.name}</strong> par <strong>{self.create_uid.name}</strong>.</p>
                            <p>Veuillez la transférer au gestionnaire SVP.</p>
                        """,
                "email_to": user.user_mail,
                "email_from": self.env.user.email,  # L'expéditeur est l'utilisateur actuel
                "author_id": self.env.user.partner_id.id,
            }
            self.env['mail.mail'].create(mail_values).send()  # Création et envoi de l'email

    def action_transfere(self):
        self.update({"state": "approved"})
        users = self.env["res.users"].search([('type_groups', '=', 'type9')])
        # Création de l'e-mail pour chaque utilisateur
        for user in users:
            mail_values = {
                "subject": "Transmission au Gestionnaire de Stock",
                "body_html": f"""
                       <p>Bonjour M. {user.name},</p>
                       <p>Une nouvelle demande vous a été transférée :</p>
                       <p><strong>{self.name}</strong></p>
                   """,
                "email_to": user.user_mail,
                "email_from": self.env.user.email,  # L'expéditeur est l'utilisateur actuel
                "author_id": self.env.user.partner_id.id,
            }
            self.env['mail.mail'].create(mail_values).send()  # Création et envoi de l'email

    def sortir_physique(self):
        self.update({"state": "sortir_physique"})

        users = self.env["res.users"].search([('type_groups', '=', 'type9')])
        # Création de l'e-mail pour chaque utilisateur
        for user in users:
            mail_values = {
                "subject": "Transmission au Gestionnaire de Stock",
                "body_html": f"""
                             <p>Bonjour M. {user.name},</p>
                             <p>Une nouvelle demande vous a été transférée :</p>
                             <p><strong>{self.name}</strong></p>
                         """,
                "email_to": user.user_mail,
                "email_from": self.env.user.email,  # L'expéditeur est l'utilisateur actuel
                "author_id": self.env.user.partner_id.id,
            }
            self.env['mail.mail'].create(mail_values).send()  # Création et envoi de l'email

        """Crée un Bon de Livraison (BL) lorsqu'une sortie physique est demandée."""
        self.ensure_one()  # S'assurer qu'on traite une seule fiche à la fois

        picking_type = self.env['stock.picking.type'].search([('code', '=', 'outgoing')], limit=1)

        if not picking_type:
            raise ValueError("Aucun type d'opération de sortie trouvé !")

        if not self.client_id:
            raise ValueError("Aucun client associé à cette demande !")

        if not self.prod_id:
            raise ValueError("Aucun produit spécifié pour cette demande !")

        # Création du BL (stock.picking)
        picking = self.env['stock.picking'].create({
            'origin': self.name,
            'partner_id': self.client_id.id,  # Client lié à la sortie
            'location_id': 1,  # Emplacement source
           # 'location_dest_id': self.client_id.property_stock_customer.id,  # Emplacement client
            'picking_type_id': picking_type.id,  # Type d'opération
        })

        print( self.prod_id.name)
        # Création des lignes du BL (stock.move)
        self.env['stock.move'].create({
            'name': self.prod_id.name,
            'product_id': self.prod_id.id,
            'picking_id': picking.id,
            'location_id': 1,
            'location_dest_id': 1
        })


        return picking

    def livraison_client(self):
        self.update({"state": "livraison_client"})

        users = self.env["res.users"].search([('type_groups', '=', 'type4')])
        # Création de l'e-mail pour chaque utilisateur
        for user in users:
            mail_values = {
                "subject": "Livraison au client",
                "body_html": f"""
                                  <p>Bonjour M. {user.name},</p>
                                  <p>La livraison été effectué au client :</p>
                              """,
                "email_to": user.user_mail,
                "email_from": self.env.user.email,  # L'expéditeur est l'utilisateur actuel
                "author_id": self.env.user.partner_id.id,
            }
            self.env['mail.mail'].create(mail_values).send()  # Création et envoi de l'email

    def action_rejeter(self):
        self.update({"state": "rejected"})
        users = self.env["res.users"].search([('type_groups', '=', 'type4')])

        # Création de l'e-mail pour chaque utilisateur
        for user in users:
            mail_values = {
                "subject": "Rejet de la sortie du matériel",
                "body_html": f"""
                               <p>Bonjour M. {user.name},</p>
                               <p>La demande <strong>{self.name}</strong> a été rejetée.</p>
                               <p>Veuillez consulter la plateforme pour plus de détails.</p>
                           """,
                "email_to": user.email,
                "email_from": self.env.user.email,
                "author_id": self.env.user.partner_id.id,
            }
            self.env['mail.mail'].create(mail_values).send()  # Création et envoi de l'email


    name = fields.Char("N°" , readonly=True)
    prod_id = fields.Many2one("product.template", string="Produit", required=True)
    client_id = fields.Many2one("res.partner", string="Client", required=True)
    demandeur = fields.Many2one("res.users", string="Demandeur",  default=lambda self: self.env.user.id , readonly=True)
    state = fields.Selection(
        [
            ("draft", "Brouillon"),
            ("submitted", "Directeur technique"),
            ("approved", "Gestionnaire de Stock"),
            ("sortir_physique", "Sortie physique"),
            ("livraison_client", "Livraison client"),
            ("rejected", "Rejetée"),
        ],
        string="État",
        default="draft",
    )
    destination = fields.Char("Destination")
    demande_jointe = fields.Binary("Demande jointe")

    _sql_constraints = [
        ("unique_name", "unique(name)", "Le libellé doit être unique !"),
    ]
