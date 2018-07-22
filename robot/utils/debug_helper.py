from aiohttp import web

routes = web.RouteTableDef()


@routes.post('/echo')
async def echo(request):
    data = await request.text()
    print(type(data))
    print(data)
    return web.Response(text=data)

app = web.Application()
app.add_routes(routes)
web.run_app(app, host="0.0.0.0", port=1559)
