import math
from datetime import date, timedelta

#Synchronized Timeline. 
#wt = total ticks in the world, output of /time query gametime
#wt_atbs = total ticks in the world, at the beginning of the seasons
#wt_as = totwl ticks in the world in the Eras After the Seasons
#t = tick
#dw = days in the world
#mw = months in the world
#yw = years in the world

#Parallelized Timeline.
#O = origin
#O^ = origin of the Eras After the Seasons
#P = present
#tO = time since origin until the beginning of the Eras After the Seasons in days, O - Ox
#tOx = time since the beginning Eras After the Seasons in days, P - Ox
#dr = duration of day in real life, expressed in real life hours
#dm_bs = duration of days in Milkantis before seasons, expressed in real life hours
#dm_as = duration of days in Millantis after seasons, expressed in real life hourd

dw = 24000
yw = 360 * dw
mw = 30 * dw
wt_atbs = 1930880897
wt = 1962121156

hr = 1
dr = 24 * hr

dm_bs = hr / 3
mm_bs = 30 * dm_bs
ym_bs = 360 * dm_bs

dm_as = hr
mm_as = 30 * dm_as
ym_as = 360 * dm_as

O = date(2012, 7, 1)
Ox = date(2025, 12, 31)
P = date.today()
tO = (Ox - O).days * dr
tOx = (P - Ox).days * dr

def st_calculate(wt: int):
        st_y = wt / yw
        st_m = 12 * (st_y % 1)
        st_d = 30 * (st_m % 1)

        st_y_atbs = wt_atbs / yw
        
        wt_as = wt - wt_atbs
        st_y_as = wt_as / yw
        st_m_as = 12 * (st_y_as % 1)
        st_d_as = 30 * (st_m_as % 1)
        return st_y, st_m, st_d, st_y_atbs, st_y_as, st_m_as, st_d_as
        
def pt_calculate():
        pt_y_bs = tO / ym_bs
        pt_y_as = tOx / ym_as
        pt_y = pt_y_bs + pt_y_as
        pt_m = 12 * (pt_y % 1)
        pt_d = 30 * (pt_m % 1)

        years_until_the_millenium = 1000 - pt_y_bs
        days_until_the_millenium = (((1000 - pt_y_bs) * ym_as) / dr)

        return pt_y, pt_m, pt_d, pt_y_bs, pt_y_as, years_until_the_millenium, days_until_the_millenium
        
st = st_calculate(wt)
pt = pt_calculate()

#print('\nSynchronized Timeline---------')
#print(f'\n[Parameters]\nOrigin: 0 ticks\nOrigin of the Eras After the Seasons: {wt_atbs} ticks\nPresent: {wt} ticks\n')
#print(f'According to the Synchronized Timeline, the age of the world is {math.floor(st[0])} years, {math.floor(st[1])} months and {math.floor(st[2])} days.\nThe Eras After the Seasons started in the year {math.floor(st[3])}, and so the current date is the year {math.floor(st[4])} EAS.')
print('\nParallelized Timeline---------')
print(f'\n[Parameters]\nOrigin: {O}\nOrigin of the Eras After the Seasons: {Ox}\nPresent: {P}\n')
print(f'According to the Parallelized Timeline, the age of the world is {math.floor(pt[0])} years, {math.floor(pt[1])} months and {math.floor(pt[2])} days.\nThe Eras After the Seasons started in the year {math.floor(pt[3])}, and so the current year is {math.floor(pt[4])} EAS.')

print(f'\nTime until the millenium: {math.floor(pt[5])} years.\nThe millenium will come on {Ox + timedelta(days=pt[6])}')
