from django.urls import path

from . import views

app_name = "boards"

urlpatterns = [
    path("", views.board_list, name="board_list"),
    path("create/", views.board_create, name="board_create"),
    path("pins/", views.pin_explore, name="pin_explore"),
    path("save-pin/<int:pin_id>/", views.save_pin_to_board, name="save_pin_to_board"),
    path("<int:pk>/", views.board_detail, name="board_detail"),
    path("<int:pk>/delete/", views.board_delete, name="board_delete"),
    path(
        "<int:pk>/remove-pin/<int:pin_id>/",
        views.remove_pin_from_board,
        name="remove_pin_from_board",
    ),
]
