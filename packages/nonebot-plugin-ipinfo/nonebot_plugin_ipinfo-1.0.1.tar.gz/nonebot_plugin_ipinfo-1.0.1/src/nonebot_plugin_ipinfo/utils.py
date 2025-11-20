import asyncio
import ipaddress

import ipinfo
import ip2locationio
from ipinfo.details import Details

from nonebot.log import logger
from nonebot import get_plugin_config

from .config import Config


plugin_config = get_plugin_config(Config)
access_token = plugin_config.ipinfo_access_token
use_ip2location = plugin_config.ipinfo_use_ip2location
ip2location_api_key = plugin_config.ipinfo_ip2location_api_key


def pick(obj, path: str, default="N/A") -> str:
    cur = obj
    try:
        for key in path.split("."):
            if isinstance(cur, dict):
                cur = cur.get(key, default)
            elif isinstance(cur, list) and key.isdigit():
                idx = int(key)
                if idx < 0 or idx >= len(cur):
                    return default
                cur = cur[idx]
            else:
                cur = getattr(cur, key, default)
            if cur == default:
                return default
        return cur
    except Exception:
        return default


async def validate_ip(ip: str) -> bool:
    if not isinstance(ip, str):
        return False
    try:
        ipaddress.ip_address(ip)
        return True
    except ipaddress.AddressValueError:
        return False
    except ValueError:
        return False


async def get_ip_info_by_ipinfo(ip: str) -> Details | None:
    try:
        handler =  ipinfo.getHandlerLite(access_token)
        response =  await asyncio.to_thread(handler.getDetails, ip)
    except Exception as e:
        logger.error(f"使用 ipinfo 查询 IP 信息时发生错误: {e}")
        return None
    return response


async def get_ip_info_by_ip2location(ip: str) -> dict | None:
    try:
        configureation = ip2locationio.Configuration(ip2location_api_key)
        ipgeolocation = ip2locationio.IPGeolocation(configureation)
        response = await asyncio.to_thread(ipgeolocation.lookup, ip)
    except Exception as e:
        logger.error(f"使用 ip2location 查询 IP 信息时发生错误: {e}")
        return
    return response


async def get_domain_information(domain: str) -> dict | None:
    try:
        configuration = ip2locationio.Configuration(ip2location_api_key)
        domainwhois = ip2locationio.DomainWHOIS(configuration)
        response =  await asyncio.to_thread(domainwhois.lookup, domain)
    except Exception as e:
        logger.error(f"使用 ip2location 查询域名信息时发生错误: {e}")
        return
    return response


async def get_hosted_domains(ip: str) -> dict | None:
    try:
        configuration = ip2locationio.Configuration(ip2location_api_key)
        hosteddomains = ip2locationio.HostedDomain(configuration)
        response = await asyncio.to_thread(hosteddomains.lookup, ip)
    except Exception as e:
        logger.error(f"使用 ip2location 查询托管域名时发生错误: {e}")
        return
    return response
