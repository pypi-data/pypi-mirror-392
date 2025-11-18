from abc import ABC, abstractmethod

from astroid import FunctionDef
from pylint.lint import PyLinter

from kognitos.bdk.linter import util
from kognitos.bdk.linter.util import get_decorator_by_name


class OAuthTokenRule(ABC):
    @abstractmethod
    def check_rule(self, linter: PyLinter, node: FunctionDef) -> None:
        pass


class OAuthTokenVerifyParameterRule(OAuthTokenRule):
    """
    Rule to check that functions with @oauthtoken decorator have a 'verify' parameter
    of type bool.
    """

    def check_rule(self, linter: PyLinter, node: FunctionDef) -> None:
        decorator = get_decorator_by_name(node, "kognitos.bdk.decorators.oauthtoken_decorator.oauthtoken")
        if not decorator:
            return

        # Find verify parameter and its annotation
        verify_arg = None
        verify_annotation = None

        for idx, arg in enumerate(node.args.arguments):
            if arg.name == "verify":
                verify_arg = arg
                verify_annotation = node.args.annotations[idx] if idx < len(node.args.annotations) else None
                break

        # Check if verify parameter exists
        if verify_arg is None:
            linter.add_message(
                "oauthtoken-missing-verify-parameter",
                node=node,
                args=(node.name,),
            )
            return

        # Check type annotation - must be bool
        if verify_annotation is None or not util.is_bool_type(verify_annotation):
            error_node = verify_annotation if verify_annotation else verify_arg
            error_arg = verify_annotation.as_string() if verify_annotation else "verify"
            linter.add_message(
                "oauthtoken-verify-parameter-wrong-type",
                node=error_node,
                args=(node.name, error_arg),
            )


class OAuthTokenAccessTokenParameterRule(OAuthTokenRule):
    """
    Rule to check that functions with @oauthtoken decorator have an 'access_token' parameter
    of type Sensitive[str].
    """

    def check_rule(self, linter: PyLinter, node: FunctionDef) -> None:
        decorator = get_decorator_by_name(node, "kognitos.bdk.decorators.oauthtoken_decorator.oauthtoken")
        if not decorator:
            return

        # Find access_token parameter by name
        access_token_arg = None
        annotation = None

        for idx, arg in enumerate(node.args.arguments):
            if arg.name == "access_token":
                access_token_arg = arg
                annotation = node.args.annotations[idx] if idx < len(node.args.annotations) else None
                break

        if access_token_arg:
            if annotation:
                if not (util.is_sensitive_str_type(annotation) and not util.is_optional_type(annotation)):
                    linter.add_message(
                        "oauthtoken-handler-wrong-arg-type",
                        node=annotation,
                        args=(annotation.as_string(), "Sensitive[str]"),
                    )
            # If no annotation, that's a different error that would be caught by type checking
        else:
            linter.add_message(
                "oauthtoken-handler-missing-arg",
                node=node,
                args=("access_token", "Sensitive[str]"),
            )


class OAuthTokenExpiresInParameterRule(OAuthTokenRule):
    """
    Rule to check that functions with @oauthtoken decorator have an 'expires_in' parameter
    of type Optional[int].
    """

    def check_rule(self, linter: PyLinter, node: FunctionDef) -> None:
        decorator = get_decorator_by_name(node, "kognitos.bdk.decorators.oauthtoken_decorator.oauthtoken")
        if not decorator:
            return

        # Find expires_in parameter by name
        expires_in_arg = None
        annotation = None

        for idx, arg in enumerate(node.args.arguments):
            if arg.name == "expires_in":
                expires_in_arg = arg
                annotation = node.args.annotations[idx] if idx < len(node.args.annotations) else None
                break

        if expires_in_arg:
            if annotation:
                if not (util.is_int_type(annotation) and util.is_optional_type(annotation)):
                    linter.add_message(
                        "oauthtoken-handler-wrong-arg-type",
                        node=annotation,
                        args=(annotation.as_string(), "Optional[int]"),
                    )
            # If no annotation, that's a different error that would be caught by type checking
        else:
            linter.add_message(
                "oauthtoken-handler-missing-arg",
                node=node,
                args=("expires_in", "Optional[int]"),
            )


class OAuthTokenUnexpectedParametersRule(OAuthTokenRule):
    """
    Rule to check that functions with @oauthtoken decorator don't have unexpected parameters.
    Expected parameters are: self, access_token, expires_in, verify.
    """

    def check_rule(self, linter: PyLinter, node: FunctionDef) -> None:
        decorator = get_decorator_by_name(node, "kognitos.bdk.decorators.oauthtoken_decorator.oauthtoken")
        if not decorator:
            return

        # Check for unexpected extra arguments
        extra_args = [arg for arg in node.args.arguments if arg.name not in ["access_token", "expires_in", "verify", "self"]]

        for extra_arg in extra_args:
            linter.add_message("oauthtoken-handler-unexpected-arg", node=node, args=(extra_arg.name,))
