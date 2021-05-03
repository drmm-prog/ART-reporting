import csv
import numpy as np
from scipy.optimize import curve_fit
import warnings

def convert_dates(times):
    return [convert_date(t) for t in times]

def convert_date(time):
    return (str(time//4) + ", Q"+str(time%4 + 1))

def cubic(x,a,b,c,d):
    return (a*x**3 + b*x**2 + c*x + d)

def calculate_cubic_model(xvals, yvals):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        popt, pcov = curve_fit(cubic, xvals, yvals)
    return lambda x: cubic(x, popt[0], popt[1], popt[2], popt[3])

def check_for_outlier(x, data):
    xvals = np.array([k for k in data.keys()])
    yvals = np.array([v for v in data.values()])
    model = calculate_cubic_model(xvals, yvals)
    model_vals = model(xvals)
    model_y = model(x)
    standard_deviation = np.sqrt(sum((yvals - model_vals)**2)/(len(yvals)))
    if x in data:
        deviance = (data[x] - model_y)
        if abs(deviance) > 2*standard_deviation:
            return True, "Deviation"
        else:
            return False, "Okay"
    else:   
        return True, "Missing data"

def check_data(data):
    xvals = np.array([k for k in data.keys()])
    yvals = np.array([v for v in data.values()])
    model = calculate_cubic_model(xvals, yvals)
    model_vals = model(xvals)
    deviance = (yvals - model_vals)/model_vals
    suspicious_points = []
    for i in range(0, len(xvals)):
        if abs(deviance[i]) > 0.05:
            suspicious_points.append(xvals[i])
    return suspicious_points

def get_deviations(district_data, district_facilities, facility_data):
    for district in district_data:
            suspicious_points = check_data(district_data[district])
            if len(suspicious_points) > 0:
                print("Suspicious data points in " + district + " at ", convert_dates(suspicious_points))
                for facility in district_facilities[district]:
                    for p in suspicious_points:
                        deviant, problem = check_for_outlier(p, facility_data[facility])
                        if deviant:
                            print("\t" + problem + " found at " + facility + " at " + convert_date(p))

def get_locations(filename):
    facility_to_district = {}
    district_facilities = {}
    with open(filename) as district_file:
        district_reader = csv.DictReader(district_file)
        for row in district_reader:
            facility = row['facility']
            district = row['district']
            facility_to_district[facility] = district
            if district in district_facilities:
                district_facilities[district].append(facility)
            else:
                district_facilities[district] = [facility]
    return facility_to_district, district_facilities

def add_to_counts(place, counts, time, num):
    if place in counts:
        if time in counts[place]:
            counts[place][time] += num
        else:
            counts[place][time] = num
    else:
        counts[place] = {}
        counts[place][time] = num

def get_art_data(filename, facility_to_district):
    district_data = {}
    facility_data = {}
    with open(filename) as dataFile:
        data_reader = csv.DictReader(dataFile)
        for row in data_reader:
            facility = row['facility']
            if facility in facility_to_district:
                district = facility_to_district[facility]
            else:
                continue
            quarter = int(row['year']) * 4 + (int(row['quarter'])-1)
            art_current = 0
            try:
                art_current = int(row['art_current'])
            except:
                continue
            add_to_counts(district, district_data, quarter, art_current)
            add_to_counts(facility, facility_data, quarter, art_current)
    return district_data, facility_data