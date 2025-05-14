class Vehicle:
    def __init__(self, ID, vehicle_type, position_x, position_y):
        self.ID = int(ID)  # Works as an ID
        self.type = str(vehicle_type)  # Car, Van, motorcycle, ...
        self.position = [position_x, position_y]  # Cartesian coordinates [x,y]
        self.fuel = 50  # Measured in litters
        self.velocity = 0  # Velocity in Km/h

    def get_ID(self):
        return self.ID

    def get_type(self):
        return self.type

    def get_position(self):
        return self.position[0], self.position[1]

    def get_fuel(self):
        return self.fuel

    def get_velocity(self):
        return self.velocity

    def set_position(self, position_x, position_y):
        self.position[0] = position_x
        self.position[1] = position_y

    def set_fuel(self, fuel):
        if fuel is None:
            return
        self.fuel = fuel

    def set_velocity(self, velocity):
        if velocity is None:
            return
        self.velocity = velocity

    def __eq__(self, vehicle) -> bool:
        return self.ID == vehicle.ID

    def __hash__(self) -> int:
        return self.ID.__hash__()

    def __str__(self) -> str:
        return super().__str__()
