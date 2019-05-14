#!/usr/bin/env python

#    Copyright 2016 - 2019 Alexey Stepanov aka penguinolog
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""Property with logging on successful get/set/delete or failure."""

__all__ = ("LogOnAccess",)

# Standard Library
import inspect
import logging
import sys
import time
import traceback
import typing

# LogWrap Implementation
from logwrap import repr_utils


_LOGGER = logging.getLogger(__name__)  # type: logging.Logger


class LogOnAccess(property):
    """Property with logging on successful get/set/delete or failure.

    .. versionadded:: 6.1.0
    """

    def __init__(
        self,
        fget: typing.Optional[typing.Callable[[typing.Any], typing.Any]] = None,
        fset: typing.Optional[typing.Callable[[typing.Any, typing.Any], None]] = None,
        fdel: typing.Optional[typing.Callable[[typing.Any], None]] = None,
        doc: typing.Optional[str] = None,
        *,
        # Extended settings start
        logger: typing.Optional[typing.Union[logging.Logger, str]] = None,
        log_object_repr: bool = True,
        log_level: int = logging.DEBUG,
        exc_level: int = logging.DEBUG,
        log_before: bool = True,
        log_success: bool = True,
        log_failure: bool = True,
        log_traceback: bool = True,
        override_name: typing.Optional[str] = None,
        max_indent: int = 20
    ) -> None:
        """Advanced property main entry point.

        :param fget: normal getter.
        :type fget: typing.Optional[typing.Callable[[typing.Any, ], typing.Any]]
        :param fset: normal setter.
        :type fset: typing.Optional[typing.Callable[[typing.Any, typing.Any], None]]
        :param fdel: normal deleter.
        :type fdel: typing.Optional[typing.Callable[[typing.Any, ], None]]
        :param doc: docstring override
        :type doc: typing.Optional[str]
        :param logger: logger instance or name to use as override
        :type logger: typing.Optional[typing.Union[logging.Logger, str]]
        :param log_object_repr: use `repr` over object to describe owner if True else owner class name and id
        :type log_object_repr: bool
        :param log_level: log level for successful operations
        :type log_level: int
        :param exc_level: log level for exceptions
        :type exc_level: int
        :param log_before: log before operation
        :type log_before: bool
        :param log_success: log successful operations
        :type log_success: bool
        :param log_failure: log exceptions
        :type log_failure: bool
        :param log_traceback: Log traceback on exceptions
        :type log_traceback: bool
        :param override_name: override property name if not None else use getter/setter/deleter name
        :type override_name: typing.Optional[str]
        :param max_indent: maximal indent before classic repr() call
        :type max_indent: int

        Usage examples:

        >>> import logging
        >>> import io

        >>> log = io.StringIO()
        >>> logging.basicConfig(level=logging.DEBUG, stream=log)

        >>> class Test:
        ...     def __init__(self, val = 'ok'):
        ...         self.val = val
        ...     def __repr__(self):
        ...         return f'{self.__class__.__name__}(val={self.val})'
        ...     @LogOnAccess
        ...     def ok(self):
        ...         return self.val
        ...     @ok.setter
        ...     def ok(self, val):
        ...         self.val = val
        ...     @ok.deleter
        ...     def ok(self):
        ...         self.val = ''
        ...     @LogOnAccess
        ...     def fail_get(self):
        ...         raise RuntimeError()
        ...     @LogOnAccess
        ...     def fail_set_del(self):
        ...         return self.val
        ...     @fail_set_del.setter
        ...     def fail_set_del(self, value):
        ...         raise ValueError(value)
        ...     @fail_set_del.deleter
        ...     def fail_set_del(self):
        ...         raise RuntimeError()

        >>> test = Test()
        >>> test.ok
        'ok'
        >>> test.ok = 'OK'
        >>> del test.ok
        >>> test.ok = 'fail_get'

        >>> test.fail_get
        Traceback (most recent call last):
        ...
        RuntimeError

        >>> test.ok = 'fail_set_del'
        >>> test.fail_set_del
        'fail_set_del'

        >>> test.fail_set_del = 'fail'
        Traceback (most recent call last):
        ...
        ValueError: fail

        >>> del test.fail_set_del
        Traceback (most recent call last):
        ...
        RuntimeError

        >>> test.fail_set_del
        'fail_set_del'

        >>> logs = log.getvalue().splitlines()
        >>> logs[0] == "DEBUG:log_on_access:Test(val=ok).ok -> 'ok'"
        True
        >>> logs[1] == "DEBUG:log_on_access:Test(val=ok).ok = 'OK'"
        True
        >>> logs[2] == "DEBUG:log_on_access:del Test(val=OK).ok"
        True
        >>> logs[3] == "DEBUG:log_on_access:Test(val=).ok = 'fail_get'"
        True
        >>> logs[4:6]
        ['DEBUG:log_on_access:Failed Test(val=fail_get).fail_get', 'Traceback (most recent call last):']
        >>> logs[14] == "DEBUG:log_on_access:Test(val=fail_get).ok = 'fail_set_del'"
        True
        >>> logs[16] == "DEBUG:log_on_access:Failed Test(val=fail_set_del).fail_set_del = 'fail'"
        True
        >>> logs[17] == 'Traceback (most recent call last):'
        True
        >>> logs[26] == 'DEBUG:log_on_access:Test(val=fail_set_del): failed to delete fail_set_del'
        True
        >>> logs[27] == 'Traceback (most recent call last):'
        True
        """
        super(LogOnAccess, self).__init__(fget=fget, fset=fset, fdel=fdel, doc=doc)

        if logger is None or isinstance(logger, logging.Logger):
            self.__logger = logger  # type: typing.Optional[logging.Logger]
        else:
            self.__logger = logging.getLogger(logger)

        self.__log_object_repr = log_object_repr  # type: bool
        self.__log_level = log_level  # type: int
        self.__exc_level = exc_level  # type: int
        self.__log_before = log_before  # type: bool
        self.__log_success = log_success  # type: bool
        self.__log_failure = log_failure  # type: bool
        self.__log_traceback = log_traceback  # type: bool
        self.__override_name = override_name  # type: typing.Optional[str]
        self.__max_indent = max_indent  # type: int

    @property
    def __traceback(self) -> str:
        """Get outer traceback text for logging."""
        if not self.log_traceback:
            return ""
        exc_info = sys.exc_info()
        stack = traceback.extract_stack()  # type: traceback.StackSummary
        exc_tb = traceback.extract_tb(exc_info[2])  # type: traceback.StackSummary
        full_tb = stack[:1] + exc_tb  # cut decorator and build full traceback
        exc_line = traceback.format_exception_only(*exc_info[:2])  # type: typing.List[str]
        # Make standard traceback string
        tb_text = "\nTraceback (most recent call last):\n" + "".join(traceback.format_list(full_tb)) + "".join(exc_line)
        return tb_text

    def __get_obj_source(self, instance: typing.Any, owner: typing.Optional[type] = None) -> str:
        """Get object repr block."""
        if self.log_object_repr:
            return repr_utils.pretty_repr(instance, max_indent=self.max_indent)
        return "<{name}() at 0x{id:X}>".format(
            name=owner.__name__ if owner is not None else instance.__class__.__name__, id=id(instance)
        )

    def _get_logger_for_instance(self, instance: typing.Any) -> logging.Logger:
        """Get logger for log calls.

        :param instance: Owner class instance. Filled only if instance created, else None.
        :type instance: typing.Optional[owner]
        :return: logger instance
        :rtype: logging.Logger
        """
        if self.logger is not None:  # pylint: disable=no-else-return
            return self.logger
        valid_logger_names = ("logger", "log")
        for logger_name in valid_logger_names:
            logger_candidate = getattr(instance, logger_name, None)
            if isinstance(logger_candidate, logging.Logger):
                return logger_candidate
        instance_module = inspect.getmodule(instance)
        for logger_name in valid_logger_names:
            logger_candidate = getattr(instance_module, logger_name.upper(), None)
            if isinstance(logger_candidate, logging.Logger):
                return logger_candidate
        return _LOGGER

    def __get__(self, instance: typing.Any, owner: typing.Optional[type] = None) -> typing.Any:
        """Get descriptor.

        :param instance: Owner class instance. Filled only if instance created, else None.
        :type instance: typing.Optional[owner]
        :param owner: Owner class for property.
        :return: getter call result if getter presents
        :rtype: typing.Any
        :raises AttributeError: Getter is not available
        :raises Exception: Something goes wrong
        """
        if instance is None or self.fget is None:
            raise AttributeError()

        source = self.__get_obj_source(instance, owner)  # type: str
        logger = self._get_logger_for_instance(instance)  # type: logging.Logger

        timestamp = time.time()  # type: float
        try:
            if self.log_before:
                logger.log(self.log_level, "Request: {source}.{name}".format(source=source, name=self.__name__))
            result = super(LogOnAccess, self).__get__(instance, owner)
            if self.log_success:
                logger.log(
                    self.log_level,
                    "Done at {duration:.03f}s: "
                    "{source}.{name} -> {repr_val}".format(
                        duration=time.time() - timestamp,
                        source=source,
                        name=self.__name__,
                        repr_val=repr_utils.pretty_repr(result),
                    ),
                )
            return result
        except Exception:
            if self.log_failure:
                logger.log(
                    self.exc_level,
                    "Failed after {duration:.03f}s: {source}.{name}{exc_tb}".format(
                        duration=time.time() - timestamp, source=source, name=self.__name__, exc_tb=self.__traceback
                    ),
                    exc_info=False,
                )
            raise

    def __set__(self, instance: typing.Any, value: typing.Any) -> None:
        """Set descriptor.

        :param instance: Owner class instance. Filled only if instance created, else None.
        :type instance: typing.Optional
        :param value: Value for setter
        :raises AttributeError: Setter is not available
        :raises Exception: Something goes wrong
        """
        if self.fset is None:
            raise AttributeError()

        source = self.__get_obj_source(instance)  # type: str
        logger = self._get_logger_for_instance(instance)  # type: logging.Logger

        timestamp = time.time()  # type: float
        try:
            if self.log_before:
                logger.log(
                    self.log_level,
                    "Request: {source}.{name} = {repr_val}".format(
                        source=source, name=self.__name__, repr_val=repr_utils.pretty_repr(value)
                    ),
                )
            super(LogOnAccess, self).__set__(instance, value)
            if self.log_success:
                logger.log(
                    self.log_level,
                    "Done at {duration:.03f}s: "
                    "{source}.{name} = {repr_val}".format(
                        duration=time.time() - timestamp,
                        source=source,
                        name=self.__name__,
                        repr_val=repr_utils.pretty_repr(value),
                    ),
                )
        except Exception:
            if self.log_failure:
                logger.log(
                    self.exc_level,
                    "Failed after {duration:.03f}s: "
                    "{source}.{name} = {repr_val}{exc_tb}".format(
                        duration=time.time() - timestamp,
                        source=source,
                        name=self.__name__,
                        repr_val=repr_utils.pretty_repr(value),
                        exc_tb=self.__traceback,
                    ),
                    exc_info=False,
                )
            raise

    def __delete__(self, instance: typing.Any) -> None:
        """Delete descriptor.

        :param instance: Owner class instance. Filled only if instance created, else None.
        :type instance: typing.Optional
        :raises AttributeError: Deleter is not available
        :raises Exception: Something goes wrong
        """
        if self.fdel is None:
            raise AttributeError()

        source = self.__get_obj_source(instance)  # type: str
        logger = self._get_logger_for_instance(instance)  # type: logging.Logger

        timestamp = time.time()  # type: float
        try:
            if self.log_before:
                logger.log(self.log_level, "Request: del {source}.{name}".format(source=source, name=self.__name__))
            super(LogOnAccess, self).__delete__(instance)
            if self.log_success:
                logger.log(
                    self.log_level,
                    "Done at {duration:.03f}s: del {source}.{name}".format(
                        duration=time.time() - timestamp, source=source, name=self.__name__
                    ),
                )
        except Exception:
            if self.log_failure:
                logger.log(
                    self.exc_level,
                    "Failed after {duration:.03f}s: del {source}.{name}{exc_tb}".format(
                        duration=time.time() - timestamp, source=source, name=self.__name__, exc_tb=self.__traceback
                    ),
                    exc_info=False,
                )
            raise

    @property
    def logger(self) -> typing.Optional[logging.Logger]:
        """Logger instance to use as override."""
        return self.__logger

    @logger.setter
    def logger(self, logger: typing.Union[logging.Logger, str, None]) -> None:
        """Logger instance to use as override."""
        if logger is None or isinstance(logger, logging.Logger):
            self.__logger = logger
        else:
            self.__logger = logging.getLogger(logger)

    @property
    def log_object_repr(self) -> bool:
        """Use `repr` over object to describe owner if True else owner class name and id."""
        return self.__log_object_repr

    @log_object_repr.setter
    def log_object_repr(self, value: bool) -> None:
        """Use `repr` over object to describe owner if True else owner class name and id."""
        self.__log_object_repr = value

    @property
    def log_level(self) -> int:
        """Log level for successful operations."""
        return self.__log_level

    @log_level.setter
    def log_level(self, value: int) -> None:
        """Log level for successful operations."""
        self.__log_level = value

    @property
    def exc_level(self) -> int:
        """Log level for exceptions."""
        return self.__exc_level

    @exc_level.setter
    def exc_level(self, value: int) -> None:
        """Log level for exceptions."""
        self.__exc_level = value

    @property
    def log_before(self) -> bool:
        """Log successful operations."""
        return self.__log_before

    @log_before.setter
    def log_before(self, value: bool) -> None:
        """Log successful operations."""
        self.__log_before = value

    @property
    def log_success(self) -> bool:
        """Log successful operations."""
        return self.__log_success

    @log_success.setter
    def log_success(self, value: bool) -> None:
        """Log successful operations."""
        self.__log_success = value

    @property
    def log_failure(self) -> bool:
        """Log exceptions."""
        return self.__log_failure

    @log_failure.setter
    def log_failure(self, value: bool) -> None:
        """Log exceptions."""
        self.__log_failure = value

    @property
    def log_traceback(self) -> bool:
        """Log traceback on exceptions."""
        return self.__log_traceback

    @log_traceback.setter
    def log_traceback(self, value: bool) -> None:
        """Log traceback on exceptions."""
        self.__log_traceback = value

    @property
    def override_name(self) -> typing.Optional[str]:
        """Override property name if not None else use getter/setter/deleter name."""
        return self.__override_name

    @override_name.setter
    def override_name(self, name: typing.Optional[str]) -> None:
        """Override property name if not None else use getter/setter/deleter name."""
        self.__override_name = name

    @property
    def max_indent(self) -> int:
        """Max indent during repr."""
        return self.__max_indent

    @max_indent.setter
    def max_indent(self, value: int) -> None:
        """Max indent during repr."""
        self.__max_indent = value

    @property
    def __name__(self) -> str:
        """Name getter."""
        return (
            self.override_name or self.fget.__name__
            if self.fget
            else self.fset.__name__
            if self.fset
            else self.fdel.__name__
            if self.fdel
            else ""
        )


if __name__ == "__main__":  # pragma: no cover
    import doctest

    doctest.testmod(verbose=True)
