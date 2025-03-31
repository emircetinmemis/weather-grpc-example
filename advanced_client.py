import argparse
import time
import uuid

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


def create_client_stub():
    channel = grpc.insecure_channel("localhost:50051")
    return weather_service_pb2_grpc.WeatherServiceStub(channel), channel


def get_weather_command(args):
    stub, channel = create_client_stub()
    try:
        get_current_weather(stub, args.city, args.country)
    finally:
        channel.close()


def subscribe_command(args):
    stub, channel = create_client_stub()
    try:
        subscribe_to_weather_updates(stub, args.city, args.country)
    finally:
        channel.close()


def report_command(args):
    stub, channel = create_client_stub()
    try:
        report_weather(stub, args.city, args.country, args.temperature, args.condition, args.humidity, args.wind_speed)
    finally:
        channel.close()


def main():
    parser = argparse.ArgumentParser(description="Weather Service gRPC Client")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Get weather command
    get_parser = subparsers.add_parser("get", help="Get current weather")
    get_parser.add_argument("--city", required=True, help="City name")
    get_parser.add_argument("--country", required=True, help="Country code")
    get_parser.set_defaults(func=get_weather_command)

    # Subscribe command
    sub_parser = subparsers.add_parser("subscribe", help="Subscribe to weather updates")
    sub_parser.add_argument("--city", required=True, help="City name")
    sub_parser.add_argument("--country", required=True, help="Country code")
    sub_parser.set_defaults(func=subscribe_command)

    # Report weather command
    report_parser = subparsers.add_parser("report", help="Report weather conditions")
    report_parser.add_argument("--city", required=True, help="City name")
    report_parser.add_argument("--country", required=True, help="Country code")
    report_parser.add_argument("--temperature", type=float, required=True, help="Temperature in Celsius")
    report_parser.add_argument("--condition", required=True, choices=["Sunny", "Partly Cloudy", "Cloudy", "Rainy", "Thunderstorm", "Snowy", "Foggy", "Windy"], help="Weather condition")
    report_parser.add_argument("--humidity", type=float, required=True, help="Humidity percentage")
    report_parser.add_argument("--wind_speed", type=float, required=True, help="Wind speed in km/h")
    report_parser.set_defaults(func=report_command)

    args = parser.parse_args()
    if args.command:
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
