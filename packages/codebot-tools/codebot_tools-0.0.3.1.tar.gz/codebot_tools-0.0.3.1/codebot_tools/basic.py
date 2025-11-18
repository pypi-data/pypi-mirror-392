## Imports ##

import botcore
import time

## Backside Variables ##

equilTriAngle = 0.352
rightAngle = 0.247
rightAngle2 = 0.21

## Functions ##

# Forward
def straight(speed, timeVar):
    motors.enable(True)
    motors.run(LEFT, speed)
    motors.run(RIGHT, speed)
    time.sleep(timeVar)
    motors.enable(False)

def elementaryTurn(speed, timeVar, direction):
    motors.enable(True)
    if direction == "right":
        motors.run(LEFT, speed)
        motors.run(RIGHT, speed*-1)
        time.sleep(timeVar)
    else:
        motors.run(LEFT, speed*-1)
        motors.run(RIGHT, speed)
        time.sleep(timeVar)
    motors.enable(False)

def simpleBrake(time):
    if timeVar == "":
        timeVar = 0.5
    motors.enable(False)
    time.sleep(timeVar)

def triangle():
    straight(100, 1)
    for i in range(2):
        time.sleep(1)
        elementaryTurn(80, equilTriAngle, "right")
        time.sleep(1)
        straight(100, 1)

def boxEight():
    straight(100, 1)
    simpleBrake(2)
    elementaryTurn(80, rightAngle, "right")
    simpleBrake(1)
    straight(100, 1)
    simpleBrake(2)
    elementaryTurn(80, rightAngle, "right")
    simpleBrake(1)
    straight(100, 1)
    simpleBrake(2)
    elementaryTurn(75, 0.29, "right")
    simpleBrake(1)
    straight(50, 4.5)
    simpleBrake(2)
    elementaryTurn(80, rightAngle2, "right")
    simpleBrake(1)
    straight(100, 1)
    simpleBrake(2)
    elementaryTurn(80, 0.24, "right")
    simpleBrake(1)
    straight(100, 1)
