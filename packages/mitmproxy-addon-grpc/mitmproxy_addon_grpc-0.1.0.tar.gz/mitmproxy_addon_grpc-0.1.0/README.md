

# mitmproxy-addon-grpc

A mitmproxy addon that exports HTTP, TCP, UDP, and DNS flows to a user-implemented gRPC server.

## What is this project?

This project provides a mitmproxy addon that exports HTTP, TCP, UDP, and DNS flows from mitmproxy to a gRPC server that you implement. The addon acts as a bridge, sending flow data to your server in real time using a defined protobuf interface.

## Why is it useful?

- **Centralized Flow Processing**: Offload flow analysis, logging, or modification to an external service written in your language of choice.
- **Automation**: Build automated systems that react to HTTP, TCP, UDP, or DNS traffic in real time.
- **Integration**: Easily integrate mitmproxy with other tools, dashboards, or pipelines via gRPC.

## Installation

1. **Clone the repository**:
   ```sh
   git clone https://github.com/sudorandom/mitmproxy-addon-grpc.git
   cd mitmproxy-addon-grpc
   ```
2. **Install dependencies** (requires Python 3.8+):
   ```sh
   pip install -r requirements.txt
   # or, if using pyproject.toml:
   pip install .
   ```
3. **Install mitmproxy** (if not already installed):
   ```sh
   pip install mitmproxy
   ```


## Usage

1. **Implement your gRPC server** using the protobuf definitions provided in this repo or via buf.build (see below).
2. **Run your gRPC server** and note its address/port.
3. **Run mitmproxy with the addon**:
   ```sh
   mitmproxy -s grpc_addon.py
   ```
4. **Configure the addon** (if needed) to point to your gRPC server.
5. **Start capturing traffic**—the addon will export each HTTP, TCP, UDP, or DNS flow to your gRPC server as it is seen by mitmproxy.


## Configuration

The addon can be configured using mitmproxy's `--set` or `-o` options, or via your mitmproxy config file.

### `grpc_addr`
- **Type:** string
- **Default:** `http://127.0.0.1:50051`
- **Description:** The address of your gRPC server to which flow data will be exported.
- **Example:**
   ```sh
   mitmproxy -s grpc_addon.py --set grpc_addr=http://localhost:6000
   ```

### `grpc_events`
- **Type:** string (comma-separated)
- **Default:** `all`
- **Description:** Comma-separated list of event types to export. Controls which flow events are sent to the gRPC server. Use `all` to export every event, or specify a subset (e.g., `request,response,tcp_message`).
- **Allowed values:**
   - `all`
   - `requestheaders`
   - `response`
   - `responseheaders`
   - `error`
   - `http_connect`
   - `http_connect_upstream`
   - `http_connected`
   - `http_connect_error`
   - `dns_request`
   - `dns_response`
   - `dns_error`
   - `tcp_start`
   - `tcp_message`
   - `tcp_end`
   - `tcp_error`
   - `udp_start`
   - `udp_message`
   - `udp_end`
   - `udp_error`
   - `websocket_start`
   - `websocket_message`
   - `websocket_end`
- **Example:**
   ```sh
   mitmproxy -s grpc_addon.py --set grpc_events=request,response
   ```

## Protobuf/gRPC Stubs for Your Server

To implement your gRPC server, use the published protobuf definitions and gRPC stubs from [buf.build/sudo-random/mitmproxygrpc](https://buf.build/sudo-random/mitmproxygrpc). Buf makes it easy to generate code in many languages:

- Visit [https://buf.build/sudo-random/mitmproxygrpc/sdks/main:protobuf](https://buf.build/sudo-random/mitmproxygrpc/sdks/main:protobuf)
- Follow the instructions to generate stubs for your language (Go, Python, Java, etc.)


## Project Structure

- `grpc_addon.py`: The mitmproxy addon implementation.
- `proto/`: Protobuf definitions for the gRPC service interface.
- `gen/`: Generated Python code from the protobufs.

## Contributing

Contributions are welcome! Please open issues or pull requests on GitHub.

## License

MIT License. See `LICENSE` file for details.
