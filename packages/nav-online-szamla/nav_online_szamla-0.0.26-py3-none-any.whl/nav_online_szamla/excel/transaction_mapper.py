"""
Field mapping logic for converting QueryTransactionStatusResponse to Excel row structures.

This module provides mapping functionality between transaction status responses
and flat Excel row representations.
"""

import logging
import base64
import gzip
from datetime import datetime
from typing import List, Tuple, Optional, Any
from xml.etree import ElementTree as ET

from ..models import QueryTransactionStatusResponse, InvoiceData, ManageInvoiceOperationType
from ..excel.mapper import ExcelFieldMapper
from .models import InvoiceHeaderRow, InvoiceLineRow, TransactionStatusRow
from xsdata.formats.dataclass.context import XmlContext
from xsdata.formats.dataclass.parsers import XmlParser

logger = logging.getLogger(__name__)


class TransactionFieldMapper:
    """
    Handles mapping between QueryTransactionStatusResponse objects and Excel row structures.
    """
    
    def __init__(self):
        """Initialize the transaction field mapper."""
        self.invoice_mapper = ExcelFieldMapper()
    
    def transaction_response_to_rows(
        self, 
        transaction_response: QueryTransactionStatusResponse,
        transaction_id: str = None
    ) -> Tuple[List[InvoiceHeaderRow], List[InvoiceLineRow], List[TransactionStatusRow]]:
        """
        Convert transaction status response to Excel row data.
        
        Args:
            transaction_response: The transaction status response
            transaction_id: The original transaction ID from the transaction list
            
        Returns:
            Tuple of (header_rows, line_rows, status_rows)
        """
        header_rows = []
        line_rows = []
        status_rows = []
        
        try:
            # Use provided transaction_id parameter, fall back to response if not provided
            if transaction_id is None:
                transaction_id = getattr(transaction_response, 'transaction_id', None)
            
            # Extract processing results if available
            processing_results = getattr(transaction_response, 'processing_results', None)
            if not processing_results:
                # Create a basic status row even if no processing results
                status_row = self._create_basic_status_row(transaction_response, transaction_id)
                status_rows.append(status_row)
                return header_rows, line_rows, status_rows
            
            # Check if processing_results is iterable
            if not hasattr(processing_results, '__iter__'):
                # If it's not a list, try to access as a single object or convert to list
                if hasattr(processing_results, 'processing_result'):
                    # Handle case where it's a container with processing_result items
                    results_list = processing_results.processing_result
                    if not hasattr(results_list, '__iter__'):
                        results_list = [results_list]
                else:
                    # Treat as single result
                    results_list = [processing_results]
            else:
                results_list = processing_results
            
            # Process each result in the processing results
            for result in results_list:
                try:
                    # Extract invoice data from original request if available
                    invoice_data = self._extract_invoice_data_from_original_request(result)
                    if invoice_data:
                        # Check if this is a full InvoiceData object or just an AnnulmentData
                        if hasattr(invoice_data, 'invoice_issue_date'):
                            # This is a full InvoiceData object - process header and lines
                            operation_type = self._extract_operation_type(result)
                            
                            header_row = self.invoice_mapper.invoice_data_to_header_row(invoice_data, operation_type)
                            header_rows.append(header_row)
                            
                            line_row_list = self.invoice_mapper.invoice_data_to_line_rows(invoice_data, operation_type)
                            line_rows.extend(line_row_list)
                        # For AnnulmentData objects, we skip header/line processing since annulments 
                        # only reference the original invoice - they don't contain invoice structure
                    
                    # Create status row for this result
                    status_row = self._create_status_row(transaction_response, result, transaction_id)
                    status_rows.append(status_row)
                    
                except Exception as e:
                    logger.warning(f"Failed to process individual result in transaction {transaction_id}: {e}")
                    # Create error status row
                    error_status_row = self._create_error_status_row(transaction_response, str(e))
                    status_rows.append(error_status_row)
                    continue
            
            return header_rows, line_rows, status_rows
            
        except Exception as e:
            logger.error(f"Failed to convert transaction response {transaction_id}: {e}")
            # Create error status row
            error_status_row = self._create_error_status_row(transaction_response, str(e))
            status_rows.append(error_status_row)
            return header_rows, line_rows, status_rows
    
    def _extract_operation_type(self, result) -> ManageInvoiceOperationType:
        """
        Extract operation type from processing result.
        
        Args:
            result: Processing result object
            
        Returns:
            ManageInvoiceOperationType: The operation type
        """
        try:
            # Try to get operation type from result
            operation = getattr(result, 'invoice_operation', None)
            if operation:
                operation_type = getattr(operation, 'operation_type', None)
                if operation_type:
                    return operation_type
            
            # Default to CREATE if not found
            return ManageInvoiceOperationType.CREATE
            
        except Exception:
            return ManageInvoiceOperationType.CREATE
    
    def _extract_invoice_data_from_original_request(self, result) -> Optional[Any]:
        """
        Extract InvoiceData or InvoiceAnnulment from the originalRequest field of a processing result.
        
        Args:
            result: Processing result object that may contain originalRequest
            
        Returns:
            Optional[Any]: Extracted invoice data/annulment data or None
        """
        try:
            # Get the original request
            original_request = getattr(result, 'original_request', None)
            if not original_request:
                return None

            # Check if content is compressed
            compressed = getattr(result, 'compressed_content_indicator', False)
            
            # Debug: Log what we have
            logger.debug(f"Original request type: {type(original_request)}")
            logger.debug(f"Compressed: {compressed}")
            
            # The original_request is BASE64 encoded XML data that needs to be decoded
            if isinstance(original_request, str):
                # BASE64 decode first
                try:
                    xml_data = base64.b64decode(original_request)
                except Exception as e:
                    logger.warning(f"Failed to BASE64 decode original request: {e}")
                    return None
            elif isinstance(original_request, bytes):
                # Check if it's already decoded or still BASE64
                try:
                    # Try to parse as XML first
                    ET.fromstring(original_request)
                    xml_data = original_request
                except ET.ParseError:
                    # If parsing failed, it might be BASE64 encoded
                    try:
                        xml_data = base64.b64decode(original_request)
                    except Exception as e:
                        logger.warning(f"Failed to BASE64 decode bytes original request: {e}")
                        return None
            else:
                xml_data = str(original_request).encode('utf-8')
            
            # Decompress if needed
            if compressed:
                xml_data = gzip.decompress(xml_data)
            
            # Parse XML to find InvoiceData or InvoiceAnnulment element
            root = ET.fromstring(xml_data)
            
            # Look for InvoiceData elements first (regular transactions)
            if root.tag.endswith('InvoiceData'):
                invoice_data_element = root
            else:
                # If not direct InvoiceData, search for it
                invoice_data_element = None
                for elem in root.iter():
                    if elem.tag.endswith('InvoiceData'):
                        invoice_data_element = elem
                        break
            
            if invoice_data_element is not None:
                # Convert XML element back to InvoiceData object using xsdata
                context = XmlContext()
                parser = XmlParser(context=context)
                
                # Convert the XML element to string and parse it as InvoiceData
                invoice_xml = ET.tostring(invoice_data_element, encoding='unicode')
                invoice_data = parser.from_string(invoice_xml, InvoiceData)
                
                return invoice_data
            
            # Look for InvoiceAnnulment elements (technical annulment transactions)
            annulment_element = None
            if root.tag.endswith('InvoiceAnnulment'):
                annulment_element = root
            else:
                # If not direct InvoiceAnnulment, search for it
                for elem in root.iter():
                    if elem.tag.endswith('InvoiceAnnulment'):
                        annulment_element = elem
                        break
            
            if annulment_element is not None:
                # For technical annulments, extract the annulmentReference as invoice number
                annulment_ref = None
                for elem in annulment_element.iter():
                    if elem.tag.endswith('annulmentReference'):
                        annulment_ref = elem.text
                        break
                
                if annulment_ref:
                    # Create a minimal object with invoice_number attribute to match InvoiceData interface
                    class AnnulmentData:
                        def __init__(self, invoice_number: str):
                            self.invoice_number = invoice_number
                    
                    return AnnulmentData(annulment_ref)
            
            logger.warning("No InvoiceData or InvoiceAnnulment element found in original request")
            return None
            
        except Exception as e:
            logger.error(f"Failed to extract invoice data from original request: {e}")
            return None
    
    def _create_basic_status_row(self, transaction_response: QueryTransactionStatusResponse) -> TransactionStatusRow:
        """
        Create a basic status row when no processing results are available.
        
        Args:
            transaction_response: The transaction status response
            
        Returns:
            TransactionStatusRow: Basic status row
        """
        return TransactionStatusRow(
            transaction_id=getattr(transaction_response, 'transaction_id', None),
            request_id=getattr(transaction_response, 'request_id', None),
            timestamp=self._format_timestamp(getattr(transaction_response, 'timestamp', None)),
            transaction_status="UNKNOWN",
            error_message="No processing results available"
        )
    
    def _create_status_row(
        self, 
        transaction_response: QueryTransactionStatusResponse, 
        result,
        transaction_id: str = None
    ) -> TransactionStatusRow:
        """
        Create a status row from transaction response and processing result.
        
        Args:
            transaction_response: The transaction status response
            result: Individual processing result
            
        Returns:
            TransactionStatusRow: Status row with detailed information
        """
        try:
            # Get basic identifiers from response header and parameters
            transaction_id = transaction_id or "n/a"  # Use provided transaction_id
            request_id = getattr(transaction_response.header, 'request_id', "n/a") if hasattr(transaction_response, 'header') else "n/a"
            timestamp = self._format_timestamp(getattr(transaction_response.header, 'timestamp', None)) if hasattr(transaction_response, 'header') else "n/a"
            
            # Extract invoice number from original request if available
            invoice_number = "n/a"
            if hasattr(result, 'original_request') and result.original_request:
                invoice_data = self._extract_invoice_data_from_original_request(result)
                if invoice_data and hasattr(invoice_data, 'invoice_number'):
                    invoice_number = invoice_data.invoice_number
            
            # Get operation information - determine from context
            invoice_operation = "CREATE"  # Most transactions are invoice creation operations
            
            # Get invoice status from processing result
            invoice_status = "n/a"
            if hasattr(result, 'invoice_status') and result.invoice_status:
                invoice_status = str(result.invoice_status.value) if hasattr(result.invoice_status, 'value') else str(result.invoice_status)
            
            # Extract validation messages
            business_validation_messages = self._extract_validation_messages(result, 'business_validation_messages')
            technical_validation_messages = self._extract_validation_messages(result, 'technical_validation_messages')
            
            # Extract error information from business validation messages
            error_code = "n/a"
            error_message = "n/a"
            
            # Check business validation messages for errors
            if hasattr(result, 'business_validation_messages') and result.business_validation_messages:
                for validation_msg in result.business_validation_messages:
                    if hasattr(validation_msg, 'validation_error_code'):
                        error_code = validation_msg.validation_error_code
                    if hasattr(validation_msg, 'message'):
                        error_message = validation_msg.message
                    break  # Take the first error
            
            # Warning and info messages not available in this structure
            warning_messages = "n/a"
            info_messages = "n/a"
            
            # Get completion date - not available in processing result
            completion_date = "n/a"
            
            # Get transaction status from main response result
            transaction_status = "n/a"
            if hasattr(transaction_response, 'result') and hasattr(transaction_response.result, 'func_code'):
                transaction_status = str(transaction_response.result.func_code.value) if hasattr(transaction_response.result.func_code, 'value') else str(transaction_response.result.func_code)
            
            # Get batch index and result index from result
            batch_index = getattr(result, 'batch_index', "n/a")
            result_index = getattr(result, 'index', "n/a")
            
            return TransactionStatusRow(
                transaction_id=transaction_id,
                request_id=request_id,
                timestamp=timestamp,
                invoice_number=invoice_number,
                invoice_operation=invoice_operation,
                invoice_status=invoice_status,
                transaction_status=transaction_status,
                completion_date=completion_date,
                business_validation_messages=business_validation_messages,
                technical_validation_messages=technical_validation_messages,
                error_code=error_code,
                error_message=error_message,
                warning_messages=warning_messages,
                info_messages=info_messages,
                batch_index=batch_index,
                original_request_version=getattr(result, 'original_request_version', "n/a") if hasattr(result, 'original_request_version') else "n/a"
            )
            
        except Exception as e:
            logger.error(f"Failed to create status row: {e}")
            return self._create_error_status_row(transaction_response, str(e))
    
    def _create_error_status_row(
        self, 
        transaction_response: QueryTransactionStatusResponse, 
        error_message: str
    ) -> TransactionStatusRow:
        """
        Create an error status row when processing fails.
        
        Args:
            transaction_response: The transaction status response
            error_message: Error message to include
            
        Returns:
            TransactionStatusRow: Error status row
        """
        return TransactionStatusRow(
            transaction_id=getattr(transaction_response, 'transaction_id', None),
            request_id=getattr(transaction_response, 'request_id', None),
            timestamp=self._format_timestamp(getattr(transaction_response, 'timestamp', None)),
            transaction_status="ERROR",
            error_message=error_message
        )
    
    def _extract_validation_messages(self, result, field_name: str) -> Optional[str]:
        """
        Extract and concatenate validation messages from a result field.
        
        Args:
            result: Processing result object
            field_name: Name of the field containing messages
            
        Returns:
            Optional[str]: Concatenated messages or None
        """
        try:
            messages = getattr(result, field_name, None)
            if not messages:
                return None
            
            if isinstance(messages, list):
                # Concatenate list of messages
                message_strings = []
                for msg in messages:
                    if hasattr(msg, 'message'):
                        message_strings.append(str(msg.message))
                    elif hasattr(msg, 'text'):
                        message_strings.append(str(msg.text))
                    else:
                        message_strings.append(str(msg))
                return " | ".join(message_strings) if message_strings else None
            else:
                # Single message
                if hasattr(messages, 'message'):
                    return str(messages.message)
                elif hasattr(messages, 'text'):
                    return str(messages.text)
                else:
                    return str(messages)
                    
        except Exception as e:
            logger.warning(f"Failed to extract {field_name}: {e}")
            return None
    
    def _format_timestamp(self, timestamp) -> Optional[str]:
        """
        Format timestamp for Excel display.
        
        Args:
            timestamp: Timestamp object or string
            
        Returns:
            Optional[str]: Formatted timestamp string
        """
        try:
            if not timestamp:
                return None
            
            if isinstance(timestamp, str):
                return timestamp
            
            if hasattr(timestamp, 'isoformat'):
                return timestamp.isoformat()
            
            return str(timestamp)
            
        except Exception:
            return str(timestamp) if timestamp else None