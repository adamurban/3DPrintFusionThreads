import math
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod

NAME = "3D-printed Metric Threads V4"
UNIT = "mm"
ANGLE = 60.0
SIZES = list(range(1, 51))
# Standard ISO metric thread pitches for each size
# Format: {size: [coarse_pitch, fine_pitch1, fine_pitch2, ...]}
ISO_PITCHES = {
    1: [0.25, 0.2],
    2: [0.4, 0.25],
    3: [0.5, 0.35],
    4: [0.7, 0.5],
    5: [0.8, 0.5],
    6: [1.0, 0.75],
    7: [1.0],  # Less common
    8: [1.25, 1.0, 0.75],
    9: [1.25],  # Less common
    10: [1.5, 1.25, 1.0],
    11: [1.5],  # Less common
    12: [1.75, 1.5, 1.25],
    13: [1.75],  # Less common
    14: [2.0, 1.5],
    15: [2.0],  # Less common
    16: [2.0, 1.5],
    17: [2.0],  # Less common
    18: [2.5, 2.0, 1.5],
    19: [2.5],  # Less common
    20: [2.5, 2.0, 1.5],
    21: [2.5],  # Less common
    22: [2.5, 2.0, 1.5],
    23: [2.5],  # Less common
    24: [3.0, 2.0, 1.5],
    25: [3.0],  # Less common
    26: [3.0],  # Less common
    27: [3.0, 2.0, 1.5],
    28: [3.0],  # Less common
    29: [3.0],  # Less common
    30: [3.5, 2.0, 1.5],
    31: [3.5],  # Less common
    32: [3.5],  # Less common
    33: [3.5, 2.0],
    34: [3.5],  # Less common
    35: [3.5],  # Less common
    36: [4.0, 3.0],
    37: [4.0],  # Less common
    38: [4.0],  # Less common
    39: [4.0, 3.0],
    40: [4.0],  # Less common
    41: [4.0],  # Less common
    42: [4.5, 3.0],
    43: [4.5],  # Less common
    44: [4.5],  # Less common
    45: [4.5, 3.0],
    46: [4.5],  # Less common
    47: [4.5],  # Less common
    48: [5.0, 3.0],
    49: [5.0],  # Less common
    50: [5.0, 3.0]
}
OFFSETS = [.0, .1, .2, .3, .4, .5, .6, .7, .8, .9]

# SAE/UTS thread specifications
# Format: {size: [coarse_pitch, fine_pitch1, fine_pitch2, ...]}
# Size format: "diameter-pitch" for numbered sizes, diameter for fractional sizes
SAE_SIZES = [
    "4-40", "4-48", "6-32", "6-40", "8-32", "8-36", "10-24", "10-32",
    "12-24", "12-28", "1/4-20", "1/4-28", "5/16-18", "5/16-24",
    "3/8-16", "3/8-24", "7/16-14", "7/16-20", "1/2-13", "1/2-20",
    "9/16-12", "9/16-18", "5/8-11", "5/8-18", "3/4-10", "3/4-16",
    "7/8-9", "7/8-14", "1-8", "1-12", "1-14", "1 1/8-7", "1 1/8-12",
    "1 1/4-7", "1 1/4-12", "1 1/2-6", "1 1/2-12", "1 3/4-5", "2-4.5"
]

# Standard diameters for numbered thread sizes (inches)
NUMBERED_DIAMETERS = {
    "4": 0.1120,    # #4
    "6": 0.1380,    # #6
    "8": 0.1640,    # #8
    "10": 0.1900,   # #10
    "12": 0.2160    # #12
}

SAE_PITCHES = {
    "112": [40, 48],    # #4 (0.112") threads per inch
    "138": [32, 40],    # #6 (0.138") threads per inch
    "164": [32, 36],    # #8 (0.164") threads per inch
    "190": [24, 32],    # #10 (0.190") threads per inch
    "216": [24, 28],    # #12 (0.216") threads per inch
    "1/4": [20, 28],    # 1/4 inch
    "5/16": [18, 24],   # 5/16 inch
    "3/8": [16, 24],    # 3/8 inch
    "7/16": [14, 20],   # 7/16 inch
    "1/2": [13, 20],    # 1/2 inch
    "9/16": [12, 18],   # 9/16 inch
    "5/8": [11, 18],    # 5/8 inch
    "3/4": [10, 16],    # 3/4 inch
    "7/8": [9, 14],     # 7/8 inch
    "1": [8, 12, 14],   # 1 inch
    "1 1/8": [7, 12],   # 1 1/8 inch
    "1 1/4": [7, 12],   # 1 1/4 inch
    "1 1/2": [6, 12],   # 1 1/2 inch
    "1 3/4": [5],       # 1 3/4 inch
    "2": [4.5]          # 2 inch
}


def designator(val: float):
    if int(val) == val:
        return str(int(val))
    else:
        return str(val)


class Thread:
    def __init__(self):
        self.gender = None
        self.clazz = None
        self.majorDia = 0
        self.pitchDia = 0
        self.minorDia = 0
        self.tapDrill = None


class ThreadProfile(ABC):
    @abstractmethod
    def sizes(self):
        pass

    @abstractmethod
    def designations(self, size):
        pass

    @abstractmethod
    def threads(self, designation):
        pass


class Metric3Dprinted(ThreadProfile):
    class Designation:
        def __init__(self, diameter, pitch):
            self.nominalDiameter = diameter
            self.pitch = pitch
            self.name = "M{}x{}".format(designator(self.nominalDiameter), designator(self.pitch))

    def __init__(self):
        self.offsets = OFFSETS

    def sizes(self):
        return SIZES

    def designations(self, size):
        # Get pitches for this size, default to [0.5] if not defined
        pitches = ISO_PITCHES.get(size, [0.5])
        return [Metric3Dprinted.Designation(size, pitch) for pitch in pitches]

    def threads(self, designation):
        ts = []
        for offset in self.offsets:
            offset_decimals = str(offset)[2:]  # skips the '0.' at the start

            # see https://en.wikipedia.org/wiki/ISO_metric_screw_thread
            P = designation.pitch
            H = 1/math.tan(math.radians(ANGLE/2)) * (P/2)
            D = designation.nominalDiameter
            Dp = D - 2 * 3*H/8
            Dmin = D - 2 * 5*H/8

            t = Thread()
            t.gender = "external"
            t.clazz = "O.{}".format(offset_decimals)
            t.majorDia = D - offset
            t.pitchDia = Dp - offset
            t.minorDia = Dmin - offset
            ts.append(t)

            t = Thread()
            t.gender = "internal"
            t.clazz = "O.{}".format(offset_decimals)
            t.majorDia = D + offset
            t.pitchDia = Dp + offset
            t.minorDia = Dmin + offset
            t.tapDrill = D - P
            ts.append(t)
        return ts


class SAE3Dprinted(ThreadProfile):
   class Designation:
       def __init__(self, diameter, tpi, thread_type="UNC"):
           self.nominalDiameter = diameter
           self.threadsPerInch = tpi
           self.threadType = thread_type
           # Convert TPI to pitch in mm
           self.pitch = 25.4 / tpi  # 25.4 mm per inch
           # Handle fractional diameters in name
           if isinstance(diameter, str) and '/' in diameter:
               self.name = "{} {}-{}".format(thread_type, diameter, tpi)
           else:
               self.name = "{} {}-{}".format(
                   thread_type,
                   designator(self.nominalDiameter),
                   tpi
               )

   def __init__(self):
       self.offsets = OFFSETS

   def sizes(self):
       return SAE_SIZES

   def designations(self, size):
       # Parse size to extract diameter and determine thread type
       if size in ["4-40", "4-48", "6-32", "6-40", "8-32", "8-36",
                  "10-24", "10-32", "12-24", "12-28"]:
           # Numbered sizes - extract the number
           parts = size.split('-')
           diameter_num = int(parts[0])
           thread_type = "UNF" if float(parts[1]) > 32 else "UNC"

           # Look up actual diameter in inches
           if str(diameter_num) in NUMBERED_DIAMETERS:
               diameter = NUMBERED_DIAMETERS[str(diameter_num)]
           else:
               diameter = diameter_num / 100.0  # Fallback conversion
       else:
           # Fractional sizes
           parts = size.replace(' ', '').split('-')
           diameter = parts[0]
           thread_type = "UNF" if float(parts[1]) > 20 else "UNC"

       # Get TPI options for this diameter - use the number string as key for numbered sizes
       if isinstance(diameter, float) and diameter < 1.0:
           # This is a numbered size, use the number as key
           diameter_key = str(int(diameter * 1000))  # Convert 0.112 to "112"
       else:
           # This is a fractional size
           diameter_key = diameter if isinstance(diameter, str) else str(int(diameter * 1000))

       if diameter_key in SAE_PITCHES:
           tpi_options = SAE_PITCHES[diameter_key]
           designations = []
           for tpi in tpi_options:
               designations.append(SAE3Dprinted.Designation(diameter, tpi, thread_type))
           return designations

       return [SAE3Dprinted.Designation(diameter, 20, "UNC")]  # Default fallback

   def threads(self, designation):
       ts = []
       for offset in self.offsets:
           offset_decimals = str(offset)[2:]  # skips the '0.' at the start

           # SAE/UTS thread calculations
           # Based on Unified Thread Standard
           P = designation.pitch  # Pitch in mm

           # Convert diameter to decimal if it's a fraction
           D = designation.nominalDiameter
           if isinstance(D, str):
               if '/' in D:
                   # Convert fraction to decimal (e.g., "1/4" -> 0.25)
                   parts = D.split('/')
                   if len(parts) == 2:
                       D = float(parts[0]) / float(parts[1])
                   else:
                       # Handle mixed fractions like "1 1/4"
                       whole_part = D.split(' ')[0]
                       fraction_part = D.split(' ')[1]
                       frac_parts = fraction_part.split('/')
                       D = float(whole_part) + float(frac_parts[0]) / float(frac_parts[1])
               else:
                   D = float(D)

           # For external threads (bolts)
           Dp_ext = D - 0.649519 * P  # Pitch diameter for external threads
           Dmin_ext = D - 1.299038 * P  # Minor diameter for external threads

           # For internal threads (nuts)
           Dp_int = D + 0.649519 * P  # Pitch diameter for internal threads
           Dmin_int = D + 1.299038 * P  # Minor diameter for internal threads

           # External thread
           t = Thread()
           t.gender = "external"
           t.clazz = "O.{}".format(offset_decimals)
           t.majorDia = D - offset
           t.pitchDia = Dp_ext - offset
           t.minorDia = Dmin_ext - offset
           ts.append(t)

           # Internal thread
           t = Thread()
           t.gender = "internal"
           t.clazz = "O.{}".format(offset_decimals)
           t.majorDia = D + offset
           t.pitchDia = Dp_int + offset
           t.minorDia = Dmin_int + offset
           # Tap drill = basic major diameter minus pitch
           t.tapDrill = D - P
           ts.append(t)

       return ts


def generate():
    # Generate Metric threads
    metric_profile = Metric3Dprinted()
    metric_root = ET.Element('ThreadType')
    metric_tree = ET.ElementTree(metric_root)

    ET.SubElement(metric_root, "Name").text = NAME
    ET.SubElement(metric_root, "CustomName").text = NAME
    ET.SubElement(metric_root, "Unit").text = UNIT
    ET.SubElement(metric_root, "Angle").text = str(ANGLE)
    ET.SubElement(metric_root, "SortOrder").text = "3"

    for size in metric_profile.sizes():
        thread_size_element = ET.SubElement(metric_root, "ThreadSize")
        ET.SubElement(thread_size_element, "Size").text = str(size)
        for designation in metric_profile.designations(size):
            designation_element = ET.SubElement(thread_size_element, "Designation")
            ET.SubElement(designation_element, "ThreadDesignation").text = designation.name
            ET.SubElement(designation_element, "CTD").text = designation.name
            ET.SubElement(designation_element, "Pitch").text = str(designation.pitch)
            for thread in metric_profile.threads(designation):
                thread_element = ET.SubElement(designation_element, "Thread")
                ET.SubElement(thread_element, "Gender").text = thread.gender
                ET.SubElement(thread_element, "Class").text = thread.clazz
                ET.SubElement(thread_element, "MajorDia").text = "{:.4g}".format(thread.majorDia)
                ET.SubElement(thread_element, "PitchDia").text = "{:.4g}".format(thread.pitchDia)
                ET.SubElement(thread_element, "MinorDia").text = "{:.4g}".format(thread.minorDia)
                if thread.tapDrill:
                    ET.SubElement(thread_element, "TapDrill").text = "{:.4g}".format(thread.tapDrill)

    ET.indent(metric_tree)
    metric_tree.write('3DPrintedMetricV4.xml', encoding='UTF-8', xml_declaration=True)

    # Generate SAE threads
    sae_profile = SAE3Dprinted()
    sae_name = "3D-printed SAE Threads V1"
    sae_root = ET.Element('ThreadType')
    sae_tree = ET.ElementTree(sae_root)

    ET.SubElement(sae_root, "Name").text = sae_name
    ET.SubElement(sae_root, "CustomName").text = sae_name
    ET.SubElement(sae_root, "Unit").text = UNIT
    ET.SubElement(sae_root, "Angle").text = str(ANGLE)
    ET.SubElement(sae_root, "SortOrder").text = "4"

    for size in sae_profile.sizes():
        thread_size_element = ET.SubElement(sae_root, "ThreadSize")
        ET.SubElement(thread_size_element, "Size").text = size
        for designation in sae_profile.designations(size):
            designation_element = ET.SubElement(thread_size_element, "Designation")
            ET.SubElement(designation_element, "ThreadDesignation").text = designation.name
            ET.SubElement(designation_element, "CTD").text = designation.name
            ET.SubElement(designation_element, "Pitch").text = "{:.4f}".format(designation.pitch)
            for thread in sae_profile.threads(designation):
                thread_element = ET.SubElement(designation_element, "Thread")
                ET.SubElement(thread_element, "Gender").text = thread.gender
                ET.SubElement(thread_element, "Class").text = thread.clazz
                ET.SubElement(thread_element, "MajorDia").text = "{:.4g}".format(thread.majorDia)
                ET.SubElement(thread_element, "PitchDia").text = "{:.4g}".format(thread.pitchDia)
                ET.SubElement(thread_element, "MinorDia").text = "{:.4g}".format(thread.minorDia)
                if thread.tapDrill:
                    ET.SubElement(thread_element, "TapDrill").text = "{:.4g}".format(thread.tapDrill)

    ET.indent(sae_tree)
    sae_tree.write('3DPrintedSAEV1.xml', encoding='UTF-8', xml_declaration=True)


generate()
