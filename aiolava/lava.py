# https://github.com/1ort/aiolava
import asyncio
import aiohttp
from typing import Dict, List, Optional
import platform
from pydantic import validate_arguments, HttpUrl


if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class LavaError(Exception):
    pass


class Lava:
    path_prefix = "https://api.lava.ru"

    def __init__(self, api_key: str) -> None:
        """__init__

        Args:
            api_key (str): Lava JWT-Token
        """
        self.api_key = api_key

    async def test_ping(self) -> Dict:
        """Проверка JWT-токена на авторизацию

        Returns:
            Dict: {
                    "status": true
                }
        """
        method = "GET"
        path = "/test/ping"
        return await self._request(method, path)

    async def wallet_list(self) -> Dict | list:
        """Список кошельков с их балансами

        Returns:
            Dict|list: [
                        {
                            "account": "U10000002",
                            "currency": "USD",
                            "balance": "10.26"
                        },
                        {
                            "account": "E10000003",
                            "currency": "EUR",
                            "balance": "1.09"
                        },
                        {
                            "account": "R10000001",
                            "currency": "RUB",
                            "balance": "1500.00"
                        }
                    ]
        """
        method = "GET"
        path = "/wallet/list"
        return await self._request(method, path)

    @validate_arguments
    async def withdraw_create(
        self,
        account: str,
        amount: float,
        service: str,
        wallet_to: str,
        order_id: Optional[str] = None,
        hook_url: Optional[HttpUrl] = None,
        substract: Optional[int] = None,
        comment: Optional[str] = None,
    ) -> Dict:
        """Создание заявки на вывод

        Args:
            account (str): Номер кошелька, с которого совершается вывод
            amount (float): Сумма вывода
            service (str): Сервис вывода
            wallet_to (str): Номер счета получателя
            order_id (Optional[str], optional): Номер счета в вашей системе. Должен быть уникальным
            hook_url (Optional[HttpUrl], optional): Url для отправки webhook (Max: 500). Defaults to None.
            substract (Optional[int], optional): Откуда списывать комиссию. 1 - с баланса, 0 - с суммы. Если параметр не передан, то комиссия берется с суммы. Defaults to None.
            comment (Optional[str], optional): Комментарий к выводу. Defaults to None.

        Returns:
            Dict: {
                    "id": "3e22b0c8-2c4a-93d8-2f6d-b93ce824ee62", // Номер заявки
                    "status": "success", // Статус создания заявки
                    "amount": "1000.01", // Сумма заявки
                    "commission": 50 // Комиссия
                }

        """
        method = "POST"
        path = "/withdraw/create"
        data = {
            "account": account,
            "amount": amount,
            "service": service,
            "wallet_to": wallet_to,
            "order_id": order_id,
            "hook_url": hook_url,
            "substract": substract,
            "comment": comment,
        }
        return await self._request(method, path, data)

    @validate_arguments
    async def withdraw_info(self, id: str) -> Dict:
        """Получение информации о выводе

        Args:
            id (str): Номер заявки

        Returns:
            Dict: {
                "id": "3e22b0c8-2c4a-93d8-2f6d-b93ce824ee62", // Номер заявки
                "created_at": "1634899536", // Время создания (В формате unix timestamp)
                "amount": "1000.01", // Сумма заявки
                "commission": "50.00", // Комиссия
                "status": "pending", // Статус заявки
                "service": "card", // Сервис
                "comment": null, // Комментарий, который вы указали при создании заявки
                "currency": "RUB" // Валюта
            }
        """
        method = "POST"
        path = "/withdraw/info"
        data = {"id": id}
        return await self._request(method, path, data)

    @validate_arguments
    async def transfer_create(
        self,
        account_from: str,
        account_to: str,
        amount: float,
        subtract: Optional[int] = None,
        comment: str = None,
    ) -> Dict:
        """Создание заявки на перевод средств

        Args:
            account_from (str): Номер кошелька, с которого совершается перевод
            account_to (str): Номер кошелька, куда совершается перевод
            amount (float): Сумма вывода
            subtract (Optional[int], optional): Откуда списывать комиссию. 1 - с баланса, 0 - с суммы. Если параметр не передан, то комиссия берется с суммы. Defaults to None.
            comment (str, optional): Комментарий к выводу. Defaults to None.

        Returns:
            Dict: {
                "id": "3e22b0c8-2c4a-93d8-2f6d-b93ce824ee62", // Номер заявки
                "status": "success", // Статус создания заявки
                "amount": "1000.01", // Сумма заявки
                "commission": 50 // Комиссия
            }
        """
        method = "POST"
        path = "/transfer/create"
        data = {
            "account_from": account_from,
            "account_to": account_to,
            "amount": amount,
            "subtract": subtract,
            "comment": comment,
        }
        return await self._request(method, path, data)

    @validate_arguments
    async def transfer_info(self, id: str) -> Dict:
        """Получение информации о переводе

        Args:
            id (str): Номер заявки

        Returns:
            Dict: {
                "id": "c3d3702b-aceb-afd1-fbb1-d073541ca3e9", // Номер заявки
                "created_at": "1634901715", // Время создания (В формате unix timestamp)
                "amount": "1.01", // Сумма заявки
                "status": "success", // Статус заявки
                "comment": null, // Комментарий, который вы указали при создании заявки
                "currency": "RUB", // Валюта
                "type": "out", // Тип
                "receiver": "R10000004", // Кошелек получателя
                "commission": "0.01" // Комиссия
            }
        """
        method = "POST"
        path = "/transfer/info"
        data = {"id": id}
        return await self._request(method, path, data)

    @validate_arguments
    async def transactions_list(
        self,
        transfer_type: Optional[str] = None,
        account: Optional[str] = None,
        period_start: Optional[str] = None,
        period_end: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List:
        """Получение списка всех транзакций

        Args:
            transfer_type (Optional[str], optional): Тип перевода. withdraw - вывод, transfer - перевод. Defaults to None.
            account (Optional[str], optional): Номер кошелька. Defaults to None.
            period_start (Optional[str], optional): С какого времени показывать транзакции. Defaults to None.
            period_end (Optional[str], optional): До какого времени показывать транзакции. Defaults to None.
            offset (Optional[int], optional): Сдвиг. Defaults to None.
            limit (Optional[int], optional): Лимит (max 50). Defaults to None.

        Returns:
            List: [
                    {
                        "id": "bc81edeb-3f81-156d-21bd-06c67010094f", // Номер транзакции
                        "created_at": "1634902579",  // Время создания (unix timestamp)
                        "created_date": "2021-10-22T11:36:19+00:00", // Время создания
                        "amount": "1230.00", // Сумма транзакции
                        "status": "success", // Статус транзакции
                        "transfer_type": "transfer", // Тип перевода
                        "comment": "Hello", // Комментарий
                        "method": "-1", // Метод 1 - зачисление, -1 - расход
                        "currency": "RUB", // Валюта
                        "account": "R10000001", // Номер аккаунта
                        "commission": "12.30", // Комиссия
                        "type": "out", // Тип in - пополнение, out - перевод
                        "receiver": "R10000000" // Номер аккаунта получателя
                    }
                ]
        """
        method = "POST"
        path = "/transactions/list"
        data = {
            "transfer_type": transfer_type,
            "account": account,
            "period_start": period_start,
            "period_end": period_end,
            "offset": offset,
            "limit": limit,
        }
        return await self._request(method, path, data)

    @validate_arguments
    async def invoice_create(
        self,
        wallet_to: str,
        sum: float,
        order_id: Optional[str] = None,
        hook_url: Optional[HttpUrl] = None,
        success_url: Optional[HttpUrl] = None,
        fail_url: Optional[HttpUrl] = None,
        exprire: Optional[int] = None,
        substract: Optional[int] = None,
        custom_fields: Optional[str] = None,
        comment: Optional[str] = None,
        merchant_id: Optional[str] = None,
        merchant_name: Optional[str] = None,
    ) -> Dict:
        """Выставление счета на оплату

        Args:
            wallet_to (str): Ваш номер счета, на который будут зачислены средства
            sum (float): Сумма, с указанием двух знаков после точки
            order_id (Optional[str], optional): Номер счета в вашей системе. Должен быть уникальным. Defaults to None.
            hook_url (Optional[HttpUrl], optional): Url для отправки webhook. (Max: 500). Defaults to None.
            success_url (Optional[HttpUrl], optional): Url для переадресации после успешной оплаты. (Max: 500). Defaults to None.
            fail_url (Optional[HttpUrl], optional): Url для переадресации после неудачной оплаты. (Max: 500). Defaults to None.
            exprire (Optional[int], optional): Время жизни счета в минутах. По умолчанию: 1440. Минимум: 1. Максимум: 43200. Defaults to None.
            substract (Optional[int], optional): С кого списывать комиссию. 1 - Списывать с клиента. 0 - Списывать с магазина. По умолчанию: 0. Defaults to None.
            custom_fields (Optional[str], optional): Дополнительное поле, которое возвращается в WebHook. Defaults to None.
            comment (Optional[str], optional): Комментарий к оплате. Defaults to None.
            merchant_id (Optional[str], optional): ID мерчанта (используется только в WebHook). Defaults to None.
            merchant_name (Optional[str], optional): Название мерчанта (отображается в форме перевода). Defaults to None.

        Returns:
            Dict: {
                // Статус запроса
                "status": "success",
                // Номер счета на оплату
                "id": "1ee31634-e3e0-34ce-1423-b5b4cb524c6a",
                // Ссылка на оплату
                "url": "https://p2p.lava.ru/form?id=1ee31634-e3e0-34ce-1423-b5b4cb524c6a",
                // Время истечения счета
                "expire": 1636983503,
                // Сумма счета
                "sum": "100.00",
                // URL для переадресации после успешной оплаты
                "success_url": "https://lava.ru?success",
                // URL для переадресации после неудачной оплаты
                "fail_url": "https://lava.ru?fail",
                // URL для отправки webhook
                "hook_url": "https://lava.ru?hook",
                // Дополнительное поле
                "custom_fields": "123",
                // ID и наименование мерчанта
                "merchant_name": "123",
                "merchant_id": "123",
            }
        """
        method = "POST"
        path = "/invoice/create"
        data = {
            "wallet_to": wallet_to,
            "sum": sum,
            "order_id": order_id,
            "hook_url": hook_url,
            "success_url": success_url,
            "fail_url": fail_url,
            "exprire": exprire,
            "substract": substract,
            "custom_fields": custom_fields,
            "comment": comment,
            "merchant_id": merchant_id,
            "merchant_name": merchant_name,
        }
        return await self._request(method, path, data)

    @validate_arguments
    async def invoice_info(
        self,
        id: Optional[str] = None,
        order_id: Optional[str] = None,
    ) -> Dict:
        """Получение информации о выставленном счете

        Args:
            id (Optional[str], optional): Номер счета в нашей системе. Обязателен если не передан 'order_id'. Defaults to None.
            order_id (Optional[str], optional): Номер счета в системе клиента. Обязателен если не передан 'id'. Defaults to None.

        Returns:
            Dict: {
                // Статус запроса
                "status": "success",
                "invoice": {
                    // Номер счета на оплату
                    "id": "1ee31634-e3e0-34ce-1423-b5b4cb524c6a",
                    // Номер счета в системе клиента
                    "order_id": "order_125",
                    // Время истечение счета
                    "expire": 1636983503,
                    // Сумма счета
                    "sum": "100.00",
                    // Ко��ментарий
                    "comment": "На бигтести с колой",
                    // Статус счета
                    "status": "success",
                    // URL для переадресации после успешной оплаты
                    "success_url": "https://lava.ru?success",
                    // URL для переадресации после неудачной оплаты
                    "fail_url": "https://lava.ru?fail",
                    // URL для отправки webhook
                    "hook_url": "https://lava.ru?hook",
                    // Дополнительное поле
                    "custom_fields": "123"
                }
            }
        """
        method = "POST"
        path = "/invoice/info"
        data = {"id": id, "order_id": order_id}
        return await self._request(method, path, data)

    @validate_arguments
    async def invoice_set_webhook(self, url: HttpUrl) -> Dict:
        """Установка URL для отправки HTTP-уведомлений

        Args:
            url (HttpUrl): URL, на который будут приходить HTTP-уведомления

        Returns:
            Dict: {
                "status": "success"
            }
        """
        method = "POST"
        path = "/invoice/set-webhook"
        data = {"url": url}
        return await self._request(method, path, data)

    async def invoice_generate_secret_key(self) -> Dict:
        """Генерация секретных ключей
            Ключ secret_key требуется для генерации сигнатуры в устаревшем способе выставление счета.
            Ключ secret_key_2 используется для генерации сигнатуры в WebHook.

        Returns:
            Dict: {
                "status": "success",
                "secret_key": "2wUgAjoyUhnvhVdn0AWSjLZyNYDUbYtA",
                "secret_key_2": "2wUgAjoyUhnvhVdn0AWSjLZyNYDUbYtA"
            }
        """
        method = "GET"
        path = "/invoice/generate-secret-key"
        return await self._request(method, path)

    async def _request(self, method, path, data={}) -> Dict:
        url = self.path_prefix + path
        headers = {
            "Authorization": self.api_key,
        }
        for key in list(data):
            if data[key] is None:
                data.pop(key)
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method, url, headers=headers, data=data
            ) as responce:
                result = await responce.json()
                if result is Dict and result.get("status") == "error":
                    raise LavaError(f'{result["code"]}: {result["messge"]}')
                else:
                    return result
