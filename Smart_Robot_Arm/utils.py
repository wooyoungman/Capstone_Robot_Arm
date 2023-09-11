import math

# Configure min and max servo pulse lengths
SERVO_MIN = 150  # min. pulse length
SERVO_MAX = 600  # max. pulse length

# arm1 & arm2 length
ARM1_LENGTH = 20
ARM2_LENGTH = 20

# distance from origin
OX = 0
OY = 0
OZ = 0


def AngleToRadian(angle):
    return int(SERVO_MIN + math.radians(angle) * (SERVO_MAX - SERVO_MIN) / math.pi)


def sqrtXYZ(_x=0, _y=0, _z=0):
    return math.sqrt(_x ** 2 + _y ** 2 + _z ** 2)


def CalculateTheta(_x, _y, _z):
    # Flag for Handling when the coordinates in distance from origin
    range_flag = 1 if _x ** 2 + _y ** 2 < math.sqrt(7.5) else 0

    th_0 = math.atan2(_y, _x)

    _x = _x - abs(OX * math.cos(th_0)) if _x >= 0 else _x + abs(OX * math.cos(th_0))
    _y = _y - abs(OY * math.sin(th_0)) if _y >= 0 else _y + abs(OY * math.sin(th_0))
    _z -= OZ

    th_2 = math.acos(
        (_x ** 2 + _y ** 2 + _z ** 2 - ARM1_LENGTH ** 2 - ARM2_LENGTH ** 2) / (2 * ARM1_LENGTH * ARM2_LENGTH))

    if range_flag == 1:
        th_1 = math.atan2(_z, -sqrtXYZ(_x, _y)) + \
               math.asin(ARM2_LENGTH * math.sin(th_2) / sqrtXYZ(_x, _y, _z))

    else:
        th_1 = math.atan2(_z, sqrtXYZ(_x, _y)) + \
               math.asin(ARM2_LENGTH * math.sin(th_2) / sqrtXYZ(_x, _y, _z))

    th_0 *= (180 / math.pi)
    if th_0 <= 90:
        th_0 += 90
    else:
        th_0 = 180 - th_0

    th_1 *= (180 / math.pi)

    th_2 *= (180 / math.pi)

    return th_0, th_1, th_2
