from dubina import SD1

arm = SD1(host="127.0.0.1", port=5000, name="Ivanov Ivan", debug=False)
arm.calibrate()
arm.close()
