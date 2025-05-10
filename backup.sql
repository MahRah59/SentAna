PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "user" (
	id INTEGER NOT NULL, 
	first_name VARCHAR(30) NOT NULL, 
	last_name VARCHAR(30) NOT NULL, 
	username VARCHAR(30) NOT NULL, 
	email VARCHAR(120) NOT NULL, 
	role VARCHAR(120) NOT NULL, 
	created_date DATETIME, 
	phone VARCHAR(15), 
	company VARCHAR(100), 
	password_hash VARCHAR(60) NOT NULL, 
	is_crm_contact BOOLEAN, 
	crm_contact_id VARCHAR(255), 
	image_file VARCHAR(20), 
	PRIMARY KEY (id), 
	CONSTRAINT uq_username UNIQUE (username), 
	CONSTRAINT uq_email UNIQUE (email)
);
INSERT INTO user VALUES(1,'Brian','Halligan (Sample Contact)','BrianHalligan (Sample Contact)','bh@hubspot.com','customer',NULL,'',NULL,'$2b$12$zDxkEShfqGJuTrjniClOx.8wn9pqxMcGGDBpzcAUuSGLbQrexFP0S',NULL,'89641926243','default.jpg');
INSERT INTO user VALUES(2,'Maria','Johnson (Sample Contact)','MariaJohnson (Sample Contact)','emailmaria@hubspot.com','customer',NULL,'',NULL,'$2b$12$/u5OT7iHSjeLHYuYMS1E5.lrx2z45pxyTtFEDZOtiJ51UjzNh7QvK',NULL,'89644159520','default.jpg');
INSERT INTO user VALUES(3,'Mah','Rah','MahRah','mahrah@hubspot.com','customer',NULL,'',NULL,'$2b$12$FRliEqF3sJJBQVS8qQ5dcOkv/H5janSJrxQ2tSAiUPynzwUPzE54u',NULL,'89651737461','default.jpg');
INSERT INTO user VALUES(4,'Zakaria','Razi','ZakariaRazi','zakaria.razi@example.se','customer',NULL,'',NULL,'$2b$12$XaRnEhpkQ/16paPpmussyeSCMcbjjD9FhSfeex06cXylxeItrPrSq',NULL,'91501069718','default.jpg');
INSERT INTO user VALUES(5,'John','Doe','JohnDoe','john.doe@example.com','customer',NULL,'',NULL,'$2b$12$wiXSJPD8vJfCdK/fcDYfC.kNwqV88fpMz8fquNO87dtwj6lFTlv2W',NULL,'91522602529','default.jpg');
INSERT INTO user VALUES(6,'Martin','Luther','MartinLuther','martin.luther@example.se','customer',NULL,'',NULL,'$2b$12$tUTRkX8AKfKH2lcTGn/SkOdBJPF2ruTq5sUW1InlyQ5aUNRA7tPwm',NULL,'91819974321','default.jpg');
INSERT INTO user VALUES(7,'Patrik','Larsson','PatrikLarsson','patrik.larsson@example.se','customer',NULL,'',NULL,'$2b$12$PlSSU3M6QJUBp8qMMKRZKO7mt9vkR5dKN2XcVBBdJ3tVNqw9GwFG.',NULL,'92262859437','default.jpg');
CREATE TABLE IF NOT EXISTS "Delivery" (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Primary key for the Delivery table
    user_id INTEGER NOT NULL,  -- Foreign key linking to User
    order_id TEXT NOT NULL UNIQUE,  -- Unique order ID
    status TEXT NOT NULL,  -- Status of the delivery
    purchase_date DATETIME,  -- Purchase date of the order
    shipped_date DATETIME,  -- Shipped date
    delivery_date DATETIME,  -- Delivery date
    estimated_time TEXT,  -- Estimated delivery time
    FOREIGN KEY (user_id) REFERENCES User(id)  -- Foreign key constraint linking user_id to User table
);
INSERT INTO Delivery VALUES(1,1,'123','Shipped','2025-01-01','2025-01-05','2025-01-07','3 days');
INSERT INTO Delivery VALUES(2,2,'1100','Purchased','2025-02-01','planned for: 2025-02-05','2025-02-10','5 days');
INSERT INTO Delivery VALUES(3,2,'1234','Shipped','2025-01-07','2025-01-09','2025-01-11','2 days');
INSERT INTO Delivery VALUES(4,1,'2100','Delivered','2025-01-06','2025-01-09','2025-01-12','Already Delivered');
INSERT INTO Delivery VALUES(5,2,'1200','Purchased','2025-02-01','planned for: 2025-02-04','2025-02-08','4 days');
CREATE TABLE IF NOT EXISTS "Products" (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	specifications VARCHAR(1028) NOT NULL, 
	release_date VARCHAR(200) NOT NULL, 
	price FLOAT NOT NULL, 
	additional_information VARCHAR(255), 
	PRIMARY KEY (id)
);
INSERT INTO Products VALUES(1,'phone','6.5-inch display, 5000mAh battery','2024-01-15',699.0,NULL);
INSERT INTO Products VALUES(3,'laptop','Intel i7 processor, 16GB RAM, 512GB SSD','2024-02-10',1299.0,NULL);
INSERT INTO Products VALUES(4,'tablet','10-inch display, 64GB storage, supports 4G connectivity','2024-03-01',499.0,NULL);
INSERT INTO Products VALUES(5,'smartwatch','Heart rate monitoring, 7-day battery life','2024-01-20',299.0,NULL);
INSERT INTO Products VALUES(6,'phone10','6.5-inch display, 5000mAh battery','2024-01-15',699.0,NULL);
INSERT INTO Products VALUES(7,'laptop10','Intel i7 processor, 16GB RAM, 512GB SSD','2024-02-10',1299.0,NULL);
INSERT INTO Products VALUES(8,'tablet10','10-inch display, 64GB storage, supports 4G connectivity','2024-03-01',499.0,NULL);
INSERT INTO Products VALUES(9,'smartwatch10','Heart rate monitoring, 7-day battery life','2024-01-20',299.0,NULL);
INSERT INTO Products VALUES(10,'charger','220v, 5000mAh battery, warranty','2024-01-15',599.0,NULL);
INSERT INTO Products VALUES(11,'headphone','Apple, Steroo, High Quality','2024-02-10',1199.0,NULL);
INSERT INTO Products VALUES(12,'speaker','20db, several colours, supports bluetooth','2024-03-01',399.0,NULL);
INSERT INTO Products VALUES(13,'monitor','24In, USB ports , Samsung','2024-03-01',399.0,NULL);
CREATE TABLE IF NOT EXISTS "Services" (
	id INTEGER NOT NULL, 
	description VARCHAR(512) NOT NULL, 
	availability VARCHAR(100) NOT NULL, 
	additional_information VARCHAR(255), 
	service_type VARCHAR(100) DEFAULT 'default_service_type' NOT NULL, 
	PRIMARY KEY (id)
);
INSERT INTO Services VALUES(1,'Fixes for electronic devices','Monday to Friday, 9AM to 6PM',NULL,'repair');
INSERT INTO Services VALUES(3,'Setup and configuration of home and office devices','Weekends only, 10AM to 4PM',NULL,'installation');
INSERT INTO Services VALUES(4,'Regular maintenance checks for devices','Monday to Saturday, 9AM to 5PM',NULL,'maintenance');
INSERT INTO Services VALUES(5,'Fixes for electronic devices including phones, laptops, and tablets','Monday to Friday, 9AM to 6PM',NULL,'repair_Lux');
INSERT INTO Services VALUES(6,'Setup and configuration of home and office devices','Weekends only, 10AM to 4PM',NULL,'installation_at_site');
INSERT INTO Services VALUES(7,'Regular maintenance checks for devices','Monday to Saturday, 9AM to 5PM',NULL,'O&M');
INSERT INTO Services VALUES(8,'7 days/week 24h/day','on_site help, Trouble repporting',NULL,'Customer Support');
INSERT INTO Services VALUES(9,'remote uppgrade','on_site help, 1AM to 6AM',NULL,'SW uppgrade');
CREATE TABLE Test_ChatMessages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Unique ID for each message
    user_id INTEGER NOT NULL,  -- User ID associated with the message
    session_id INTEGER NOT NULL,  -- Session ID associated with the message
    message TEXT NOT NULL,  -- The chat message text
    timestamp DATETIME NOT NULL,  -- Timestamp of the message
    additional_info TEXT,  -- Optional additional information, 500 chars
    FOREIGN KEY (user_id) REFERENCES User(id),  -- Ensure user exists
    FOREIGN KEY (session_id) REFERENCES ChatSessionAnalysis(id)  -- Ensure session exists
);
CREATE TABLE alembic_version (
	version_num VARCHAR(32) NOT NULL, 
	CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);
DELETE FROM sqlite_sequence;
INSERT INTO sqlite_sequence VALUES('Delivery',5);
COMMIT;
