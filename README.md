# Technical Helpdesk
Hosted on http://technicalhelpdesk.herokuapp.com/ <br/>
> This project is totally built on Desktop View, so rendering on responsive screen will generate random positioning of elements.

## Overview
“Technical Helpdesk” aims to tackle issues faced by service centres that do not have a dedicated management system. Our solution aims to enable the client to couple 
the entire organization with itself and the organization to the end user i.e. clients of the organization.

On the management side,
* The superuser is placed at the top of the hierarchy. His job is to authorize each and every employee to work for the organization. He can also see the entire database of the 
organization. There may be one or multiple admin under him in the hierarchy.
* The admin is the leader of his respective department. His job is to allocate technician to manager and take care if the operations are carried out properly in his department.
He can have one or more manager under him in the hierarchy.
* The manager does the task of allocating tickets to technician. He can view which technicians are assigned to him and how many tickets are allotted to him thus providing 
judgement on allocation of tickets. He can also view which tickets are under which technician and since when are they in inventory. He can have one or more technician under 
him in the hierarchy.
* The technician views the tickets assigned to him and and picks up the inventory and keeps updating the work progress on the site in realtime. Once the job is done, he updates 
the status of the respective ticket and the executive is thus informed who in turn makes the necessary arrangements for the product pickup.
* The executive is an exception to the organizational hierarchy. He is assigned by the superuser and he forms a separate department of his own. His job is to make arrangements 
for the pickup incase the customer has demanded a pickup. Once the product reaches, the executive assesses the product and makes an entry to the inventory which is linked to 
the respective ticket.

On the other hand, the customer can initiate a ticket and choose if he wants to avail pickup or seldom deliver. Once the item is accepted then the customer keeps receiving 
live status. He also gets the option to cancel the ticket while it is still in its processing state. Customer can also go to “contact” page to provide feedback if any.

In addition to the aforementioned, all users except superuser, can modify their profile and add their profile pictures if they so desire.

## Project
The project is built with
* Flask Framework
* HTML CSS JS
* MySQL

## Setup

The first thing to do is to clone the repository:

```sh
$ git clone https://github.com/Jaspreet8843/mysite.git
$ cd mysite
```

Create a virtual environment to install dependencies in and activate it:

```sh
$ py -m virtualenv myenv
$ myenv\Scripts\activate
```

Then install the dependencies:

```sh
(myenv)$ pip install -r requirements.txt
```
Note the `(myenv)` in front of the prompt. This indicates that this terminal
session operates in a virtual environment set up by `virtualenv`.

Once `pip` has finished downloading the dependencies:
```sh
(myenv)$ py site12.py
```
And navigate to `http://127.0.0.1:5000/`.

## Walkthrough
The project has the user side and admin side. The user side allows 
1. Book tickets

The admin side allows
1. View tickets

## Snapshots
Column 1 | Column 2
------------ | -------------
Login | Homepage
