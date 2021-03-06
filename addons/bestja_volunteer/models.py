# -*- coding: utf-8 -*-
import re
from itertools import izip

from lxml import etree

from openerp import models, fields, api, exceptions, SUPERUSER_ID
from openerp.addons.auth_signup.res_users import SignupError
from openerp.addons.base.res.res_users import res_users


class VolunteerWish(models.Model):
    _name = 'volunteer.wish'
    name = fields.Char(required=True, string=u"nazwa")


class VolunteerSkill(models.Model):
    _name = 'volunteer.skill'
    name = fields.Char(required=True, string=u"nazwa")


class VolunteerOccupation(models.Model):
    _name = 'volunteer.occupation'
    name = fields.Char(required=True, string=u"nazwa")


class VolunteerLanguage(models.Model):
    _name = 'volunteer.language'
    name = fields.Char(required=True, string=u"nazwa")


class Daypart(models.Model):
    _name = 'volunteer.daypart'
    name = fields.Char(required=True, string=u"nazwa")


class Voivodeship(models.Model):
    _name = 'volunteer.voivodeship'
    name = fields.Char(required=True, string=u"nazwa")


class Volunteer(models.Model):
    _name = 'res.users'
    _inherit = [
        'res.users',
        'message_template.mixin'
    ]

    wishes = fields.Many2many(
        'volunteer.wish',
        string=u"zainteresowania",
        ondelete='restrict',
    )
    skills = fields.Many2many(
        'volunteer.skill',
        string=u"umiejętności",
        ondelete='restrict',
    )
    languages = fields.Many2many(
        'volunteer.language',
        string=u"języki",
        ondelete='restrict'
    )
    occupation = fields.Many2one(
        'volunteer.occupation',
        string=u"status zawodowy",
        ondelete='restrict',
    )
    # 'email' field from partner is hidden by group permissions,
    # this field is a proxy, without the group restrictions.
    user_email = fields.Char(
        string=u"adres email",
        required=True,
        compute='_compute_user_email',
        inverse='_inverse_user_email',
    )
    phone = fields.Char(string=u"numer tel.")
    birthdate = fields.Date(string=u"data urodzenia")
    curriculum_vitae = fields.Binary(string=u"CV")
    cv_filename = fields.Char()
    daypart = fields.Many2many('volunteer.daypart', string=u"pora dnia")
    daypart_comments = fields.Text(string=u"uwagi")
    sex = fields.Selection([('f', 'kobieta'), ('m', 'mężczyzna')], string=u"płeć")
    place_of_birth = fields.Char(string=u"miejsce urodzenia")
    citizenship = fields.Many2one(
        'res.country',
        ondelete='restrict',
        string=u"obywatelstwo",
    )
    document_id_kind = fields.Selection(
        [('id', 'dowód osobisty'), ('passport', 'paszport')],
        string=u"rodzaj dokumentu",
    )
    document_id = fields.Char(string=u"numer dokumentu")

    # mailing address
    street_gov = fields.Char(string=u"ulica")
    street_number_gov = fields.Char(string=u"numer budynku")
    apt_number_gov = fields.Char(string=u"mieszk.")
    zip_code_gov = fields.Char(size=6, string=u"kod pocztowy")
    city_gov = fields.Char(string=u"miejscowość")
    voivodeship_gov = fields.Many2one(
        'volunteer.voivodeship',
        string=u"Województwo",
    )
    country_gov = fields.Many2one(
        'res.country',
        ondelete='restrict',
        string=u"Kraj",
    )
    different_addresses = fields.Boolean(
        default=False,
        string=u"adres zamieszkania jest inny niż zameldowania",
    )
    # address of residence
    street = fields.Char(string=u"ulica")
    street_number = fields.Char(string=u"numer budynku")
    apt_number = fields.Char(string=u"mieszk.")
    zip_code = fields.Char(size=6, string=u"kod pocztowy")
    city = fields.Char(string=u"miejscowość")
    voivodeship = fields.Many2one(
        'volunteer.voivodeship',
        string=u"województwo",
    )
    country = fields.Many2one(
        'res.country',
        ondelete='restrict',
        string=u"kraj",
    )
    user_role = fields.Char(compute="_compute_user_role", string="Rola użytkownika")

    #######################################
    # Fields permissions code begins here #
    #######################################
    user_access_level = fields.Char(compute="_compute_user_access_level")

    permitted_fields = {
        'all': {  # Fields accessible to all users
            'id', 'name', 'image', 'image_small', 'image_medium', 'user_access_level',
            'groups_id', 'partner_id',
        },
        'privileged': {  # Fields accessible to privileged users (coordinators, managers)
            'wishes', 'skills', 'languages', 'occupation',
            'user_email', 'phone', 'birthdate', 'curriculum_vitae', 'cv_filename',
            'daypart', 'daypart_comments', 'sex', 'place_of_birth', 'citizenship',
            'street_gov', 'street_number_gov', 'apt_number_gov', 'zip_code_gov',
            'city_gov', 'voivodeship_gov', 'country_gov', 'different_addresses',
            'street', 'street_number', 'apt_number', 'zip_code', 'city', 'voivodeship',
            'country', 'active_state',
        },
        'owner': {  # Fields accessible to the owner (i.e. the user herself)
            'wishes', 'skills', 'languages', 'occupation',
            'user_email', 'phone', 'birthdate', 'curriculum_vitae', 'cv_filename',
            'daypart', 'daypart_comments', 'sex', 'place_of_birth', 'citizenship',
            'street_gov', 'street_number_gov', 'apt_number_gov', 'zip_code_gov',
            'city_gov', 'voivodeship_gov', 'country_gov', 'different_addresses',
            'street', 'street_number', 'apt_number', 'zip_code', 'city', 'voivodeship',
            'country', 'document_id_kind', 'document_id', 'notify_email', 'active_state',
        }
    }
    # Add fields whitelisted for the owner in base.res_users
    permitted_fields['owner'] |= set(res_users.SELF_READABLE_FIELDS)

    def __init__(self, pool, cr):
        super(Volunteer, self).__init__(pool, cr)
        # this method should run only once - when the model is being registered.
        self._sync_permitted_fields()

    def _add_permitted_fields(self, level, fields):
        """
        Make fields (provided as a `fields` set) accessible to users with access
        level `level` (either 'all', 'privileged' or 'owner').
        """
        self.permitted_fields[level] |= fields
        if level in ('owner', 'all'):
            self._sync_permitted_fields()

    def _remove_permitted_fields(self, level, fields):
        """
        Mark fields (provided as a `fields` set) as no longer accessible to users
        with access level `level` (either 'all', 'privileged' or 'owner').
        """
        self.permitted_fields[level] -= fields
        if level in ('owner', 'all'):
            self._sync_permitted_fields()

    def _sync_permitted_fields(self):
        """
        Sync SELF_WRITEABLE_FIELDS
        (part of rudimentary field permissions defined in base.res_users)
        with our field permission definitions.
        Do not sync SELF_READABLE_FIELDS, as user has rights to read his
        own profile.
        """
        self.SELF_WRITEABLE_FIELDS = list(
            set(self.SELF_WRITEABLE_FIELDS) |
            self.permitted_fields['all'] | self.permitted_fields['owner']
        )

    @api.v8
    def read(self, fields=None, load='_classic_read'):
        """
        Hide values for fields current user doesn't have access to.
        """
        results = super(Volunteer, self).read(fields=fields, load=load)
        if self.env.uid == SUPERUSER_ID:
            return results

        for record, fields_dict in izip(self, results):
            level = record.user_access_level
            if level == 'admin':
                continue
            available_fields = self.permitted_fields['all'] | \
                self.permitted_fields.get(level, set())

            for field_name in fields_dict:
                if field_name not in available_fields:
                    fields_dict[field_name] = False
        return results

    @api.v7  # noqa
    def read(self, cr, user, ids, fields=None, context=None, load='_classic_read'):
        # It turns out that the read() method in Odoo works differently depending
        # whether it was launched using old style API or new style API.
        # New style API read() always returns a list, while the old style API read()
        # returns a list or a single element, depending on the type of
        # its `ids` argument.
        #
        # We explicitly define the old style API method here, because if we were
        # to only define a new style API method, this would make Odoo to only
        # use new style API methods in super classes, breaking code in Odoo that depends
        # on old style API read() behavior (as the difference in behavior won't be
        # corrected by the usual old style <-> new style automatic conversion).
        #
        # Ask me how long this took to debug. Or better don't.
        records = self.browse(cr, user, ids, context)
        result = Volunteer.read(records, fields, load=load)
        return result if isinstance(ids, list) else (bool(result) and result[0])

    @api.model
    def create(self, vals):
        """
        New user needs a default timezone. Here set to Warsaw.
        """
        record = super(Volunteer, self).create(vals)
        record_sudo = record.sudo()
        record_sudo.tz = 'Europe/Warsaw'
        return record

    @api.one
    @api.depends('groups_id')
    def _compute_user_access_level(self):
        """
        Access level that the current (logged in) user has for the object.
        Either "owner", "admin", "privileged" or None.
        """
        if self.id == self.env.uid:
            self.user_access_level = 'owner'
        elif self.env.uid == SUPERUSER_ID or self.user_has_groups('bestja_base.instance_admin'):
            self.user_access_level = 'admin'
        else:
            self.user_access_level = None

    #######################################
    # / Fields permissions code ends here #
    #######################################

    @api.one
    @api.depends('groups_id')
    def _compute_user_role(self):
        """
        Human redable information about current user's roles.
        """
        roles = []
        current_user_env = self.sudo(user=self.id)
        if current_user_env.user_has_groups('bestja_base.instance_admin'):
            roles.append(u"Administrator")

        if current_user_env.user_has_groups('bestja_organization.coordinators'):
            roles.append(u"Koordynator organizacji")
        elif current_user_env.user_has_groups('bestja_project.managers'):
            roles.append(u"Menadżer projektów")

        self.user_role = u", ".join(roles)

    @api.one
    @api.depends('partner_id.email')
    def _compute_user_email(self):
        self.user_email = self.sudo().partner_id.email

    @api.one
    def _inverse_user_email(self):
        # There is no reason for self.user_email to ever be blank,
        # as the field is required.
        # The conditional statement is needed, because all fields are initialized
        # to False during user creation, and we don't want to propagate this to
        # the `email` field on the partner object (clearing it in the process).
        if self.user_email:
            self.sudo().partner_id.email = self.user_email

    @api.model
    def _get_group(self):
        # default groups
        # A shorter list than defined in base.res_user
        return [self.env.ref('base.group_user').id]

    @api.multi
    def preference_save(self):
        # Odoo reloads the page after preferences are saved, because
        # UI language might have changed. We don't allow users to change the
        # language, so we can overwrite the method to suppress the page refresh.
        pass

    @api.model
    def _authenticate_after_confirmation(self, values, token=None):
        """
        Send welcome message after user account is authenticated
        """
        user = super(Volunteer, self)._authenticate_after_confirmation(values, token)
        if user:
            self.env.ref('bestja_volunteer.welcome_msg').send(
                recipients=user,
            )
        return user

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        """
        Force user preferences modal fields to be in edit mode.
        """
        view = super(Volunteer, self).fields_view_get(
            view_id=view_id,
            view_type=view_type,
            toolbar=toolbar,
            submenu=submenu,
        )
        modal_view = self.env.ref('bestja_volunteer.bestja_volunteer_form_modal')
        if view_id != modal_view.id:
            return view

        doc = etree.XML(view['arch'])
        fields = doc.xpath("//field[not(@readonly) and not(@invisible)]")
        for field in fields:
            field.attrib['modifiers'] = '{"readonly": false}'
        view['arch'] = etree.tostring(doc)
        return view

    @api.one
    @api.constrains('document_id_kind', 'document_id')
    def _check_document_id_kind(self):
        if self.document_id and not self.document_id_kind:
            raise exceptions.ValidationError("Podaj rodzaj dokumentu tożsamości!")

    @api.one
    @api.constrains('voivodeship', 'voivodeship_gov', 'country', 'country_gov')
    def _voivodeship_not_in_poland(self):
        """
        If the chosen country is not Poland, voivodeship has to be empty.
        """
        if ((self.country.code != 'PL' and self.voivodeship)
                or (self.country_gov.code != 'PL' and self.voivodeship_gov)):
            raise exceptions.ValidationError("Województwa dotyczą tylko Polski!")

    @api.model
    def _set_default_language(self, lang_code):
        """
        Set default language for all new users.
        If the language is not already loaded
        (for example using `--load-language` option)
        it will be ignored.
        """
        lang = self.env['res.lang'].search([('code', '=', lang_code)])
        if lang:
            self.env['ir.values'].set_default('res.partner', 'lang', lang_code)

    @api.one
    def _sync_group(self, group, domain):
        """
        if the current user satisfies the domain `domain` she should be a member
        of a group `group`. Otherwise she should be removed.
        """
        results = self.search_count(domain + [('id', '=', self.id)])
        command = 4 if results else 3  # add if true else remove
        self.sudo().write({
            'groups_id': [(command, group.id)],
        })

    @staticmethod
    def _is_password_safe(password):
        """
        Does password follow the security rules?
        """
        return len(password) >= 6 and re.search('[a-zA-Z]+', password) \
            and not password.islower() and not password.isupper()

    @api.model
    def signup(self, values, token=None):
        """
        Added for password validation: at least 6 characters, any letters,
        any uppercase letter, not only lowercase.
        You can't do it using constraints, as password is hashed in the database.
        """
        if not self._is_password_safe(values.get('password')):
            raise SignupError("Hasło powinno zawierać co najmniej 6 znaków, w tym litery różnej wielkości!")
        return super(Volunteer, self).signup(values, token)

    @api.model
    def change_password(self, old_passwd, new_passwd):
        """
        For changing password in preferences.
        """
        if not self._is_password_safe(new_passwd):
            raise exceptions.ValidationError(
                "Hasło powinno zawierać co najmniej 6 znaków, w tym litery różnej wielkości!"
            )
        return super(Volunteer, self).change_password(old_passwd, new_passwd)

    @api.onchange('different_addresses')
    def _equal_addresses(self):
        """
        If mailing address is the same as address of residence
        than it should be empty.
        """
        if not self.different_addresses:
            self.street = None
            self.street_number = None
            self.apt_number = None
            self.zip_code = None
            self.city = None
            self.country = None
            self.voivodeship = None

    @api.onchange('country', 'country_gov')
    def _onchange_country(self):
        """
        If the chosen country is not Poland, reset voivodeship
        """
        if self.country.code != 'PL':
            self.voivodeship = None
        if self.country_gov.code != 'PL':
            self.voivodeship_gov = None

    @api.onchange('voivodeship', 'voivodeship_gov')
    def _onchange_voivodeship(self):
        """
        If a voivodeship is chosen we can safely
        assume the country is Poland.
        """
        poland = self.env.ref('base.pl')
        if self.voivodeship:
            self.country = poland.id
        if self.voivodeship_gov:
            self.country_gov = poland.id

        # limit list of countries to Poland
        return {
            'domain': {
                'country': [('id', '=', poland.id)] if self.voivodeship else [],
                'country_gov': [('id', '=', poland.id)] if self.voivodeship_gov else []
            }
        }


class Partner(models.Model):
    _inherit = 'res.partner'

    EMAIL_NOTIFICATIONS = [
        ('always', 'Tak, chcę otrzymywać wszystkie powiadomienia'),
        ('none', 'Nie chcę otrzymywać żadnych powiadomień'),
    ]

    email = fields.Char(groups='base.group_system')  # hide email
    notify_email = fields.Selection(EMAIL_NOTIFICATIONS, default='always', help=None)

    @api.multi
    def check_access_rule(self, operation):
        """
        To access a partner object one need to have access permissions
        for the corresponding user object.
        """
        super(Partner, self).check_access_rule(operation)
        related_users = self.sudo().user_ids
        if related_users:
            related_users.sudo(self.env.uid).check_access_rule(operation)
