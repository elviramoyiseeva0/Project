from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from NeiroSlopTerest.models import Pin

from .models import Board

User = get_user_model()


class BoardViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="password123")
        self.other_user = User.objects.create_user(username="bob", password="password123")
        self.pin = Pin.objects.create(
            title="Test Pin",
            description="A nice pin",
            image_url="https://example.com/pin.jpg",
        )

    def test_guest_can_create_up_to_two_boards_only(self):
        create_url = reverse("boards:board_create")

        # 1st board
        resp1 = self.client.post(create_url, {"title": "Guest Board 1", "description": "First"})
        self.assertEqual(resp1.status_code, 302)
        self.assertEqual(Board.objects.count(), 1)

        # 2nd board
        resp2 = self.client.post(create_url, {"title": "Guest Board 2", "description": "Second"})
        self.assertEqual(resp2.status_code, 302)
        self.assertEqual(Board.objects.count(), 2)

        # 3rd board should be rejected
        resp3 = self.client.post(create_url, {"title": "Guest Board 3", "description": "Third"})
        self.assertEqual(resp3.status_code, 200)
        self.assertEqual(Board.objects.count(), 2)
        self.assertContains(resp3, "Достигнут лимит")

    def test_registered_user_has_no_board_limit(self):
        self.client.force_login(self.user)
        create_url = reverse("boards:board_create")

        for idx in range(1, 6):
            resp = self.client.post(create_url, {"title": f"User Board {idx}", "description": ""})
            self.assertEqual(resp.status_code, 302)

        self.assertEqual(Board.objects.filter(owner=self.user).count(), 5)

    def test_board_list_and_detail_display(self):
        self.client.force_login(self.user)
        board = Board.objects.create(title="Design", description="UI ideas", owner=self.user)
        board.pins.add(self.pin)

        list_resp = self.client.get(reverse("boards:board_list"))
        self.assertEqual(list_resp.status_code, 200)
        self.assertContains(list_resp, "Design")

        detail_resp = self.client.get(reverse("boards:board_detail", args=[board.pk]))
        self.assertEqual(detail_resp.status_code, 200)
        self.assertContains(detail_resp, "Design")
        self.assertContains(detail_resp, "Test Pin")

    def test_board_delete_permissions(self):
        board = Board.objects.create(title="Alice Board", owner=self.user)
        delete_url = reverse("boards:board_delete", args=[board.pk])

        # Other user cannot delete
        self.client.force_login(self.other_user)
        resp_forbidden = self.client.post(delete_url)
        self.assertEqual(resp_forbidden.status_code, 403)
        self.assertTrue(Board.objects.filter(pk=board.pk).exists())

        # Owner can delete
        self.client.force_login(self.user)
        resp_ok = self.client.post(delete_url)
        self.assertEqual(resp_ok.status_code, 302)
        self.assertFalse(Board.objects.filter(pk=board.pk).exists())

    def test_guest_can_delete_own_board_but_not_other_guest_board(self):
        # Create a board with guest 1
        self.client.post(reverse("boards:board_create"), {"title": "G1 Board"})
        board = Board.objects.get(title="G1 Board")
        delete_url = reverse("boards:board_delete", args=[board.pk])

        # Another guest cannot delete
        other_guest = Client()
        resp_forbidden = other_guest.post(delete_url)
        self.assertEqual(resp_forbidden.status_code, 403)
        self.assertTrue(Board.objects.filter(pk=board.pk).exists())

        # Original guest can delete
        resp_ok = self.client.post(delete_url)
        self.assertEqual(resp_ok.status_code, 302)
        self.assertFalse(Board.objects.filter(pk=board.pk).exists())

    def test_save_and_remove_pin_on_board(self):
        self.client.force_login(self.user)
        board = Board.objects.create(title="Saved Pins", owner=self.user)

        save_url = reverse("boards:save_pin_to_board", args=[self.pin.pk])
        resp_save = self.client.post(save_url, {"board": board.pk})
        self.assertEqual(resp_save.status_code, 302)
        self.assertTrue(board.pins.filter(pk=self.pin.pk).exists())

        remove_url = reverse("boards:remove_pin_from_board", args=[board.pk, self.pin.pk])
        resp_remove = self.client.post(remove_url)
        self.assertEqual(resp_remove.status_code, 302)
        self.assertFalse(board.pins.filter(pk=self.pin.pk).exists())

    def test_pin_explore_renders(self):
        resp = self.client.get(reverse("boards:pin_explore"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Test Pin")
