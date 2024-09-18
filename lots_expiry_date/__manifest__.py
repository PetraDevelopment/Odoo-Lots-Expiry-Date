{
    'name': 'Lots/Serial Expiry Date App',
    'author': 'www.t-petra.com',
    'website': 'www.t-petra.com',
    'summary': 'Odoo 14 Development',
    'maintainer': 'Petra Software',
    'company': 'Petra Software',
    'depends': ['base', 'web', 'stock', 'account', 'purchase', 'purchase_stock', 'sale', 'sale_stock', 'sale_management'],
    'data': [
        # 'views/assets.xml',
        'secuirty/lots_expiry_date_secuirty.xml',
        "secuirty/ir.model.access.csv",
        # "views/menu.xml",

        'views/productionlot_inherit.xml',
        'views/inherit_invoice.xml',


        'report/inherit_invoice_report.xml',
        'wizard/confirm_expiry_view.xml'


    ],
          'images': ['static/description/banner.png'],
    'application': True,
     'price':10,
      'currency':'USD',
}
