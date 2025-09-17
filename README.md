# Airport API

## Features

- User registration, authentication (JWT), profile management
- CRUD for AirplaneType, Airplane, Country, City, Airport, Route, CrewMember, Flight, Order
- Advanced filtering, searching, and ordering for all major entities
- Permissions: admin/user/anonymous access control for all endpoints
- Ticket and Order validation (unique, valid seat/row, no duplicates)
- Browsable API with DRF interface

## Getting Started


## Local Setup (Docker Compose Only)

1. **Clone the repository:**
	```sh
	git clone <your-repo-url>
	cd airport-api
	```
2. **Start the project with Docker Compose:**
	```sh
	docker-compose up --build
	```
3. **Create superuser (for admin access):**
	```sh
	docker-compose exec web python manage.py createsuperuser
	```
4. **Access the Browsable API:**
	- Visit [http://localhost:8000/api/](http://localhost:8000/api/) in your browser.
	- Register a user at `/api/accounts/register/` or login via JWT at `/api/accounts/token/`.
	- Use `/api/accounts/me/` for profile management.
	- All other endpoints are available under `/api/airport/`.


## API Authentication

- Obtain JWT token at `/api/accounts/token/` (POST username & password)
- Use token in `Authorization: Bearer <token>` header for authenticated requests

---

## API Endpoints & Features

- **User (accounts):** Registration, JWT authentication, profile view/update/delete
- **AirplaneType:** CRUD, search by name
- **Airplane:** CRUD, search by name/type, ordering by capacity
- **Country:** CRUD, search and ordering by name
- **City:** CRUD, search by name/country, filter by country, ordering
- **Airport:** CRUD, search by name/city/country, filter by city/country, ordering
- **Route:** CRUD, search by source/destination/city/country, filter, ordering
- **CrewMember:** CRUD, search and ordering by name
- **Flight:** CRUD, search by route/airplane/city/country, filter by time/source/destination, ordering
- **Order:** List, create, retrieve, delete; ticket validation (unique, valid seat/row, no duplicates)
- **Permissions:** Admin can manage all, users have restricted access, anonymous users can only view public endpoints
- **Filtering, searching, ordering:** Supported for all major entities
- **Browsable API:** All endpoints available via DRF web interface
