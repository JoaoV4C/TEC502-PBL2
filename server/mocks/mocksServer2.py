from models.flight import Flight
from models.airport import Airport

airports = [
    ['São Luís', 'SLZ', ['Recife', 'Aracaju']],
    ['Teresina', 'SBTE',['João Pessoa', 'Maceió']],
    ['Fortaleza', 'FOR', ['Salvador', 'Aracaju']],
    ['Natal', 'NAT', ['Maceió', 'São Luís']],
    ['João Pessoa', 'JPA', ['Teresina', 'Fortaleza']],
    ['Recife', 'REC', ['Salvador', 'São Luís']],
    ['Maceió', 'MCZ', ['Teresina', 'São Luís']],
    ['Aracaju', 'AJU', ['Fortaleza', 'João Pessoa']],
    ['Salvador', 'SSA', ['Natal', 'Teresina']]
]

def create_flights(airport_objects):
    flights = []
    for origin in airport_objects:
        for destination in origin.connections:
            destination_obj = next((airport for airport in airport_objects if airport.name == destination), None)
            if destination_obj:
                flight = Flight(origin.name, destination_obj.name)
                flights.append(flight)
    return flights

def create_airports():
    airport_objects = []
    for airport in airports:
        name = airport[0]
        code = airport[1]
        connections = airport[2]
        airport_obj = Airport(name, code, connections)
        airport_objects.append(airport_obj)
    return airport_objects