from abc import ABC, abstractmethod

from astroid import FunctionDef, nodes
from pylint.lint import PyLinter

from kognitos.bdk.linter.util import get_decorator_by_name
from kognitos.bdk.reflection import BookProcedureDescriptor


class ProcedureRule(ABC):
    @abstractmethod
    def check_rule(self, linter: PyLinter, book_procedure: BookProcedureDescriptor, node: FunctionDef) -> None:
        pass


class ProcedureExamplesRule(ProcedureRule):
    def check_rule(self, linter: PyLinter, book_procedure: BookProcedureDescriptor, node: FunctionDef):
        if not book_procedure.examples or len(book_procedure.examples) < 1:
            linter.add_message("procedure-missing-examples", args=node.repr_name(), node=node)


class ProcedureConnectionRequiredRule(ProcedureRule):
    def check_rule(
        self,
        linter: PyLinter,
        book_procedure: BookProcedureDescriptor,
        node: FunctionDef,
    ):
        decorator = get_decorator_by_name(node, "kognitos.bdk.decorators.procedure_decorator.procedure")
        if not decorator or not decorator.keywords:
            return

        for keyword in decorator.keywords:
            if keyword.arg == "connection_required":
                value = keyword.value
                if not isinstance(value, nodes.Attribute) or getattr(value.expr, "name", None) != "ConnectionRequired":
                    linter.add_message(
                        "connection_required-invalid-type",
                        args=node.repr_name(),
                        node=node,
                    )
                return


class ProcedureIsMutationRule(ProcedureRule):
    def check_rule(
        self,
        linter: PyLinter,
        book_procedure: BookProcedureDescriptor,
        node: FunctionDef,
    ):
        decorator = get_decorator_by_name(node, "kognitos.bdk.decorators.procedure_decorator.procedure")
        if not decorator:
            return

        # Check if is_mutation is explicitly defined as a keyword argument
        has_is_mutation_kwarg = False
        is_mutation_value = None
        if decorator.keywords:
            for keyword in decorator.keywords:
                if keyword.arg == "is_mutation":
                    has_is_mutation_kwarg = True
                    is_mutation_value = keyword.value
                    break

        if not has_is_mutation_kwarg:
            linter.add_message(
                "procedure-missing-is-mutation",
                args=node.repr_name(),
                node=node,
            )
            return

        # Check if is_mutation is a boolean
        if is_mutation_value is not None:
            if not isinstance(is_mutation_value, nodes.Const) or not isinstance(is_mutation_value.value, bool):
                linter.add_message(
                    "procedure-is-mutation-invalid-type",
                    args=node.repr_name(),
                    node=node,
                )
