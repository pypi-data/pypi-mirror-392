def typename_to_port(type_name: str) -> str:
    event_types = {"event"}
    data_types = {"int", "integer", "real", "float", "double", "string"}
    mixed_types = {"event_data", "event data"}

    if type_name in event_types:
        return "event"
    if type_name in data_types:
        return "data"
    if type_name in mixed_types:
        return "event data"
    return "data"
