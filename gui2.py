from __future__ import print_function
import can
from ecu import ecu 
from ecu import helper

import datetime
import gi
from gi.repository import Gtk, GObject, GLib

gi.require_version("Gtk", "3.0")


class main_window(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="vCar")
        engine = ecu.Engine()
        grid = ecu_widget(engine,"Engine")
        grid22 = ecu_widget(engine,"hello2")
        self.rate = 5 # rate at which can messages are sent in a second, right now it's 10
        bus_freq = 500

        self.button = Gtk.Button.new_with_label("Accelerate")
        self.button.connect("pressed", self.button_clicked, engine)
        self.button.connect("released", self.button_released, engine)
        
        grid.attach_next_to(self.button, None ,Gtk.PositionType.BOTTOM, 1,1)
        self.add(grid) # init tasks 
        self._task = 0
        self._timeout = 0

        # setup can bus, requires can module 
        can_interface = 'vcan0'
        self.bus = can.interface.Bus(can_interface, bustype='socketcan', receive_own_messages=True)

    # acceleration
    def button_clicked(self, widget, engine):
        # on button click add a timeout to periodically run the accelerate func
        if self._task:
            GObject.source_remove(self._task)
        timeout = 1/self.rate*1000
        start_time = datetime.datetime.now() # to be used for acceleration.
        self._timeout = GObject.timeout_add(timeout, self.accelerate, engine, start_time)
        self._recv_timeout = GObject.timeout_add(5, self.recv_can, engine)
        
    def button_released(self, widget, engine):
        # removes the periodic function added in button_clicked().
        GObject.source_remove(self._timeout)
        # GObject.source_remove(self._recv_timeout)
        # start another timeout until button is clicked to decelerate 
        timeout = 1/self.rate*1000
        start_time = datetime.datetime.now() # to be used for acceleration.
        self._task = GObject.timeout_add(timeout, self.decelerate, engine, start_time)

        return 0 

    def accelerate(self, engine, start_time):
        ''' takes in a ecu engine to apply the accelerate function to along
        with a start time (using datetime.now()) of when the button is pressed.'''
        x = engine.get_speed() 
        # check if speed is equal to 250km/h if not then gen message with 
        # accel rate (7 km/h) added to it. Cap it to 250 km/h
        if x <= 250:
            if x + 7 > 250:
                self.bus.send(engine.gen_message(250))
            if x + 7 < 250:
                self.bus.send(engine.gen_message(x+7))
            if x == 250:
                self.bus.send(engine.gen_message(250))

        return True
        
    def decelerate(self, engine, start_time):
        x = engine.get_speed()
        if x >= 2:
            if x - 7 > 2:
                self.bus.send(engine.gen_message(x - 7))
            if x - 7 < 2:
                self.bus.send(engine.gen_message(2))
            if x == 2:
                self.bus.send(engine.gen_message(2))

        return True

    def recv_can(self, engine):
        msg = self.bus.recv(0.0)
        if msg != None:
            engine.recv_can(msg.data)

        return True

def ecu_widget(ecu_input, name):
    ''' Takes the ecu object and a name to encode it with and returns 
    a grid with the information laid out in it. For now it assumes both 
    are engines. '''
    grid = Gtk.Grid()
    # initialize all the ecu variables into an array
    ecu_var = []
    name = Gtk.Label(label="ECU name = " + str(name))
    ecu_id = Gtk.Label(label=ecu_input.get_id())
    state = Gtk.Label(label=ecu_input.get_state())
    error_count = Gtk.Label(label=ecu_input.get_tec())
    speed_val = Gtk.Label(label=ecu_input.get_speed() *0.01)
    ecu_var.extend([state, error_count, speed_val])
    GLib.timeout_add_seconds(1, update_label_val, ecu_var, ecu_input)

    # initalize all the labels
    id_label = Gtk.Label(label="ecu id: ")
    state_label = Gtk.Label(label="state: ")
    error_count_label = Gtk.Label(label="tec error count: ")
    speed_label = Gtk.Label(label="car speed(km/h): ")


    grid.add(name)
    # attach id and it's value
    grid.attach(id_label,1,1,1,1)
    grid.attach_next_to(ecu_id, id_label,Gtk.PositionType.RIGHT, 1,1)
    # attach state and it's value
    grid.attach(state_label, 1,2,1,1)
    grid.attach_next_to(state, state_label, Gtk.PositionType.RIGHT, 1,1)
    # attach tec count label and it's value
    grid.attach(error_count_label, 1,3,1,1)
    grid.attach_next_to(error_count, error_count_label, Gtk.PositionType.RIGHT, 1,1)
    # attach speed and it's value
    grid.attach(speed_label, 1,4,1,1)
    grid.attach_next_to(speed_val, speed_label, Gtk.PositionType.RIGHT, 1,1)

    # add seperator
    h_seperator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    grid.attach(h_seperator,0,6,12,12)
    return grid
    
def update_label_val(labels, ecu):
    ''' Takes in a list of labels and updates their values. In this case it
    probes the ecu to be updated and updates the values. The second parameter
    takes in a ecu object. First index of array is the state, second is the
    error count, third is the speed. '''
    # update the state text
    labels[0].set_text(str(ecu.get_state()))
    labels[1].set_text(str(ecu.get_tec()))
    labels[2].set_text(str(ecu.get_speed()))
    return GLib.SOURCE_CONTINUE





window = main_window()
window.connect("destroy", Gtk.main_quit)
window.show_all()
Gtk.main()


