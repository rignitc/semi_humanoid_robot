execute_process(COMMAND "/home/nvidia/rigguv2/catkin_ws/build/audio_common-master/sound_play/catkin_generated/python_distutils_install.sh" RESULT_VARIABLE res)

if(NOT res EQUAL 0)
  message(FATAL_ERROR "execute_process(/home/nvidia/rigguv2/catkin_ws/build/audio_common-master/sound_play/catkin_generated/python_distutils_install.sh) returned error code ")
endif()
