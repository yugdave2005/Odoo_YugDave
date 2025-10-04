# -*- coding: utf-8 -*-

import base64
import re
import logging
import requests
from datetime import datetime
from io import BytesIO

try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

from odoo import http, fields, api
from odoo.http import request
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ExpenseOCRController(http.Controller):
    """Controller for OCR-related endpoints - PDF Requirements Implementation"""

    @http.route('/expense/ocr/process', type='json', auth='user', methods=['POST'])
    def process_receipt_api(self, attachment_id):
        """API endpoint to process receipt OCR"""
        try:
            result = process_receipt_ocr(attachment_id)
            return {'success': True, 'data': result}
        except Exception as e:
            _logger.error(f"OCR API processing failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    @http.route('/expense/countries', type='json', auth='user', methods=['GET'])
    def get_countries_with_currencies(self):
        """PDF Requirement: API for country and their currency"""
        try:
            countries_data = get_countries_currencies()
            return {'success': True, 'data': countries_data}
        except Exception as e:
            _logger.error(f"Countries API failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    @http.route('/expense/currency/convert', type='json', auth='user', methods=['POST'])
    def convert_currency(self, amount, from_currency, to_currency):
        """PDF Requirement: Currency conversion API"""
        try:
            rate = get_currency_rate(from_currency, to_currency)
            converted_amount = float(amount) * rate
            return {
                'success': True, 
                'data': {
                    'rate': rate,
                    'converted_amount': converted_amount,
                    'from_currency': from_currency,
                    'to_currency': to_currency
                }
            }
        except Exception as e:
            _logger.error(f"Currency conversion API failed: {str(e)}")
            return {'success': False, 'error': str(e)}


def process_receipt_ocr(attachment_id):
    """
    Process receipt OCR to extract amount, date, and vendor information
    
    Args:
        attachment_id (int): ID of the attachment to process
        
    Returns:
        dict: Dictionary containing extracted data with keys: amount, date, vendor
    """
    if not OCR_AVAILABLE:
        raise UserError("OCR functionality is not available. Please install pytesseract and PIL.")
    
    try:
        # Get the attachment record
        attachment = request.env['ir.attachment'].sudo().browse(attachment_id)
        if not attachment.exists():
            raise UserError(f"Attachment with ID {attachment_id} not found.")
        
        # Check if it's an image
        if not attachment.mimetype or not attachment.mimetype.startswith('image/'):
            raise UserError("Attachment must be an image file for OCR processing.")
        
        # Get the binary data
        if attachment.datas:
            image_data = base64.b64decode(attachment.datas)
        else:
            raise UserError("No image data found in attachment.")
        
        # Process the image with OCR
        extracted_data = _extract_data_from_image(image_data)
        
        _logger.info(f"OCR processing completed for attachment {attachment_id}: {extracted_data}")
        return extracted_data
        
    except Exception as e:
        _logger.error(f"OCR processing failed for attachment {attachment_id}: {str(e)}")
        raise UserError(f"OCR processing failed: {str(e)}")


def _extract_data_from_image(image_data):
    """
    Extract data from image using OCR
    
    Args:
        image_data (bytes): Binary image data
        
    Returns:
        dict: Extracted data
    """
    try:
        # Open image using PIL
        image = Image.open(BytesIO(image_data))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Extract text using pytesseract
        extracted_text = pytesseract.image_to_string(image, config='--oem 3 --psm 6')
        
        _logger.info(f"Extracted text: {extracted_text}")
        
        # Parse the extracted text
        result = _parse_extracted_text(extracted_text)
        
        return result
        
    except Exception as e:
        _logger.error(f"Image processing failed: {str(e)}")
        raise UserError(f"Failed to process image: {str(e)}")


def _parse_extracted_text(text):
    """
    Parse extracted text to find amount, date, and vendor
    
    Args:
        text (str): OCR extracted text
        
    Returns:
        dict: Parsed data
    """
    result = {
        'amount': None,
        'date': None,
        'vendor': None
    }
    
    if not text:
        return result
    
    # Clean the text
    text = text.strip()
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # Extract amount using various patterns
    result['amount'] = _extract_amount(text)
    
    # Extract date using various patterns
    result['date'] = _extract_date(text)
    
    # Extract vendor (usually first line or prominent text)
    result['vendor'] = _extract_vendor(lines)
    
    return result


def _extract_amount(text):
    """Extract amount from text"""
    # Common currency symbols and patterns
    amount_patterns = [
        r'(?:total|amount|sum|price)[\s:]*[\$£€¥₹]?\s*(\d+[,.]?\d*)',  # Total: $123.45
        r'[\$£€¥₹]\s*(\d+[,.]?\d*)',  # $123.45
        r'(\d+[,.]\d{2})\s*(?:usd|eur|gbp|inr|jpy)',  # 123.45 USD
        r'(?:^|\s)(\d+[,.]\d{2})(?:\s|$)',  # Standalone decimal amount
        r'(\d+[,.]\d{2})',  # Any decimal amount
    ]
    
    for pattern in amount_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
        if matches:
            # Return the first match, clean it up
            amount_str = matches[0].replace(',', '')
            try:
                return float(amount_str)
            except ValueError:
                continue
    
    return None


def _extract_date(text):
    """Extract date from text"""
    # Common date patterns
    date_patterns = [
        r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',  # MM/DD/YYYY or DD/MM/YYYY
        r'(\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{2,4})',  # DD MMM YYYY
        r'((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{1,2},?\s+\d{2,4})',  # MMM DD, YYYY
        r'(\d{4}-\d{1,2}-\d{1,2})',  # YYYY-MM-DD
    ]
    
    for pattern in date_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            date_str = matches[0]
            # Try to parse the date
            parsed_date = _parse_date_string(date_str)
            if parsed_date:
                return parsed_date.strftime('%Y-%m-%d')
    
    return None


def _parse_date_string(date_str):
    """Parse various date string formats"""
    date_formats = [
        '%m/%d/%Y', '%d/%m/%Y', '%m/%d/%y', '%d/%m/%y',
        '%Y-%m-%d', '%Y/%m/%d',
        '%d %b %Y', '%d %B %Y',
        '%b %d, %Y', '%B %d, %Y',
        '%b %d %Y', '%B %d %Y',
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    
    return None


def _extract_vendor(lines):
    """Extract vendor name from text lines"""
    if not lines:
        return None
    
    # Skip common receipt headers and footers
    skip_patterns = [
        r'receipt|invoice|bill|tax|thank\s+you|visit|again',
        r'\d+[/-]\d+[/-]\d+',  # dates
        r'[\$£€¥₹]\s*\d+',  # amounts
        r'total|subtotal|amount|price|change',
        r'cash|card|credit|debit',
    ]
    
    for line in lines[:5]:  # Check first 5 lines
        if len(line) < 3 or len(line) > 50:  # Skip very short or long lines
            continue
        
        # Skip if line matches skip patterns
        if any(re.search(pattern, line, re.IGNORECASE) for pattern in skip_patterns):
            continue
        
        # Skip if line is mostly numbers
        if re.search(r'^\d+[\d\s]*$', line):
            continue
        
        # This looks like a vendor name
        return line.strip().title()
    
    # Fallback to first line if nothing better found
    return lines[0].strip().title() if lines else None


# Utility function for direct usage in models
def get_ocr_data_from_attachment(env, attachment_id):
    """
    Utility function to get OCR data from an attachment
    Can be called directly from models
    """
    try:
        attachment = env['ir.attachment'].browse(attachment_id)
        if not attachment.exists():
            return {}
        
        if attachment.datas:
            image_data = base64.b64decode(attachment.datas)
            return _extract_data_from_image(image_data)
        
    except Exception as e:
        _logger.error(f"OCR utility function failed: {str(e)}")
    
    return {}


def get_countries_currencies():
    """PDF Requirement: API for country and their currency
    Uses: https://restcountries.com/v3.1/all?fields=name,currencies
    """
    try:
        url = "https://restcountries.com/v3.1/all?fields=name,currencies"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        countries_data = response.json()
        processed_data = []
        
        for country in countries_data:
            country_name = country.get('name', {}).get('common', 'Unknown')
            currencies = country.get('currencies', {})
            
            country_currencies = []
            for currency_code, currency_info in currencies.items():
                country_currencies.append({
                    'code': currency_code,
                    'name': currency_info.get('name', currency_code),
                    'symbol': currency_info.get('symbol', '')
                })
            
            if country_currencies:  # Only include countries with currencies
                processed_data.append({
                    'country': country_name,
                    'currencies': country_currencies
                })
        
        return processed_data[:50]  # Limit to first 50 for performance
        
    except Exception as e:
        _logger.error(f"Failed to fetch countries and currencies: {str(e)}")
        return []


def get_currency_rate(from_currency, to_currency):
    """PDF Requirement: Currency conversion using external API
    Uses: https://api.exchangerate-api.com/v4/latest/{BASE_CURRENCY}
    """
    if from_currency == to_currency:
        return 1.0
    
    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        rates = data.get('rates', {})
        
        if to_currency not in rates:
            raise ValueError(f"Currency {to_currency} not found in rates")
        
        return rates[to_currency]
        
    except Exception as e:
        _logger.error(f"Currency rate fetch failed: {str(e)}")
        # Fallback rates for common currencies
        fallback_rates = {
            ('USD', 'EUR'): 0.85,
            ('EUR', 'USD'): 1.18,
            ('USD', 'GBP'): 0.73,
            ('GBP', 'USD'): 1.37,
            ('USD', 'INR'): 83.0,
            ('INR', 'USD'): 0.012,
        }
        
        rate_key = (from_currency, to_currency)
        if rate_key in fallback_rates:
            return fallback_rates[rate_key]
        
        reverse_key = (to_currency, from_currency)
        if reverse_key in fallback_rates:
            return 1.0 / fallback_rates[reverse_key]
        
        return 1.0  # Default fallback


# Alternative implementation without tesseract dependency
def process_receipt_ocr_fallback(attachment_id):
    """
    Fallback OCR function that uses simple text patterns
    when pytesseract is not available
    """
    _logger.warning("Using fallback OCR processing - pytesseract not available")
    
    try:
        attachment = request.env['ir.attachment'].sudo().browse(attachment_id)
        if not attachment.exists():
            return {'amount': None, 'date': None, 'vendor': None}
        
        # If attachment has a description or name that might contain useful info
        text_to_search = f"{attachment.name or ''} {attachment.description or ''}"
        
        result = {
            'amount': _extract_amount(text_to_search),
            'date': _extract_date(text_to_search),
            'vendor': attachment.name[:30] if attachment.name else None,
        }
        
        return result
        
    except Exception as e:
        _logger.error(f"Fallback OCR processing failed: {str(e)}")
        return {'amount': None, 'date': None, 'vendor': None}
