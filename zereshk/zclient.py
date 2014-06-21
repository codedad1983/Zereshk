import zmq
import sys

port = 7766


context = zmq.Context()
print "Connecting to server..."
socket = context.socket(zmq.REQ)
# socket.connect("tcp://192.168.1.12:%s" % port)
socket.connect("tcp://localhost:%s" % port)

if len(sys.argv) > 1:
    link = sys.argv[1]
    print "Sending link ", link, "..."
    socket.send_json({'link': link})
    #  Get the reply.
    message = socket.recv()
    print "Received reply [", message, "]"
else:
    while True:
        link = raw_input('zdl> ')
        print "Sending link ", link, "..."
        socket.send_json({'link': link})
        #  Get the reply.
        message = socket.recv()
        print "Received reply [", message, "]"
