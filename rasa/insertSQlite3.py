import sqlite3

# Connect to the database
conn = sqlite3.connect("knowledge_base.db")
cursor = conn.cursor()

# Insert products
products = [
    ('phone10', '6.5-inch display, 5000mAh battery', '2024-01-15', 699),
    ('laptop10', 'Intel i7 processor, 16GB RAM, 512GB SSD', '2024-02-10', 1299),
    ('tablet10', '10-inch display, 64GB storage, supports 4G connectivity', '2024-03-01', 499),
    ('smartwatch10', 'Heart rate monitoring, 7-day battery life', '2024-01-20', 299),
    ('charger', '220v, 5000mAh battery, warranty', '2024-01-15', 599),
    ('headphone', 'Apple, Steroo, High Quality', '2024-02-10', 1199),
    ('speaker', '20db, several colours, supports bluetooth', '2024-03-01', 399),
    ('monitor', '24In, USB ports , Samsung', '2024-03-01', 399),
    ]
cursor.executemany("INSERT INTO Products (name, specifications, release_date, price) VALUES (?, ?, ?, ?)", products)

# Insert services
services = [
    ('repair_Lux', 'Fixes for electronic devices including phones, laptops, and tablets', 'Monday to Friday, 9AM to 6PM'),
    ('installation_at_site', 'Setup and configuration of home and office devices', 'Weekends only, 10AM to 4PM'),
    ('O&M', 'Regular maintenance checks for devices', 'Monday to Saturday, 9AM to 5PM'),
    ('Customer Support', '7 days/week 24h/day', 'on_site help, Trouble repporting'),
    ('SW uppgrade', 'remote uppgrade', 'on_site help, 1AM to 6AM'),


]
cursor.executemany("INSERT INTO Services (type, description, availability) VALUES (?, ?, ?)", services)

# Insert deliveries
deliveries = [
    ('order1231', 'In Transit', '2024-01-05'),
    ('order4561', 'Delivered', '2023-12-28'),
    ('order7891', 'Pending', '2024-01-10'),
    ('order987', 'shipped', '2024-11-05'),
    ('order654', 'arrived destination terminal', '2024-12-28'),
    ('order321', 'Ready for delivery', '2025-01-12'),
]
cursor.executemany("INSERT INTO Delivery (order_id, status, estimated_time) VALUES (?, ?, ?)", deliveries)

# Commit and close the connection
conn.commit()
conn.close()

print("Database has been populated successfully!")
