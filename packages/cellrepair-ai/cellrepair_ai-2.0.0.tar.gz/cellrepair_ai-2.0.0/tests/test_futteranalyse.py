"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧬 CELLREPAIR™ SYSTEMS - PROPRIETÄRER CODE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
© 2024-2025 Oliver Winkel - CellRepair™ Systems | NIP: PL9292072406
System ID: CR-4882-AURORA-GENESIS-2.0 | DNA: 4882-AURORA-OW-CR-SYSTEMS-2025

EIGENTÜMER: Oliver Winkel, ul. Zbożowa 13, 65-375 Zielona Góra, Polen
KONTAKT: ai@cellrepair.ai | https://cellrepair.ai

⚠️  Unerlaubte Nutzung, Kopie oder Verbreitung VERBOTEN!
⚠️  Unauthorized use, copying, or distribution PROHIBITED!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
"""
Tests für CellRepair Futteranalyse
"""

import pytest
import os
import tempfile
from fastapi.testclient import TestClient
from app.main import app
from app.models import FutteranalyseRequest, Tier
from app.services.analysis.scoring import calculate_scores

client = TestClient(app)

# Test-Daten
test_tier = Tier(
    name="Bello",
    art="Hund",
    rasse="Labrador",
    alter=3,
    gewicht=25.5,
    geschlecht="männlich"
)

test_request_basic = FutteranalyseRequest(
    tier=test_tier,
    futter="Hochwertiges Hundefutter mit frischem Fleisch, ohne Zusatzstoffe",
    beobachtungen="Tier ist sehr aktiv, glänzendes Fell, regelmäßiger Kot, guter Appetit",
    package="basic",
    vitalfeld_fragen=[8, 7, 9, 8, 7],  # Gute Werte
    email="test@example.com"
)

test_request_plus = FutteranalyseRequest(
    tier=test_tier,
    futter="Bio-Hundefutter mit Monoprotein, frisch verarbeitet",
    beobachtungen="Sehr lebhaft, glänzendes Fell, regelmäßiger geformter Kot, keine Blähungen",
    package="plus",
    vitalfeld_fragen=[9, 8, 9, 8, 9],  # Sehr gute Werte
    email="test@example.com"
)

test_request_pro = FutteranalyseRequest(
    tier=test_tier,
    futter="Premium Bio-Hundefutter, roh gefüttert, ohne Konservierungsstoffe",
    beobachtungen="Extrem vital, glänzendes Fell, perfekter Kot, sehr aktiv und aufmerksam",
    package="pro",
    vitalfeld_fragen=[10, 9, 10, 9, 10],  # Exzellente Werte
    email="test@example.com"
)

test_request_schlecht = FutteranalyseRequest(
    tier=test_tier,
    futter="Billiges Futter mit Fleischmehl, Zucker, Farbstoffen und Aromen",
    beobachtungen="Tier ist träge, stumpfes Fell, weicher Kot, Blähungen, wenig Appetit",
    package="basic",
    vitalfeld_fragen=[2, 3, 2, 3, 2],  # Schlechte Werte
    email="test@example.com"
)

class TestScoring:
    """Tests für die Scoring-Engine"""

    def test_vitalfeld_score_gut(self):
        """Test für guten Vitalfeld-Score"""
        scores = calculate_scores(test_request_basic)
        assert scores.vitalfeld >= 70  # Sollte gut sein
        assert scores.ampel in ["gruen", "gelb"]

    def test_vitalfeld_score_schlecht(self):
        """Test für schlechten Vitalfeld-Score"""
        scores = calculate_scores(test_request_schlecht)
        assert scores.vitalfeld < 50  # Sollte schlecht sein
        assert scores.ampel in ["orange", "rot"]

    def test_milieu_score_aus_beobachtungen(self):
        """Test für Milieu-Score aus Beobachtungen"""
        scores = calculate_scores(test_request_basic)
        assert 0 <= scores.milieu <= 100
        assert isinstance(scores.milieu, int)

    def test_frequenz_score_aus_futter(self):
        """Test für Frequenz-Score aus Futter"""
        scores = calculate_scores(test_request_basic)
        assert 0 <= scores.frequenz <= 100
        assert isinstance(scores.frequenz, int)

    def test_matrix_score_berechnung(self):
        """Test für Matrix-Score Berechnung"""
        scores = calculate_scores(test_request_basic)
        assert 0 <= scores.matrix <= 100
        assert isinstance(scores.matrix, int)

    def test_ampel_bestimmung(self):
        """Test für Ampel-Bestimmung"""
        scores_gut = calculate_scores(test_request_pro)
        assert scores_gut.ampel == "gruen"

        scores_schlecht = calculate_scores(test_request_schlecht)
        assert scores_schlecht.ampel in ["orange", "rot"]

    def test_hinweise_generierung(self):
        """Test für Hinweise-Generierung"""
        scores = calculate_scores(test_request_basic)
        assert isinstance(scores.hinweise, list)
        assert len(scores.hinweise) > 0
        assert all(isinstance(h, str) for h in scores.hinweise)

class TestAPI:
    """Tests für die FastAPI Endpoints"""

    def test_health_endpoint(self):
        """Test für Health Check"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_packages_endpoint(self):
        """Test für Packages Endpoint"""
        response = client.get("/futteranalyse/packages")
        assert response.status_code == 200
        data = response.json()
        assert "packages" in data
        assert len(data["packages"]) == 3

        packages = [p["id"] for p in data["packages"]]
        assert "basic" in packages
        assert "plus" in packages
        assert "pro" in packages

    def test_generate_basic(self):
        """Test für Basic Package Generation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Temporäres Verzeichnis für PDFs
            os.environ["PDF_OUTPUT_DIR"] = temp_dir

            response = client.post(
                "/futteranalyse/generate",
                json=test_request_basic.dict()
            )

            assert response.status_code == 200
            data = response.json()

            assert data["ok"] is True
            assert data["package"] == "basic"
            assert "scores" in data
            assert "pdf_path" in data
            assert "preview" in data

            # PDF-Datei sollte existieren
            assert os.path.exists(data["pdf_path"])

    def test_generate_plus(self):
        """Test für Plus Package Generation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.environ["PDF_OUTPUT_DIR"] = temp_dir

            response = client.post(
                "/futteranalyse/generate",
                json=test_request_plus.dict()
            )

            assert response.status_code == 200
            data = response.json()
            assert data["package"] == "plus"

    def test_generate_pro(self):
        """Test für Pro Package Generation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.environ["PDF_OUTPUT_DIR"] = temp_dir

            response = client.post(
                "/futteranalyse/generate",
                json=test_request_pro.dict()
            )

            assert response.status_code == 200
            data = response.json()
            assert data["package"] == "pro"

    def test_invalid_package(self):
        """Test für ungültiges Package"""
        invalid_request = test_request_basic.copy()
        invalid_request.package = "invalid"

        response = client.post(
            "/futteranalyse/generate",
            json=invalid_request.dict()
        )

        # Sollte 422 (Validation Error) oder 400 (Bad Request) sein
        assert response.status_code in [400, 422]

    def test_missing_email(self):
        """Test für fehlende E-Mail"""
        invalid_request = test_request_basic.copy()
        invalid_request.email = "invalid-email"

        response = client.post(
            "/futteranalyse/generate",
            json=invalid_request.dict()
        )

        assert response.status_code == 422  # Validation Error

class TestScoringEdgeCases:
    """Tests für Edge Cases in der Scoring-Engine"""

    def test_empty_beobachtungen(self):
        """Test mit leeren Beobachtungen"""
        request = test_request_basic.copy()
        request.beobachtungen = ""

        scores = calculate_scores(request)
        assert 0 <= scores.vitalfeld <= 100
        assert 0 <= scores.milieu <= 100

    def test_no_vitalfeld_fragen(self):
        """Test ohne Vitalfeld-Fragen"""
        request = test_request_basic.copy()
        request.vitalfeld_fragen = None

        scores = calculate_scores(request)
        assert 0 <= scores.vitalfeld <= 100

    def test_extreme_scores(self):
        """Test für extreme Score-Werte"""
        # Sehr gute Werte
        request_gut = test_request_pro.copy()
        request_gut.vitalfeld_fragen = [10, 10, 10, 10, 10]
        scores_gut = calculate_scores(request_gut)
        assert scores_gut.vitalfeld == 100

        # Sehr schlechte Werte
        request_schlecht = test_request_schlecht.copy()
        request_schlecht.vitalfeld_fragen = [1, 1, 1, 1, 1]
        scores_schlecht = calculate_scores(request_schlecht)
        assert scores_schlecht.vitalfeld == 10

if __name__ == "__main__":
    pytest.main([__file__, "-v"])





































