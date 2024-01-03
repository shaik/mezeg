def get_weather_icon(cloud_cover, precipitation):
    if precipitation > 7.6:
        return "heavy_rain.png"
    elif precipitation > 2.5:
        return "moderate_rain.png"
    elif precipitation > 0:
        if cloud_cover < 3/8:
            return "clear_light_rain.png"
        else:
            return "light_rain.png"
    elif cloud_cover > 5/8:
        return "cloudy.png"
    elif cloud_cover > 3/8:
        return "mostly_cloudy.png"
    elif cloud_cover > 1/8:
        return "partly_cloudy.png"
    else:
        return "clear_sunny.png"


def K2C(kelvin_temp):
    celsius_temp = kelvin_temp - 273.15
    return round(celsius_temp)


def mps_to_kph(speed_mps):
    speed_kph = speed_mps * 3.6  # 1 m/s is approximately 3.6 kph
    return round(speed_kph)


def get_sky_condition(cloud_cover):
    if cloud_cover <= 1/8:
        return "Clear"
    elif 1/8 < cloud_cover <= 3/8:
        return "Mostly Clear"
    elif 3/8 < cloud_cover <= 5/8:
        return "Partly Cloudy"
    elif 5/8 < cloud_cover <= 7/8:
        return "Mostly Cloudy"
    else:  # cloud_cover > 7/8
        return "Cloudy"


def format_precipitation(precipitation):
    if precipitation == 0:
        return "-"
    elif precipitation < 1:
        return "<1 mm"
    else:
        return f"{round(precipitation)} mm"

