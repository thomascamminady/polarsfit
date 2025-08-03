"""
FIT Protocol Field Mappings and Message Types.

This module contains the official field mappings and message type definitions
based on the Garmin FIT SDK and protocol documentation.

References
----------
- https://developer.garmin.com/fit/protocol/
- FIT SDK Global Profile
"""

from enum import IntEnum
from typing import Dict


class MessageType(IntEnum):
    """FIT Message Types (Global Message Numbers)."""

    FILE_ID = 0
    CAPABILITIES = 1
    DEVICE_SETTINGS = 2
    USER_PROFILE = 3
    HRM_PROFILE = 4
    SDM_PROFILE = 5
    BIKE_PROFILE = 6
    ZONES_TARGET = 7
    HR_ZONE = 8
    POWER_ZONE = 9
    MET_ZONE = 10
    SPORT = 12
    GOAL = 15
    SESSION = 18
    LAP = 19
    RECORD = 20  # Most common - GPS tracks, heart rate, power, etc.
    EVENT = 21
    DEVICE_INFO = 23
    WORKOUT = 26
    WORKOUT_STEP = 27
    SCHEDULE = 28
    WEIGHT_SCALE = 30
    COURSE = 31
    COURSE_POINT = 32
    TOTALS = 33
    ACTIVITY = 34
    SOFTWARE = 35
    FILE_CAPABILITIES = 37
    MESG_CAPABILITIES = 38
    FIELD_CAPABILITIES = 39
    FILE_CREATOR = 49
    BLOOD_PRESSURE = 51
    SPEED_ZONE = 53
    MONITORING = 55
    TRAINING_FILE = 72
    HRV = 78
    ANT_RX = 80
    ANT_TX = 81
    ANT_CHANNEL_ID = 82
    LENGTH = 101
    MONITORING_INFO = 103
    PAD = 105
    SLAVE_DEVICE = 106
    CONNECTIVITY = 127
    WEATHER_CONDITIONS = 128
    WEATHER_ALERT = 129
    CADENCE_ZONE = 131
    HR = 132
    SEGMENT_LAP = 142
    MEMO_GLOB = 145
    SEGMENT_ID = 148
    SEGMENT_LEADERBOARD_ENTRY = 149
    SEGMENT_POINT = 150
    SEGMENT_FILE = 151
    WORKOUT_SESSION = 158
    WATCHFACE_SETTINGS = 159
    GPS_METADATA = 160
    CAMERA_EVENT = 161
    TIMESTAMP_CORRELATION = 162
    GYROSCOPE_DATA = 164
    ACCELEROMETER_DATA = 165
    THREE_D_SENSOR_CALIBRATION = 167
    VIDEO_FRAME = 169
    OBDII_DATA = 174
    NMEA_SENTENCE = 177
    AVIATION_ATTITUDE = 178
    VIDEO = 184
    VIDEO_TITLE = 185
    VIDEO_DESCRIPTION = 186
    VIDEO_CLIP = 187
    OHR_SETTINGS = 188
    EXD_SCREEN_CONFIGURATION = 200
    EXD_DATA_FIELD_CONFIGURATION = 201
    EXD_DATA_CONCEPT_CONFIGURATION = 202
    FIELD_DESCRIPTION = 206
    DEVELOPER_DATA_ID = 207
    MAGNETOMETER_DATA = 208
    BAROMETER_DATA = 209
    ONE_D_SENSOR_CALIBRATION = 210
    SET = 225
    STRESS_LEVEL = 227
    DIVE_SETTINGS = 258
    DIVE_GAS = 259
    DIVE_ALARM = 262
    EXERCISE_TITLE = 264
    DIVE_SUMMARY = 268
    JUMP = 285
    CLIMB_PRO = 317


# Record Message Fields (Message Type 20 - most commonly used)
RECORD_FIELDS = {
    253: "timestamp",  # Unix timestamp (seconds since UTC 00:00 Dec 31 1989)
    0: "position_lat",  # Latitude in semicircles
    1: "position_long",  # Longitude in semicircles
    2: "altitude",  # Altitude in meters (with 5m offset, 1m resolution)
    3: "heart_rate",  # Heart rate in beats per minute
    4: "cadence",  # Cadence in revolutions per minute
    5: "distance",  # Distance in meters (accumulated)
    6: "speed",  # Speed in meters per second
    7: "power",  # Power in watts
    8: "compressed_speed_distance",  # Special compressed field
    9: "grade",  # Grade in percent
    10: "resistance",  # Equipment resistance
    11: "time_from_course",  # Time from course in seconds
    12: "cycle_length",  # Cycle length in meters
    13: "temperature",  # Temperature in degrees Celsius
    17: "speed_1s",  # 1-second speed in meters per second
    18: "cycles",  # Number of cycles (strokes, steps, etc.)
    19: "total_cycles",  # Total cycles
    28: "compressed_accumulated_power",  # Special compressed field
    29: "accumulated_power",  # Accumulated power in watts
    30: "left_right_balance",  # Left/right balance
    31: "gps_accuracy",  # GPS accuracy in meters
    32: "vertical_speed",  # Vertical speed in meters per second
    33: "calories",  # Calories burned
    39: "vertical_oscillation",  # Vertical oscillation in millimeters
    40: "stance_time_percent",  # Stance time percentage
    41: "stance_time",  # Stance time in milliseconds
    42: "activity_type",  # Activity type
    43: "left_torque_effectiveness",  # Left torque effectiveness percentage
    44: "right_torque_effectiveness",  # Right torque effectiveness percentage
    45: "left_pedal_smoothness",  # Left pedal smoothness percentage
    46: "right_pedal_smoothness",  # Right pedal smoothness percentage
    47: "combined_pedal_smoothness",  # Combined pedal smoothness percentage
    48: "time128",  # Time in 1/128 second resolution
    49: "stroke_type",  # Stroke type
    50: "zone",  # Training zone
    51: "ball_speed",  # Ball speed in meters per second
    52: "cadence256",  # Cadence in 1/256 rpm resolution
    53: "fractional_cadence",  # Fractional cadence in rpm
    54: "total_hemoglobin_conc",  # Total hemoglobin concentration
    55: "total_hemoglobin_conc_min",  # Minimum total hemoglobin concentration
    56: "total_hemoglobin_conc_max",  # Maximum total hemoglobin concentration
    57: "saturated_hemoglobin_percent",  # Saturated hemoglobin percentage
    58: "saturated_hemoglobin_percent_min",  # Minimum saturated hemoglobin percentage
    59: "saturated_hemoglobin_percent_max",  # Maximum saturated hemoglobin percentage
    62: "device_index",  # Device index
    67: "left_pco",  # Left platform center offset in millimeters
    68: "right_pco",  # Right platform center offset in millimeters
    69: "left_power_phase",  # Left power phase angles
    70: "left_power_phase_peak",  # Left power phase peak angles
    71: "right_power_phase",  # Right power phase angles
    72: "right_power_phase_peak",  # Right power phase peak angles
    73: "enhanced_speed",  # Enhanced speed in meters per second
    78: "enhanced_altitude",  # Enhanced altitude in meters
    81: "battery_soc",  # Battery state of charge in percent
    82: "left_right_balance_100",  # Left/right balance in 0.5% resolution
    83: "motor_power",  # Motor power in watts
    84: "vertical_ratio",  # Vertical ratio in percent
    85: "stance_time_balance",  # Stance time balance in percent
    86: "step_length",  # Step length in millimeters
    87: "absolute_pressure",  # Absolute pressure in Pascal
    88: "depth",  # Depth in meters
    89: "next_stop_depth",  # Next stop depth in meters
    90: "next_stop_time",  # Next stop time in seconds
    91: "time_to_surface",  # Time to surface in seconds
    92: "ndl_time",  # No decompression limit time in seconds
    93: "cns_load",  # CNS toxicity load in percent
    94: "n2_load",  # Nitrogen tissue load in percent
    114: "grit",  # Grit score
    115: "flow",  # Flow score
    117: "ebike_travel_range",  # E-bike travel range in meters
    118: "ebike_battery_level",  # E-bike battery level in percent
    119: "ebike_assist_mode",  # E-bike assist mode
    120: "ebike_assist_level_percent",  # E-bike assist level in percent
    139: "core_temperature",  # Core body temperature in degrees Celsius
}

# Session Message Fields (Message Type 18)
SESSION_FIELDS = {
    253: "timestamp",  # Start time of session
    254: "message_index",  # Message index
    0: "event",  # Session trigger event
    1: "event_type",  # Session trigger event type
    2: "start_time",  # Start time
    3: "start_position_lat",  # Start latitude in semicircles
    4: "start_position_long",  # Start longitude in semicircles
    5: "sport",  # Sport type
    6: "sub_sport",  # Sub sport type
    7: "total_elapsed_time",  # Total elapsed time in seconds
    8: "total_timer_time",  # Total timer time in seconds
    9: "total_distance",  # Total distance in meters
    10: "total_cycles",  # Total cycles (strokes, steps, etc.)
    11: "total_calories",  # Total calories
    13: "total_fat_calories",  # Total fat calories
    14: "avg_speed",  # Average speed in meters per second
    15: "max_speed",  # Maximum speed in meters per second
    16: "avg_heart_rate",  # Average heart rate in beats per minute
    17: "max_heart_rate",  # Maximum heart rate in beats per minute
    18: "avg_cadence",  # Average cadence in revolutions per minute
    19: "max_cadence",  # Maximum cadence in revolutions per minute
    20: "avg_power",  # Average power in watts
    21: "max_power",  # Maximum power in watts
    22: "total_ascent",  # Total ascent in meters
    23: "total_descent",  # Total descent in meters
    24: "total_training_effect",  # Total training effect
    25: "first_lap_index",  # Index of first lap
    26: "num_laps",  # Number of laps
    27: "event_group",  # Event group
    28: "trigger",  # Session trigger
    29: "nec_lat",  # Northeast corner latitude in semicircles
    30: "nec_long",  # Northeast corner longitude in semicircles
    31: "swc_lat",  # Southwest corner latitude in semicircles
    32: "swc_long",  # Southwest corner longitude in semicircles
    34: "normalized_power",  # Normalized power in watts
    35: "training_stress_score",  # Training stress score
    36: "intensity_factor",  # Intensity factor
    37: "left_right_balance",  # Left/right balance
    41: "avg_stroke_count",  # Average stroke count
    42: "avg_stroke_distance",  # Average stroke distance in meters
    43: "swim_stroke",  # Swimming stroke type
    44: "pool_length",  # Pool length in meters
    45: "threshold_power",  # Threshold power in watts
    46: "pool_length_unit",  # Pool length unit
    47: "num_active_lengths",  # Number of active lengths
    48: "total_work",  # Total work in joules
    49: "avg_altitude",  # Average altitude in meters
    50: "max_altitude",  # Maximum altitude in meters
    51: "gps_accuracy",  # GPS accuracy in meters
    52: "avg_grade",  # Average grade in percent
    53: "avg_pos_grade",  # Average positive grade in percent
    54: "avg_neg_grade",  # Average negative grade in percent
    55: "max_pos_grade",  # Maximum positive grade in percent
    56: "max_neg_grade",  # Maximum negative grade in percent
    57: "avg_temperature",  # Average temperature in degrees Celsius
    58: "max_temperature",  # Maximum temperature in degrees Celsius
    59: "total_moving_time",  # Total moving time in seconds
    60: "avg_pos_vertical_speed",  # Average positive vertical speed in meters per second
    61: "avg_neg_vertical_speed",  # Average negative vertical speed in meters per second
    62: "max_pos_vertical_speed",  # Maximum positive vertical speed in meters per second
    63: "max_neg_vertical_speed",  # Maximum negative vertical speed in meters per second
    64: "min_heart_rate",  # Minimum heart rate in beats per minute
    65: "time_in_hr_zone",  # Time in heart rate zones in seconds
    66: "time_in_speed_zone",  # Time in speed zones in seconds
    67: "time_in_cadence_zone",  # Time in cadence zones in seconds
    68: "time_in_power_zone",  # Time in power zones in seconds
    69: "avg_lap_time",  # Average lap time in seconds
    70: "best_lap_index",  # Index of best lap
    71: "min_altitude",  # Minimum altitude in meters
    72: "player_score",  # Player score
    73: "opponent_score",  # Opponent score
    74: "opponent_name",  # Opponent name
    75: "stroke_count",  # Total stroke count
    76: "zone_count",  # Zone count
    77: "max_ball_speed",  # Maximum ball speed in meters per second
    78: "avg_ball_speed",  # Average ball speed in meters per second
    79: "avg_vertical_oscillation",  # Average vertical oscillation in millimeters
    80: "avg_stance_time_percent",  # Average stance time percentage
    81: "avg_stance_time",  # Average stance time in milliseconds
    82: "avg_fractional_cadence",  # Average fractional cadence in revolutions per minute
    83: "max_fractional_cadence",  # Maximum fractional cadence in revolutions per minute
    84: "total_fractional_cycles",  # Total fractional cycles
    85: "avg_total_hemoglobin_conc",  # Average total hemoglobin concentration
    86: "min_total_hemoglobin_conc",  # Minimum total hemoglobin concentration
    87: "max_total_hemoglobin_conc",  # Maximum total hemoglobin concentration
    88: "avg_saturated_hemoglobin_percent",  # Average saturated hemoglobin percentage
    89: "min_saturated_hemoglobin_percent",  # Minimum saturated hemoglobin percentage
    90: "max_saturated_hemoglobin_percent",  # Maximum saturated hemoglobin percentage
    91: "avg_left_torque_effectiveness",  # Average left torque effectiveness percentage
    92: "avg_right_torque_effectiveness",  # Average right torque effectiveness percentage
    93: "avg_left_pedal_smoothness",  # Average left pedal smoothness percentage
    94: "avg_right_pedal_smoothness",  # Average right pedal smoothness percentage
    95: "avg_combined_pedal_smoothness",  # Average combined pedal smoothness percentage
    98: "sport_index",  # Sport index
    99: "time_standing",  # Time standing in seconds
    100: "stand_count",  # Stand count
    101: "avg_left_pco",  # Average left platform center offset in millimeters
    102: "avg_right_pco",  # Average right platform center offset in millimeters
    103: "avg_left_power_phase",  # Average left power phase angles
    104: "avg_left_power_phase_peak",  # Average left power phase peak angles
    105: "avg_right_power_phase",  # Average right power phase angles
    106: "avg_right_power_phase_peak",  # Average right power phase peak angles
    107: "avg_power_position",  # Average power position in watts
    108: "max_power_position",  # Maximum power position in watts
    109: "avg_cadence_position",  # Average cadence position in revolutions per minute
    110: "max_cadence_position",  # Maximum cadence position in revolutions per minute
    111: "enhanced_avg_speed",  # Enhanced average speed in meters per second
    112: "enhanced_max_speed",  # Enhanced maximum speed in meters per second
    113: "enhanced_avg_altitude",  # Enhanced average altitude in meters
    114: "enhanced_min_altitude",  # Enhanced minimum altitude in meters
    115: "enhanced_max_altitude",  # Enhanced maximum altitude in meters
    116: "avg_lev_motor_power",  # Average motor power in watts
    117: "max_lev_motor_power",  # Maximum motor power in watts
    118: "lev_battery_consumption",  # Battery consumption in percent
    119: "avg_vertical_ratio",  # Average vertical ratio in percent
    120: "avg_stance_time_balance",  # Average stance time balance in percent
    121: "avg_step_length",  # Average step length in millimeters
    122: "avg_vam",  # Average velocity ascending in meters per hour
    123: "total_grit",  # Total grit score
    124: "total_flow",  # Total flow score
    125: "jump_count",  # Jump count
    126: "avg_grit",  # Average grit score
    127: "avg_flow",  # Average flow score
    128: "total_fractional_ascent",  # Total fractional ascent in meters
    129: "total_fractional_descent",  # Total fractional descent in meters
}

# Lap Message Fields (Message Type 19)
LAP_FIELDS = {
    253: "timestamp",  # Lap end time
    254: "message_index",  # Message index
    0: "event",  # Lap trigger event
    1: "event_type",  # Lap trigger event type
    2: "start_time",  # Lap start time
    3: "start_position_lat",  # Start latitude in semicircles
    4: "start_position_long",  # Start longitude in semicircles
    5: "end_position_lat",  # End latitude in semicircles
    6: "end_position_long",  # End longitude in semicircles
    7: "total_elapsed_time",  # Total elapsed time in seconds
    8: "total_timer_time",  # Total timer time in seconds
    9: "total_distance",  # Total distance in meters
    10: "total_cycles",  # Total cycles
    11: "total_calories",  # Total calories
    12: "total_fat_calories",  # Total fat calories
    13: "avg_speed",  # Average speed in meters per second
    14: "max_speed",  # Maximum speed in meters per second
    15: "avg_heart_rate",  # Average heart rate in beats per minute
    16: "max_heart_rate",  # Maximum heart rate in beats per minute
    17: "avg_cadence",  # Average cadence in revolutions per minute
    18: "max_cadence",  # Maximum cadence in revolutions per minute
    19: "avg_power",  # Average power in watts
    20: "max_power",  # Maximum power in watts
    21: "total_ascent",  # Total ascent in meters
    22: "total_descent",  # Total descent in meters
    23: "intensity",  # Lap intensity
    24: "lap_trigger",  # Lap trigger
    25: "sport",  # Sport type
    26: "event_group",  # Event group
    32: "num_lengths",  # Number of lengths
    33: "normalized_power",  # Normalized power in watts
    34: "left_right_balance",  # Left/right balance
    35: "first_length_index",  # Index of first length
    37: "avg_stroke_count",  # Average stroke count
    38: "avg_stroke_distance",  # Average stroke distance in meters
    39: "swim_stroke",  # Swimming stroke type
    40: "sub_sport",  # Sub sport type
    41: "num_active_lengths",  # Number of active lengths
    42: "total_work",  # Total work in joules
    43: "avg_altitude",  # Average altitude in meters
    44: "max_altitude",  # Maximum altitude in meters
    45: "gps_accuracy",  # GPS accuracy in meters
    46: "avg_grade",  # Average grade in percent
    47: "avg_pos_grade",  # Average positive grade in percent
    48: "avg_neg_grade",  # Average negative grade in percent
    49: "max_pos_grade",  # Maximum positive grade in percent
    50: "max_neg_grade",  # Maximum negative grade in percent
    51: "avg_temperature",  # Average temperature in degrees Celsius
    52: "max_temperature",  # Maximum temperature in degrees Celsius
    53: "total_moving_time",  # Total moving time in seconds
    54: "avg_pos_vertical_speed",  # Average positive vertical speed in meters per second
    55: "avg_neg_vertical_speed",  # Average negative vertical speed in meters per second
    56: "max_pos_vertical_speed",  # Maximum positive vertical speed in meters per second
    57: "max_neg_vertical_speed",  # Maximum negative vertical speed in meters per second
    58: "time_in_hr_zone",  # Time in heart rate zones in seconds
    59: "time_in_speed_zone",  # Time in speed zones in seconds
    60: "time_in_cadence_zone",  # Time in cadence zones in seconds
    61: "time_in_power_zone",  # Time in power zones in seconds
    62: "repetition_num",  # Repetition number
    63: "min_altitude",  # Minimum altitude in meters
    64: "min_heart_rate",  # Minimum heart rate in beats per minute
    65: "wkt_step_index",  # Workout step index
    66: "opponent_score",  # Opponent score
    67: "stroke_count",  # Total stroke count
    68: "zone_count",  # Zone count
    69: "avg_vertical_oscillation",  # Average vertical oscillation in millimeters
    70: "avg_stance_time_percent",  # Average stance time percentage
    71: "avg_stance_time",  # Average stance time in milliseconds
    72: "avg_fractional_cadence",  # Average fractional cadence in revolutions per minute
    73: "max_fractional_cadence",  # Maximum fractional cadence in revolutions per minute
    74: "total_fractional_cycles",  # Total fractional cycles
    75: "player_score",  # Player score
    76: "avg_total_hemoglobin_conc",  # Average total hemoglobin concentration
    77: "min_total_hemoglobin_conc",  # Minimum total hemoglobin concentration
    78: "max_total_hemoglobin_conc",  # Maximum total hemoglobin concentration
    79: "avg_saturated_hemoglobin_percent",  # Average saturated hemoglobin percentage
    80: "min_saturated_hemoglobin_percent",  # Minimum saturated hemoglobin percentage
    81: "max_saturated_hemoglobin_percent",  # Maximum saturated hemoglobin percentage
    82: "avg_left_torque_effectiveness",  # Average left torque effectiveness percentage
    83: "avg_right_torque_effectiveness",  # Average right torque effectiveness percentage
    84: "avg_left_pedal_smoothness",  # Average left pedal smoothness percentage
    85: "avg_right_pedal_smoothness",  # Average right pedal smoothness percentage
    86: "avg_combined_pedal_smoothness",  # Average combined pedal smoothness percentage
    87: "time_standing",  # Time standing in seconds
    88: "stand_count",  # Stand count
    89: "avg_left_pco",  # Average left platform center offset in millimeters
    90: "avg_right_pco",  # Average right platform center offset in millimeters
    91: "avg_left_power_phase",  # Average left power phase angles
    92: "avg_left_power_phase_peak",  # Average left power phase peak angles
    93: "avg_right_power_phase",  # Average right power phase angles
    94: "avg_right_power_phase_peak",  # Average right power phase peak angles
    95: "avg_power_position",  # Average power position in watts
    96: "max_power_position",  # Maximum power position in watts
    97: "avg_cadence_position",  # Average cadence position in revolutions per minute
    98: "max_cadence_position",  # Maximum cadence position in revolutions per minute
    99: "enhanced_avg_speed",  # Enhanced average speed in meters per second
    100: "enhanced_max_speed",  # Enhanced maximum speed in meters per second
    101: "enhanced_avg_altitude",  # Enhanced average altitude in meters
    102: "enhanced_min_altitude",  # Enhanced minimum altitude in meters
    103: "enhanced_max_altitude",  # Enhanced maximum altitude in meters
    104: "avg_lev_motor_power",  # Average motor power in watts
    105: "max_lev_motor_power",  # Maximum motor power in watts
    106: "lev_battery_consumption",  # Battery consumption in percent
    107: "avg_vertical_ratio",  # Average vertical ratio in percent
    108: "avg_stance_time_balance",  # Average stance time balance in percent
    109: "avg_step_length",  # Average step length in millimeters
    110: "avg_vam",  # Average velocity ascending in meters per hour
}

# All field mappings by message type
FIELD_MAPPINGS = {
    MessageType.RECORD: RECORD_FIELDS,
    MessageType.SESSION: SESSION_FIELDS,
    MessageType.LAP: LAP_FIELDS,
}


def get_field_mapping(message_type: MessageType) -> Dict[int, str]:
    """Get field mapping for a specific message type."""
    return FIELD_MAPPINGS.get(message_type, {})


def get_field_name(message_type: MessageType, field_number: int) -> str:
    """Get the field name for a message type and field number."""
    mapping = get_field_mapping(message_type)
    return mapping.get(field_number, f"field_{field_number}")


def get_available_message_types() -> Dict[str, int]:
    """Get all available message types that can be read."""
    return {
        "record": MessageType.RECORD,
        "session": MessageType.SESSION,
        "lap": MessageType.LAP,
        "file_id": MessageType.FILE_ID,
        "event": MessageType.EVENT,
        "device_info": MessageType.DEVICE_INFO,
        "activity": MessageType.ACTIVITY,
        "workout": MessageType.WORKOUT,
        "course": MessageType.COURSE,
        "course_point": MessageType.COURSE_POINT,
        "hr": MessageType.HR,
        "length": MessageType.LENGTH,
    }


def convert_semicircles_to_degrees(semicircles: float) -> float:
    """Convert position coordinates from semicircles to degrees."""
    return semicircles * 180.0 / (2**31)


def convert_degrees_to_semicircles(degrees: float) -> int:
    """Convert position coordinates from degrees to semicircles."""
    return int(degrees * (2**31) / 180.0)
