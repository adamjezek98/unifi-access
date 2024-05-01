class UnifiAccessDoor():
    def __init__(self,
                 ua_controller,
                 uuid,
                 name,
                 full_name,
                 floor_id,
                 door_position_status,
                 door_lock_relay_status,
                 type,
                 is_bind_hub):
        self.ua_controller = ua_controller
        self.uuid = uuid
        self.name = name
        self.full_name = full_name
        self.floor_id = floor_id
        self.door_position_status = door_position_status
        self.door_lock_relay_status = door_lock_relay_status
        self.type = type
        self.is_bind_hub = is_bind_hub

    def __str__(self):
        return self.full_name

    def __repr__(self):
        return f"<UnifiAccessDoor {self.full_name} {self.uuid}>"

    def unlock(self):
        return self.ua_controller.unlock_door(self.uuid)
