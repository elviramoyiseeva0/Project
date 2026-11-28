from django.contrib import messages
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from NeiroSlopTerest.models import Pin

from .forms import BoardForm, SavePinToBoardForm
from .models import Board


def _get_or_create_session_key(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def _get_user_boards(request):
    if request.user.is_authenticated:
        return Board.objects.filter(owner=request.user)
    session_key = request.session.session_key
    if not session_key:
        return Board.objects.none()
    return Board.objects.filter(owner__isnull=True, session_key=session_key)


def _can_manage_board(request, board):
    if request.user.is_authenticated:
        return board.owner_id == request.user.id
    session_key = request.session.session_key
    return board.owner_id is None and bool(session_key) and board.session_key == session_key


def _guest_limit_status(request):
    boards_count = _get_user_boards(request).count()
    if request.user.is_authenticated:
        return False, boards_count
    return boards_count >= Board.GUEST_BOARD_LIMIT, boards_count


def board_list(request):
    boards = _get_user_boards(request).prefetch_related("pins")
    limit_reached, boards_count = _guest_limit_status(request)
    return render(
        request,
        "boards/board_list.html",
        {
            "boards": boards,
            "boards_count": boards_count,
            "guest_limit": Board.GUEST_BOARD_LIMIT,
            "limit_reached": limit_reached,
        },
    )


def board_create(request):
    limit_reached, boards_count = _guest_limit_status(request)

    if request.method == "POST":
        form = BoardForm(request.POST)
        if limit_reached:
            messages.error(
                request,
                f"Гости могут создать максимум {Board.GUEST_BOARD_LIMIT} доски. "
                "Войдите или зарегистрируйтесь, чтобы создавать доски без ограничений.",
            )
            form.add_error(
                None,
                f"Достигнут лимит для гостей ({Board.GUEST_BOARD_LIMIT} доски).",
            )
        elif form.is_valid():
            board = form.save(commit=False)
            if request.user.is_authenticated:
                board.owner = request.user
            else:
                board.owner = None
                board.session_key = _get_or_create_session_key(request)
            board.save()
            messages.success(request, f"Доска «{board.title}» создана.")
            return redirect("boards:board_detail", pk=board.pk)
    else:
        form = BoardForm()

    return render(
        request,
        "boards/board_form.html",
        {
            "form": form,
            "boards_count": boards_count,
            "guest_limit": Board.GUEST_BOARD_LIMIT,
            "limit_reached": limit_reached,
        },
    )


def board_detail(request, pk):
    board = get_object_or_404(Board.objects.prefetch_related("pins"), pk=pk)
    can_manage = _can_manage_board(request, board)
    pins = board.pins.all()
    available_pins = Pin.objects.exclude(pk__in=pins.values_list("pk", flat=True))
    return render(
        request,
        "boards/board_detail.html",
        {
            "board": board,
            "pins": pins,
            "available_pins": available_pins,
            "can_manage": can_manage,
        },
    )


def board_delete(request, pk):
    board = get_object_or_404(Board, pk=pk)
    if not _can_manage_board(request, board):
        return HttpResponseForbidden("У вас нет прав на удаление этой доски.")

    if request.method == "POST":
        title = board.title
        board.delete()
        messages.success(request, f"Доска «{title}» удалена.")
        return redirect("boards:board_list")

    return render(request, "boards/board_confirm_delete.html", {"board": board})


def pin_explore(request):
    query = request.GET.get("q", "").strip()
    pins = Pin.objects.all()
    if query:
        pins = pins.filter(title__icontains=query) | pins.filter(description__icontains=query)
    user_boards = _get_user_boards(request)
    return render(
        request,
        "boards/pin_explore.html",
        {
            "pins": pins,
            "user_boards": user_boards,
            "query": query,
        },
    )


def save_pin_to_board(request, pin_id):
    pin = get_object_or_404(Pin, pk=pin_id)
    user_boards = _get_user_boards(request)

    if request.method == "POST":
        form = SavePinToBoardForm(request.POST, boards_queryset=user_boards)
        if form.is_valid():
            board = form.cleaned_data["board"]
            if not _can_manage_board(request, board):
                return HttpResponseForbidden("У вас нет прав на изменение этой доски.")
            board.pins.add(pin)
            messages.success(request, f"Пин «{pin.title}» сохранён на доску «{board.title}».")
            next_url = request.POST.get("next")
            if next_url:
                return redirect(next_url)
            return redirect("boards:board_detail", pk=board.pk)
    else:
        form = SavePinToBoardForm(boards_queryset=user_boards)

    return render(
        request,
        "boards/save_pin.html",
        {
            "pin": pin,
            "form": form,
            "user_boards": user_boards,
        },
    )


@require_POST
def remove_pin_from_board(request, pk, pin_id):
    board = get_object_or_404(Board, pk=pk)
    if not _can_manage_board(request, board):
        return HttpResponseForbidden("У вас нет прав на изменение этой доски.")

    pin = get_object_or_404(Pin, pk=pin_id)
    board.pins.remove(pin)
    messages.info(request, f"Пин «{pin.title}» убран с доски «{board.title}».")
    return redirect("boards:board_detail", pk=board.pk)
