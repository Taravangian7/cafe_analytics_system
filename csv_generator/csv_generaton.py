import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Configuración
np.random.seed(42)
random.seed(42)

# Fecha de inicio: últimas 4 semanas
end_date = datetime(2024, 10, 27)
start_date = end_date - timedelta(days=28)

# 1. PRODUCTS - Menú del café
products_data = {
    'product_id': range(1, 26),
    'sku': [f'PROD{str(i).zfill(3)}' for i in range(1, 26)],
    'product_name': [
        'Flat White', 'Cappuccino', 'Latte', 'Long Black', 'Espresso',
        'Mocha', 'Iced Latte', 'Iced Coffee', 'Hot Chocolate', 'Chai Latte',
        'Croissant', 'Almond Croissant', 'Pain au Chocolat', 'Muffin Blueberry', 'Muffin Choc Chip',
        'Banana Bread', 'Avocado Toast', 'Bacon & Egg Roll', 'Ham & Cheese Toastie', 'Vegetarian Wrap',
        'Caesar Salad', 'Greek Salad', 'Chicken Sandwich', 'BLT Sandwich', 'Orange Juice'
    ],
    'category': [
        'Coffee', 'Coffee', 'Coffee', 'Coffee', 'Coffee',
        'Coffee', 'Coffee', 'Coffee', 'Hot Drinks', 'Hot Drinks',
        'Pastries', 'Pastries', 'Pastries', 'Pastries', 'Pastries',
        'Food', 'Food', 'Food', 'Food', 'Food',
        'Food', 'Food', 'Food', 'Food', 'Beverages'
    ],
    'price': [
        4.50, 4.50, 4.50, 4.00, 3.50,
        5.00, 5.50, 5.00, 4.50, 4.50,
        4.50, 5.50, 5.00, 5.00, 5.00,
        5.50, 12.00, 10.00, 8.50, 9.50,
        14.00, 12.50, 11.50, 10.50, 5.00
    ],
    'cost': [
        1.20, 1.25, 1.30, 1.10, 0.90,
        1.50, 1.60, 1.40, 1.30, 1.20,
        1.50, 2.00, 1.80, 1.70, 1.60,
        2.00, 5.50, 4.50, 3.80, 4.20,
        6.50, 5.80, 5.20, 4.80, 1.50
    ]
}

products_df = pd.DataFrame(products_data)

# 2. ORDERS - Comandas principales
num_orders = 350  # ~12 orders por día durante 28 días

# Generar fechas aleatorias con más peso en horarios típicos (7am-3pm)
dates = []
for _ in range(num_orders):
    random_day = start_date + timedelta(
        days=random.randint(0, 27),
        hours=random.choices([7, 8, 9, 10, 11, 12, 13, 14, 15], weights=[5, 15, 20, 15, 12, 10, 8, 10, 5])[0],
        minutes=random.randint(0, 59)
    )
    dates.append(random_day)

dates.sort()

orders_data = {
    'order_id': range(1, num_orders + 1),
    'receipt_number': [f'R{str(i).zfill(6)}' for i in range(1, num_orders + 1)],
    'order_datetime': dates,
    'order_date': [d.date() for d in dates],
    'order_time': [d.strftime('%H:%M:%S') for d in dates],
    'day_of_week': [d.strftime('%A') for d in dates],
    'staff_member': np.random.choice(['Sarah', 'Mike', 'Emma', 'Tom', 'Lisa'], num_orders),
    'payment_method': np.random.choice(['Card', 'Cash', 'Mobile'], num_orders, p=[0.70, 0.20, 0.10]),
    'order_type': np.random.choice(['Dine In', 'Takeaway'], num_orders, p=[0.60, 0.40]),
    'status': ['Completed'] * num_orders
}

orders_df = pd.DataFrame(orders_data)

# 3. ORDER_ITEMS - Items de cada comanda
order_items_list = []
item_id_counter = 1

for order_id in range(1, num_orders + 1):
    # Cada orden tiene entre 1 y 4 items
    num_items = random.choices([1, 2, 3, 4], weights=[30, 45, 20, 5])[0]
    
    # Seleccionar productos aleatorios (sin repetición en la misma orden)
    selected_products = random.sample(range(1, 26), num_items)
    
    for product_id in selected_products:
        product_info = products_df[products_df['product_id'] == product_id].iloc[0]
        quantity = 1  # Casi siempre 1, raramente 2
        if random.random() < 0.05:
            quantity = 2
            
        order_items_list.append({
            'item_id': item_id_counter,
            'order_id': order_id,
            'product_id': product_id,
            'sku': product_info['sku'],
            'product_name': product_info['product_name'],
            'category': product_info['category'],
            'quantity': quantity,
            'unit_price': product_info['price'],
            'line_total': round(product_info['price'] * quantity, 2),
            'cost_per_unit': product_info['cost'],
            'line_cost': round(product_info['cost'] * quantity, 2)
        })
        item_id_counter += 1

order_items_df = pd.DataFrame(order_items_list)

# Calcular totales por orden
order_totals = order_items_df.groupby('order_id').agg({
    'line_total': 'sum',
    'line_cost': 'sum'
}).reset_index()
order_totals.columns = ['order_id', 'total_amount', 'total_cost']
order_totals['gross_profit'] = round(order_totals['total_amount'] - order_totals['total_cost'], 2)

# Agregar totales a orders_df
orders_df = orders_df.merge(order_totals, on='order_id')

# Guardar CSVs
products_df.to_csv('products.csv', index=False)
orders_df.to_csv('orders.csv', index=False)
order_items_df.to_csv('order_items.csv', index=False)

print("✅ Datasets generados exitosamente!")
print(f"\n📊 Resumen:")
print(f"- products.csv: {len(products_df)} productos")
print(f"- orders.csv: {len(orders_df)} órdenes")
print(f"- order_items.csv: {len(order_items_df)} items")
print(f"\n💰 Métricas:")
print(f"- Revenue total: ${orders_df['total_amount'].sum():,.2f}")
print(f"- Costo total: ${orders_df['total_cost'].sum():,.2f}")
print(f"- Ganancia bruta: ${orders_df['gross_profit'].sum():,.2f}")
print(f"- Margen promedio: {(orders_df['gross_profit'].sum() / orders_df['total_amount'].sum() * 100):.1f}%")
print(f"- Ticket promedio: ${orders_df['total_amount'].mean():.2f}")