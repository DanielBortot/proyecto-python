from fastapi import FastAPI
from src.common.infrastructure import CorsConfig
from src.common.infrastructure import PostgresDatabase
from contextlib import asynccontextmanager
from src.auth.infrastructure.controllers.register.user_register import UserRegisterController
from src.auth.infrastructure.controllers.login.user_login import UserLoginController
from src.auth.infrastructure.controllers.update.user_update import UserUpdateController
from src.dashboard.infraestructure.controllers.get_occupacy_percentage.get_occupacy_percentage import GetOccupancyPercentageController
from src.dashboard.infraestructure.controllers.get_reservation_count.get_reservation_count import GetReservationCountController
from src.dashboard.infraestructure.controllers.get_top_preordered_dishses.get_top_preordered_dishses import GetTopPreorderedDishesController
from src.reservation.infraestructure.controllers.admin_cancel_reservation import AdminCancelReservationController
from src.reservation.infraestructure.controllers.cancel_reservation import CancelReservationController
from src.reservation.infraestructure.controllers.create_reservation import CreateReservationController
from src.reservation.infraestructure.controllers.find_active_reservation_by_client import FindActiveReservationController
from src.reservation.infraestructure.controllers.find_reservation import FindReservationController
from src.restaurant.infraestructure.controllers.create_restaurant.create_restaurant import CreateRestaurantController
from src.restaurant.infraestructure.controllers.create_table.create_table import CreateTableController
from src.restaurant.infraestructure.controllers.delete_restaurant_by_id.delete_restaurant_by_id import DeleteRestaurantByIdController
from src.restaurant.infraestructure.controllers.delete_table_by_id.delete_table_by_id import DeleteTableByIdController
from src.restaurant.infraestructure.controllers.get_all_restaurant.get_all_restaurant import GetAllRestaurantController
import faulthandler
from src.restaurant.infraestructure.controllers.get_restaurant_by_id.get_restaurant_by_id import GetRestaurantByIdController
from src.restaurant.infraestructure.controllers.update_restaurant.update_restaurant import UpdateRestaurantController
from src.restaurant.infraestructure.controllers.update_table.update_restaurant import UpdateTableController
from src.menu.infrastructure.controllers.add_dish_to_menu.add_dish_to_menu import AddDishToMenuController
from src.menu.infrastructure.controllers.get_dishes_by_restaurant.get_dishes_by_restaurant import GetDishesByRestaurantController
from src.menu.infrastructure.controllers.remove_dish_from_menu.remove_dish_from_menu import RemoveDishFromMenuController
from src.menu.infrastructure.controllers.update_dish_in_menu.update_dish_in_menu import UpdateDishInMenuController

faulthandler.enable()           # colócalo en tu módulo principal, p.ej. src/main.py


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Esta llamada asegura que el _engine y _async_session_factory se inicialicen
    PostgresDatabase()
    # Para llamar a create_db_and_tables, necesitamos una instancia.
    # Puede ser la misma que la de arriba, o una nueva (que usará el motor ya inicializado).
    initial_db_instance = PostgresDatabase()
    await initial_db_instance.create_db_and_tables()
    print("Base de datos y tablas creadas.")
    
    yield
    if PostgresDatabase._engine:
        await PostgresDatabase._engine.dispose()
        print("Motor de base de datos dispuesto en el shutdown de la app.")

app = FastAPI(lifespan=lifespan)

CorsConfig.setup_cors(app)

@app.get("/")
def root():
    return {"Hello": "World"}

# Auth Controllers
UserRegisterController(app)
UserUpdateController(app)
UserLoginController(app)

# Restaurants Controllers
CreateRestaurantController(app)
GetAllRestaurantController(app)

# Reservation Controllers
CreateReservationController(app)
CancelReservationController(app)
FindActiveReservationController(app)
FindReservationController(app)
AdminCancelReservationController(app)

# Restaurnat
GetRestaurantByIdController(app)
DeleteRestaurantByIdController(app)

# Table Controllers
DeleteTableByIdController(app)
CreateTableController(app)
UpdateRestaurantController(app)
UpdateTableController(app)

# Menu Controllers
AddDishToMenuController(app)
GetDishesByRestaurantController(app)
RemoveDishFromMenuController(app)
UpdateDishInMenuController(app)

# Dashboard Controllers
GetOccupancyPercentageController(app)
GetReservationCountController(app)
GetTopPreorderedDishesController(app)
