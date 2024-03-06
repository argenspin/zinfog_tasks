from odoo import models,api,fields
import logging

class ProductTemplate(models.Model):
    _inherit = "product.template"
    is_delivery_charge_product = fields.Boolean()
    minimum_cost = fields.Monetary(string="Minimum Cost")
    brand_id = fields.Many2one('product.brand',string="Brand Name")

class ProductProduct(models.Model):
    _inherit = "product.product"
    minimum_cost = fields.Monetary(string="Minimum Cost")

    def create(self,vals_list):
        for vals in vals_list:
            prod_template = self.env['product.template'].browse(vals.get('product_tmpl_id'))
            vals['minimum_cost'] = prod_template.minimum_cost
            vals['brand_id'] = prod_template.brand_id.id
        return super(ProductProduct,self).create(vals)

    brand_id = fields.Many2one('product.brand',string="Brand Name")

class ProductBrand(models.Model):
    _name = "product.brand"
    name = fields.Char("Brand Name")