from django.core.exceptions import FieldDoesNotExist
from django.db.models import Field, Q, QuerySet
from django.db.models.fields.related import ManyToManyField, ManyToOneRel

from fango.log import logger, logging


class NP1_Detector_QuerySet(QuerySet):
    M2M_CHAIN = "Chain of 2+ M2M/reverse relations - O(^2)"
    M2M_ANNOTATION = "M2M annotation"
    M2M_FILTER = "M2M filter"
    REVERSE_FK_ANNOTATION = "Reverse FK annotation"
    REVERSE_FK_FILTER = "Reverse FK filter"

    def annotate(self, **annotations):
        for annotation in annotations.values():
            self._check_expression_for_m2m(annotation, source="annotation")
        return super().annotate(**annotations)

    def _filter_or_exclude(self, negate, args, kwargs):
        for lookup in kwargs:
            self._check_m2m_path(lookup, source="filter")

        for arg in args:
            if hasattr(arg, "children"):
                self._check_q_expression(arg, source="filter")

        return super()._filter_or_exclude(negate, args, kwargs)

    def _check_q_expression(self, q, source: str) -> None:
        for child in q.children:
            if isinstance(child, Q):
                self._check_q_expression(child, source)
            elif isinstance(child, tuple) and len(child) == 2:
                lookup, value = child
                self._check_m2m_path(lookup, source)

    def _check_expression_for_m2m(self, expression, source: str) -> None:
        if hasattr(expression, "get_source_expressions"):
            for expr in expression.get_source_expressions():
                self._check_expression_for_m2m(expr, source)
        if hasattr(expression, "name") and expression.name:
            self._check_m2m_path(expression.name, source=source)

    def _classify_danger_level(self, path: str, source: str, field: Field, danger_count: int) -> tuple[int, str] | None:
        if danger_count >= 2 and path.count("__") >= 3:
            return logging.CRITICAL, self.M2M_CHAIN

        is_dangerous_related = (
            isinstance(field, ManyToManyField)
            or (isinstance(field, ManyToOneRel) and not field.one_to_one)
            or (hasattr(field, "many_to_many") and field.many_to_many)
        )

        if is_dangerous_related and source in ("annotation", "aggregate"):
            if isinstance(field, ManyToManyField) or (hasattr(field, "many_to_many") and field.many_to_many):
                return logging.ERROR, self.M2M_ANNOTATION
            else:
                return logging.ERROR, self.REVERSE_FK_ANNOTATION

        if is_dangerous_related and source == "filter":
            if isinstance(field, ManyToManyField) or (hasattr(field, "many_to_many") and field.many_to_many):
                return logging.INFO, self.M2M_FILTER
            else:
                return logging.INFO, self.REVERSE_FK_FILTER

    def _is_dangerous_field(self, field: Field) -> bool:
        return (
            isinstance(field, ManyToManyField)
            or (isinstance(field, ManyToOneRel) and not field.one_to_one)
            or (hasattr(field, "many_to_many") and bool(field.many_to_many))
        )

    def _check_m2m_path(self, path: str, source: str) -> None:
        if not path or "__" not in path:
            return

        parts = path.split("__")
        model = self.model
        danger_count = 0
        first_danger_field = None

        for part in parts:
            try:
                field = model._meta.get_field(part)

                if self._is_dangerous_field(field):
                    danger_count += 1
                    if not first_danger_field:
                        first_danger_field = field

                model = field.related_model if hasattr(field, "related_model") else None
                if not model:
                    break

            except FieldDoesNotExist:
                break

        if first_danger_field and (
            danger_level := self._classify_danger_level(path, source, first_danger_field, danger_count)
        ):
            logger.log(level=danger_level[0], msg=f"{danger_level[1]} -- {self.model.__name__} {source}: {path}")
