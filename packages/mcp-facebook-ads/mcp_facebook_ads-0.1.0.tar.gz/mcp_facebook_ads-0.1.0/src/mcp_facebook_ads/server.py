"""Servidor MCP para Facebook Ads implementado em Python."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()


@dataclass(frozen=True)
class FacebookAdsConfig:
    access_token: str
    account_id: str
    api_version: str = "v21.0"

    @classmethod
    def from_env(cls) -> "FacebookAdsConfig":
        token = os.getenv("FB_ACCESS_TOKEN")
        account_id = os.getenv("FB_ACCOUNT_ID")
        api_version = os.getenv("FB_API_VERSION", "v21.0")

        missing: list[str] = []
        if not token:
            missing.append("FB_ACCESS_TOKEN")
        if not account_id:
            missing.append("FB_ACCOUNT_ID")
        if missing:
            raise RuntimeError(
                "Variáveis de ambiente obrigatórias ausentes: " + ", ".join(missing)
            )

        normalized_account_id = account_id.removeprefix("act_")
        return cls(access_token=token, account_id=normalized_account_id, api_version=api_version)


class FacebookAdsClient:
    """Encapsula chamadas HTTP para a Graph API."""

    def __init__(self, config: FacebookAdsConfig) -> None:
        self._config = config
        self._base_url = f"https://graph.facebook.com/{config.api_version}"

    def _call(self, path: str, params: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self._base_url}{path}"
        final_params = {"access_token": self._config.access_token, **params}

        try:
            response = requests.get(url, params=final_params, timeout=30)
        except requests.RequestException as exc:  # pragma: no cover - rede de terceiros
            raise RuntimeError(f"Erro de rede ao chamar Graph API: {exc}") from exc

        if not response.ok:
            try:
                payload = response.json()
            except ValueError:
                payload = {"error": response.text}
            raise RuntimeError(
                f"Facebook API Error {response.status_code}: {json.dumps(payload, ensure_ascii=False)}"
            )

        return response.json()

    def get_campaigns(self, fields: str, limit: int) -> Dict[str, Any]:
        return self._call(
            path=f"/act_{self._config.account_id}/campaigns",
            params={"fields": fields, "limit": limit},
        )

    def get_campaign_insights(
        self,
        campaign_id: str,
        fields: str,
        date_preset: Optional[str],
        since: Optional[str],
        until: Optional[str],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {"fields": fields}
        _apply_time_filters(params, date_preset, since, until, default_date="lifetime")
        return self._call(path=f"/{campaign_id}/insights", params=params)

    def get_ad_creatives(self, ad_id: str, fields: str) -> Dict[str, Any]:
        return self._call(path=f"/{ad_id}/creatives", params={"fields": fields})

    def get_account_insights(
        self,
        fields: str,
        level: str,
        date_preset: Optional[str],
        since: Optional[str],
        until: Optional[str],
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {"fields": fields, "level": level}
        _apply_time_filters(params, date_preset, since, until, default_date="last_7d")
        return self._call(path=f"/act_{self._config.account_id}/insights", params=params)

    def get_campaign_ads(self, campaign_id: str, fields: str, limit: int) -> Dict[str, Any]:
        return self._call(
            path=f"/{campaign_id}/ads",
            params={"fields": fields, "limit": limit},
        )


def _apply_time_filters(
    params: Dict[str, Any],
    date_preset: Optional[str],
    since: Optional[str],
    until: Optional[str],
    *,
    default_date: str,
) -> None:
    """Aplica parâmetros de data seguindo mesma regra do projeto em Node."""

    if since or until:
        if not (since and until):
            raise ValueError("Os parâmetros 'since' e 'until' devem ser usados em conjunto")
        params["time_range"] = json.dumps({"since": since, "until": until})
    else:
        params["date_preset"] = date_preset or default_date


def _normalize_limit(value: Optional[int], fallback: int) -> int:
    limit = value if value and value > 0 else fallback
    return max(1, limit)


CONFIG = FacebookAdsConfig.from_env()
CLIENT = FacebookAdsClient(CONFIG)
MCP_SERVER = FastMCP("mcp_facebook_ads")


@MCP_SERVER.tool()
def get_campaigns(fields: Optional[str] = None, limit: Optional[int] = None) -> Dict[str, Any]:
    """Retorna lista de campanhas da conta de anúncios."""

    resolved_fields = fields or "id,name,status,objective"
    resolved_limit = _normalize_limit(limit, fallback=25)
    return CLIENT.get_campaigns(resolved_fields, resolved_limit)


@MCP_SERVER.tool()
def get_campaign_insights(
    campaign_id: str,
    date_preset: Optional[str] = None,
    since: Optional[str] = None,
    until: Optional[str] = None,
    fields: Optional[str] = None,
) -> Dict[str, Any]:
    """Retorna métricas e performance de uma campanha específica."""

    if not campaign_id:
        raise ValueError("'campaign_id' é obrigatório")

    resolved_fields = fields or "impressions,clicks,spend,ctr,cpc,cpm"
    return CLIENT.get_campaign_insights(campaign_id, resolved_fields, date_preset, since, until)


@MCP_SERVER.tool()
def get_ad_creatives(ad_id: str, fields: Optional[str] = None) -> Dict[str, Any]:
    """Retorna informações sobre os criativos de um anúncio."""

    if not ad_id:
        raise ValueError("'ad_id' é obrigatório")

    resolved_fields = fields or "id,name,thumbnail_url,object_story_spec"
    return CLIENT.get_ad_creatives(ad_id, resolved_fields)


@MCP_SERVER.tool()
def get_account_insights(
    date_preset: Optional[str] = None,
    since: Optional[str] = None,
    until: Optional[str] = None,
    fields: Optional[str] = None,
    level: Optional[str] = None,
) -> Dict[str, Any]:
    """Retorna insights e relatórios da conta de anúncios."""

    resolved_fields = fields or "impressions,clicks,spend,cpc,cpm,ctr"
    resolved_level = level or "account"
    return CLIENT.get_account_insights(resolved_fields, resolved_level, date_preset, since, until)


@MCP_SERVER.tool()
def get_campaign_ads(
    campaign_id: str,
    fields: Optional[str] = None,
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    """Retorna lista de anúncios de uma campanha específica."""

    if not campaign_id:
        raise ValueError("'campaign_id' é obrigatório")

    resolved_fields = fields or "id,name,status,creative"
    resolved_limit = _normalize_limit(limit, fallback=100)
    return CLIENT.get_campaign_ads(campaign_id, resolved_fields, resolved_limit)


def main() -> None:
    """Inicializa o servidor MCP utilizando transporte stdio."""

    MCP_SERVER.run(transport="stdio")


if __name__ == "__main__":  # pragma: no cover
    main()
