# pylint: skip-file

# Standard Library
import io
import logging
import unittest

# LogWrap Implementation
import logwrap


VALUE = "ok"


class TestLogOnAccess(unittest.TestCase):
    def setUp(self):
        self.stream = io.StringIO()
        logging.getLogger().handlers.clear()
        logging.basicConfig(level=logging.DEBUG, stream=self.stream)

    def tearDown(self):
        logging.getLogger().handlers.clear()
        self.stream.close()

    def test_01_positive(self):
        class Target:
            def __init__(tself, val=VALUE):
                tself.val = val

            def __repr__(tself):
                return "{cls}(val={tself.val})".format(cls=tself.__class__.__name__, tself=tself)

            @logwrap.LogOnAccess
            def ok(tself):
                return tself.val

            @ok.setter
            def ok(tself, val):
                tself.val = val

            @ok.deleter
            def ok(tself):
                tself.val = ""

        target = Target()
        self.assertEqual(target.ok, VALUE)
        self.assertEqual(
            self.stream.getvalue(),
            "DEBUG:logwrap.log_on_access:Target(val=ok).ok -> {pr_val}\n".format(pr_val=logwrap.pretty_repr(VALUE))
        )

        self.stream.seek(0)
        self.stream.truncate()

        target.ok = VALUE.upper()
        self.assertEqual(
            self.stream.getvalue(),
            "DEBUG:logwrap.log_on_access:Target(val=ok).ok = {pr_val}\n".format(
                pr_val=logwrap.pretty_repr(VALUE.upper())
            ),
        )

        self.assertEqual(target.ok, VALUE.upper())

        self.stream.seek(0)
        self.stream.truncate()

        del target.ok
        self.assertEqual(self.stream.getvalue(), "DEBUG:logwrap.log_on_access:del Target(val=OK).ok\n")

    def test_02_positive_properties(self):
        class Target:
            def __init__(tself, val=VALUE):
                tself.val = val

            def __repr__(tself):
                return "{cls}(val={tself.val})".format(cls=tself.__class__.__name__, tself=tself)

            @logwrap.LogOnAccess
            def ok(tself):
                return tself.val

            ok.log_level = logging.INFO
            ok.log_object_repr = False
            ok.override_name = "override"

        target = Target()

        self.assertEqual(target.ok, VALUE)
        self.assertEqual(
            self.stream.getvalue(),
            "INFO:logwrap.log_on_access:<Target() at 0x{id:X}>.override -> {pr_val}\n".format(
                id=id(target), pr_val=logwrap.pretty_repr(VALUE)
            ),
        )

    def test_03_positive_no_log(self):
        class Target:
            def __init__(tself, val=VALUE):
                tself.val = val

            def __repr__(tself):
                return "{cls}(val={tself.val})".format(cls=tself.__class__.__name__, tself=tself)

            @logwrap.LogOnAccess
            def ok(tself):
                return tself.val

            ok.log_success = False

        target = Target()

        self.assertEqual(target.ok, VALUE)
        self.assertEqual(self.stream.getvalue(), "")

    def test_04_negative(self):
        class Target:
            def __repr__(tself):
                return "{cls}()".format(cls=tself.__class__.__name__)

            @logwrap.LogOnAccess
            def ok(tself):
                raise AttributeError()

            @ok.setter
            def ok(tself, val):
                raise ValueError(val)

            @ok.deleter
            def ok(tself):
                raise RuntimeError()

        target = Target()

        with self.assertRaises(AttributeError):
            self.assertIsNone(target.ok)

        self.assertEqual(self.stream.getvalue().splitlines()[0], "DEBUG:logwrap.log_on_access:Failed: Target().ok")
        self.assertEqual(self.stream.getvalue().splitlines()[1], "Traceback (most recent call last):")

        self.stream.seek(0)
        self.stream.truncate()

        with self.assertRaises(ValueError):
            target.ok = VALUE

        self.assertEqual(
            self.stream.getvalue().splitlines()[0],
            "DEBUG:logwrap.log_on_access:Failed: Target().ok = {pr_val}".format(pr_val=logwrap.pretty_repr(VALUE)),
        )

        self.stream.seek(0)
        self.stream.truncate()

        with self.assertRaises(RuntimeError):
            del target.ok

        self.assertEqual(self.stream.getvalue().splitlines()[0], "DEBUG:logwrap.log_on_access:Target(): Failed: del ok")

    def test_05_negative_properties(self):
        class Target:
            def __init__(tself, val=VALUE):
                tself.val = val

            def __repr__(tself):
                return "{cls}(val={tself.val})".format(cls=tself.__class__.__name__, tself=tself)

            @logwrap.LogOnAccess
            def ok(tself):
                raise AttributeError()

            ok.exc_level = logging.ERROR
            ok.log_traceback = False
            ok.log_object_repr = False
            ok.override_name = "override"

        target = Target()

        with self.assertRaises(AttributeError):
            self.assertIsNone(target.ok)

        self.assertEqual(
            self.stream.getvalue().splitlines()[0],
            "ERROR:logwrap.log_on_access:Failed: <Target() at 0x{id:X}>.override".format(id=id(target)),
        )
        self.assertEqual(len(self.stream.getvalue().splitlines()), 1)

    def test_06_negative_no_log(self):
        class Target:
            def __init__(tself, val=VALUE):
                tself.val = val

            def __repr__(tself):
                return "{cls}(val={tself.val})".format(cls=tself.__class__.__name__, tself=tself)

            @logwrap.LogOnAccess
            def ok(tself):
                raise AttributeError()

            ok.log_failure = False

        target = Target()

        with self.assertRaises(AttributeError):
            self.assertIsNone(target.ok)

        self.assertEqual(self.stream.getvalue(), "")

    def test_07_property_mimic(self):
        class Target:
            def __repr__(tself):
                return "{cls}()".format(cls=tself.__class__.__name__)

            empty = logwrap.LogOnAccess(doc="empty_property")

        target = Target()

        with self.assertRaises(AttributeError):
            self.assertIsNone(target.empty)

        with self.assertRaises(AttributeError):
            target.empty = None

        with self.assertRaises(AttributeError):
            del target.empty

        self.assertEqual(self.stream.getvalue(), "")

    def test_08_logger(self):
        v_on_init_set = "on_init_set"
        v_on_init_name = "on_init_name"
        v_prop_set = "prop_set"
        v_prop_name = "prop_name"

        class Target:
            on_init_set = logwrap.LogOnAccess(logger=logging.getLogger(v_on_init_set), fget=lambda self: v_on_init_set)
            on_init_name = logwrap.LogOnAccess(logger=v_on_init_name, fget=lambda self: v_on_init_name)

            @logwrap.LogOnAccess
            def prop_set(self):
                return v_prop_set

            prop_set.logger = logging.getLogger(v_prop_set)

            @logwrap.LogOnAccess
            def prop_name(self):
                return v_prop_name

            prop_name.logger = v_prop_name

            def __repr__(tself):
                return "{cls}()".format(cls=tself.__class__.__name__)

        target = Target()

        getattr(target, "on_init_set")  # noqa: B009
        self.assertEqual(
            self.stream.getvalue(), "DEBUG:on_init_set:Target().<lambda> -> {pr_val}\n".format(
                pr_val=logwrap.pretty_repr(v_on_init_set)
            )
        )

        self.stream.seek(0)
        self.stream.truncate()

        getattr(target, "on_init_name")  # noqa: B009
        self.assertEqual(
            self.stream.getvalue(), "DEBUG:on_init_name:Target().<lambda> -> {pr_val}\n".format(
                pr_val=logwrap.pretty_repr(v_on_init_name)
            )
        )

        self.stream.seek(0)
        self.stream.truncate()

        getattr(target, "prop_set")  # noqa: B009
        self.assertEqual(
            self.stream.getvalue(), "DEBUG:prop_set:Target().prop_set -> {pr_val}\n".format(
                pr_val=logwrap.pretty_repr(v_prop_set)
            )
        )

        self.stream.seek(0)
        self.stream.truncate()

        getattr(target, "prop_name")  # noqa: B009
        self.assertEqual(
            self.stream.getvalue(), "DEBUG:prop_name:Target().prop_name -> {pr_val}\n".format(
                pr_val=logwrap.pretty_repr(v_prop_name)
            )
        )

    def test_09_logger_implemented(self):
        class Target:
            def __init__(tself, val=VALUE):
                tself.val = val
                tself.logger = logging.getLogger(tself.__class__.__name__)

            def __repr__(tself):
                return "{cls}(val={tself.val})".format(cls=tself.__class__.__name__, tself=tself)

            @logwrap.LogOnAccess
            def ok(tself):
                return tself.val

            @ok.setter
            def ok(tself, val):
                tself.val = val

            @ok.deleter
            def ok(tself):
                tself.val = ""

        target = Target()
        self.assertEqual(target.ok, VALUE)
        self.assertEqual(
            self.stream.getvalue(),
            "DEBUG:Target:Target(val=ok).ok -> {pr_val}\n".format(pr_val=logwrap.pretty_repr(VALUE))
        )

        self.stream.seek(0)
        self.stream.truncate()

        target.ok = VALUE.upper()
        self.assertEqual(
            self.stream.getvalue(),
            "DEBUG:Target:Target(val=ok).ok = {pr_val}\n".format(pr_val=logwrap.pretty_repr(VALUE.upper()))
        )

        self.assertEqual(target.ok, VALUE.upper())

        self.stream.seek(0)
        self.stream.truncate()

        del target.ok
        self.assertEqual(self.stream.getvalue(), "DEBUG:Target:del Target(val=OK).ok\n")

    def test_10_log_implemented(self):
        class Target:
            def __init__(tself, val=VALUE):
                tself.val = val
                tself.log = logging.getLogger(tself.__class__.__name__)

            def __repr__(tself):
                return "{cls}(val={tself.val})".format(cls=tself.__class__.__name__, tself=tself)

            @logwrap.LogOnAccess
            def ok(tself):
                return tself.val

            @ok.setter
            def ok(tself, val):
                tself.val = val

            @ok.deleter
            def ok(tself):
                tself.val = ""

        target = Target()
        self.assertEqual(target.ok, VALUE)
        self.assertEqual(
            self.stream.getvalue(),
            "DEBUG:Target:Target(val=ok).ok -> {pr_val}\n".format(pr_val=logwrap.pretty_repr(VALUE))
        )

        self.stream.seek(0)
        self.stream.truncate()

        target.ok = VALUE.upper()
        self.assertEqual(
            self.stream.getvalue(),
            "DEBUG:Target:Target(val=ok).ok = {pr_val}\n".format(pr_val=logwrap.pretty_repr(VALUE.upper()))
        )

        self.assertEqual(target.ok, VALUE.upper())

        self.stream.seek(0)
        self.stream.truncate()

        del target.ok
        self.assertEqual(self.stream.getvalue(), "DEBUG:Target:del Target(val=OK).ok\n")