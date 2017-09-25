# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2017 Solucións Aloxa S.L. <info@aloxa.eu>
#                        Alexandre Díaz <alex@aloxa.eu>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Price Dimension',
    'version': '1.0',
    'author': "Alexandre Díaz (Aloxa Solucións S.L.) <alex@aloxa.eu>",
    'website': 'https://www.eiqui.com',
    'category': 'eiqui/manzano',
    'summary': "Price Dimension",
    'description': "Price Dimension",
    'depends': [
        'sale',
        'stock',
        'purchase',
        'product_variant_configurator',
    ],
    'external_dependencies': {
        'python': [
            'xlrd',
        ]
    },
    'data': [
        'views/general.xml',
        'views/supplier_attribute_value.xml',
        'views/inherit_product_template.xml',
        'views/inherit_product_product.xml',
        'views/inherit_product_supplier_info.xml',
        'views/inherit_product_attribute_value.xml',
        'views/inherit_product_attribute_price.xml',
        'views/inherit_sale_order.xml',
        'views/inherit_purchase_order.xml',
        'views/inherit_stock_move.xml',
        'views/inherit_stock_picking.xml',
        'security/ir.model.access.csv',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'AGPL-3',
}
