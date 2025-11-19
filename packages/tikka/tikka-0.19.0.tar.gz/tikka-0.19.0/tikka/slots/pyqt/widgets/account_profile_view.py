# Copyright 2021 Vincent Texier <vit@free.fr>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from typing import Any, Dict


def create_profile_html(
    profile_data: Dict[str, Any], updated_on_localized_string: str
) -> str:
    """
    Return HTML content string of Cesium+ Profile

    :param profile_data:
    :param updated_on_localized_string: Updated date localized string
    :return:
    """
    # display avatar image
    avatar_html = ""
    if "avatar" in profile_data and "_content" in profile_data["avatar"]:
        mime_type = profile_data["avatar"].get("_content_type", "image/png")
        avatar_data = profile_data["avatar"]["_content"]
        avatar_html = f'<img src="data:{mime_type};base64,{avatar_data}" alt="Avatar" class="avatar">'

    # web site button
    web_button_html = ""
    if "socials" in profile_data:
        for social in profile_data["socials"]:
            if social.get("type") == "web":
                web_url = social.get("url", "#")
                web_button_html = f'<a href="{web_url}" class="web-button" onclick="return true;">🌐 {web_url}</a>'

    # extract geolocation data
    geo_point = profile_data.get("geoPoint", {}) or {}
    lat = geo_point.get("lat", 0)
    lon = geo_point.get("lon", 0)
    city = profile_data.get("city", "Localisation inconnue")

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <style>
            {get_css()}
        </style>
    </head>
    <body>
        <div class="profile-container">
            <div class="profile-header">
                <div class="profile-main">
                    {avatar_html}
                    <div class="profile-info">
                        <h1 class="profile-title">{profile_data.get('title', '')}</h1>
                        <p class="profile-description">{profile_data.get('description', '')}</p>
                        <div class="profile-location">
                            📍 {city}
                        </div>
                        {web_button_html}
                        <div class="profile-date">{updated_on_localized_string}</div>
                    </div>
                </div>
            </div>

            <div class="map-column">
                <div id="minimap" data-lat="{lat}" data-lon="{lon}" data-city="{city}"></div>
            </div>
        </div>

        <script>
            {get_map_js()}
        </script>
    </body>
    </html>
    """

    return html_content


def get_css() -> str:
    """
    Return Profile CSS

    :return:
    """
    return """
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        /* background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);*/
        min-height: 100vh;
        padding: 20px;
        display: flex;
        justify-content: center;
        align-items: flex-start;
    }

    .profile-container {
        display: flex;
        gap: 20px;
        /* max-width: 1000px;*/
        width: 100%;
    }

    .profile-header {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        padding: 30px;
        flex: 1;
        color: white;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    .profile-main {
        display: flex;
        align-items: flex-start;
        gap: 20px;
        margin-bottom: 20px;
    }

    .avatar {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        border: 3px solid white;
        object-fit: cover;
        flex-shrink: 0;
    }

    .profile-info {
        flex: 1;
    }

    .profile-title {
        font-size: 24px;
        font-weight: 600;
        margin-bottom: 8px;
    }

.profile-description {
    font-size: 16px;
    opacity: 0.9;
    margin-bottom: 12px;
    line-height: 1.4;
    white-space: pre-wrap;      /* Respecte les sauts de ligne */
    word-wrap: break-word;      /* Casse les mots longs */
    overflow-wrap: break-word;  /* Alternative moderne */
}

    .profile-location {
        font-size: 14px;
        opacity: 0.9;
        margin-bottom: 15px;
    }

    .web-button {
        display: inline-block;
        padding: 10px 20px;
        background: rgba(255, 255, 255, 0.2);
        color: white;
        text-decoration: none;
        border-radius: 25px;
        border: 2px solid white;
        font-weight: 600;
        transition: all 0.3s ease;
        margin-bottom: 10px;
    }

    .web-button:hover {
        background: white;
        color: #4facfe;
        transform: translateY(-2px);
    }

    .profile-date {
        font-size: 12px;
        opacity: 0.8;
        font-style: italic;
    }

    .map-column {
        flex: 0 0 400px;
    }

    #minimap {
        height: 100%;
        min-height: 300px;
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        overflow: hidden;
        background: white;
    }

    /* Style pour la carte Leaflet */
    .leaflet-container {
        background: #f8f9fa;
        border-radius: 12px;
    }

    .custom-marker {
        background: #e74c3c;
        border: 3px solid white;
        border-radius: 50%;
        width: 20px;
        height: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
    }

    /* Responsive pour petits écrans */
    @media (max-width: 768px) {
        .profile-container {
            flex-direction: column;
        }

        .map-column {
            flex: 0 0 250px;
        }
    }
    """


def get_map_js() -> str:
    """
    Return Profile Javascript

    :return:
    """
    return """
    function initMap() {
        const mapElement = document.getElementById('minimap');
        const lat = parseFloat(mapElement.dataset.lat);
        const lon = parseFloat(mapElement.dataset.lon);
        const city = mapElement.dataset.city;

        // Vérifier si les coordonnées sont valides
        if (lat === 0 && lon === 0) {
            mapElement.innerHTML = '<div style="display: flex; align-items: center; justify-content: center; height: 100%; background: #f8f9fa; color: #6c757d; font-size: 16px;">📍 Localisation non disponible</div>';
            return;
        }

        // Initialiser la carte
        const map = L.map('minimap').setView([lat, lon], 13);

        // Ajouter les tuiles OpenStreetMap
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 18
        }).addTo(map);

        // Créer un marqueur personnalisé
        const customIcon = L.divIcon({
            className: 'custom-marker',
            html: '📍',
            iconSize: [30, 30],
            iconAnchor: [15, 30]
        });

        // Ajouter le marqueur
        const marker = L.marker([lat, lon], {icon: customIcon})
            .addTo(map)
            .bindPopup(`<b>${city}</b><br>${lat.toFixed(6)}, ${lon.toFixed(6)}`)
            .openPopup();
    }

    // Initialiser la carte quand la page est chargée
    document.addEventListener('DOMContentLoaded', initMap);
    """
