# File: sgpaynow/dynamic.py
import qrcode
import sys
from .core import crc16, serialize_data

class dynamic_generator:
    """
    Generates a PayNow QR with a pre-filled amount.
    - By default (editable=False), creates a DYNAMIC QR (amount locked).
    - With (editable=True), creates a STATIC QR (amount suggested but editable).
    """

    def generate_qr_string(self, mobile_number: str, amount: str, ref_number: str = "NA", 
                             merchant_name: str = "NA", editable: bool = False) -> str:
        """
        Generates the QR payload string.
        
        :param mobile_number: Your 8-digit mobile number (e.g., "80000000")
        :param amount: The fixed/suggested amount (e.g., "12.34")
        :param ref_number: The invoice or reference ID (e.g., "INV-456")
        :param merchant_name: The name to display (defaults to "NA")
        :param editable: If True, amount is pre-filled but can be changed.
                         If False, amount is locked (default dynamic QR).
        :return: The final QR code string, or None if an error occurs.
        """
        
        # --- Handle Editable Logic ---
        if editable:
            # Static QR with a suggested amount
            point_of_initiation = '11' # 11 = Static
            editable_flag = '1'        # 1 = True
        else:
            # True Dynamic QR with a locked amount
            point_of_initiation = '12' # 12 = Dynamic
            editable_flag = '0'        # 0 = False

        # Ensure mobile number has the correct '+65' prefix
        if not mobile_number.startswith('+'):
            mobile_number = '+65' + mobile_number.lstrip('65')

        data_blueprint = [
            {'id': '00', 'value': '01'},
            {'id': '01', 'value': point_of_initiation}, # 11 (Static) or 12 (Dynamic)
            {
                'id': '26',
                'value': [
                    {'id': '00', 'value': 'SG.PAYNOW'},
                    {'id': '01', 'value': '0'},       # Proxy Type: 0 = Mobile
                    {'id': '02', 'value': mobile_number},
                    {'id': '03', 'value': editable_flag}, # 1 (True) or 0 (False)
                ]
            },
            {'id': '52', 'value': '0000'},
            {'id': '53', 'value': '702'},
            {'id': '54', 'value': amount},        # Transaction amount
            {'id': '58', 'value': 'SG'},
            {'id': '59', 'value': merchant_name},
            {'id': '60', 'value': 'Singapore'},
            {                                     # Reference number
                'id': '62',
                'value': [
                    {'id': '01', 'value': ref_number} # ID 01 = Bill Number
                ]
            }
        ]

        try:
            payload = serialize_data(data_blueprint)
            payload_with_crc_header = payload + "6304"
            crc_val = crc16(payload_with_crc_header)
            return payload_with_crc_header + crc_val
        except Exception as e:
            print(f"An error occurred during string generation: {e}", file=sys.stderr)
            return None

    def show_qr(self, mobile_number: str, amount: str, ref_number: str, 
                merchant_name: str = "NA", editable: bool = False):
        """
        Generates and displays the QR code in a new window.
        """
        qr_string = self.generate_qr_string(mobile_number, amount, ref_number, 
                                            merchant_name, editable)
        if qr_string:
            img = qrcode.make(qr_string)
            img.show()
        else:
            print("Error: Could not generate QR to show.", file=sys.stderr)

    def save_qr(self, filename: str, mobile_number: str, amount: str, ref_number: str, 
                merchant_name: str = "NA", editable: bool = False):
        """
        Generates and saves the QR code to a file.
        """
        qr_string = self.generate_qr_string(mobile_number, amount, ref_number, 
                                            merchant_name, editable)
        if qr_string:
            try:
                img = qrcode.make(qr_string)
                img.save(filename)
                print(f"Successfully saved QR code to: {filename}")
            except Exception as e:
                print(f"Error saving image: {e}", file=sys.stderr)
        else:
            print("Error: Could not generate QR to save.", file=sys.stderr)