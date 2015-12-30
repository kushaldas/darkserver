import socket
hostname = socket.gethostname().split('.')[0]


config = {
    # Consumer stuff
    "darkserver.consumer.enabled":True,
    # Turn on logging for bugyou
    "logging": dict(
        loggers=dict(
            darkserver={
                "level": "DEBUG",
                "propagate": False,
                "handlers": ["console"],
            },
        ),
    ),
}
