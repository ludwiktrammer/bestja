# -*- coding: utf-8 -*-
{
    'name': "Bestja: Stores",
    'summary': "Support for stores in hierarchical projects",
    'description': """
BestJa Stores
=============
Add stores to hierarchical projects.
""",
    'author': "Laboratorium EE",
    'website': "http://www.laboratorium.ee",
    'depends': [
        'bestja_project_hierarchy',
    ],
    'data': [
        'views/store_in_project.xml',
        'views/store.xml',
        'views/project.xml',
        'views/in_project_state_wizard.xml',
        'views/store_to_project_wizard.xml',
        'views/deactivate_wizard.xml',
        'menu.xml',
        'data/chains.xml',
        'messages.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
    ],
}
