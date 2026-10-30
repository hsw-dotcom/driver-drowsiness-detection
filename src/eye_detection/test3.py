from picamera2 import Picamera2, Preview
import cv2

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"size": (640, 480)}))
picam2.start()
	
while True:
	frame = picam2.capture_array()
	cv2.imshow("Camera", frame)

	key = cv2.waitKey(30)
	if key == 27:
		break

cv2.destroyAllWindows()
"""
[0:08:12.225116023] [2489]  INFO Camera camera.cpp:1028 configuring streams: (0) 2304x1296-YUV420
[0:08:12.225605148] [2490]  INFO RPI raspberrypi.cpp:851 Sensor: /base/soc/i2c0mux/i2c@1/imx708@1a - 
Selected sensor format: 2304x1296-SBGGR10_1X10 - Selected unicam format: 2304x1296-pBAA


[0:09:56.382962399] [2583]  INFO Camera camera.cpp:1028 configuring streams: (0) 800x600-XBGR8888
[0:09:56.383293810] [2591]  INFO RPI raspberrypi.cpp:851 Sensor: /base/soc/i2c0mux/i2c@1/imx708@1a - 
Selected sensor format: 1536x864-SBGGR10_1X10 - Selected unicam format: 1536x864-pBAA

"""
