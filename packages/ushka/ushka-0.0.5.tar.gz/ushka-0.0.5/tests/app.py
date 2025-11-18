from ushka import Ushka


app = Ushka()


def hello_world(name):
    return f"""<html>
<body>
<h1 style="font-size:5rem;text-align:center;">Hello {name} {__file__} {__name__}!</h1>
</body>
</html>
    """


def debug():
    from pathlib import Path

    base_path = Path(__file__).parent
    base_path = base_path.joinpath("routes")
    return str(base_path)


app.router.add_route("GET", "/d/[name]", hello_world)
app.router.add_route("GET", "/debug", debug)

app.router.autodiscover()


if __name__ == "__main__":
    print(app.router.static_routes)
    app.run("0.0.0.0", 8000)
