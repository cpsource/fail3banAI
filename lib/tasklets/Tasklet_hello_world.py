#
# Tasklets are small routines that are kicked off from our thread pool, because
# these guys can wait around and when they are done, just return.
#
# The thread that was running it will then go back to the thread pool and
# wait for more work

def Tasklet_hello_world():
    print("Hello World")


