
class CancelReservationRequest:
    def __init__(self, client_id: str, reservation_id: str):
        self.client_id = client_id
        self.reservation_id = reservation_id
        