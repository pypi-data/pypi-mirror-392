from wiliot_tools.test_equipment.test_equipment import ZebraPrinter

# You can create and edit labels here: https://labelary.com/viewer.html
p = ZebraPrinter()
label = """
^XA

^FX Third section with bar code.
^BY5,2,270
^FO100,550^BC^FD12345078^FS

^FX Fourth section (the two boxes on the bottom).
^FO50,900^GB700,250,3^FS
^FO400,900^GB3,250,3^FS
^CF0,40
^FO100,960^FDCtr. X34B-1^FS
^FO100,1010^FDREF1 F00B47^FS
^FO100,1060^FDREF2 BL4H8^FS
^CF0,190
^FO470,955^FDCA^FS

^XZ
"""
p.print_label(label)
