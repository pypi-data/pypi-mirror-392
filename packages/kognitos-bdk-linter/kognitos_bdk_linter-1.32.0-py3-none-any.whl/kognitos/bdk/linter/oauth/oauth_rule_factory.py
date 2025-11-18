from abc import ABC, abstractmethod
from typing import List

from kognitos.bdk.linter.oauth.rules.oauth_token_rules import (
    OAuthTokenAccessTokenParameterRule, OAuthTokenExpiresInParameterRule,
    OAuthTokenRule, OAuthTokenUnexpectedParametersRule,
    OAuthTokenVerifyParameterRule)


class OAuthTokenRuleFactory(ABC):
    @abstractmethod
    def get_rules(self) -> List[OAuthTokenRule]:
        pass


class DefaultOAuthTokenRuleFactory(OAuthTokenRuleFactory):
    def get_rules(self) -> List[OAuthTokenRule]:
        return [
            OAuthTokenAccessTokenParameterRule(),
            OAuthTokenExpiresInParameterRule(),
            OAuthTokenVerifyParameterRule(),
            OAuthTokenUnexpectedParametersRule(),
        ]
