# Weather Service gRPC Example

This is a complete gRPC example in Python that implements a weather service with various RPC patterns.

## Features

- **Unary RPC**: Get current weather for a location
- **Server Streaming RPC**: Subscribe to weather updates
- **User Reporting**: Report weather conditions from clients
- **Command-line Interface**: Advanced client with CLI options

## File Structure

- `weather_service.proto` - Protocol Buffer definition
- `server.py` - gRPC server implementation
- `client.py` - Basic client implementation
- `advanced_client.py` - Advanced client with command-line interface

## Setup Instructions

1. **Install the required packages**:

```bash
pip install grpcio grpcio-tools
```

2. **Generate the gRPC code**:

```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. weather_service.proto
```

This will generate two files:
- `weather_service_pb2.py` - Contains message classes
- `weather_service_pb2_grpc.py` - Contains server and client classes

## Running the Example

1. **Start the server**:

```bash
python server.py
```

2. **Run the basic client in another terminal**:

```bash
python client.py
```

3. **Or use the advanced client with command-line options**:

```bash
# Get current weather
python advanced_client.py get --city "London" --country "UK"

# Subscribe to weather updates
python advanced_client.py subscribe --city "Tokyo" --country "JP"

# Report weather conditions
python advanced_client.py report --city "Berlin" --country "DE" \
  --temperature 22.5 --condition "Partly Cloudy" \
  --humidity 65.0 --wind_speed 12.0
```

## How It Works

- The server maintains a simulated database of weather conditions
- The client can request current weather for a location
- The client can subscribe to a stream of weather updates
- The client can report weather conditions which update the server's database
- Weather conditions change over time with some randomness for demo purposes

## Examples of gRPC Patterns

1. **Unary RPC (Request/Response)**: 
   - `GetWeather(LocationRequest) returns (WeatherResponse)`

2. **Server Streaming RPC**:
   - `SubscribeWeather(LocationRequest) returns (stream WeatherResponse)`

3. **Simple Data Modification**:
   - `ReportWeather(WeatherReport) returns (ReportResponse)`

## Extending the Example

You could extend this example with:

- **Client Streaming RPC**: Allow clients to send a stream of weather reports
- **Bidirectional Streaming RPC**: Create a chat system between weather observers
- **Authentication**: Add API keys or other authentication methods
- **Error Handling**: Implement more robust error handling and recovery
- **Persistent Storage**: Replace the in-memory database with a real database