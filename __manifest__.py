{
    'name': 'Demande equipement',
    'version': '1.0',
    'author': 'CONDE MOUSSA',
    'category': 'article',
    'depends': ['base',"purchase","sale","account"],
    'data': [
            "security/ir.model.access.csv",
            "views/fiche_bordereau_cogitech.xml",
            "views/menu_generale.xml"
        ],
    'installable': True,
    'application': True,
}
