from django.contrib.auth.tokens import PasswordResetTokenGenerator

class TokenGenerator1(PasswordResetTokenGenerator):
    def _make_hash_value1(self, user, timestamp):
        return(
            str(user.pk) + str(timestamp)+
            str(user.is_active)
        )

account_activation_token1 = TokenGenerator1()
