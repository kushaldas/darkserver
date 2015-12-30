import socket
hostname = socket.gethostname().split('.')[0]


config = {
    # Consumer stuff
    "darkserver.consumer.enabled":True,
    # Turn on logging for darkserver
    "logging": dict(
        loggers=dict(
            drkserver={
                "level": "DEBUG",
                "propagate": False,
                "handlers": ["console"],
            },
        ),
    ),
}
