from typing import Hashable


class IdentifierFacade:
    """Identifier getter facade."""

    @classmethod
    def get_identifier_within_args(cls, position: int, *args) -> Hashable:
        args_length = len(args)
        if position > args_length:
            raise KeyError(f"Position: {position} used to access identifier"
                           f" within {args} exceeds input length.")
        if position < 1:
            raise KeyError(f"Position: {position} cant be smaller than 1.")

        return args[position-1]

    @classmethod
    def get_identifier_within_kwarg(cls, key_word: str, **kwargs) -> Hashable:
        if key_word not in kwargs:
            raise KeyError(f"Key word: {key_word} used to access identifier"
                           f" within {kwargs} doesnt exist.")

        return kwargs[key_word]
