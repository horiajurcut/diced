def register_routes(app, handler):
    routing_engine = app.router
    h = handler

    routing_engine.add_get('/', h.index, name='index')
