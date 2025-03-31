import datetime
import random
import time
import uuid
from concurrent import futures

import grpc

import weather_service_pb2
import weather_service_pb2_grpc

# Simulated weather database
weather_db = {
    "New York:US": {"temperature_celsius": 22.5, "condition": "Partly Cloudy", "humidity": 65.0, "wind_speed": 10.2},
    "London:UK": {"temperature_celsius": 18.0, "condition": "Rainy", "humidity": 80.0, "wind_speed": 15.5},
    "Tokyo:JP": {"temperature_celsius": 26.0, "condition": "Clear", "humidity": 70.0, "wind_speed": 8.0},
    "Sydney:AU": {"temperature_celsius": 28.0, "condition": "Sunny", "humidity": 55.0, "wind_speed": 12.3},
}

# Weather reports submitted by users
weather_reports = []

# Weather condition options for simulation
weather_conditions = ["Sunny", "Partly Cloudy", "Cloudy", "Rainy", "Thunderstorm", "Snowy", "Foggy", "Windy"]


class WeatherServiceServicer(weather_service_pb2_grpc.WeatherServiceServicer):
    def GetWeather(self, request, context):
        location_key = f"{request.city}:{request.country}"

        if location_key not in weather_db:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Weather data for {request.city}, {request.country} not found")
            return weather_service_pb2.WeatherResponse()

        weather_data = weather_db[location_key]

        return weather_service_pb2.WeatherResponse(
            city=request.city,
            country=request.country,
            temperature_celsius=weather_data["temperature_celsius"],
            condition=weather_data["condition"],
            humidity=weather_data["humidity"],
            wind_speed=weather_data["wind_speed"],
            timestamp=datetime.datetime.now().isoformat(),
        )

    def SubscribeWeather(self, request, context):
        location_key = f"{request.city}:{request.country}"

        if location_key not in weather_db:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Weather data for {request.city}, {request.country} not found")
            return

        # Simulate weather changes every 2 seconds
        for _ in range(10):  # Send 10 updates
            if context.is_active():
                # Get current weather and slightly modify it to simulate changes
                weather_data = weather_db[location_key]

                # Randomly update temperature within a small range
                temp_change = random.uniform(-1.5, 1.5)
                new_temp = weather_data["temperature_celsius"] + temp_change

                # Randomly update condition sometimes
                if random.random() < 0.3:  # 30% chance of condition change
                    new_condition = random.choice(weather_conditions)
                else:
                    new_condition = weather_data["condition"]

                # Update humidity
                humidity_change = random.uniform(-5, 5)
                new_humidity = min(max(weather_data["humidity"] + humidity_change, 0), 100)

                # Update wind speed
                wind_change = random.uniform(-2, 2)
                new_wind = max(weather_data["wind_speed"] + wind_change, 0)

                # Update the database
                weather_db[location_key] = {"temperature_celsius": new_temp, "condition": new_condition, "humidity": new_humidity, "wind_speed": new_wind}

                # Send the updated weather data
                yield weather_service_pb2.WeatherResponse(city=request.city, country=request.country, temperature_celsius=new_temp, condition=new_condition, humidity=new_humidity, wind_speed=new_wind, timestamp=datetime.datetime.now().isoformat())

                time.sleep(2)  # Wait for 2 seconds before the next update
            else:
                return  # Client disconnected

    def ReportWeather(self, request, context):
        location_key = f"{request.city}:{request.country}"

        # Create a new report
        report_id = str(uuid.uuid4())
        new_report = {
            "report_id": report_id,
            "city": request.city,
            "country": request.country,
            "temperature_celsius": request.temperature_celsius,
            "condition": request.condition,
            "humidity": request.humidity,
            "wind_speed": request.wind_speed,
            "reporter_id": request.reporter_id,
            "timestamp": datetime.datetime.now().isoformat(),
        }

        # Add to reports
        weather_reports.append(new_report)

        # Update the weather database with the reported data
        # In a real implementation, we might want to validate or average multiple reports
        weather_db[location_key] = {"temperature_celsius": request.temperature_celsius, "condition": request.condition, "humidity": request.humidity, "wind_speed": request.wind_speed}

        return weather_service_pb2.ReportResponse(success=True, report_id=report_id, message=f"Weather report for {request.city}, {request.country} received. Thank you!")


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    weather_service_pb2_grpc.add_WeatherServiceServicer_to_server(WeatherServiceServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("Weather Service server started on port 50051...")
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == "__main__":
    serve()
