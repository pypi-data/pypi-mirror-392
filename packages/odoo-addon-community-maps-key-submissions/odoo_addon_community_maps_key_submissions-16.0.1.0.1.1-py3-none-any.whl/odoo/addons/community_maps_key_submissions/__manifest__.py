{
    'name': "community_maps_key_submissions",

    'summary': """
        Define some submissions on the map as key submissions
    """,

    'description': """
        Define some submissions on the map as key submissions
    """,

    'author': "Community maps",
    'website': "https://gitlab.com/somitcoop/erp-research/community-maps",

    'category': 'community-maps',
    'version': '16.0.1.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','community_maps'],

    # always loaded
    'data': [
        'views/cm_form_submission.xml',
        'views/cm_map.xml',
        'views/cm_place.xml',
    ],
}
