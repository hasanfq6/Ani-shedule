from ani_mation import loading,CustomLoading

loader = CustomLoading()

def get():
    import time
    time.sleep(5)
    return "Succes"
loader.start()
x = get()
loader.stop()
