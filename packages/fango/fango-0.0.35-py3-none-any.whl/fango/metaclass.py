class ImmutableMeta(type):
    def __new__(cls, name, bases, namespace, **kwargs):
        new_class = super().__new__(cls, name, bases, namespace, **kwargs)

        immutable_attrs = set()
        for base in new_class.__mro__:
            if hasattr(base, "_immutable_attrs"):
                immutable_attrs.update(base._immutable_attrs)

        for attr in immutable_attrs:
            if attr in namespace:
                original_value = namespace[attr]

                def getter(self, attr=attr, original_value=original_value):
                    return original_value

                def setter(self, value, attr=attr):
                    raise AttributeError(f"Cannot modify immutable attribute '{attr}'")

                setattr(new_class, attr, property(getter, setter))

        return new_class
