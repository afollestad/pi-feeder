# Pi Feeder

Welcome, this is the code for my WIP Raspberry Pi powered pet feeder.

<img src="https://raw.githubusercontent.com/afollestad/pi-feeder/master/art/webdashboard.png" width="800" />

---

# Hardware

All that this project *really* requires is a DC motor wired up so that a Raspberry Pi can control it. However, you can get a bit more creative with the setup...

<img src="https://raw.githubusercontent.com/afollestad/pi-feeder/master/art/pifeederhardware.jpg" width="600" />

The wiring you see in the picture above is basically equivelent to the two images below. Both are basically the same thing; the main difference is that in the 
the left image, the Raspberry Pi would connect to the breadboard through the blue "Pi Header"; in the right image, the diagram shows the Pi's GPIO pins connecting 
directly to the breadboard. My actual setup is more like the left image as you can see above.

<table>
<tr>
<td><img src="https://raw.githubusercontent.com/afollestad/pi-feeder/master/art/breadboardsetup.png" width="500" /></td>
<td><img src="https://raw.githubusercontent.com/afollestad/pi-feeder/master/art/breadboardsetup2.png" width="500" /></td>
</tr>
</table>

I'm using a Raspberry Pi, connected to a breadboard that is using a L293D motor driver chip. The little blue LED is there just to verify 
that the AA battery pack is successfully providing power to the breadboard for the DC motor. The DC motor is attached to the top inside the box, 
which is attached to a D-Shaft using a Shaft Coupler. The other side of the D-Shaft goes into the cereal dispender attached to the side of the box. 
And of a course, a few PVC pipes attached to the bottom of the cereal dispender help route outcoming food into a dish.

You can find some detailed information on circuit setup, how this stuff actually works, etc. all over the internet. Here's a few good sources:

1. [Controlling a DC Motor with the Raspberry Pi - YouTube](https://www.youtube.com/watch?v=W7cV9_W12sM)
2. [Adafruit's Raspberry Pi Lesson 9. Controlling a DC Motor](https://learn.adafruit.com/adafruit-raspberry-pi-lesson-9-controlling-a-dc-motor/overview)
3. [Controlling DC Motors Using Python With a Raspberry Pi - TutsPlus](https://business.tutsplus.com/tutorials/controlling-dc-motors-using-python-with-a-raspberry-pi--cms-20051)
4. [Controlling direction and speed of DC motor using Raspberry Pi - Instructables](http://www.instructables.com/id/Controlling-Direction-and-Speed-of-DC-Motor-Using-/)
5. [GPIOZero - A Python lib which wraps around Pi's lower-level APIOs to control the GPIO pins](https://gpiozero.readthedocs.io/en/v1.3.1/api_output.html#motor)

---

# Code Dependencies

This is a Python project, written from Visual Studio Code. Install dependencies using `pip`, preferably `pip3` since this server needs to be run with Python 3.

* Flask
* sqlite3
* gpiozero
* bcrypt
* tzlocal
* dateutil
* time_uuid
* phonenumbers
* twilio SDK

---

# Running

To run the server:

```bash
$ python3 server.py
```

This will run the HTTP server, create a default admin account, and do any other required initial setup.

The default admin credentials are `admin` / `feeder`.

---

# (Optional) SMS Notifications

You can receive SMS notifications when the feeder runs (not from manual activation, but from automatic schedule activation). You just need a 
[Twilio account](https://www.twilio.com), where you can copy and paste your account SID, auth token, and sender number into `sms.py`.  