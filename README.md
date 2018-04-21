# item-catalog-project
This application is a `Catalog Application` that allows users to catalog items based on categories. The application demonstrates: `API endpoints`, `CRUD` operations on the database via `SQLAlchemy`, `local authentication/authorization` via `ItsDangerous` and `PassLib`, and `third party authentication/authorization` via `Facebook's Graph API`. Additionally, `Bootstrap` is used for the styling of the application. 

For testing purposes the `catalog` database is populated with `video game` data. This data consists of `video game categories` as the `categories` and `video games` as the `items` themselves.  

## Getting Started
These instructions will get you a copy of the project on your local machine for development and/or testing purposes.

### Prerequisites
To use the `VirtualBox` virtual machine (VM) the user will require [VirtualBox 5.1.34](https://www.virtualbox.org/wiki/Downloads)
or higher and [Vagrant 1.9.2](https://www.vagrantup.com/downloads.html) or higher . 

To run the python script the user will require [Python 2.7.14](https://www.python.org/downloads/) or higher.

To view the webpage correctly an internet connection is required. 

### Installing
To get a copy of the project to work on locally, the user can either `download the zip` or `clone the repository`.

### Initial Setup
In order for the python script to run correctly, the `catalog` database must be created. To create the database:
1) Open Terminal/Powershell.
2) Using the `cd` command, navigate to the directory where the project is located.
3) Start the VM by using the `vagrant up` command.
4) Connect to the VM using the `vagrant ssh` command.
5) Navigate to the directory in the VM where the `games.py` script is located using the command `cd`.
6) Create the database using the command `python games.py`

## Run the Project
In order to run the project:
1) Open Terminal/Powershell.
2) Using the `cd` command, navigate to the directory where the project is located.
3) Start the VM by using the command `vagrant up`.
4) Connect to the VM using the command `vagrant ssh`.
5) Navigate to the directory in the VM where the python script is located using the command `cd`.
6) Run the python script using the command `python application.py`.
7) Using a web browser navigate to the catalog web page at `http://localhost:5000/catalog/`. 

## Built with
* `Python 2.7.14`
* `Flask 0.9`
* `SQLAclchemy 1.2.5`
* `ItsDangerous 0.20`
* `PassLib 1.7.1`
* `Bootstrap 4.1.0`

## Authors
* Ricardo Rivera