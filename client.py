import time
import uuid
from datetime import datetime

import grpc

import weather_service_pb2
import weather_service_pb2_grpc


def get_current_weather(stub, city, country):
    print(f"\nGetting current weather for {city}, {country}...")
    try:
        response = stub.GetWeather(weather_service_pb2.LocationRequest(city=city, country=country))

        print(f"Current weather for {response.city}, {response.country}:")
        print(f"  Temperature: {response.temperature_celsius:.1f}°C")
        print(f"  Condition: {response.condition}")
        print(f"  Humidity: {response.humidity:.1f}%")
        print(f"  Wind Speed: {response.wind_speed:.1f} km/h")
        print(f"  Last Updated: {response.timestamp}")
        return response

    except grpc.RpcError as e:
        print(f"RPC error: {e.details()}")
        return None


def subscribe_to_weather_updates(stub, city, country):
    print(f"\nSubscribing to weather updates for {city}, {country}...")
    try:
        request = weather_service_pb2.LocationRequest(city=city, country=country)

        responses = stub.SubscribeWeather(request)

        for response in responses:
            print(f"\nWeather update for {response.city}, {response.country} at {response.timestamp}:")
            print(f"  Temperature: {response.temperature_celsius:.1f}°C")
            print(f"  Condition: {response.condition}")
            print(f"  Humidity: {response.humidity:.1f}%")
            print(f"  Wind Speed: {response.wind_speed:.1f} km/h")

    except grpc.RpcError as e:
        print(f"RPC error: {e.details()}")
        return None


def report_weather(stub, city, country, temperature, condition, humidity, wind_speed):
    print(f"\nReporting weather for {city}, {country}...")
    try:
        reporter_id = str(uuid.uuid4())[:8]  # Generate a random reporter ID

        response = stub.ReportWeather(weather_service_pb2.WeatherReport(city=city, country=country, temperature_celsius=temperature, condition=condition, humidity=humidity, wind_speed=wind_speed, reporter_id=reporter_id))

        if response.success:
            print(f"Weather report submitted successfully!")
            print(f"Report ID: {response.report_id}")
            print(f"Message: {response.message}")
        else:
            print(f"Failed to submit weather report: {response.message}")

        return response

    except grpc.RpcError as e:
        print(f"RPC error: {e.details()}")
        return None


def run():
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = weather_service_pb2_grpc.WeatherServiceStub(channel)

        # Get weather for a few cities
        get_current_weather(stub, "New York", "US")
        get_current_weather(stub, "London", "UK")
        get_current_weather(stub, "Tokyo", "JP")

        # Report a weather condition
        report_weather(stub, "San Francisco", "US", temperature=23.5, condition="Foggy", humidity=75.0, wind_speed=18.2)

        # Get the updated weather for the reported city
        get_current_weather(stub, "San Francisco", "US")

        # Subscribe to weather updates for a city
        print("\nSubscribing to weather updates for London, UK for 20 seconds...")
        subscribe_to_weather_updates(stub, "London", "UK")


if __name__ == "__main__":
    run()
