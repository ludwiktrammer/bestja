# -*- coding: utf-8 -*-
{
    # Theme information
    'name': "UCW Theme",
    'summary': "Html5 Responsive Bootstrap Theme for Odoo CMS",
    'description': """
    This is a custom theme made for Uniwersyteckie Centrum Wolontariatu
    """,
    'category': 'Theme',
    'version': '1.0',
    'css': ['static/src/css/custom.css'],
    'depends': [
        'website',
        'collage_photo',
    ],

    # assets
    'data': [
        'views/assets.xml',
        'views/login_signup.xml',
        'views/cookie_reminder.xml',
        # after collage was added this page is now dynamic
        'views/home_page.xml',
        # 'views/banner_change_for_carousel.xml',
    ],
    'application': True,
    # About information
    'author': "Laboratorium EE, Kamil Woźniak",
    'website': "http://laboratorium.ee",
}
