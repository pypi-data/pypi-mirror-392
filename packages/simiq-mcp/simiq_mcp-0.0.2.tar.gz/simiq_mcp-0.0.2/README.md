# SimIQ-MCP

The `simiq-mcp` package provides a lightweight STDIO, Streamable HTTP, and SSE MCP server for calling SimIQ.

It exposes one tool: `analyze_waveforms(uri)`, where uri can be any `http:`, `https:`, `file:`, or `data:` URI.

## Installation

To install the package, use pip:

```bash
pip install simiq-mcp
```

## Usage

To run the MCP server, using STDIO (default) use the following command:


```bash	
simiq-mcp
```

To run the MCP server, using Streamable HTTP and SSE use the following command:

```bash	
simiq-mcp --http --host 127.0.0.1 --port 3001
```

## Running in Docker

To run `simiq-mcp` in Docker, build the Docker image using the provided Dockerfile:
```bash
docker build -t simiq-mcp:latest .
```

And run it using:
```bash
docker run -it --rm simiq-mcp:latest
```
This will be sufficient for remote URIs. To access local files, you need to mount the local directory into the container. For example, if you want to access files in `/home/user/data`, you can run:

```bash
docker run -it --rm -v /home/user/data:/workdir simiq-mcp:latest
```

Once mounted, all files under data will be accessible under `/workdir` in the container. For example, if you have a file `example.txt` in `/home/user/data`, it will be accessible in the container at `/workdir/example.txt`.

## Accessing from Claude Desktop

It is recommended to use the Docker image when running the MCP server for Claude Desktop.

Follow [these instructions](https://modelcontextprotocol.io/quickstart/user#for-claude-desktop-users) to access Claude's `claude_desktop_config.json` file.

Edit it to include the following JSON entry:

```json
{
  "mcpServers": {
    "simiq": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "simiq-mcp:latest"
      ]
    }
  }
}
```

If you want to mount a directory, adjust it accordingly:

```json
{
  "mcpServers": {
    "simiq": {
      "command": "docker",
      "args": [
	"run",
	"--rm",
	"-i",
	"-v",
	"/home/user/data:/workdir",
	"simiq-mcp:latest"
      ]
    }
  }
}
```

## Debugging

To debug the MCP server you can use the `mcpinspector` tool.

```bash
npx @modelcontextprotocol/inspector
```

You can then connect to the inspector through the specified host and port (e.g., `http://localhost:5173/`).

If using STDIO:
* select `STDIO` as the transport type,
* input `simiq-mcp` as the command, and
* click `Connect`

If using Streamable HTTP:
* select `Streamable HTTP` as the transport type,
* input `http://127.0.0.1:3001/mcp` as the URL, and
* click `Connect`

If using SSE:
* select `SSE` as the transport type,
* input `http://127.0.0.1:3001/sse` as the URL, and
* click `Connect`

Finally:
* click the `Tools` tab,
* click `List Tools`,
* click `analyze_waveforms`, and
* run the tool on any valid URI.

## Security Considerations

The server does not support authentication, and runs with the privileges of the user running it. For this reason, when running in SSE or Streamable HTTP mode, it is recommended to run the server bound to `localhost` (default).

