#!/usr/bin/env python
# Copyright (C) 2015 Swift Navigation Inc.
# Contact: Bhaskar Mookerji <mookerji@swiftnav.com>
#
# This source is subject to the license found in the file 'LICENSE' which must
# be be distributed together with this source. All other rights reserved.
#
# THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND,
# EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A PARTICULAR PURPOSE.

from sbp import SBP
from sbp.client.drivers.file_driver import FileDriver
from sbp.client.loggers.base_logger import LogIterator
from sbp.client.loggers.json_logger import JSONLogIterator
from sbp.client.loggers.pickle_logger import PickleLogIterator
from sbp.piksi import SBP_MSG_PRINT
from sbp.table import _SBP_TABLE, dispatch
from sbp.table import InvalidSBPMessageType
import pytest

def test_log():
  """
  Abstract interface won't work
  """
  log_datafile = "./data/serial_link_log_20141125-150750_test1.log.dat"
  with LogIterator(FileDriver(log_datafile)) as log:
    with pytest.raises(NotImplementedError) as exc_info:
      for delta, timestamp, msg in log.next():
        pass
  assert exc_info.value.message == "next() not implemented!"

def test_pickle_log():
  """
  pickle log iterator sanity tests.
  """
  log_datafile = "./data/serial_link_log_20141125-150750_test1.log.dat"
  count = 0
  with PickleLogIterator(FileDriver(log_datafile)) as log:
    for delta, timestamp, msg in log.next():
      assert type(delta) == int
      assert type(timestamp) == int
      assert issubclass(type(msg), SBP)
      count += 1
  assert count == 1111

def test_basic_pickle_log():
  """
  pickle log iterator sanity tests with a normal handle.
  """
  log_datafile = "./data/serial_link_log_20141125-150750_test1.log.dat"
  count = 0
  with open(log_datafile, 'r+') as f:
    with PickleLogIterator(f) as log:
      for delta, timestamp, msg in log.next():
        assert type(delta) == int
        assert type(timestamp) == int
        assert issubclass(type(msg), SBP)
        count += 1
  assert count == 1111

def test_json_log():
  """
  JSON log iterator sanity tests.
  """
  log_datafile = "./data/serial_link_log_20150310-115522-test.log.dat"
  count = 0
  with JSONLogIterator(FileDriver(log_datafile)) as log:
    for delta, timestamp, msg in log.next():
      assert type(delta) == int
      assert type(timestamp) == int
      assert issubclass(type(msg), SBP)
      count += 1
  assert count == 2650

def test_pickle_log_missing():
  """
  Remove a key from the dispatch and make sure that the iterator
  chokes.

  """
  log_datafile = "./data/serial_link_log_20141125-150750_test1.log.dat"
  new_table = _SBP_TABLE.copy()
  new_table.pop(SBP_MSG_PRINT, None)
  d = lambda msg: dispatch(msg, table=new_table)
  with PickleLogIterator(FileDriver(log_datafile), dispatcher=d) as log:
    with pytest.raises(InvalidSBPMessageType) as exc_info:
      for delta, timestamp, msg in log.next():
        pass
  assert str(exc_info.value).find("No message found for msg_type id 16*")
