from django.core.management.base import BaseCommand
from catalog.models import Product, ProductCostComponent
from decimal import Decimal


class Command(BaseCommand):
    help = 'Create sample products with cost components'

    def handle(self, *args, **options):
        # Sample products with detailed costing
        sample_products = [
            {
                'name': 'Cream of Tomato Soup',
                'category': 'soups',
                'unit': '250ml',
                'selling_price': Decimal('80.00'),
                'description': 'Rich and creamy tomato soup with fresh basil',
                'is_active': True,
                'cost_components': [
                    {'item_name': 'Tomatoes', 'item_type': 'ingredient', 'quantity': Decimal('0.150'), 'unit_of_measure': 'kg', 'cost_per_unit': Decimal('40.00')},
                    {'item_name': 'Fresh Cream', 'item_type': 'ingredient', 'quantity': Decimal('0.030'), 'unit_of_measure': 'liters', 'cost_per_unit': Decimal('200.00')},
                    {'item_name': 'Onions', 'item_type': 'ingredient', 'quantity': Decimal('0.020'), 'unit_of_measure': 'kg', 'cost_per_unit': Decimal('30.00')},
                    {'item_name': 'Garlic', 'item_type': 'ingredient', 'quantity': Decimal('0.005'), 'unit_of_measure': 'kg', 'cost_per_unit': Decimal('100.00')},
                    {'item_name': 'Butter', 'item_type': 'ingredient', 'quantity': Decimal('0.010'), 'unit_of_measure': 'kg', 'cost_per_unit': Decimal('450.00')},
                    {'item_name': 'Spices & Seasoning', 'item_type': 'ingredient', 'quantity': Decimal('1.000'), 'unit_of_measure': 'batch', 'cost_per_unit': Decimal('5.00')},
                    {'item_name': 'Cooking Labor', 'item_type': 'labor', 'quantity': Decimal('0.100'), 'unit_of_measure': 'hours', 'cost_per_unit': Decimal('100.00')},
                    {'item_name': 'Gas/Fuel', 'item_type': 'fuel', 'quantity': Decimal('1.000'), 'unit_of_measure': 'batch', 'cost_per_unit': Decimal('8.00')},
                    {'item_name': 'Container', 'item_type': 'packaging', 'quantity': Decimal('1.000'), 'unit_of_measure': 'piece', 'cost_per_unit': Decimal('12.00')},
                ]
            },
            {
                'name': 'Cream of Tomato Soup',
                'category': 'soups',
                'unit': '500ml',
                'selling_price': Decimal('140.00'),
                'description': 'Rich and creamy tomato soup with fresh basil - Large size',
                'is_active': True,
                'cost_components': [
                    {'item_name': 'Tomatoes', 'item_type': 'ingredient', 'quantity': Decimal('0.300'), 'unit_of_measure': 'kg', 'cost_per_unit': Decimal('40.00')},
                    {'item_name': 'Fresh Cream', 'item_type': 'ingredient', 'quantity': Decimal('0.060'), 'unit_of_measure': 'liters', 'cost_per_unit': Decimal('200.00')},
                    {'item_name': 'Onions', 'item_type': 'ingredient', 'quantity': Decimal('0.040'), 'unit_of_measure': 'kg', 'cost_per_unit': Decimal('30.00')},
                    {'item_name': 'Garlic', 'item_type': 'ingredient', 'quantity': Decimal('0.010'), 'unit_of_measure': 'kg', 'cost_per_unit': Decimal('100.00')},
                    {'item_name': 'Butter', 'item_type': 'ingredient', 'quantity': Decimal('0.020'), 'unit_of_measure': 'kg', 'cost_per_unit': Decimal('450.00')},
                    {'item_name': 'Spices & Seasoning', 'item_type': 'ingredient', 'quantity': Decimal('1.000'), 'unit_of_measure': 'batch', 'cost_per_unit': Decimal('8.00')},
                    {'item_name': 'Cooking Labor', 'item_type': 'labor', 'quantity': Decimal('0.150'), 'unit_of_measure': 'hours', 'cost_per_unit': Decimal('100.00')},
                    {'item_name': 'Gas/Fuel', 'item_type': 'fuel', 'quantity': Decimal('1.000'), 'unit_of_measure': 'batch', 'cost_per_unit': Decimal('12.00')},
                    {'item_name': 'Container', 'item_type': 'packaging', 'quantity': Decimal('1.000'), 'unit_of_measure': 'piece', 'cost_per_unit': Decimal('18.00')},
                ]
            },
            {
                'name': 'Masala Bajji',
                'category': 'snacks',
                'unit': '6 pieces',
                'selling_price': Decimal('60.00'),
                'description': 'Spicy deep-fried fritters with mixed vegetables',
                'is_active': True,
                'cost_components': [
                    {'item_name': 'Besan (Gram flour)', 'item_type': 'ingredient', 'quantity': Decimal('0.080'), 'unit_of_measure': 'kg', 'cost_per_unit': Decimal('80.00')},
                    {'item_name': 'Potatoes', 'item_type': 'ingredient', 'quantity': Decimal('0.100'), 'unit_of_measure': 'kg', 'cost_per_unit': Decimal('25.00')},
                    {'item_name': 'Onions', 'item_type': 'ingredient', 'quantity': Decimal('0.050'), 'unit_of_measure': 'kg', 'cost_per_unit': Decimal('30.00')},
                    {'item_name': 'Cooking Oil', 'item_type': 'ingredient', 'quantity': Decimal('0.050'), 'unit_of_measure': 'liters', 'cost_per_unit': Decimal('150.00')},
                    {'item_name': 'Spices', 'item_type': 'ingredient', 'quantity': Decimal('1.000'), 'unit_of_measure': 'batch', 'cost_per_unit': Decimal('8.00')},
                    {'item_name': 'Preparation Labor', 'item_type': 'labor', 'quantity': Decimal('0.150'), 'unit_of_measure': 'hours', 'cost_per_unit': Decimal('100.00')},
                    {'item_name': 'Gas/Fuel', 'item_type': 'fuel', 'quantity': Decimal('1.000'), 'unit_of_measure': 'batch', 'cost_per_unit': Decimal('10.00')},
                    {'item_name': 'Packaging Box', 'item_type': 'packaging', 'quantity': Decimal('1.000'), 'unit_of_measure': 'piece', 'cost_per_unit': Decimal('8.00')},
                ]
            },
            {
                'name': 'Upma',
                'category': 'lunch',
                'unit': '1 plate',
                'selling_price': Decimal('50.00'),
                'description': 'Traditional South Indian breakfast/lunch dish with semolina',
                'is_active': True,
                'cost_components': [
                    {'item_name': 'Rava (Semolina)', 'item_type': 'ingredient', 'quantity': Decimal('0.080'), 'unit_of_measure': 'kg', 'cost_per_unit': Decimal('50.00')},
                    {'item_name': 'Vegetables (mixed)', 'item_type': 'ingredient', 'quantity': Decimal('0.050'), 'unit_of_measure': 'kg', 'cost_per_unit': Decimal('40.00')},
                    {'item_name': 'Oil', 'item_type': 'ingredient', 'quantity': Decimal('0.015'), 'unit_of_measure': 'liters', 'cost_per_unit': Decimal('150.00')},
                    {'item_name': 'Spices & Seasoning', 'item_type': 'ingredient', 'quantity': Decimal('1.000'), 'unit_of_measure': 'batch', 'cost_per_unit': Decimal('5.00')},
                    {'item_name': 'Cooking Labor', 'item_type': 'labor', 'quantity': Decimal('0.100'), 'unit_of_measure': 'hours', 'cost_per_unit': Decimal('100.00')},
                    {'item_name': 'Gas/Fuel', 'item_type': 'fuel', 'quantity': Decimal('1.000'), 'unit_of_measure': 'batch', 'cost_per_unit': Decimal('6.00')},
                    {'item_name': 'Plate/Container', 'item_type': 'packaging', 'quantity': Decimal('1.000'), 'unit_of_measure': 'piece', 'cost_per_unit': Decimal('10.00')},
                ]
            },
            {
                'name': 'Mango Pickle',
                'category': 'pickle',
                'unit': '200g jar',
                'selling_price': Decimal('120.00'),
                'description': 'Homemade spicy mango pickle',
                'is_active': True,
                'cost_components': [
                    {'item_name': 'Raw Mangoes', 'item_type': 'ingredient', 'quantity': Decimal('0.150'), 'unit_of_measure': 'kg', 'cost_per_unit': Decimal('60.00')},
                    {'item_name': 'Mustard Oil', 'item_type': 'ingredient', 'quantity': Decimal('0.040'), 'unit_of_measure': 'liters', 'cost_per_unit': Decimal('200.00')},
                    {'item_name': 'Spice Mix', 'item_type': 'ingredient', 'quantity': Decimal('0.020'), 'unit_of_measure': 'kg', 'cost_per_unit': Decimal('400.00')},
                    {'item_name': 'Salt', 'item_type': 'ingredient', 'quantity': Decimal('0.010'), 'unit_of_measure': 'kg', 'cost_per_unit': Decimal('20.00')},
                    {'item_name': 'Preparation Labor', 'item_type': 'labor', 'quantity': Decimal('0.200'), 'unit_of_measure': 'hours', 'cost_per_unit': Decimal('100.00')},
                    {'item_name': 'Glass Jar', 'item_type': 'packaging', 'quantity': Decimal('1.000'), 'unit_of_measure': 'piece', 'cost_per_unit': Decimal('25.00')},
                ]
            },
        ]

        created_count = 0
        skipped_count = 0

        for product_data in sample_products:
            cost_components_data = product_data.pop('cost_components', [])
            
            # Check if product already exists
            if not Product.objects.filter(
                name=product_data['name'], 
                unit=product_data['unit']
            ).exists():
                product = Product.objects.create(**product_data)
                
                # Add cost components
                for component_data in cost_components_data:
                    ProductCostComponent.objects.create(product=product, **component_data)
                
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Created: {product.name} ({product.unit}) - '
                        f'Cost: ₹{product.unit_cost:.2f}, Price: ₹{product.selling_price:.2f}, '
                        f'Profit: ₹{product.unit_profit:.2f} ({product.margin_percent:.1f}%)'
                    )
                )
            else:
                skipped_count += 1
                self.stdout.write(
                    self.style.WARNING(
                        f'⊘ Skipped: {product_data["name"]} ({product_data["unit"]}) (already exists)'
                    )
                )

        self.stdout.write(self.style.SUCCESS(f'\n✅ Created {created_count} products'))
        if skipped_count > 0:
            self.stdout.write(self.style.WARNING(f'⊘ Skipped {skipped_count} existing products'))
