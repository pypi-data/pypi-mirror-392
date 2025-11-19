# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.
import numpy as np
from blissdata.exceptions import (
    IndexNoMoreThereError,
    UnknownEncodingError,
    MissingPluginException,
)
from . import EventRange, StreamDefinition, BaseStream, BaseView
from .encoding.numeric import NumericStreamEncoder
from .encoding.json import JsonStreamEncoder


class View(BaseView):
    def __init__(self, event_range: EventRange):
        self._events = event_range

    @property
    def index(self) -> int:
        return self._events.index

    def __len__(self) -> int:
        return len(self._events)

    def __iter__(self):
        yield from self.get_data()

    def get_data(self, start=None, stop=None):
        trimmed_range = range(len(self))[start:stop]
        offset = self._events.nb_expired
        data_start = trimmed_range.start - offset
        data_stop = trimmed_range.stop - offset
        if data_start < 0:
            raise IndexNoMoreThereError
        else:
            return self._events.data[data_start:data_stop]


class Stream(BaseStream):
    def __init__(self, event_stream):
        super().__init__(event_stream)
        if event_stream.encoding["type"] == "numeric":
            self._kind = "array"
        elif event_stream.encoding["type"] == "json":
            self._kind = "json"
        else:
            raise UnknownEncodingError(
                f"Unknow stream encoding {event_stream.encoding}"
            )

    @staticmethod
    def make_definition(name, dtype, shape=None, info={}) -> StreamDefinition:
        if dtype == "json":
            if shape is None:
                return StreamDefinition(name, info, JsonStreamEncoder())
            else:
                raise ValueError("JSON stream cannot have shape")
        else:
            if shape is None:
                shape = ()
            info = info.copy()
            info["dtype"] = np.dtype(dtype).name
            info["shape"] = shape
            return StreamDefinition(name, info, NumericStreamEncoder(dtype, shape))

    @property
    def kind(self):
        return self._kind

    @property
    def plugin(self):
        None

    @property
    def dtype(self):
        return self.event_stream.dtype

    @property
    def shape(self):
        return self.event_stream.shape

    def __len__(self):
        return len(self._event_stream)

    def __getitem__(self, key):
        return self._event_stream[key]

    def _need_last_only(self, last_only):
        return last_only

    def _build_view_from_events(self, index, events: EventRange, last_only):
        # NOTE event_range is never empty
        return View(events)


class BrokenStream(BaseStream):
    def __init__(self, event_stream, plugin_name, exception, kind):
        self._event_stream = event_stream
        self._plugin_name = plugin_name
        self._exception = exception
        self._kind = kind

    @property
    def kind(self):
        self._kind

    @staticmethod
    def make_definition(*args, **kwargs) -> StreamDefinition:
        raise NotImplementedError

    @property
    def plugin(self):
        return self._plugin_name

    @property
    def dtype(self):
        raise self._exception

    @property
    def shape(self):
        raise self._exception

    def __len__(self):
        raise self._exception

    def __getitem__(self, key):
        raise self._exception

    def _need_last_only(self, last_only):
        raise self._exception

    def _build_view_from_events(
        self, hl_index: int, events: EventRange, last_only: bool
    ):
        raise self._exception


class BrokenPluginStream(BrokenStream):
    """A stream class instanciated in place of a plugin, if it can't be
    instantiated. A warning is issued, but the scan object is not affected,
    ensuring memory tracker robustness against plugins."""

    def __init__(self, event_stream, plugin_name, exception):
        super().__init__(event_stream, plugin_name, exception, "broken_plugin")


class MissingPluginStream(BrokenStream):
    """A stream class instanciated in place of a plugin if not installed."""

    def __init__(self, event_stream, plugin_name):
        super().__init__(
            event_stream,
            plugin_name,
            MissingPluginException(event_stream.name, plugin_name),
            "missing_plugin",
        )
