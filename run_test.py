import Data_Checks as DC
import sys

if not (len(sys.argv) == 3):
    print("Please run the script with two arguments as follows:")
    print("python3 testfile.py <facility_list> <art_reporting>")
else:
    facility_to_district, district_facilities = DC.get_locations(sys.argv[1])
    district_data, facility_data = DC.get_art_data(sys.argv[2], facility_to_district)
    DC.get_deviations(district_data, district_facilities, facility_data)