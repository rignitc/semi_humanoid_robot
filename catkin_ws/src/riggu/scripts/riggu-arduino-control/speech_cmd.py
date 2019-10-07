#!/usr/bin/env python3
# This code tries to get the voice command  and convert it to text and publishes it speech_text topic
import rospy
import time
from std_msgs.msg import String

import speech_recognition as sr

def recognize_speech_from_mic(recognizer,microphone):

	if not isinstance(recognizer,sr.Recognizer):
		raise TypeError("recognizer not Recognizer instance")
		print ("error.... line 10")
	if not isinstance(microphone,sr.Microphone):
		raise TypeError("microphone not microphone instance")
		print ("error.... line 13")

	with microphone as source:
		#recognizer.adjust_for_ambient_noise(source) #adjusting the recognizer sensitivty to ambient noise
		audio=recognizer.listen(source) #recording audio from microphone
	response={
		
		"success":True,
		"error":None,
		"transcription":None
	}

	try:
		response["transcription"]=recognizer.recognize_google(audio)
	except sr.RequestError:
		#API was unreachable and unresponsive
		response["success"]=False
		redsponse["error"]="API unaivalable"
	except sr.UnknownValueError:
		#speech not clear
		response["error"]="Unable to recognize speech"

	return response


def publisher(number):
	
		pub.publish(number)
		rate.sleep()

def voice_cmd():
	while True:
		time.sleep(1)
		print('Speak!')
		word = recognize_speech_from_mic(recognizer, microphone)
		print ("the word transcription is ....",word["transcription"])
		print ("the word error is ....",word["error"])
		print ("the word success is ....",word["success"])
		string=word["transcription"]
		publisher(string)

if __name__ == '__main__':
	try:
		recognizer = sr.Recognizer()
		microphone = sr.Microphone()
		pub = rospy.Publisher('text_voice_writing', String, queue_size=10)
		rospy.init_node('voicecmd', anonymous=False)
		rate = rospy.Rate(10) # 10hz
		voice_cmd()
	except rospy.ROSInterruptException:
		pass
