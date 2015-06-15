{
    # Theme information
    'name': "FPBŻ Theme",
    'summary': "Html5 Responsive Bootstrap Theme for Odoo CMS",
    'description': """
    This is a custom theme made for Federacja Polskich Banków Żywności
    """,
    'category': 'Theme',
    'version': '1.0',
    'css': ['static/src/css/custom.css'],
    'depends': [
        'website',
        'website_embedded',
    ],

    'data': [
        # assets
        'views/assets.xml',
        'views/cookie_reminder.xml',
        'views/login_signup.xml',

        # snippets
        'templates/snippets/introduction.xml',
        'templates/snippets/big_title.xml',
        'templates/snippets/why_act_with_us.xml',
        'templates/snippets/map_of_poland.xml',
        'templates/snippets/quote_div.xml',
        'templates/snippets/recrutation_steps.xml',
        'templates/snippets/meet_our_volunteers.xml',
        'templates/snippets/get_knowledge.xml',
    ],
    'application': True,
    # About information
    'author': "Laboratorium EE, Kamil Woźniak",
    'website': "http://laboratorium.ee",
}
