import datetime
import aiohttp
import asyncio
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from functools import wraps
from enum import Enum



"""  ======== models.py ======== """

class RentalState(str, Enum):
    VERIFICATION_PENDING = "verificationPending"
    VERIFICATION_COMPLETED = "verificationCompleted"
    VERIFICATION_CANCELED = "verificationCanceled"
    VERIFICATION_TIMED_OUT = "verificationTimedOut"
    VERIFICATION_REPORTED = "verificationReported"
    VERIFICATION_REFUNDED = "verificationRefunded"
    VERIFICATION_REUSED = "verificationReused"
    VERIFICATION_REACTIVATED = "verificationReactivated"
    RENEWABLE_ACTIVE = "renewableActive"
    RENEWABLE_OVERDUE = "renewableOverdue"
    RENEWABLE_EXPIRED = "renewableExpired"
    RENEWABLE_REFUNDED = "renewableRefunded"
    NONRENEWABLE_ACTIVE = "nonrenewableActive"
    NONRENEWABLE_EXPIRED = "nonrenewableExpired"
    NONRENEWABLE_REFUNDED = "nonrenewableRefunded"

class LinkModel(BaseModel):
    method: Optional[str] = None
    href: Optional[str] = None


class RefundModel(BaseModel):
    canRefund: bool
    link: LinkModel
    refundableUntil: Optional[str] = None

# Модель для элемента в списке аренд (get_rentals)
class RentalListItem(BaseModel):
    createdAt: str
    id: str
    sale: LinkModel
    saleId: Optional[str] = None
    serviceName: str
    link: LinkModel
    state: RentalState
    billingCycle: Optional[LinkModel] = None
    billingCycleId: Optional[str] = None
    isIncludedForNextRenewal: Optional[bool] = None
    number: str
    alwaysOn: Optional[bool] = None


# Модель для детальной информации об аренде (get_rental_by_id)
class RentalDetail(BaseModel):
    createdAt: str
    id: str
    refund: RefundModel
    sale: LinkModel
    saleId: Optional[str] = None
    serviceName: str
    sms: LinkModel
    calls: LinkModel
    state: RentalState
    billingCycle: LinkModel
    billingCycleId: str
    isIncludedForNextRenewal: bool
    number: str
    alwaysOn: bool

class LinksCursor(BaseModel):
    current: LinkModel
    next: Optional[LinkModel] = None

class RentalsListResponse(BaseModel):
    data: List[RentalListItem]
    hasNext: bool
    links: LinksCursor

class NonRentalDetail(BaseModel):
    calls: LinkModel
    createdAt: str
    endsAt: str
    id: str
    refund: RefundModel
    sale: LinkModel
    saleId: Optional[str] = None
    serviceName: str
    sms: LinkModel
    state: RentalState
    number: str
    alwaysOn: bool

class NonRentalListItem(BaseModel):
    createdAt: str
    id: str
    link: LinkModel
    sale: LinkModel
    saleId: Optional[str] = None
    serviceName: str
    state: RentalState
    number: str
    alwaysOn: bool

class NonRentalListResponse(BaseModel):
    data: List[NonRentalListItem]
    hasNext: bool
    links: LinksCursor

class SmsListItem(BaseModel):
    id: str
    _from: str = None
    to: str
    createdAt: str
    smsContent: str = None
    parsedCode: str = None
    encrypted: bool

class SmsListResponse(BaseModel):
    data: List[SmsListItem]

class WakeRequestResponse(BaseModel):
    id: str
    usageWindowStart: str = None
    usageWindowEnd: str = None
    isScheduled: bool
    reservationId: str = None

class AccountInfo(BaseModel):
    username: str
    currentBalance: float

# ========== API ==========

class TextVerifiedApi:
    """
    Unofficial API client for working with the Textverified REST API
    
    """
    def __init__(self, api_key, username):
        self.api_key = api_key
        self.api_username = username
        self.token_data = None
        self.token_expires = None
        self.base_url = "https://www.textverified.com/api/pub/v2"

    @staticmethod
    def bearer_auth(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            if (self.token_data is None or 
                datetime.datetime.now(datetime.timezone.utc) > self.token_expires):
                await self.generate_bearer()
            return await func(self, *args, **kwargs)
        return wrapper

    def parse_datetime(self, datetime_str):
        """Парсит строку datetime с возможными разными форматами микросекунд"""
        try:
            return datetime.datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%f%z')
        except ValueError:
            if '.' in datetime_str and '+' in datetime_str:
                main_part, tz_part = datetime_str.split('+')
                date_part, time_part = main_part.split('T')
                hours, minutes, seconds_with_ms = time_part.split(':')
                seconds, milliseconds = seconds_with_ms.split('.')
                milliseconds = milliseconds[:6]
                normalized_str = f"{date_part}T{hours}:{minutes}:{seconds}.{milliseconds}+{tz_part}"
                return datetime.datetime.strptime(normalized_str, '%Y-%m-%dT%H:%M:%S.%f%z')
            else:
                raise

    async def generate_bearer(self):
        async with aiohttp.ClientSession() as session:
            response = await session.post(
                f"{self.base_url}/auth",
                headers={
                    "X-API-KEY": self.api_key,
                    "X-API-USERNAME": self.api_username,
                },
            )
            resp = await response.json()
            # print("Token response:", resp)
            
            self.token_data = resp
            expires_at_str = resp['expiresAt']
            self.token_expires = self.parse_datetime(expires_at_str)
            
            # print(f"Token expires at: {self.token_expires}")
            return self.token_data

    def get_auth_headers(self):
        if self.token_data:
            return {"Authorization": f"Bearer {self.token_data['token']}"}
        return {}

    @bearer_auth
    async def get_account_info(self) -> Dict[str, Any]:
        """Получает информацию об аккаунте"""
        headers = self.get_auth_headers()
        async with aiohttp.ClientSession() as session:
            response = await session.get(
                f"{self.base_url}/account/me",
                headers=headers
            )
            if response.status == 200:
                data = await response.json()
                return AccountInfo(**data)
            else:
                raise Exception(f"API request failed with status {response.status}")

    @bearer_auth
    async def get_rentals(self) -> List[RentalListItem]:
        all_rentals: List[RentalListItem] = []
        url = f"{self.base_url}/reservations/rental/renewable"
        
        while url:
            async with aiohttp.ClientSession() as session:
                response = await session.get(url, headers=self.get_auth_headers())
                if response.status != 200:
                    raise Exception(f"API request failed with status {response.status}")
                
                data = await response.json()
                rentals_page = RentalsListResponse(**data)
                all_rentals.extend(rentals_page.data)
                
                if hasattr(rentals_page, "links") and rentals_page.links.next and rentals_page.links.next.href:
                    url = rentals_page.links.next.href
                    # print(f"Next page: {url}")
                else:
                    url = None

        return all_rentals

    @bearer_auth
    async def get_rental_by_id(self, rental_id: str) -> RentalDetail:
        """Получает информацию о конкретном арендованном номере"""
        headers = self.get_auth_headers()
        async with aiohttp.ClientSession() as session:
            response = await session.get(
                f"{self.base_url}/reservations/rental/renewable/{rental_id}",
                headers=headers
            )
            if response.status == 200:
                data = await response.json()
                return RentalDetail(**data)
            else:
                raise Exception(f"API request failed with status {response.status}")
            
    @bearer_auth
    async def get_nonrentals(self) -> List[NonRentalListItem]:
        all_rentals: List[NonRentalListItem] = []
        url = f"{self.base_url}/reservations/rental/nonrenewable"
        
        while url:
            async with aiohttp.ClientSession() as session:
                response = await session.get(url, headers=self.get_auth_headers())
                if response.status != 200:
                    raise Exception(f"API request failed with status {response.status}")
                
                data = await response.json()
                rentals_page = NonRentalListResponse(**data)
                all_rentals.extend(rentals_page.data)
                
                # Проверяем, есть ли следующая страница
                if hasattr(rentals_page, "links") and rentals_page.links.next and rentals_page.links.next.href:
                    url = rentals_page.links.next.href  # берем ссылку на следующую страницу
                    print(f"Next page: {url}")
                else:
                    url = None  # больше страниц нет

        return all_rentals
            
    @bearer_auth
    async def get_nonrental_by_id(self, rental_id: str) -> NonRentalDetail:
        """Получает информацию о конкретном арендованном номере"""
        headers = self.get_auth_headers()
        async with aiohttp.ClientSession() as session:
            response = await session.get(
                f"{self.base_url}/reservations/rental/nonrenewable/{rental_id}",
                headers=headers
            )
            if response.status == 200:
                data = await response.json()
                return NonRentalDetail(**data)
            else:
                raise Exception(f"API request failed with status {response.status}")
            
    @bearer_auth
    async def get_sms(self, rental_id) -> SmsListResponse: #                     "to": number,
        headers = self.get_auth_headers()
        async with aiohttp.ClientSession() as session:
            response = await session.get(
                f"{self.base_url}/sms",
                headers=headers,
                params={
                    "rentalId": rental_id
                }
            )
            if response.status == 200:
                data = await response.json()
                return SmsListResponse(**data)
            else:
                raise Exception(f"API request failed with status {response.status}")
            
    @bearer_auth
    async def wake_request(self, rental_id: str) -> str:
        """Создает wake request и возвращает wake_id из заголовка Location"""
        headers = self.get_auth_headers()
        async with aiohttp.ClientSession() as session:
            response = await session.post(
                f"{self.base_url}/wake-requests",
                headers=headers,
                json={
                    "reservationId": rental_id
                }
            )
            
            if response.status == 201:
                # Извлекаем wake_id из заголовка Location
                location_header = response.headers.get('Location')
                if location_header:
                    # URL выглядит как: /api/pub/v2/wake-requests/{wake_id}
                    wake_id = location_header.rstrip('/').split('/')[-1]
                    print(f"Wake request created successfully. ID: {wake_id}")
                    return wake_id
                else:
                    raise Exception("Location header not found in response")
            else:
                error_text = await response.text()
                raise Exception(f"API request failed with status {response.status}: {error_text}")

    @bearer_auth
    async def get_wake_request(self, wake_id: str) -> WakeRequestResponse:
        """Получает информацию о wake request по ID"""
        headers = self.get_auth_headers()
        async with aiohttp.ClientSession() as session:
            response = await session.get(
                f"{self.base_url}/wake-requests/{wake_id}",
                headers=headers,
            )
            if response.status == 200:
                data = await response.json()
                return WakeRequestResponse(**data)
            else:
                error_text = await response.text()
                raise Exception(f"API request failed with status {response.status}: {error_text}")

    # Дополнительный удобный метод для полного процесса пробуждения
    async def wake_up_reservation(self, rental_id: str) -> WakeRequestResponse:
        """Полный процесс: создает wake request и возвращает его детали"""
        wake_id = await self.wake_request(rental_id)
        return await self.get_wake_request(wake_id)

    async def check_token_status(self):
        if self.token_data is None:
            return "No token"
        elif datetime.datetime.now(datetime.timezone.utc) > self.token_expires:
            return "Expired"
        else:
            time_left = self.token_expires - datetime.datetime.now(datetime.timezone.utc)
            return f"Valid, expires in {time_left}"


# Usage / Использование
async def main():
    api = TextVerifiedApi("api", "mail")
    
    await api.generate_bearer()
    status = await api.check_token_status()
    print(f"Token status: {status}")

    try:
        # Получаем все арендованные номера
        all_rentals = await api.get_rentals()
        print(f"Found {len(all_rentals)} rentals:")

        for rental in all_rentals:
            print(f"- {rental.serviceName}: {rental.number} ({rental.state})")
                
        # Пример получения детальной информации о конкретном номере
        if all_rentals:
            first_rental = all_rentals[0]
            print(f"\nGetting details for rental: {first_rental.id}")
            rental_details = await api.get_rental_by_id(first_rental.id)
            print(f"Detailed info for {rental_details.number}:")
            print(f"  Service: {rental_details.serviceName}")
            print(f"  State: {rental_details.state}")
            print(f"  Always on: {rental_details.alwaysOn}")
            print(f"  Can refund: {rental_details.refund.canRefund}")
            print(f"  Billing cycle ID: {rental_details.billingCycleId}")

        wake = await api.wake_up_reservation(first_rental.id)
        print(f"\nWoke up {wake.usageWindowStart} | Woke down {wake.usageWindowEnd} with wake ID {wake.id}")
                
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())