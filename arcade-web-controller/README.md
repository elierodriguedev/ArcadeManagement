# Arcade Web Controller

This project provides a web-based interface and API to manage multiple Arcade Agent instances running on your arcade and pinball machines. It acts as a central point to monitor agent status, manage control layouts, and potentially trigger agent updates and manage LaunchBox data remotely.

The web controller is designed to be run in a Docker container on a server, allowing access from any web browser on your network.

## Features

- List and monitor the status of configured Arcade Agents.
- View and update control layouts for individual agents (basic implementation).
- (Future) Implement additional features to replicate the functionality of the desktop Arcade Controller, such as managing games, playlists, and triggering agent updates.

## Setup

1.  **Prerequisites:**
    *   Docker installed on your server.
    *   Arcade Agent running on your Windows arcade/pinball machines, accessible from the server running Docker.

2.  **Configuration:**
    *   Create a `machines.json` file in the `arcade-web-controller` directory (or mount it into the Docker container). This file should list your agents, similar to the `machines.json` used by the desktop controller:

    ```json
    [
      {
        "name": "YourMachineName1",
        "host": "your_machine_hostname_or_ip_1",
        "type": "arcade"
      },
      {
        "name": "YourMachineName2",
        "host": "your_machine_hostname_or_ip_2",
        "type": "pinball"
      }
      // Add more machines as needed
    ]
    ```
    *   Ensure the `host` values are resolvable from within the Docker container (e.g., use hostnames if your network has local DNS or mDNS, or use static IP addresses).

3.  **Web UI:**
    *   The project includes a basic placeholder `static/index.html`. To use a more complete web interface, you would place your web UI files (HTML, CSS, JavaScript, or a built frontend application) in the `static` directory.

## Building the Docker Image

1.  Navigate to the `arcade-web-controller` directory in your terminal.
2.  Build the Docker image:

    ```bash
    docker build -t arcade-web-controller .
    ```

## Running the Docker Container

Run the Docker container, mapping a local port to the container's port 5000, and setting a restart policy:

```bash
docker run -d -p 8080:5000 --name web-controller --restart=always -v /mnt/user/Projets/Studio Code/ArcadeProject/arcade-web-controller:/app arcade-web-controller
```

This command:
- Runs the container in detached mode (`-d`).
- Maps port 8080 on your host to port 5000 in the container (`-p 8080:5000`). You can change the host port (8080) if needed.
- Sets the container to always restart unless explicitly stopped (`--restart=always`).
- **Maps the host directory `/mnt/user/Projets/Studio Code/ArcadeProject/arcade-web-controller` to the `/app` directory inside the container (`-v /mnt/user/Projets/Studio Code/ArcadeProject/arcade-web-controller:/app`). This allows the container to access your local project files.**

You should now be able to access the web controller by navigating to `http://your_server_ip:8080` (replace `your_server_ip` with your server's actual IP or hostname).

**Note on Updates:**
When using the volume mapping (`-v` flag), changes you make to the files on your host machine (`/mnt/user/Projets/Studio Code/ArcadeProject/arcade-web-controller`) will be immediately reflected inside the running container. This is useful for development. For a production environment, you would typically build a new Docker image with your updated code and replace the running container with a new one based on the updated image.

## Development

- The main application logic is in `app.py`.
- API endpoints are defined using Flask routes.
- Agent interactions are handled using the `requests` library.
- The web UI files are served from the `static` directory.

## Contributing

(Add contribution guidelines here if applicable)

## License

(Specify license, e.g., MIT)
