"""
InputValidator - Validate các input từ người dùng
"""
import re


class InputValidator:
    @staticmethod
    def validate_room_code(room_code):
        """
        Validate mã phòng (6 chữ số)

        Returns:
            (is_valid, error_message)
        """
        if not room_code:
            return False, "Mã phòng không được để trống"

        if not room_code.isdigit():
            return False, "Mã phòng phải là số"

        if len(room_code) != 6:
            return False, "Mã phòng phải có 6 chữ số"

        return True, ""

    @staticmethod
    def validate_ip(ip):
        """
        Validate địa chỉ IP

        Returns:
            (is_valid, error_message)
        """
        if not ip:
            return False, "IP không được để trống"

        pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(pattern, ip):
            return False, "Định dạng IP không hợp lệ"

        parts = ip.split('.')
        for part in parts:
            if int(part) > 255:
                return False, "IP không hợp lệ (mỗi phần phải <= 255)"

        return True, ""

    @staticmethod
    def validate_port(port):
        """
        Validate port number

        Returns:
            (is_valid, error_message)
        """
        try:
            port_num = int(port)
            if port_num < 1 or port_num > 65535:
                return False, "Port phải trong khoảng 1-65535"
            return True, ""
        except:
            return False, "Port phải là số"

    @staticmethod
    def sanitize_input(text, max_length=100):
        """
        Làm sạch input text

        Args:
            text: Text cần làm sạch
            max_length: Độ dài tối đa

        Returns:
            Text đã làm sạch
        """
        if not text:
            return ""

        # Loại bỏ khoảng trắng thừa
        text = text.strip()

        # Giới hạn độ dài
        if len(text) > max_length:
            text = text[:max_length]

        return text

