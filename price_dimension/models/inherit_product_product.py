# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2017 Solucións Aloxa S.L. <info@aloxa.eu>
#                        Alexandre Díaz <alex@aloxa.eu>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import openerp
from openerp import api, tools, SUPERUSER_ID
from openerp.osv import osv, fields, expression
import openerp.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)


class product_product(osv.osv):
    _inherit = 'product.product'

    def _get_price_extra(self, cr, uid, ids, name, args, context=None):
        result = super(product_product, self)._get_price_extra(cr, uid, ids, name, args, context=context)
        _logger.info("3333333")
        for product in self.browse(cr, uid, ids, context=context):
            price_extra = 0.0
            for variant_id in product.attribute_value_ids:
                if variant_id.price_extra_type != 'standard':
                    continue
                for price_id in variant_id.price_ids:
                    if price_id.product_tmpl_id.id == product.product_tmpl_id.id:
                        price_extra += price_id.price_extra
            result[product.id] = price_extra
        return result

    def origin_check_sale_dim_values(self, cr, uid, id, width, height, context=None):
        product = self.browse(cr, uid, id, context=context)
        if product.sale_price_type in ['table_1d', 'table_2d']:
            product_prices_table_obj = self.pool.get('product.prices_table')
            norm_width = self.origin_normalize_sale_width_value(cr, uid, id, width, context=context)
            if product.sale_price_type == 'table_2d':
                norm_height = self.origin_normalize_sale_height_value(cr, uid, id, height, context=context)
                return product_prices_table_obj.search_count(cr, uid, [('sale_product_tmpl_id', '=', product.product_tmpl_id.id),
                                                                       ('pos_x', '=', norm_width),
                                                                       ('pos_y', '=', norm_height),
                                                                       ('value', '!=', 0)], context=context) > 0
            return product_prices_table_obj.search_count(cr, uid, [('sale_product_tmpl_id', '=', product.product_tmpl_id.id),
                                                                   ('pos_x', '=', norm_width),
                                                                   ('value', '!=', 0)], context=context) > 0
        elif product.sale_price_type == 'area':
            return width >= product.sale_price_area_min_width and width <= product.sale_price_area_max_width and height >= product.sale_price_area_min_height and height <= product.sale_price_area_max_height
        return True

    def origin_normalize_sale_width_value(self, cr, uid, id, width, context=None):
        headers = self.get_sale_price_table_headers(cr, uid, id, context=context)
        norm_val = width
        for index in range(len(headers[id]['x'])-1):
            if width > headers[id]['x'][index] and width <= headers[id]['x'][index+1]:
                norm_val = headers[id]['x'][index+1]
        return norm_val

    def origin_normalize_sale_height_value(self, cr, uid, id, height, context=None):
        headers = self.get_sale_price_table_headers(cr, uid, id, context=context)
        norm_val = height
        for index in range(len(headers[id]['y'])-1):
            if height > headers[id]['y'][index] and height <= headers[id]['y'][index+1]:
                norm_val = headers[id]['y'][index+1]
        return norm_val

    def _product_lst_price(self, cr, uid, ids, name, arg, context=None):
        res = super(product_product, self)._product_lst_price(cr, uid, ids, name, arg, context=context)
        _logger.info("4444444")
        product_uom_obj = self.pool.get('product.uom')
        product_ids = self.browse(cr, uid, ids, context=context)
        sale_prices = product_ids.get_sale_price(context=context)
        for product in product_ids:
            if 'uom' in context:
                uom = product.uom_id
                res[product.id] = product_uom_obj._compute_price(cr,
                                                                 uid,
                                                                 uom.id,
                                                                 sale_prices[product.id],
                                                                 context['uom'])
            else:
                res[product.id] = sale_prices[product.id]
            res[product.id] += (res[product.id] * product.price_extra_perc) / 100.0
            res[product.id] += product.price_extra
            _logger.info(product.price_extra_perc)


        return res

    def _set_product_lst_price(self, cr, uid, id, name, value, args, context=None):
        _logger.info("55555555")
        super(product_product, self)._set_product_lst_price(cr, uid, id, name, value, args, context=context)
        product_uom_obj = self.pool.get('product.uom')
        product = self.browse(cr, uid, id, context=context)
        if 'uom' in context:
            uom = product.uom_id
            value = product_uom_obj._compute_price(cr, uid,
                    context['uom'], value, uom.id)
        value -= (product.get_sale_price(context=context)[id] * product.price_extra_perc) / 100.0
        value -= product.price_extra

        return product.write({'list_price': value})

    def get_sale_price_table_headers(self, cr, uid, id, context=None):
        product = self.browse(cr, uid, id, context=context)
        result = {product.id: {'x': [0], 'y': [0]}}
        for rec in product.sale_prices_table:
            result[product.id]['x'].append(rec.pos_x)
            result[product.id]['y'].append(rec.pos_y)
        result[product.id].update({
            'x': sorted(list(set(result[product.id]['x']))),
            'y': sorted(list(set(result[product.id]['y'])))
        })
        return result

    def get_sale_price(self, cr, uid, ids, context=False):
        _logger.info("666666666")
        result = dict.fromkeys(ids, False)
        product_ids = self.browse(cr, uid, ids, context=context)

        origin_width = context and context.get('width') or False
        origin_height = context and context.get('height') or False

        for product in product_ids:
            result[product.id] = False
            if origin_width:
                product_prices_table_obj = self.pool.get('product.prices_table')
                origin_width = self.origin_normalize_sale_width_value(cr, uid, product.id, origin_width, context=context)
                if product.sale_price_type == 'table_2d':
                    origin_height = self.origin_normalize_sale_height_value(cr, uid, product.id, origin_height, context=context)
                    res = product_prices_table_obj.search_read(cr, uid, [
                        ('sale_product_tmpl_id', '=', product.product_tmpl_id.id),
                        ('pos_x', '=', origin_width),
                        ('pos_y', '=', origin_height)
                    ], limit=1, context=context)
                    result[product.id] = res and res[0]['value'] or False
                elif product.sale_price_type == 'table_1d':
                    res = product_prices_table_obj.search_read(cr, uid, [
                        ('sale_product_tmpl_id', '=', product.product_tmpl_id.id),
                        ('pos_x', '=', origin_width)
                    ], limit=1, context=context)
                    result[product.id] = res and res[0]['value'] or False
                elif product.sale_price_type == 'area':
                    result[product.id] = product.list_price * origin_width * origin_height
                    result[product.id] = max(product.sale_min_price_area, result[product.id])
            if not result[product.id]:
                result[product.id] = product.list_price
        return result

    def _get_price_extra_percentage(self, cr, uid, ids, name, args, context=None):
        _logger.info("77777777")
        result = dict.fromkeys(ids, False)
        for product in self.browse(cr, uid, ids, context=context):
            price_extra = 0.0
            for variant_id in product.attribute_value_ids:
                if variant_id.price_extra_type != 'percentage':
                    continue
                for price_id in variant_id.price_ids:
                    if price_id.product_tmpl_id.id == product.product_tmpl_id.id:
                        price_extra += price_id.price_extra
            result[product.id] = price_extra
        return result



    _columns = {
        'price_extra': fields.function(_get_price_extra, type='float', string='Variant Extra Price', help="This is the sum of the extra price of all attributes", digits_compute=dp.get_precision('Product Price')),
        'lst_price': fields.function(_product_lst_price, fnct_inv=_set_product_lst_price, type='float', string='Sale Price', digits_compute=dp.get_precision('Product Price')),

        'price_extra_perc': fields.function(_get_price_extra_percentage, type='float', string='Variant Extra Price Percentage', help="This is the percentage of the extra price of all attributes", digits_compute=dp.get_precision('Product Price')),
    }
