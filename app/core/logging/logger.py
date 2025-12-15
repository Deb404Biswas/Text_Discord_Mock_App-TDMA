from loguru import logger
logger.add(
    'log/app.log',
    format="{time:MMMM D, YYYY - HH:mm:ss} {level} ----- {message}",
    rotation="1 hours",
    retention="24 hours"
)