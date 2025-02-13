import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import requests
import json
import time
from typing import Optional

# Configuration de la page
st.set_page_config(
    page_title="RAG Document Analyzer",
    page_icon="📊",
    layout="wide"
)

# Styles CSS personnalisés
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stProgress > div > div > div > div {
        background-color: #1f77b4;
    }
    </style>
    """, unsafe_allow_html=True)

class DocumentAnalyzer:
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url

    def analyze_document(self, file) -> Optional[dict]:
        """Envoie un document pour analyse."""
        try:
            files = {'file': (file.name, file, 'text/plain')}
            response = requests.post(f"{self.api_url}/documents/analyze", files=files)
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Erreur lors de l'analyse: {response.text}")
                return None
        except Exception as e:
            st.error(f"Erreur de connexion: {str(e)}")
            return None

def main():
    st.title("📊 RAG Document Analyzer")
    st.subheader("Analysez vos documents pour l'implémentation RAG")

    # Initialisation de l'analyseur
    analyzer = DocumentAnalyzer()

    # Interface principale
    tabs = st.tabs(["📝 Analyse", "📊 Métriques", "ℹ️ Aide"])

    # Onglet Analyse
    with tabs[0]:
        st.markdown("""
        ### Analyse de documents
        Uploadez vos documents pour obtenir une analyse détaillée et des recommandations 
        pour l'implémentation RAG.
        """)

        # Upload de fichier
        uploaded_file = st.file_uploader(
            "Choisissez un fichier à analyser",
            type=['txt', 'md', 'rst']
        )

        if uploaded_file:
            with st.spinner('Analyse en cours...'):
                # Affichage de la progression
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.01)
                    progress_bar.progress(i + 1)

                # Analyse du document
                result = analyzer.analyze_document(uploaded_file)

                if result:
                    # Affichage des résultats dans des colonnes
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("### 📈 Métriques générales")
                        metrics = {
                            "Nombre de chunks": result.get("chunks_count", 0),
                            "Tokens estimés": result.get("estimated_tokens", 0),
                            "Score de complexité": f"{result.get('complexity_score', 0):.2f}/10"
                        }
                        for key, value in metrics.items():
                            st.metric(key, value)

                    with col2:
                        st.markdown("### 💰 Estimation des coûts")
                        costs = {
                            "Coût de base": f"{result.get('base_cost', 0):.2f}€",
                            "Coût mensuel": f"{result.get('monthly_cost', 0):.2f}€",
                            "ROI estimé": "3-6 mois"
                        }
                        for key, value in costs.items():
                            st.metric(key, value)

                    # Graphiques
                    st.markdown("### 📊 Visualisations")
                    if "quality_metrics" in result:
                        qm = result["quality_metrics"]
                        fig = px.bar(
                            x=list(qm.keys()),
                            y=list(qm.values()),
                            title="Métriques de qualité"
                        )
                        st.plotly_chart(fig)

    # Onglet Métriques
    with tabs[1]:
        st.markdown("""
        ### Métriques globales
        Visualisez les statistiques d'utilisation et les tendances.
        """)
        # Exemple de métriques fictives pour la démo
        col1, col2, col3 = st.columns(3)
        col1.metric("Documents analysés", "1,234")
        col2.metric("Tokens traités", "1.2M")
        col3.metric("Temps moyen d'analyse", "2.3s")

    # Onglet Aide
    with tabs[2]:
        st.markdown("""
        ### Guide d'utilisation
        1. **Upload de document**
           - Formats supportés: .txt, .md, .rst
           - Taille maximale: 10MB

        2. **Analyse**
           - L'analyse prend en compte plusieurs facteurs:
             - Complexité du texte
             - Structure du document
             - Besoins en prétraitement
             - Estimation des coûts RAG

        3. **Résultats**
           - Métriques détaillées
           - Recommandations
           - Visualisations
           - Estimation des coûts
        """)

if __name__ == "__main__":
    main()
