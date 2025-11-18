from typing import Tuple

import win32gui
import win32con
import win32ui
import win32api
import numpy as np
from PIL import Image

class Helper:
	def __init__(self, normalized: bool = True):
		self.hwnd = None
		self.normalized = bool(normalized)

	def set_hwnd_by_pid(self, pid: int) -> bool:
		"""
		Устанавливает hwnd по pid процесса. Возвращает True если найдено, иначе False.
		"""
		if not win32gui:
			return False
		try:
			def enum_windows_callback(hwnd, pid_target):
				if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
					_, found_pid = win32gui.GetWindowThreadProcessId(hwnd)
					if found_pid == pid_target:
						self.hwnd = hwnd
						return False
				return True

			win32gui.EnumWindows(enum_windows_callback, pid)
			return self.hwnd is not None
		except Exception:
			return False

	def set_hwnd_by_title(self, title: str) -> bool:
		"""
		Устанавливает hwnd по названию окна. Возвращает True если найдено, иначе False.
		"""
		if not win32gui:
			return False
		try:
			def enum_windows_callback(hwnd, search_title):
				if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
					window_text = win32gui.GetWindowText(hwnd)
					if search_title.lower() in window_text.lower():
						self.hwnd = hwnd
						return False
				return True
	
			self.hwnd = None
			win32gui.EnumWindows(enum_windows_callback, title)
			return self.hwnd is not None
		except Exception:
			return False

	def set_normalized(self, normalized: bool) -> bool:
		try:
			self.normalized = normalized
			return True
		except:
			return False

	def _get_client_size_and_origin(self):
		try:
			if not self.hwnd:
				return False, "hwnd is not set"
			cr = win32gui.GetClientRect(self.hwnd)
			w = cr[2] - cr[0]
			h = cr[3] - cr[1]
			left_top = win32gui.ClientToScreen(self.hwnd, (0, 0))
			return (left_top[0], left_top[1], w, h), None
		except Exception as e:
			return False, f"_get_client_size_and_origin error: {str(e)}"

	def _scale_coords_to_client(self, coords) -> Tuple[int,int]:
		if isinstance(coords, tuple) or isinstance(coords, list):
			x, y = coords
		else:
			x, y = coords, coords
	
		info, err = self._get_client_size_and_origin()
		if err:
			raise RuntimeError(err)
		_, _, w, h = info
		if self.normalized:
			x_client = int(round(x * w))
			y_client = int(round(y * h))
		else:
			x_client = int(round(x))
			y_client = int(round(y))
		x_client = max(0, min(x_client, w))
		y_client = max(0, min(y_client, h))
		return x_client, y_client

	def screenshot(self):
		try:
			if not self.hwnd:
				return False, "hwnd is not set"
			left, top, right, bottom = win32gui.GetClientRect(self.hwnd)
			width = right - left
			height = bottom - top

			hwnd_dc = win32gui.GetWindowDC(self.hwnd)
			mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
			mem_dc = mfc_dc.CreateCompatibleDC()

			bmp = win32ui.CreateBitmap()
			bmp.CreateCompatibleBitmap(mfc_dc, width, height)
			mem_dc.SelectObject(bmp)

			mem_dc.BitBlt((0, 0), (width, height), mfc_dc, (0, 0), win32con.SRCCOPY)

			bmp_info = bmp.GetInfo()
			bmp_str = bmp.GetBitmapBits(True)
			img = Image.frombuffer(
				'RGB',
				(bmp_info['bmWidth'], bmp_info['bmHeight']),
				bmp_str, 'raw', 'BGRX', 0, 1
			)
			mem_dc.DeleteDC()
			mfc_dc.DeleteDC()
			win32gui.ReleaseDC(self.hwnd, hwnd_dc)
			win32gui.DeleteObject(bmp.GetHandle())

			return img, None
		except Exception as e:
			return False, f"screenshot error: {str(e)}"

	def click(self, coords) -> bool:
		try:
			if not self.hwnd:
				return False
			x_client, y_client = self._scale_coords_to_client(coords)
			lparam = (y_client << 16) | (x_client & 0xFFFF)
			win32gui.PostMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lparam)
			win32gui.PostMessage(self.hwnd, win32con.WM_LBUTTONUP, 0, lparam)
			return True
		except Exception:
			return False

	def get_color(self, coords: tuple):
		try:
			if not self.hwnd:
				return None
			x, y = self._scale_coords_to_client(coords)

			hdc_window = win32gui.GetWindowDC(self.hwnd)
			color_bgr = win32gui.GetPixel(hdc_window, x, y)
			win32gui.ReleaseDC(self.hwnd, hdc_window)

			r, g, b = (color_bgr & 0xFF), ((color_bgr >> 8) & 0xFF), ((color_bgr >> 16) & 0xFF)
			return (r << 16) + (g << 8) + b
		except:
			return None

	def get_value(self, coord1, coord2, frmt):
		if isinstance(frmt, int):
			return 0

		elif isinstance(frmt, float):
			return self._get_float_value(coord1, coord2)

	def _get_float_value(self, coord1, coord2):
		try:
			x1c, y1c = self._scale_coords_to_client(coord1)
			x2c, y2c = self._scale_coords_to_client(coord2)
			left, top = min(x1c, x2c), min(y1c, y2c)
			width, height = abs(x2c - x1c), abs(y2c - y1c)
	
			hwnd_dc = win32gui.GetWindowDC(self.hwnd)
			mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
			mem_dc = mfc_dc.CreateCompatibleDC()
	
			bmp = win32ui.CreateBitmap()
			bmp.CreateCompatibleBitmap(mfc_dc, width, height)
			mem_dc.SelectObject(bmp)
	
			mem_dc.BitBlt((0, 0), (width, height), mfc_dc, (left, top), win32con.SRCCOPY)
	
			bmp_bits = bmp.GetBitmapBits(True)
			arr = np.frombuffer(bmp_bits, dtype=np.uint8)
			arr = arr.reshape((height, width, 4))
			gray = 255 - (0.299*arr[:,:,2] + 0.587*arr[:,:,1] + 0.114*arr[:,:,0])
			avg = gray.mean()
			value = round((avg / 255) * 100, 2)
	
			mem_dc.DeleteDC()
			mfc_dc.DeleteDC()
			win32gui.ReleaseDC(self.hwnd, hwnd_dc)
			win32gui.DeleteObject(bmp.GetHandle())
	
			return float(value)
		except:
			return None