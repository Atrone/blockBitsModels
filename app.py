from aiohttp import web
import main
from rq import Queue
from worker import conn

q = Queue(connection=conn)

async def handle(request):
    q.enqueue(main.storeMetrics,
                            int(request.rel_url.query['limit']),
                            str(request.rel_url.query['sortDir']),str(request.rel_url.query['identifier']), job_timeout=600000)

    return web.Response(text=("we are making le results 2! :)"))

app = web.Application()
app.router.add_get('/storeMetrics', handle)
