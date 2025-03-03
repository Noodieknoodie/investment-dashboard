# backend/models/schemas.py
# All data schemas in one file (keeps it simple)

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List, Union, Literal
from datetime import datetime, date
from decimal import Decimal

class Client(BaseModel):
    """Basic client information model"""
    client_id: Optional[int] = None
    display_name: str
    full_name: Optional[str] = None
    ima_signed_date: Optional[str] = None
    onedrive_folder_path: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class Contact(BaseModel):
    """Client contact model"""
    contact_id: Optional[int] = None
    client_id: int
    contact_type: str
    contact_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    fax: Optional[str] = None
    physical_address: Optional[str] = None
    mailing_address: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class Contract(BaseModel):
    """Client contract model"""
    contract_id: Optional[int] = None
    client_id: int
    contract_number: Optional[str] = None
    provider_name: Optional[str] = None
    contract_start_date: Optional[str] = None
    fee_type: Optional[str] = None
    percent_rate: Optional[Decimal] = None
    flat_rate: Optional[Decimal] = None
    payment_schedule: Optional[str] = None
    num_people: Optional[int] = None
    notes: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class ClientWithContract(Client):
    """Client with associated contract information"""
    contracts: List[Contract] = []
    
    model_config = ConfigDict(from_attributes=True)

class Payment(BaseModel):
    """Payment model with validation"""
    payment_id: Optional[int] = None
    contract_id: int
    client_id: int
    received_date: str
    total_assets: Optional[int] = None
    expected_fee: Optional[Decimal] = None
    actual_fee: Decimal
    method: Optional[str] = None
    notes: Optional[str] = None
    split_group_id: Optional[str] = None
    
    # Period fields
    applied_start_month: Optional[int] = None
    applied_start_month_year: Optional[int] = None
    applied_end_month: Optional[int] = None
    applied_end_month_year: Optional[int] = None
    applied_start_quarter: Optional[int] = None
    applied_start_quarter_year: Optional[int] = None
    applied_end_quarter: Optional[int] = None
    applied_end_quarter_year: Optional[int] = None
    
    @field_validator('received_date')
    @classmethod
    def validate_received_date(cls, v):
        try:
            # Check if date is valid
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('received_date must be in YYYY-MM-DD format')
    
    @field_validator('actual_fee')
    @classmethod
    def validate_actual_fee(cls, v):
        if v <= 0:
            raise ValueError('actual_fee must be greater than zero')
        return v
    
    model_config = ConfigDict(from_attributes=True)

class PaymentCreate(BaseModel):
    """Model for creating a new payment"""
    contract_id: int
    client_id: int
    received_date: str
    total_assets: Optional[int] = None
    expected_fee: Optional[Decimal] = None
    actual_fee: Decimal
    method: Optional[str] = None
    notes: Optional[str] = None
    is_split_payment: bool = False
    
    # Period fields - monthly or quarterly based on contract
    start_period: int  # month or quarter number
    start_period_year: int
    end_period: Optional[int] = None  # Required only for split payments
    end_period_year: Optional[int] = None  # Required only for split payments
    
    @field_validator('received_date')
    @classmethod
    def validate_received_date(cls, v):
        try:
            # Check if date is valid and not in the future
            date_obj = datetime.strptime(v, '%Y-%m-%d').date()
            if date_obj > date.today():
                raise ValueError('received_date cannot be in the future')
            return v
        except ValueError as e:
            if 'format' in str(e):
                raise ValueError('received_date must be in YYYY-MM-DD format')
            raise
    
    @field_validator('actual_fee')
    @classmethod
    def validate_actual_fee(cls, v):
        if v <= 0:
            raise ValueError('actual_fee must be greater than zero')
        return v
    
    @field_validator('end_period', 'end_period_year')
    @classmethod
    def validate_end_period(cls, v, info):
        values = info.data
        if values.get('is_split_payment') and v is None:
            raise ValueError('end_period and end_period_year are required for split payments')
        return v
    
    model_config = ConfigDict(from_attributes=True)

class PaymentUpdate(BaseModel):
    """Model for updating an existing payment"""
    received_date: Optional[str] = None
    total_assets: Optional[int] = None
    actual_fee: Optional[Decimal] = None
    method: Optional[str] = None
    notes: Optional[str] = None
    
    # We don't allow updating period fields to avoid complex data integrity issues
    # If a period needs to change, the payment should be deleted and recreated
    
    @field_validator('received_date')
    @classmethod
    def validate_received_date(cls, v):
        if v is not None:
            try:
                # Check if date is valid and not in the future
                date_obj = datetime.strptime(v, '%Y-%m-%d').date()
                if date_obj > date.today():
                    raise ValueError('received_date cannot be in the future')
                return v
            except ValueError as e:
                if 'format' in str(e):
                    raise ValueError('received_date must be in YYYY-MM-DD format')
                raise
        return v
    
    @field_validator('actual_fee')
    @classmethod
    def validate_actual_fee(cls, v):
        if v is not None and v <= 0:
            raise ValueError('actual_fee must be greater than zero')
        return v
    
    model_config = ConfigDict(from_attributes=True)

class ClientMetrics(BaseModel):
    """Client metrics model for dashboard display"""
    client_id: int
    last_payment_date: Optional[str] = None
    last_payment_amount: Optional[Decimal] = None
    last_payment_quarter: Optional[int] = None
    last_payment_year: Optional[int] = None
    total_ytd_payments: Optional[Decimal] = None
    avg_quarterly_payment: Optional[Decimal] = None
    last_recorded_assets: Optional[Decimal] = None
    
    model_config = ConfigDict(from_attributes=True)

class PaymentWithDetails(Payment):
    """Payment with additional details for display"""
    client_name: str  # client.display_name
    provider_name: Optional[str] = None  # contract.provider_name
    fee_type: Optional[str] = None  # contract.fee_type
    percent_rate: Optional[Decimal] = None  # contract.percent_rate
    flat_rate: Optional[Decimal] = None  # contract.flat_rate
    payment_schedule: Optional[str] = None  # contract.payment_schedule
    files: List[dict] = []  # Associated files
    
    model_config = ConfigDict(from_attributes=True)

class ClientFile(BaseModel):
    """Client file model"""
    file_id: Optional[int] = None
    client_id: int
    file_name: str
    onedrive_path: str
    uploaded_at: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class PaymentFile(BaseModel):
    """Payment-file association model"""
    payment_id: int
    file_id: int
    linked_at: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class FileUpload(BaseModel):
    """File upload response model"""
    file_id: int
    client_id: int
    file_name: str
    onedrive_path: str
    
    model_config = ConfigDict(from_attributes=True)

class ExpectedFeeRequest(BaseModel):
    """Request model for calculating expected fee"""
    client_id: int
    contract_id: int
    total_assets: Optional[int] = None
    period_type: Literal["month", "quarter"]
    period: int  # Month or quarter number
    year: int
    
    model_config = ConfigDict(from_attributes=True)

class ExpectedFeeResponse(BaseModel):
    """Response model for expected fee calculation"""
    expected_fee: Optional[Decimal] = None
    fee_type: Optional[str] = None
    calculation_method: str  # How the fee was calculated
    
    model_config = ConfigDict(from_attributes=True)

class ClientSnapshot(BaseModel):
    """Comprehensive client snapshot for dashboard display"""
    client: Client
    contracts: List[Contract] = []
    metrics: Optional[ClientMetrics] = None
    
    model_config = ConfigDict(from_attributes=True)

class PaginatedResponse(BaseModel):
    """Generic paginated response model"""
    total: int
    page: int
    page_size: int
    items: List[dict]
    
    model_config = ConfigDict(from_attributes=True)