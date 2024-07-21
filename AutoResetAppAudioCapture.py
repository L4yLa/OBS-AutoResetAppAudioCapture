import sys
import asyncio

# OBS integration
import simpleobsws as obsws
# sched run
import time

# .env
import os
from os.path import join, dirname
from dotenv import load_dotenv
if os.path.exists('./.env') == False:
	print('[ERROR] .envファイルが見つかりません。終了します。')
	time.sleep(3)
	sys.exit()
load_dotenv()



# data storage
class BotGlobalData:
	def __init__(self):	
		self.OBSHost = os.environ.get('OBSHost')
		self.OBSPort = os.environ.get('OBSPort')
		self.OBSPass = os.environ.get('OBSPass')
		self.obsConnected = False
		self.ws = None
		self.fQuit = False
		self.wasapicaptures = []
		self.currentscene = ''
		self.currentwasapicaptureID = []
		self.currentwasapicaptureEN = []
		self.timethread = None
		self.delaytimef = float(os.environ.get('IntervalSec'))

	async def resetAppAudioCapture(self):
		await asyncio.sleep(dat.delaytimef)
		request = obsws.Request('GetCurrentProgramScene')
		ret = await dat.ws.call(request)
		if dat.currentscene != ret.responseData['currentProgramSceneName']:
			dat.currentscene = ret.responseData['currentProgramSceneName']
			print("シーンが変更されています。変更後シーン名：", end='')
			print(dat.currentscene)
			dat.currentwasapicaptureID.clear()
			dat.currentwasapicaptureEN.clear()
			request = obsws.Request('GetSceneItemList', {'sceneName': dat.currentscene})
			ret = await dat.ws.call(request)
			for idx in ret.responseData['sceneItems']:
				if idx['sourceName'] in dat.wasapicaptures:
					dat.currentwasapicaptureID.append(idx['sceneItemId'])
			for idx in dat.currentwasapicaptureID:
				request = obsws.Request('GetSceneItemEnabled', {'sceneName': dat.currentscene, 'sceneItemId': idx})
				ret = await dat.ws.call(request)
				dat.currentwasapicaptureEN.append(ret.responseData['sceneItemEnabled'])

		# 対象ソースを無効にする
		for idx, id in enumerate(dat.currentwasapicaptureID):
			if dat.currentwasapicaptureEN[idx] == True:
				# 対象ソースを無効にする
				request = obsws.Request('SetSceneItemEnabled', {'sceneName': dat.currentscene, 'sceneItemId': id, 'sceneItemEnabled': False})
				ret = await dat.ws.call(request)
				# 対象ソースを複製する
				request = obsws.Request('DuplicateSceneItem', {'sceneName': dat.currentscene, 'sceneItemId': id, 'destinationSceneName': dat.currentscene})
				ret = await dat.ws.call(request)
				dupID = ret.responseData['sceneItemId']
				# 対象ソースを削除する
				request = obsws.Request('RemoveSceneItem', {'sceneName': dat.currentscene, 'sceneItemId': id})
				ret = await dat.ws.call(request)
				# 複製ソースにIDを差し替え
				dat.currentwasapicaptureID[idx] = dupID
		# 複製ソースの有効にする
		for idx, id in enumerate(dat.currentwasapicaptureID):
			if dat.currentwasapicaptureEN[idx] == True:
				request = obsws.Request('SetSceneItemEnabled', {'sceneName': dat.currentscene, 'sceneItemId': id, 'sceneItemEnabled': True})
				ret = await dat.ws.call(request)
		print("次回時刻: ", time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(time.time() + dat.delaytimef)))
		if dat.fQuit == False:
			dat.timetask = asyncio.create_task(dat.resetAppAudioCapture())



# 非同期系初期化処理
async def async_main():
	# OBS-Websocketに接続
	ret = await dat.ws.connect()
	if not ret:
		print("[OBSWS] Connect failed.")
		return ret
	ret = await dat.ws.wait_until_identified()
	if not ret:
		print("[OBSWS] Identified timeout.")
		return ret
	request = obsws.Request('GetVersion')
	ret = await dat.ws.call(request)
	#print(ret)
	if ret.ok():
		print('OBS Connected. Plugin v' + ret.responseData['obsWebSocketVersion'] + ', OBS v' + ret.responseData['obsVersion'], flush=True)
		obsConnected = True
	else:
		print(ret)
		print('OBS Connect failed.', flush=True)
		obsConnected = False
		return obsConnected
	print('')

	print('OBS上のアプリケーション音声キャプチャの一覧：')
	request = obsws.Request('GetInputList', {'inputKind': 'wasapi_process_output_capture',})
	ret = await dat.ws.call(request)
	if ret.ok():
		#print("[OBSWS] GetInputList(App-audiocapture): {}".format(ret.responseData))
		for idx in ret.responseData['inputs']:
			dat.wasapicaptures.append(idx['inputName'])
		print(dat.wasapicaptures)
	else:
		print(ret)
	print('')
	
	print('現在のシーン名：')
	request = obsws.Request('GetCurrentProgramScene')
	ret = await dat.ws.call(request)
	if ret.ok():
		#print("[OBSWS] GetCurrentProgramScene: {}".format(ret.responseData))
		dat.currentscene = ret.responseData['currentProgramSceneName']
		print(dat.currentscene)
	else:
		print(ret)
	print('')

	print('現在のシーン内にあるアプリケーション音声キャプチャID：')
	request = obsws.Request('GetSceneItemList', {'sceneName': dat.currentscene})
	ret = await dat.ws.call(request)
	if ret.ok():
		#print("[OBSWS] GetSceneItemList(App-audiocapture): {}".format(ret.responseData))
		for idx in ret.responseData['sceneItems']:
			#print("{}:{}".format(idx['sourceName'], idx['sceneItemId']))
			if idx['sourceName'] in dat.wasapicaptures:
				dat.currentwasapicaptureID.append(idx['sceneItemId'])
		print(dat.currentwasapicaptureID)
	else:
		print(ret)
	print('')
	
	print('現在のシーン内にあるアプリケーション音声キャプチャの有効状態：')
	for idx in dat.currentwasapicaptureID:
		request = obsws.Request('GetSceneItemEnabled', {'sceneName': dat.currentscene, 'sceneItemId': idx})
		ret = await dat.ws.call(request)
		if ret.ok():
			#print("[OBSWS] GetSceneItemEnabled(App-audiocapture): {}".format(ret.responseData))
			dat.currentwasapicaptureEN.append(ret.responseData['sceneItemEnabled'])
		else:
			print(ret)
	print(dat.currentwasapicaptureEN)
	print('')
	
	
	# Timer
	if dat.delaytimef < 5.0:
		print('エラー：IntervalSec（リセット間隔）には 5(秒) 以上を設定してください。')
		sys.exit()
	dat.timetask = asyncio.create_task(dat.resetAppAudioCapture())
	print("初回時刻: ", time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(time.time() + dat.delaytimef)), flush=True)

	return obsConnected

dat = BotGlobalData()

# Start
if __name__ == '__main__':
	print('////////////////////////////////////////')
	print('Auto-reset OBS Application Audio Capture')
	print('////////////////////////////////////////')

	# start OBSWS
	print("Connecting to OBS...")
	parameters = obsws.IdentificationParameters(ignoreNonFatalRequestChecks = False)
	dat.ws = obsws.WebSocketClient(
		url = 'ws://' + dat.OBSHost + ':' + dat.OBSPort, 
		password = dat.OBSPass, 
		identification_parameters = parameters
	) 

	dat.eventloop = asyncio.get_event_loop()
	fret = dat.eventloop.run_until_complete(async_main())
	if fret == False:
		input()
		sys.exit()
	
	try:
		dat.eventloop.run_forever()
	except KeyboardInterrupt:
		sys.exit()
	sys.exit()
