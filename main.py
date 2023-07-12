import asyncio
import aiohttp


class Flashlight:
	"""Flashlight"""
	def __init__(self):
		self.commands = {
			"ON": self.change_flashlight_state_command,
			"OFF": self.change_flashlight_state_command,
			"COLOR": self.change_flashlight_color_command
		}

		self.current_status = 'OFF'
		self.current_color = 0

	def validation_and_run_command(self, command: str, metadata: float) -> None:
		if command in self.commands:
				self.commands[command](command=command, metadata=metadata)
				self.get_current_status_and_color_flashlight()

	def change_flashlight_state_command(self, **data):
		self.current_status = data['command']

	def change_flashlight_color_command(self, **data):
		self.current_color = data['metadata']

	def get_current_status_and_color_flashlight(self):
		print('Статус состояния фонарика: {}\nЦвет света: {}\n'.format(self.current_status, self.current_color))

class FCP(Flashlight):
	"""Flashlight Control Protocol"""
	def __init__(self, host_port):
		super().__init__()

		self.url = "ws://" + host_port
		self.session = aiohttp.ClientSession()

	async def listening(self):
		try:
			async with self.session.ws_connect(self.url) as websocket:
				async for message in websocket:
					if message.type == aiohttp.WSMsgType.TEXT:
						try:
							data = message.json()
							self.validation_and_run_command(data['command'], data['metadata'])
						except Exception:
							pass
					elif message.type == aiohttp.WSMsgType.CLOSED:
						print('Соединение с сервером прекращено')
						break
					elif message.type == aiohttp.WSMsgType.ERROR:
						print('Соединение с сервером прекращено с ошибкой %s' % websocket.exception())
						break
		except aiohttp.client_exceptions.ClientConnectorError:
			print("Не удалось подключиться к серверу")
		except aiohttp.client_exceptions.InvalidURL:
			print("Некорректный url")
		except aiohttp.client_exceptions.ServerDisconnectedError:
			print("Соединение с сервером прервано")

async def main():
	while True:
		txt = input("Введите хост и порт или exit для выхода: ") or "127.0.0.1:9999"
		if txt == "exit":
			break

		fcp = FCP(txt)
		await fcp.listening()


if __name__ == '__main__':
	asyncio.run(main())