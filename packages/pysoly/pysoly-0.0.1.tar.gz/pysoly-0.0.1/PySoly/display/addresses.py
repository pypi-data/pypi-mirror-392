import win32gui
import win32process
import pymem
import pymem.process

class Helper:
	def __init__(self):
		self.hwnd = None
		self.pid = None
		self.pm = None
		self.base_addr = None
		self.modules = {}

	# ------------------------------ WINDOW ATTACH ------------------------------

	def _find_window_by_title(self, title: str):
		found = {"hwnd": None}

		def enum_callback(hwnd, search_title):
			if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
				txt = win32gui.GetWindowText(hwnd)
				if search_title.lower() in txt.lower():
					found["hwnd"] = hwnd
					return False
			return True

		win32gui.EnumWindows(enum_callback, title)

		if not found["hwnd"]:
			return None, None

		_, pid = win32process.GetWindowThreadProcessId(found["hwnd"])
		return found["hwnd"], pid

	def attach(self, title: str) -> bool:
		"""
		Ищет окно по названию, открывает процесс через pymem.
		"""
		try:
			self.hwnd, self.pid = self._find_window_by_title(title)
			if not self.hwnd or not self.pid:
				return False

			self.pm = pymem.Pymem()
			self.pm.open_process_from_id(self.pid)

			self._load_modules()
			self.base_addr = pymem.process.module_from_name(self.pm.process_handle, self._main_module())["lpBaseOfDll"]

			return True
		except:
			return False

	def is_attached(self) -> bool:
		return self.pm is not None

	def refresh(self) -> bool:
		"""
		Переоткрывает процесс, если он закрыт.
		"""
		try:
			if not self.pid:
				return False

			self.pm = pymem.Pymem()
			self.pm.open_process_from_id(self.pid)

			self._load_modules()
			self.base_addr = pymem.process.module_from_name(self.pm.process_handle, self._main_module())["lpBaseOfDll"]
			return True
		except:
			return False

	# ------------------------------ MODULES ------------------------------

	def _main_module(self) -> str:
		for name in self.modules:
			if name.lower().endswith(".exe"):
				return name
		return list(self.modules.keys())[0]

	def _load_modules(self):
		self.modules = {}
		for mod in pymem.process.list_modules(self.pm.process_handle):
			self.modules[mod.name] = mod.lpBaseOfDll

	def get_module_base(self, module_name: str):
		return self.modules.get(module_name, None)

	# ------------------------------ POINTER CHAIN ------------------------------

	def read_ptr(self, base: int, offsets: list) -> int | None:
		"""
		Читает указатель по цепочке.
		"""
		try:
			addr = base
			for off in offsets:
				addr = self.pm.read_int(addr) + off
			return addr
		except:
			return None

	# ------------------------------ READ METHODS ------------------------------

	def read_int(self, addr: int) -> int | None:
		try:
			return self.pm.read_int(addr)
		except:
			return None

	def read_float(self, addr: int) -> float | None:
		try:
			return self.pm.read_float(addr)
		except:
			return None

	def read_double(self, addr: int) -> float | None:
		try:
			return self.pm.read_double(addr)
		except:
			return None

	def read_bytes(self, addr: int, size: int) -> bytes | None:
		try:
			return self.pm.read_bytes(addr, size)
		except:
			return None

	def read_string(self, addr: int, size: int = 64) -> str | None:
		try:
			data = self.pm.read_bytes(addr, size)
			return data.split(b'\x00')[0].decode(errors="ignore")
		except:
			return None

	# ------------------------------ WRITE METHODS ------------------------------

	def write_int(self, addr: int, value: int) -> bool:
		try:
			self.pm.write_int(addr, value)
			return True
		except:
			return False

	def write_float(self, addr: int, value: float) -> bool:
		try:
			self.pm.write_float(addr, value)
			return True
		except:
			return False

	def write_double(self, addr: int, value: float) -> bool:
		try:
			self.pm.write_double(addr, value)
			return True
		except:
			return False

	def write_bytes(self, addr: int, data: bytes) -> bool:
		try:
			self.pm.write_bytes(addr, data)
			return True
		except:
			return False

	def write_string(self, addr: int, text: str) -> bool:
		try:
			data = text.encode() + b"\x00"
			self.pm.write_bytes(addr, data)
			return True
		except:
			return False

	# ------------------------------ INFO ------------------------------

	def get_hwnd(self):
		return self.hwnd

	def get_pid(self):
		return self.pid

	def get_base(self):
		return self.base_addr

	# ------------------------------ CLOSE ------------------------------

	def detach(self):
		try:
			if self.pm:
				self.pm.close_process()
			self.pm = None
			self.hwnd = None
			self.pid = None
			self.base_addr = None
			self.modules = {}
			return True
		except:
			return False