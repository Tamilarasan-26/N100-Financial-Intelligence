import requests
import streamlit as st


# ============================================================
# FASTAPI CONFIGURATION
# ============================================================

API_BASE_URL = "http://127.0.0.1:8000/api/v1"


# ============================================================
# GENERIC API REQUEST
# ============================================================

def api_get(endpoint, params=None):
    """
    Send a GET request to the FastAPI backend.
    """

    url = f"{API_BASE_URL}{endpoint}"

    response = requests.get(
        url,
        params=params,
        timeout=10,
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# HEALTH
# ============================================================

@st.cache_data(ttl=60)
def get_health():

    return api_get(
        "/health"
    )


# ============================================================
# COMPANIES
# ============================================================

@st.cache_data(ttl=600)
def get_companies():

    return api_get(
        "/companies"
    )


# ============================================================
# COMPANY PROFILE
# ============================================================

@st.cache_data(ttl=600)
def get_company(company_id):

    return api_get(
        f"/companies/{company_id}"
    )


# ============================================================
# SCREENER
# ============================================================

@st.cache_data(ttl=600)
def get_screener(params=None):

    return api_get(
        "/screener",
        params=params,
    )


# ============================================================
# SECTORS
# ============================================================

@st.cache_data(ttl=600)
def get_sectors():

    return api_get(
        "/sectors"
    )


# ============================================================
# COMPANIES BY SECTOR
# ============================================================

@st.cache_data(ttl=600)
def get_sector_companies(sector):

    return api_get(
        f"/sectors/{sector}/companies"
    )