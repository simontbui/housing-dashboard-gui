-- Tables
DROP TABLE IF EXISTS Appliance, AirHandler,WaterHeater,AirConditioner,HeatPump,Heater,PermanentPowerGeneration,PowerGeneration,PublicUtilities,HouseHold, PostalCode, Manufacturer CASCADE;

CREATE TABLE PostalCode (
code varchar(20) NOT NULL,
city varchar(50) NOT NULL,
state varchar(2) NOT NULL,
longitude float NOT NULL,
latitude float NOT NULL,

PRIMARY KEY(code),
UNIQUE(code)
);

CREATE TABLE HouseHold (
email varchar(50) NOT NULL,
household_type varchar(50) NOT NULL,
square_footage int NOT NULL,
heating_setting float NULL,
cooling_setting float NULL,
code varchar(20) NOT NULL,

PRIMARY KEY (email),
UNIQUE(email),
FOREIGN KEY (code) REFERENCES PostalCode(code) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE PublicUtilities (
email varchar(50) NOT NULL,
public_utility varchar(50) NULL,

Primary Key (email, public_utility),
FOREIGN KEY (email) REFERENCES HouseHold (email) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE Manufacturer (
name varchar(50) NOT NULL,
PRIMARY KEY(name)
);

CREATE TABLE Appliance (
email varchar(50) NOT NULL,
entry_order_number int NOT NULL,

PRIMARY KEY (email, entry_order_number),
FOREIGN KEY (email) REFERENCES HouseHold (email) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE AirHandler (
email varchar(50) NOT NULL,
entry_order_number int NOT NULL,

btu_rating int NOT NULL,
model_name varchar(50) NULL,
manufacturer varchar(256) NOT NULL,

PRIMARY KEY (email, entry_order_number),
FOREIGN KEY (email) REFERENCES HouseHold (email) ON DELETE CASCADE ON UPDATE CASCADE,
FOREIGN KEY (manufacturer) REFERENCES Manufacturer(name) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE WaterHeater (
email varchar(50) NOT NULL,
entry_order_number int NOT NULL,

capacity float NOT NULL,
temperature_setting int NULL,
energy_source varchar(50) NOT NULL,
	
btu_rating int NOT NULL,
model_name varchar(50) NULL,
manufacturer varchar(50) NOT NULL,

PRIMARY KEY(email, entry_order_number),
FOREIGN KEY (email) REFERENCES HouseHold (email) ON DELETE CASCADE ON UPDATE CASCADE,
FOREIGN KEY (manufacturer) REFERENCES Manufacturer(name) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE AirConditioner (
email varchar(50) NOT NULL,
entry_order_number int NOT NULL,
eer float NOT NULL,

PRIMARY KEY (email, entry_order_number),
FOREIGN KEY (email) REFERENCES HouseHold (email) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE HeatPump (
email varchar(50) NOT NULL,
entry_order_number int NOT NULL,
seer float NOT NULL,
hspf float NOT NULL,

PRIMARY KEY (email, entry_order_number),
FOREIGN KEY (email) REFERENCES HouseHold (email) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Heater (
email varchar(50) NOT NULL,
entry_order_number int NOT NULL,

energy_source varchar(50) NOT NULL,

UNIQUE(email, entry_order_number),
PRIMARY KEY (email, entry_order_number),
FOREIGN KEY (email) REFERENCES HouseHold (email) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE PermanentPowerGeneration (
email varchar(50) NOT NULL,
entry_order_number SERIAL,
PRIMARY KEY (email, entry_order_number),
UNIQUE (email, entry_order_number),
FOREIGN KEY (email) REFERENCES HouseHold (email) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE PowerGeneration (
power_generation_type varchar(16) NULL,
storage_capacity int NULL,
avg_kwh_generated int NULL,
email varchar(50) NOT NULL,
entry_order_number SERIAL,

PRIMARY KEY (email, entry_order_number),
FOREIGN KEY (email) REFERENCES HouseHold (email) ON DELETE CASCADE ON UPDATE CASCADE
);