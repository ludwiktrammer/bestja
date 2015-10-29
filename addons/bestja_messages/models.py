# -*- coding: utf-8 -*-
from urlparse import urljoin

from openerp import models, api


class Mail(models.Model):
    _inherit = 'mail.mail'

    @api.model
    def _get_partner_access_link(self, mail, partner=None):
        if partner and partner.user_ids and mail.model and mail.record_name:
            base_url = self.env['ir.config_parameter'].get_param('web.base.url')

            url = urljoin(base_url, self.env[mail.model]._get_access_link(mail, partner))
            return u"<br/>Zobacz szczegóły na temat: <a href='{url}'>{name}</a>".format(
                url=url,
                name=mail.record_name,
            )
        else:
            return None
