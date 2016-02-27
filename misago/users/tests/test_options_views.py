from django.core import mail
from django.core.urlresolvers import reverse
from misago.users.testutils import AuthenticatedUserTestCase


class OptionsViewsTests(AuthenticatedUserTestCase):
    def test_lander_view_returns_200(self):
        """/options has no show stoppers"""
        response = self.client.get(reverse('misago:options'))
        self.assertEqual(response.status_code, 200)

    def test_form_view_returns_200(self):
        """/options/some-form has no show stoppers"""
        response = self.client.get(reverse('misago:options_form', kwargs={
            'form_name': 'some-fake-form'
        }))
        self.assertEqual(response.status_code, 200)


class ConfirmChangeEmailTests(AuthenticatedUserTestCase):
    def setUp(self):
        super(ConfirmChangeEmailTests, self).setUp()
        link = '/api/users/%s/change-email/' % self.user.pk

        response = self.client.post(link, data={
            'new_email': 'n3w@email.com',
            'password': self.USER_PASSWORD
        })
        self.assertEqual(response.status_code, 200)

        for line in [l.strip() for l in mail.outbox[0].body.splitlines()]:
            if line.startswith('http://'):
                self.link = line.strip()
                break

    def test_invalid_token(self):
        """invalid token is rejected"""
        response = self.client.get(
            reverse('misago:options_confirm_email_change', kwargs={
                'token': 'invalid'
            }))

        self.assertEqual(response.status_code, 400)
        self.assertIn("Change confirmation link is invalid.", response.content)

    def test_change_email(self):
        """valid token changes email"""
        response = self.client.get(self.link)

        self.assertEqual(response.status_code, 200)
        self.assertIn("your e-mail has been changed", response.content)

        self.reload_user()
        self.assertEqual(self.user.email, 'n3w@email.com')


class ConfirmChangePasswordTests(AuthenticatedUserTestCase):
    def setUp(self):
        super(ConfirmChangePasswordTests, self).setUp()
        link = '/api/users/%s/change-password/' % self.user.pk

        response = self.client.post(link, data={
            'new_password': 'n3wp4ssword',
            'password': self.USER_PASSWORD
        })
        self.assertEqual(response.status_code, 200)

        for line in [l.strip() for l in mail.outbox[0].body.splitlines()]:
            if line.startswith('http://'):
                self.link = line.strip()
                break

    def test_invalid_token(self):
        """invalid token is rejected"""
        response = self.client.get(
            reverse('misago:options_confirm_password_change', kwargs={
                'token': 'invalid'
            }))

        self.assertEqual(response.status_code, 400)
        self.assertIn("Change confirmation link is invalid.", response.content)

    def test_change_password(self):
        """valid token changes password"""
        response = self.client.get(self.link)

        self.assertEqual(response.status_code, 200)
        self.assertIn("your password has been changed", response.content)

        self.reload_user()
        self.assertFalse(self.user.check_password(self.USER_PASSWORD))
        self.assertTrue(self.user.check_password('n3wp4ssword'))