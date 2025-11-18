import qrcode
import sys
from .core import crc16, serialize_data

class static_generator:
    """
    Generates a static, personal PayNow QR (editable amount).
    """

    def generate_qr_string(self, mobile_number: str, merchant_name: str = "NA") -> str:
        """
        Generates the QR payload string.
        
        :param mobile_number: Your 8-digit mobile number (e.g., "80000000")
        :param merchant_name: The name to display (defaults to "NA")
        :return: The final QR code string, or None if an error occurs.
        """
        # Ensure mobile number has the correct '+65' prefix
        if not mobile_number.startswith('+'):
            if mobile_number.startswith('65'):
                mobile_number = '+' + mobile_number
            else:
                mobile_number = '+65' + mobile_number
        
        data_blueprint = [
            {'id': '00', 'value': '01'},
            {'id': '01', 'value': '11'}, # Point of Initiation: 11 = Static
            {
                'id': '26',
                'value': [
                    {'id': '00', 'value': 'SG.PAYNOW'},
                    {'id': '01', 'value': '0'},       # Proxy Type: 0 = Mobile
                    {'id': '02', 'value': mobile_number},
                    {'id': '03', 'value': '1'},       # Editable Amount: 1 = True
                ]
            },
            {'id': '52', 'value': '0000'},
            {'id': '53', 'value': '702'},
            {'id': '58', 'value': 'SG'},
            {'id': '59', 'value': merchant_name},
            {'id': '60', 'value': 'Singapore'},
        ]

        try:
            payload = serialize_data(data_blueprint)
            payload_with_crc_header = payload + "6304"
            crc_val = crc16(payload_with_crc_header)
            return payload_with_crc_header + crc_val
        except Exception as e:
            print(f"An error occurred during string generation: {e}", file=sys.stderr)
            return None

    def show_qr(self, mobile_number: str, merchant_name: str = "NA"):
        """
        Generates and displays the QR code in a new window.
        """
        qr_string = self.generate_qr_string(mobile_number, merchant_name)
        if qr_string:
            img = qrcode.make(qr_string)
            img.show()
        else:
            print("Error: Could not generate QR to show.", file=sys.stderr)

    def save_qr(self, filename: str, mobile_number: str, merchant_name: str = "NA"):
        """
        Generates and saves the QR code to a file.
        """
        qr_string = self.generate_qr_string(mobile_number, merchant_name)
        if qr_string:
            try:
                img = qrcode.make(qr_string)
                img.save(filename)
                print(f"Successfully saved QR code to: {filename}")
            except Exception as e:
                print(f"Error saving image: {e}", file=sys.stderr)
        else:
            print("Error: Could not generate QR to save.", file=sys.stderr)