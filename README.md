
# Gym Management App



* This is a simple gym management system built using Django REST framework, that manages a gym.

### Installation and Setup

## Requirements

* Python 3.9 Docker

* Clone the repository: git clone  ![alt text] https://github.com/okiemute04/Gym_management_system

* cd gym-management

## Install the project dependencies:

* pip install -r requirements.txt

* Build and run the Docker container:

* docker-compose up -d --build

## Running the tests:

* docker-compose run web python manage.py test

or

* python manage.py test

### Endpoints and Parameters:


### InvoiceViewSet

GET /api/invoices/ : Returns a list of all invoices.
POST /api/invoices/ : Creates a new invoice.
GET /api/invoices/{id}/ : Returns a specific invoice by ID.
PUT /api/invoices/{id}/ : Updates a specific invoice by ID.
DELETE /api/invoices/{id}/ : Deletes a specific invoice by ID.
POST /api/invoices/{id}/add_line/ : Adds a new invoice line item to the specified invoice.

## Parameters:

id: The ID of the invoice (integer).

### MembershipViewSet

GET /api/memberships/ : Returns a list of all memberships.
POST /api/memberships/ : Creates a new membership.
GET /api/memberships/{id}/ : Returns a specific membership by ID.
PUT /api/memberships/{id}/ : Updates a specific membership by ID.
DELETE /api/memberships/{id}/ : Deletes a specific membership by ID.

## Parameters:

id: The ID of the membership (integer).
start_date: Filters the list of memberships to those with a start date greater than or equal to the specified date (ISO 8601 date string).

### CheckinViewSet

GET /api/checkins/ : Returns a list of all check-ins.
POST /api/checkins/ : Creates a new check-in.
GET /api/checkins/{id}/ : Returns a specific check-in by ID.
PUT /api/checkins/{id}/ : Updates a specific check-in by ID.
DELETE /api/checkins/{id}/ : Deletes a specific check-in by ID.

## Parameters:

id: The ID of the check-in (integer).

### MembershipMiddleware

This middleware intercepts requests to the CheckinViewSet to ensure that memberships are valid before allowing a check-in to be created.

## Parameters:

membership: The ID of the membership associated with the check-in (integer).


#### Code Structure:

* The application is built with the Django framework and follows the Model-View-Controller (MVC) architecture.


### models.py - 
               
* These are the models defined in the Django application.

* Invoice: This model represents an invoice with a date, status, description, and amount. It has a one-to-many relationship with InvoiceLine via related_name='lines'.

* InvoiceLine: This model represents a line item on an invoice with a description and amount. It has a foreign key to Invoice.

* Membership: This model represents a membership with a user, state, credits, start_date, end_date, and amount. It has a foreign key to the User model, and a one-to-many relationship with Checkin via related_name='checkins'.

* Checkin: This model represents a check-in with a user, membership, and timestamp. It has a foreign key to both the User and Membership models.


### serializers.py - 
                     
* It provides endpoints to manage invoices, memberships, and check-ins.

* The Invoice model represents a bill for a user, and each invoice can have multiple InvoiceLine objects, which represent individual line items on the bill. The InvoiceViewSet provides basic CRUD operations for invoices and also has an additional add_line action to add new line items to an invoice.

* The Membership model represents a membership plan for a user, and the MembershipViewSet provides CRUD operations for memberships.

* The Checkin model represents a user checking in to the gym, and the CheckinViewSet provides CRUD operations for check-ins. The perform_create method in the viewset also checks if the user's membership is active, has credits available, and has not expired before allowing the check-in to be created.

* The serializers define how the data in the models is represented in the API. The InvoiceLineSerializer and InvoiceSerializer are used for the Invoice model and its related InvoiceLine objects. The MembershipSerializer is used for the Membership model. The CheckinSerializer is used for displaying check-ins and includes a hidden field for the currently authenticated user. The CheckinCreateSerializer is used for creating new check-ins and includes validation to check if the user's membership is valid before allowing a check-in to be created.


### views.py - 
               
* It defines three viewsets for the Django REST framework: InvoiceViewSet, MembershipViewSet, and CheckinViewSet.

* InvoiceViewSet and MembershipViewSet are fairly straightforward, and simply define the queryset and serializer class to use for their respective models.

* CheckinViewSet is a bit more complicated. It defines the queryset and serializer class as before, but also overrides the get_serializer_class method to return a different serializer class if the action is create. This is useful for using a different serializer for creating objects than for updating or retrieving them.

* The perform_create method is also overridden to add some custom logic when a new Checkin object is created. It first checks if the associated Membership is canceled, has no credits left, or has expired, and returns an error response if any of these conditions are met. Otherwise, it decrements the credits attribute of the Membership, saves it, and then saves the new Checkin object. Finally, it creates a new Invoice object if one does not already exist for today's date, and adds an InvoiceLine object to it for the monthly membership fee.


### middlewares.py - 

* It contains a class MembershipMiddleware that serves as a middleware for a Django application. The middleware performs some checks before allowing access to a view.

* The middleware checks for a POST request to a view named CheckinViewSet.as_view. If the request is a POST request to that view, it retrieves a membership ID from the request data and retrieves the membership from the database.

* It then checks if the membership state is "canceled", and if so, returns a JSON response with a message stating that the membership is canceled and a status code of 400 (bad request). If the membership has no credits available, the middleware returns a JSON response with a message stating that there are no credits available and a status code of 400. If the membership has an end date and the end date is in the past, the middleware returns a JSON response with a message stating that the membership has expired and a status code of 400.

* The purpose of this middleware is to enforce some business rules related to a membership-based system. By checking the state of the membership, available credits, and expiration date, the middleware ensures that only valid memberships are allowed to check in.


### urls.py - 
              

* It defines the URL routing for the Django REST framework.

* It first imports the necessary modules and views, and then creates a new DefaultRouter object. The register method is called on the router for each viewset, with the name of the endpoint as the first argument and the viewset as the second argument.

* The urlpatterns list is defined to include the router's URLs using the include function. This means that any URLs that match the registered endpoints will be handled by the corresponding viewset's methods.


### tests.py - 
                 
* Its a collection of test cases for the gym management system. It includes unit tests for the project's models as well as integration tests for the API endpoints associated with those models.

* The ModelTestCase class sets up instances of the project's models for use in testing. Then, there are individual tests for each of the models that check that their str methods return the expected string.

* The InvoiceViewSetTests, MembershipViewSetTests, and CheckinViewSetTests classes are test cases for the API endpoints associated with each model. Each test sends a request to the API and checks that the response has the expected status code and content.

* These tests ensure that the models are functioning correctly and that the API endpoints return the expected data.


### Dockerfile - 
                  
* This file defines the Docker image for the application. It uses the official Python 3.9 image as the base and copies the application code into the container. It then installs the required Python packages and sets the command to start the Django development server.

### docker-compose.yml -
                      
* This file defines the Docker Compose configuration for the application. It specifies the Docker image to use, the port to expose, and the volumes to mount.
