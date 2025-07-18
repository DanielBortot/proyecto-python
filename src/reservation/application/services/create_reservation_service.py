from datetime import date, datetime, timedelta
from src.auth.domain.value_objects.user_id_vo import UserIdVo
from src.common.application import IService
from src.common.application.id_generator.id_generator import IIdGenerator
from src.common.utils import Result
from src.menu.domain.value_objects.dish_id_vo import DishIdVo
from src.reservation.application.dtos.request.create_reservation_request_dto import CreateReservationRequest
from src.reservation.application.dtos.response.create_reservation_response_dto import CreateReservationResponse
from src.reservation.application.exceptions.active_reservation_conflict_exception import ActiveReservationConflictException
from src.reservation.application.exceptions.pre_order_limit_exceeded_exception import PreorderLimitExceededException
from src.reservation.application.exceptions.reservation_duration_exceeded_exception import ReservationDurationExceededException
from src.reservation.application.exceptions.restaurant_not_found_exception import RestaurantNotFoundException
from src.reservation.application.exceptions.table_not_available_exception import TableNotAvailableException
from src.reservation.application.repositories.command.reservation_command_repository import IReservationCommandRepository
from src.reservation.application.repositories.query.reservation_query_repository import IReservationQueryRepository
from src.reservation.domain.aggregate.reservation import Reservation
from src.reservation.domain.value_objects.reservation_date_end_vo import ReservationDateEndVo
from src.reservation.domain.value_objects.reservation_date_start_vo import ReservationDateStartVo
from src.reservation.domain.value_objects.reservation_date_vo import ReservationDateVo
from src.reservation.domain.value_objects.reservation_id_vo import ReservationIdVo
from src.reservation.domain.value_objects.reservation_status_vo import ReservationStatusVo
from src.restaurant.application.repositories.query.restaurant_query_repository import IRestaurantQueryRepository
from src.restaurant.domain.entities.value_objects.table_number_id_vo import TableNumberId
from src.restaurant.domain.value_objects.restaurant_id_vo import RestaurantIdVo
from src.menu.application.repositories.query.menu_query_repository import MenuQueryRepository
from src.common.application import ApplicationException

class CreateReservationService(IService[CreateReservationRequest, CreateReservationResponse]):

    def __init__(
        self,    
        query_reser: IReservationQueryRepository, 
        command_reser: IReservationCommandRepository,
        query_restau: IRestaurantQueryRepository,
        id_generator: IIdGenerator,
        menu_repo: MenuQueryRepository
        ):
        super().__init__()
        self.query_repository = query_reser
        self.command_repository = command_reser
        self.id_generator = id_generator
        self.query_restau = query_restau
        self.menu_repo = menu_repo
        
    async def execute(self, value: CreateReservationRequest) -> Result[CreateReservationResponse]:
        
        date_base = date.today()
        start_dt = datetime.combine(date_base, value.date_start)
        end_dt = datetime.combine(date_base, value.date_end)
        
        print(f"end_dt - start_dt :{end_dt - start_dt }")

        
        print(f"end_dt - start_dt > timedelta(hours=4):{end_dt - start_dt > timedelta(hours=4)}")

        # Validamos si la diferencia es mayor a 4 horas
        if end_dt - start_dt > timedelta(hours=4):
            return Result.fail(ReservationDurationExceededException())
        
        # MESA DISPONIBLE. No pueden haber mas de dos reservas activas para la misma mesa en el mismo horario
        findTable = await self.query_repository.exists_by_table(
            table_id=value.table_number_id,
            date_start=value.date_start,
            date_end=value.date_end,
            reservation_date=value.reservation_date,
            restaurant_id = value.restaurant_id
        )
        
        if (findTable.is_success != True):
            raise findTable.error
        
        if (findTable.value == True):
            return Result.fail(TableNotAvailableException())
        
        # Cliente reserva activa en el mismo horario, incluso si son en diferentes restaurantes
        findReser = await self.query_repository.exists_by_date_client(
            date_start= value.date_start, 
            date_end= value.date_end, 
            reservation_date= value.reservation_date, 
            client_id= value.client_id
        )
        if (findReser.value == True ):
            return Result.fail(ActiveReservationConflictException())
        
        # Horario de reserva debe estar dentro del horario de apertura, cierre del restarurante
        restau = await self.query_restau.get_by_id(
            value.restaurant_id
        )
        
        if (restau.is_success == False):
            return Result.fail(RestaurantNotFoundException())
        
        close_time = restau.value.closing_time
        open_time = restau.value.opening_time

        start_rt = datetime.combine(date_base, close_time.closing_time)
        end_rt = datetime.combine(date_base, open_time.opening_time)
        
        # Validamos si la diferencia es mayor a 4 horas
        #if start_rt < start_dt or end_rt < end_dt:
        #    raise Exception("Horario de reserva fuera del horario de trabajo del restaurante")
        
        # No pueden haber mas de cinco platos reservados
        if ( len(value.dish_id) > 5 ):
            return Result.fail(PreorderLimitExceededException())
        
        # Los platos deben pertenecer al menu del restaurante de la mesa reservada
        #menu = await self.menu_repo.find_by_restaurant_id(restaurant_id=RestaurantIdVo(value.restaurant_id))
        #if (menu==None):
        #    raise Exception("Restaurant no posee menu registrado")
        
        # Proceso
        id = self.id_generator.generate_id()
        
        listId = []
        for i in value.dish_id:
            listId.append( DishIdVo(i) )

        menu = await self.menu_repo.find_by_restaurant_id(RestaurantIdVo(value.restaurant_id))

        if not menu:
            return Result.fail(ApplicationException("Menu not found"))
        
        listDishesMenuId = [d.id.value for d in menu.dishes]
        listDishesInputId = [d for d in value.dish_id]

        if set(listDishesInputId).issubset(set(listDishesMenuId)) == False:
            return Result.fail(ApplicationException("One or more dishes entered are not part of the menu"))
            
        reservation = Reservation(
                client_id=UserIdVo(value.client_id),
                id=ReservationIdVo(id),
                date_end=ReservationDateEndVo(value.date_end),
                date_start=ReservationDateStartVo(value.date_start),
                reservation_date=ReservationDateVo(value.reservation_date),
                status=ReservationStatusVo("pendiente"),
                table_number_id=TableNumberId(value.table_number_id),
                restaurant_id=RestaurantIdVo(value.restaurant_id),
                dish=listId
            )
        
        save_result=await self.command_repository.save(
            reservation
        )

        if save_result.is_error:
            return Result.fail(save_result.error)
        
        response = CreateReservationResponse.from_domain(r=reservation)
        return Result.success(response)

