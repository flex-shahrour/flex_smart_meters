{
    'name': 'Flex Smart Meters',
    'version': '1.0',
    'summary': 'Flex Smart Meters',
    'description': 'Flex Smart Meters',
    'category': 'Uncategorized',
    'author': 'Abdalrahman Shahrour',
    'website': 'https://www.flex-ops.com',
    'license': 'AGPL-3',
    'depends': ['base', 'liwan'],
    'data': [
        'security/ir.model.access.csv',
        'security/group.xml',
        'data/sequence.xml',
        'views/flex_smart_meters.xml',
        'wizard/assign_user_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    # 'external_dependencies': {
    #     'python': [''],
    # }
}
