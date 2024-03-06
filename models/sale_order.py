from odoo import fields,api,models
from odoo.exceptions import UserError, ValidationError

class SaleOrder(models.Model):
    _inherit = "sale.order"
    include_delivery_charge = fields.Boolean(string="Include Delivery Charges")
    delivery_charge = fields.Float(string="Delivery Charge (%)", default=10)

    @api.onchange('include_delivery_charge','delivery_charge','order_line')
    def _onchange_delivery_charge(self):
        delivery_product = self.env['product.product'].search([('name','=','Delivery Charges')],limit=1)[0]
        delivery_line = self.order_line.filtered(lambda line: line.is_delivery_charge)
        if self.include_delivery_charge and self.delivery_charge>0:
            total_without_delivery = 0
            for line in self.order_line.filtered(lambda line: not line.is_delivery_charge and not line.display_type):
                total_without_delivery+=line.price_total

            if not delivery_line:
                data_list = self.order_line.ids
                data_list.append(self.env['sale.order.line'].create({
                    'order_id': self._origin.id,
                    'name': delivery_product.name,
                    'product_id': delivery_product.id,
                    'price_unit': (total_without_delivery) * (self.delivery_charge/100),
                    'is_delivery_charge': True,   
                    'tax_id': False,    
                }).id)
                self.update({'order_line': [(6,0,data_list)]})
            else:
                delivery_line.update({
                    'price_unit': (total_without_delivery) * (self.delivery_charge/100),
                })
        else:
            if delivery_line:
                self.update({'order_line': [(2,delivery_line.id)]})

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    is_delivery_charge = fields.Boolean()
    brand_id = fields.Many2one('product.brand',string="Brand", compute="_compute_brand_id",readonly=False,store=True)
            
    def create(self,vals):
        sale_line = super(SaleOrderLine,self).create(vals)
        if sale_line.price_unit < sale_line.product_id.minimum_cost:
            raise UserError(f'Unit Price of {sale_line.name} ({sale_line.currency_id.symbol}{sale_line.price_unit}) cannot be less than its Minimum cost ({sale_line.currency_id.symbol}{sale_line.product_id.minimum_cost})')
        return sale_line
    
    def write(self,vals):
        if vals.get('product_id'):
            product = self.env['product.product'].browse(vals['product_id'])
        else:
            product = self.product_id
        if vals.get('price_unit'):
            price_unit = vals['price_unit']
        else:
            price_unit = self.price_unit

        if price_unit < product.minimum_cost:
            raise UserError(f'Unit Price of {self.name} ({self.currency_id.symbol}{price_unit}) cannot be less than its Minimum cost ({self.currency_id.symbol}{product.minimum_cost})')
        sale_line = super(SaleOrderLine,self).write(vals)
        return sale_line
    
    @api.depends('product_id')
    def _compute_brand_id(self):
        for record in self:
            if record.product_id:
                record.brand_id = record.product_id.brand_id.id

