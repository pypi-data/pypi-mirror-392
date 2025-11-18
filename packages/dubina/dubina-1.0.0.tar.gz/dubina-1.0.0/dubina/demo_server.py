from dubina import Server

server = Server(manipulator_type="sd1", port=5000, internal_port=50055)
server.start()
