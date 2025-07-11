import logfire
import asyncio
import os
from sexybabeycord.main import main

logfire.configure(token=os.getenv("LOGFIRE_TOKEN"))
logfire.install_auto_tracing(modules=["sexybabeycord"], min_duration=0.01)

asyncio.run(main())
