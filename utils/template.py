from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(
    directory="templates"
)


def render(
    name,
    request,
    context=None
):

    if context is None:
        context = {}


    context["request"] = request


    # lấy user từ request.state
    context["user"] = getattr(
        request.state,
        "user",
        None
    )


    return templates.TemplateResponse(
        name,
        context
    )