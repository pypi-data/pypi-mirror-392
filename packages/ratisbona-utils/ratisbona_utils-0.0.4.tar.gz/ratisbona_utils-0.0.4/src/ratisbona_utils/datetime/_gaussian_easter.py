from collections import defaultdict
from datetime import date, timedelta
import matplotlib.pyplot as plt


def calculate_easter_date(year_x: int) -> date:

    saekularzahl_k = year_x // 100
    mondparameter_a = year_x % 19

    zweimal_benoetigt = (3 * saekularzahl_k + 3) // 4

    saekulare_mondschaltung_m = 15 + zweimal_benoetigt - (8 * saekularzahl_k + 13) // 25
    saekulare_sonnenschaltung_s = 2 - zweimal_benoetigt

    keim_des_ersten_vollmonds_im_fruehling_d = (
        19 * mondparameter_a + saekulare_mondschaltung_m
    ) % 30
    kalendarische_korrekturgroesse_r = (
        keim_des_ersten_vollmonds_im_fruehling_d + mondparameter_a // 11
    ) // 29
    erster_sonntag_im_maerz_sz = 7 - (year_x + year_x // 4 + saekulare_sonnenschaltung_s) % 7

    ostergrenze_og = 21 + keim_des_ersten_vollmonds_im_fruehling_d - kalendarische_korrekturgroesse_r

    osterentfernung_von_ostergrenze_oe = 7 - (ostergrenze_og - erster_sonntag_im_maerz_sz) % 7

    ostersonntag_als_maerzdatum = ostergrenze_og + osterentfernung_von_ostergrenze_oe

    return date(year_x, 3, 1) + timedelta(days=ostersonntag_als_maerzdatum - 1)


