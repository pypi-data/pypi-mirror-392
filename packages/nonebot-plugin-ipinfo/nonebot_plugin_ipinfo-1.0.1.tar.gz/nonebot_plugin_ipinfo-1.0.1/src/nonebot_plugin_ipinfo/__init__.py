import json

from nonebot.rule import Rule
from nonebot.log import logger
from nonebot.exception import ActionFailed
from nonebot import require, get_plugin_config, get_bots
from nonebot.plugin import PluginMetadata, inherit_supported_adapters

require("nonebot_plugin_alconna")
from nonebot_plugin_alconna import(
    Args,
    Option,
    Alconna,
    on_alconna,
    UniMessage,
    CustomNode,
    CommandMeta,
)

from .config import Config
from .utils import (
    pick,
    validate_ip,
    get_hosted_domains,
    get_ip_info_by_ipinfo,
    get_domain_information,
    get_ip_info_by_ip2location,
)


__plugin_meta__ = PluginMetadata(
    name="iPinfo",
    description="查询 IP 地址的信息",
    usage="/ipinfo <IP 地址>",
    type="application",
    config=Config,
    homepage="https://github.com/lyqgzbl/nonebot-plugin-ipinfo",
    supported_adapters=inherit_supported_adapters("nonebot_plugin_alconna"),
    extra={
        "author": "lyqgzbl <admin@lyqgzbl.com>",
        "version": "1.0.1",
    },
)


plugin_config = get_plugin_config(Config)
access_token = plugin_config.ipinfo_access_token
use_ip2location = plugin_config.ipinfo_use_ip2location
ip2location_api_key = plugin_config.ipinfo_ip2location_api_key
verbose_use_reference = plugin_config.ipinfo_verbose_use_reference


if use_ip2location and not ip2location_api_key:
        logger.opt(colors=True).warning(
            "<yellow>启用 IP2Location 但缺失必要配置项"
            " 'ipinfo_ip2location_api_key' 已禁用该插件</yellow>"
        )
if  not use_ip2location and not access_token:
    logger.opt(colors=True).warning(
        "<yellow>缺失必要配置项 'ipinfo_access_token' 已禁用该插件</yellow>"
    )


async def send_verbose_message(info: str, title: str):
    bot = get_bots()
    onebot = next((b for b in bot.values() if b.type == "OneBot V11"), None)
    if onebot:
        if verbose_use_reference:
            try:
                node1 = CustomNode(
                    content=UniMessage.text(info),
                    uid="3556416206",
                    name=title,
                )
                await UniMessage.reference(node1).finish()
            except ActionFailed as e:
                logger.error(f"发送详细信息时发生错误: {e}")
                await UniMessage.text(info).finish(reply_to=True)
        else:
            await UniMessage.text(info).finish(reply_to=True)
    else:
        await UniMessage.text(info).finish(reply_to=True)


ipinfo_is_enable = Rule(lambda: bool(access_token))
ip2location_is_enable = Rule(lambda: bool(ip2location_api_key))
is_enable = Rule(lambda: bool(access_token or ip2location_api_key))


domain_info_command = on_alconna(
    Alconna(
        "domaininfo",
        Option("--verbose|-v", help_text="显示详细信息"),
        Args["user_input_domain#需要查询的域名", str],
        meta=CommandMeta(
            compact=True,
            description="查询域名的 WHOIS 信息",
            usage="/domaininfo <域名>",
            example="/domaininfo nonebot.dev",
        ),
    ),
    block=True,
    priority=10,
    rule=ip2location_is_enable,
    use_cmd_start=True,
)


ip_info_commnd = on_alconna(
    Alconna(
        "ipinfo",
        Option("--verbose|-v", help_text="显示详细信息"),
        Args["user_input_ip#需要查询的 IP 地址", str],
        meta=CommandMeta(
            compact=True,
            description="查询 IP 地址的地理位置信息",
            usage="/ipinfo <IP 地址>",
            example="/ipinfo",
        ),
    ),
    block=True,
    priority=10,
    aliases={"ip"},
    rule=is_enable,
    use_cmd_start=True,
)


get_domain_command = on_alconna(
    Alconna(
        "getdomain",
        Args["user_input_ip#需要查询的 IP 地址", str],
        Option("--verbose|-v", help_text="显示详细信息"),
        meta=CommandMeta(
            compact=True,
            description="查询 IP 地址的托管域名",
            usage="/getdomain <IP 地址>",
            example="/getdomain",
        ),
    ),
    block=True,
    priority=10,
    rule=ip2location_is_enable,
    use_cmd_start=True,
)


@domain_info_command.assign("verbose")
async def verbose_domain_info_command(user_input_domain: str):
    reponse = await get_domain_information(user_input_domain)
    if not reponse:
        await domain_info_command.finish("查询域名信息时发生错误, 请稍后再试")
    info = json.dumps(reponse, indent=4, ensure_ascii=False)
    if not info:
        await domain_info_command.finish("查询域名信息时发生错误, 请稍后再试")
    await send_verbose_message(info, "域名详细信息")


@domain_info_command.handle()
async def handle_domain_info_command(user_input_domain: str):
    response = await get_domain_information(user_input_domain)
    if not response:
        await domain_info_command.finish("查询域名信息时发生错误, 请稍后再试")
    info = (
        f"域名: {pick(response, 'domain')}\n"
        f"注册商: {pick(response, 'registrar.name')}\n"
        f"注册时间: {pick(response, 'create_date')}\n"
        f"更新日期: {pick(response, 'update_date')}\n"
        f"到期时间: {pick(response, 'expire_date')}\n"
        f"域名权威服务器: {pick(response, 'nameservers')}\n"
    )
    await UniMessage.text(info).finish(reply_to=True)


@get_domain_command.assign("verbose")
async def verbose_get_domain_command(user_input_ip: str):
    is_valid = await validate_ip(user_input_ip)
    if not is_valid:
        await get_domain_command.finish("请输入有效的 IP 地址")
    response = await get_hosted_domains(user_input_ip)
    if not response:
        await get_domain_command.finish("查询托管域名时发生错误, 请稍后再试")
    info = json.dumps(response, indent=4, ensure_ascii=False)
    if not info:
        await get_domain_command.finish("查询托管域名时发生错误, 请稍后再试")
    await send_verbose_message(info, "托管域名详细信息")


@get_domain_command.handle()
async def handle_get_domain_command(user_input_ip: str):
    is_valid = await validate_ip(user_input_ip)
    if not is_valid:
        await get_domain_command.finish("请输入有效的 IP 地址")
    response = await get_hosted_domains(user_input_ip)
    if not response:
        await get_domain_command.finish("查询托管域名时发生错误, 请稍后再试")
    logger.debug(f"托管域名查询结果: {response}")
    domains = response.get("domains", [])
    if not domains:
        await get_domain_command.finish(f"IP 地址 {user_input_ip} 没有托管任何域名")
    info = f"IP 地址 {user_input_ip} 托管的域名有:\n" + "\n".join(domains)
    await UniMessage.text(info).finish(reply_to=True)


@ip_info_commnd.assign("verbose")
async def verbose_ipinfo_command(user_input_ip: str):
    is_valid = await validate_ip(user_input_ip)
    if not is_valid:
        await ip_info_commnd.finish("请输入有效的 IP 地址")
    response = (
        await get_ip_info_by_ip2location(user_input_ip)
        if use_ip2location
        else await get_ip_info_by_ipinfo(user_input_ip)
    )
    if not response:
        await ip_info_commnd.finish("查询 IP 信息时发生错误, 请稍后再试")
    info = json.dumps(response, indent=4, ensure_ascii=False)
    if not info:
        await ip_info_commnd.finish("查询 IP 信息时发生错误, 请稍后再试")
    await send_verbose_message(info, "IP 详细信息")


@ip_info_commnd.handle()
async def handle_ipinfo_command(user_input_ip: str):
    is_valid = await validate_ip(user_input_ip)
    if not is_valid:
        await ip_info_commnd.finish("请输入有效的 IP 地址")
    if use_ip2location:
        response = await get_ip_info_by_ip2location(user_input_ip)
        if not response:
            await ip_info_commnd.finish("查询 IP 信息时发生错误, 请稍后再试")
        info = (
            f"IP地址: {response.get('ip', 'N/A')}\n"
            f"国家/地区: {response.get('country_name', 'N/A')}\n"
            f"省份/州: {response.get('region_name', 'N/A')}\n"
            f"城市: {response.get('city_name', 'N/A')}\n"
            f"纬度: {response.get('latitude', 'N/A')}\n"
            f"经度: {response.get('longitude', 'N/A')}\n"
            f"ASN编号: {response.get('asn', 'N/A')}\n"
            f"组织名称: {response.get('as', 'N/A')}\n"
        )
        await UniMessage.text(info).finish(reply_to=True)
    else:
        response = await get_ip_info_by_ipinfo(user_input_ip)
        if not response:
            await ip_info_commnd.finish("查询 IP 信息时发生错误, 请稍后再试")
        info = (
            f"IP地址: {getattr(response, 'ip', 'N/A')}\n"
            f"ASN编号: {getattr(response, 'asn', 'N/A')}\n"
            f"组织名称: {getattr(response, 'as_name', 'N/A')}\n"
            f"国家/地区: {getattr(response, 'country', 'N/A')}\n"
            f"大陆: {getattr(response, 'continent', 'N/A')}\n"
        )
        await UniMessage.text(info).finish(reply_to=True)
