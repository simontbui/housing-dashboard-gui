-----
To initiate your database locally, you will need to create a database in PostgreSQL/PGAdmin4. You must name your database "Dashboard". Proceed by using either the GUI's or the PSQL command line's database Restore function using the db-dump.sql file from the DataBase_Scripts directory. The utils.py file has information pertaining to the DB user, password, and name. Ensure that these values matches your database user.

Default username for Database in python: admin

Default Password for Database in python: password

Default name for Database in PostgreSQL: Dashboard

-----

To run this locally, ensure you have the Pandas, Pandastable, Tkinter, and Python >= 3.9. Initialize the GUI by executing main.py.

----

This project was a group project of 5 for a database class in my graduate studies. My responsibilities involved:
* Designing the database schemas and constraints
* Writing the SQL queries for the reports 
* Design and implementation of all UI views in the Reports directory
* Writing a custom class that inherits from the publically available pandastable; some method overwriting to make the functionality more compatible with the project's use case.
