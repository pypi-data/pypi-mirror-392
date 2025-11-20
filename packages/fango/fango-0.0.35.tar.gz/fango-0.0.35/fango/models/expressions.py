from django.core.exceptions import FieldDoesNotExist
from django.db.models import BooleanField, Func, Q


class ExistsLookup(Func):
    """
    Universal and cheap Exists Lookup for checking relationship existence
    without expensive joins.

    """

    function = "EXISTS"
    template = "%(function)s (SELECT 1 FROM %(tables)s WHERE %(conditions)s %(field_condition)s)"
    output_field: BooleanField = BooleanField()

    def __init__(self, lookup: str, filter: Q | dict | None = None):
        self.lookup = lookup
        self._additional_filter = filter
        super().__init__()

    def resolve_expression(self, query=None, *args, **kwargs):
        if not query:
            return self
        self.model = query.model
        parts = self.lookup.split("__")
        tables, conditions = set(), []
        last_model, field_condition = self._build_chain(self.model, parts, tables, conditions)
        if self._additional_filter and last_model is not None:
            sql = self._build_filter_sql(last_model._meta.db_table, self._additional_filter)
            if sql:
                conditions.append(sql)
        self.extra["tables"] = ", ".join(tables)
        self.extra["conditions"] = " AND ".join(conditions)
        self.extra["field_condition"] = field_condition or ""
        return super().resolve_expression(query, *args, **kwargs)

    def _get_field(self, model, name):
        try:
            return model._meta.get_field(name)
        except FieldDoesNotExist:
            for rel in model._meta.related_objects:
                if rel.get_accessor_name() == name:
                    return rel
            raise ValueError(f"Field '{name}' not found in {model.__name__}")

    def _build_chain(self, model, parts, tables, conditions):
        field = self._get_field(model, parts[0])
        if field.many_to_many:
            through = getattr(model, field.name).through
            tables.add(through._meta.db_table)
            for f in through._meta.fields:
                if getattr(f, "related_model", None) == model:
                    conditions.append(f"{through._meta.db_table}.{f.column} = {model._meta.db_table}.id")
                    break
            if len(parts) == 1:
                return field.related_model, ""
            for f in through._meta.fields:
                if getattr(f, "related_model", None) == field.related_model:
                    tables.add(field.related_model._meta.db_table)
                    conditions.append(f"{field.related_model._meta.db_table}.id = {through._meta.db_table}.{f.attname}")
                    break
            next_field = self._get_field(field.related_model, parts[1])
            if not next_field.is_relation:
                return field.related_model, self._terminal_condition(field.related_model, parts[1], next_field)
            return self._build_chain(field.related_model, parts[1:], tables, conditions)
        else:
            tables.add(field.related_model._meta.db_table)
            if hasattr(field, "attname"):
                conditions.append(f"{field.related_model._meta.db_table}.id = {model._meta.db_table}.{field.attname}")
            else:
                conditions.append(
                    f"{field.related_model._meta.db_table}.{field.remote_field.attname} = {model._meta.db_table}.id"
                )
            if len(parts) == 1:
                return field.related_model, ""
            next_field = self._get_field(field.related_model, parts[1])
            if not next_field.is_relation:
                return field.related_model, self._terminal_condition(field.related_model, parts[1], next_field)
            return self._build_chain(field.related_model, parts[1:], tables, conditions)

    def _terminal_condition(self, model, column, field):
        table = model._meta.db_table
        is_boolean = isinstance(field, BooleanField)
        return f"AND {table}.{column} IS TRUE" if is_boolean else f"AND {table}.{column} IS NOT NULL"

    def _build_filter_sql(self, table: str, filt: Q | dict) -> str:
        items, clauses = [], []
        if isinstance(filt, Q):
            if filt.negated or filt.connector != Q.AND:
                raise ValueError("ExistsLookup filter supports only flat AND Q without negation")
            for child in filt.children:
                if isinstance(child, Q) or not (isinstance(child, tuple) and len(child) == 2):
                    raise ValueError("Unsupported Q child in ExistsLookup filter; only simple key=value supported")
                items.append(child)
        elif isinstance(filt, dict):
            items = list(filt.items())
        for key, value in items:
            if "__" in key:
                raise ValueError("ExistsLookup filter keys must not contain lookups (__)")
            column = f"{table}.{key}"
            if isinstance(value, bool):
                clauses.append(f"{column} IS {'TRUE' if value else 'FALSE'}")
            elif value is None:
                clauses.append(f"{column} IS NULL")
            elif isinstance(value, (int, float)):
                clauses.append(f"{column} = {value}")
            else:
                raise ValueError("Unsupported value type in ExistsLookup filter; only bool, int, float, None supported")
        return " AND ".join(clauses) if clauses else ""
