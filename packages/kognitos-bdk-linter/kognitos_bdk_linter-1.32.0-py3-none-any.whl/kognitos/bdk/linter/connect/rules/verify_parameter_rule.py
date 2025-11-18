from astroid import FunctionDef
from pylint.lint import PyLinter

from kognitos.bdk.linter import util
from kognitos.bdk.linter.connect.rules.connect_rule import ConnectRule
from kognitos.bdk.linter.util import get_decorator_by_name


class VerifyParameterRule(ConnectRule):
    """
    Rule to check that functions with @connect decorator have a 'verify' parameter
    of type bool.
    """

    def check_rule(self, linter: PyLinter, node: FunctionDef) -> None:
        decorator = get_decorator_by_name(node, "kognitos.bdk.decorators.connect_decorator.connect")
        if not decorator:
            return

        # Build a mapping of argument names to their annotations
        arg_annotations = {}
        for idx, arg in enumerate(node.args.arguments):
            annotation = node.args.annotations[idx] if idx < len(node.args.annotations) else None
            arg_annotations[arg.name] = annotation

        # Find verify parameter by name
        verify_arg = None

        for idx, arg in enumerate(node.args.arguments):
            if arg.name == "verify":
                verify_arg = arg
                break

        if verify_arg is None:
            linter.add_message(
                "connect-missing-verify-parameter",
                node=node,
                args=(node.name,),
            )
            return

        # Check type annotation
        annotation = arg_annotations.get("verify")
        if annotation:
            if not util.is_bool_type(annotation):
                linter.add_message(
                    "connect-verify-parameter-wrong-type",
                    node=annotation,
                    args=(node.name, annotation.as_string()),
                )
