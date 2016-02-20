import struct
import bluetooth
import bluetooth._bluetooth as bluez

def fetch_rssi(socket, bdaddr):
    flt = bluez.hci_filter_new()
    bluez.hci_filter_all_events(flt)
    bluez.hci_filter_set_ptype(flt, bluez.HCI_EVENT_PKT)
    socket.setsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, flt )
    
    cmd_pkt = struct.pack("????")
    bluez.hci_send_cmd(socket, bluez.OGF_LINK_CTL, bluez.OCF_READ_RSSI, cmd_pkt)

    pkt = socket.recv(255)
    ptype, event, plen = struct.unpack("BBB", pkt[:3])
    if event == bluez.EVT_INQUIRY_RESULT_WITH_RSSI:
        pkt = pkt[3:]
        nrsp = bluetooth.get_byte(pkt[0])
        for i in range(nrsp):
            addr = bluez.ba2str( pkt[1+6*i:1+6*i+6] )
            rssi = bluetooth.byte_to_signed_int(
                    bluetooth.get_byte(pkt[1+13*nrsp+i]))
            results.append( ( addr, rssi ) )
            print("[%s] RSSI: [%d]" % (addr, rssi))
    elif event == bluez.EVT_CMD_STATUS:
        status, ncmd, opcode = struct.unpack("BBH", pkt[3:7])
        if status != 0:
            print("uh oh...")
            done = True
    elif event == bluez.EVT_INQUIRY_RESULT:
        pkt = pkt[3:]
        nrsp = bluetooth.get_byte(pkt[0])
        for i in range(nrsp):
            addr = bluez.ba2str( pkt[1+6*i:1+6*i+6] )
            results.append( ( addr, -1 ) )
            print("[%s] (no RRSI)" % addr)
    else:
        print("unrecognized packet type 0x%02x" % ptype)
    print("event ", event)

dev_id = bluez.hci_get_route("hci0")
try:
    socket = bluez.hci_open_dev(dev_id)
except:
    print("error accessing bluetooth device...")
    sys.exit(1)

fetch_rssi(socket, "TARGET_DEVICE_ID")
    


    
