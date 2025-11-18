#
# Stanislav Georgiev, Softel Labs
#
# This is a proprietary file and may not be copied,
# distributed, or modified without express permission
# from the owner. For licensing inquiries, please
# contact s.georgiev@softel.bg.
#
# 2025
#

import time
from pymodbus.client import ModbusTcpClient
from sciveo.tools.logger import *
from sciveo.tools.daemon import DaemonBase
from sciveo.monitoring.power.tools import *


class PowerEMS300(DaemonBase):
  def __init__(self, host, port=502, device_id=247, delay=0.01, period=30):
    super().__init__(period=period)
    self.host = host
    self.port = port
    self.device_id = device_id
    self.delay = delay
    self.client = None

    self.client = ModbusTcpClient(host=self.host, port=self.port)
    self.connected = False

  def connect(self):
    if not (self.connected or self.client.connect()):
      error("Connect FAIL", (self.host, self.port))
      self.connected = False
    else:
      self.connected = True
    return self.connected

  def loop(self):
    self.connect()
    if not self.connected:
      warning("Not connected", (self.host, self.port))
      return

    try:
      # iterate known addresses in map (sorted)
      for addr in sorted(REG_MAP.keys()):
        dtype, factor, name = REG_MAP[addr]
        count = count_for_type(dtype)
        protocol_addr = addr - 1  # doc addresses start at 1; pymodbus expects zero-based
        try:
          rr = self.client.read_input_registers(address=protocol_addr, count=count, device_id=self.device_id)
          if rr is None:
            warning(f"No response for {addr} ({name})")
            continue
          if hasattr(rr, "isError") and rr.isError():
            warning(f"Modbus exception at {addr} ({name}): {rr}")
            continue
          regs = getattr(rr, "registers", None)
          if not regs or len(regs) < count:
            warning(f"Incomplete registers at {addr} ({name}): {regs}")
            continue

          val_raw = decode_registers(regs, dtype)
          if val_raw is None:
            warning(f"Unable to decode {addr} ({name}) regs={regs}")
            continue
          # apply factor
          value = val_raw * factor
          # format integer-looking floats without trailing .0
          if isinstance(value, float) and value.is_integer():
            value = int(value)
          info(f"{addr} {name}: raw={regs} -> {value} (factor={factor}, type={dtype})")
        except Exception as e:
          error(f"Error reading {addr} ({name}): {e}")
        time.sleep(self.delay)

      # Optionally scan remaining addresses 8000..8200 for any non-zero single-register values
      info("\nQuick scan for single-register non-zero values (8000..8200):")
      for addr in range(8000, 8201):
        if addr in REG_MAP:
          continue
        try:
          rr = self.client.read_input_registers(address=addr - 1, count=1, device_id=self.device_id)
          if rr is None:
            continue
          if hasattr(rr, "isError") and rr.isError():
            continue
          regs = getattr(rr, "registers", None)
          if regs and regs[0] != 0:
            info(f"{addr}: {regs[0]} (0x{regs[0]:04X})")
        except Exception:
          pass
        time.sleep(0.005)
    except Exception as e:
      exception(e)

  def close(self):
    self.client.close()


if __name__ == "__main__":

  mon = PowerEMS300(host="localhost", port=1502, period=10)
  mon.start()

  while(True):
    time.sleep(30)
