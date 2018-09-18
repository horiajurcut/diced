def register_routes(app, handler):
    routing_engine = app.router

    routing_engine.add_get("/", handler.index, name="index")
    routing_engine.add_get("/{short_url}", handler.redirect, name="short_url")
    routing_engine.add_post("/dice", handler.dice, name="long_url")
