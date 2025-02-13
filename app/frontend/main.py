import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import requests
import json
import time
from typing import Optional
from datetime import datetime

# Configuration de la page
st.set_page_config(
    page_title="RAG Document Analyzer",
    page_icon="📊",
    layout="wide"
)

# Chargement des styles CSS personnalisés
with open(Path(__file__).parent / "assets" / "styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

class DocumentAnalyzer:
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.temp_dir = Path(__file__).parent.parent / "data" / "temp"
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def analyze_document(self, file) -> Optional[dict]:
        """Envoie un document pour analyse."""
        try:
            # Sauvegarde temporaire du fichier
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_path = self.temp_dir / f"upload_{timestamp}_{file.name}"
            with open(temp_path, "wb") as f:
                f.write(file.getbuffer())

            # Envoi au serveur
            with open(temp_path, "rb") as f:
                files = {'file': (file.name, f, 'text/plain')}
                response = requests.post(f"{self.api_url}/documents/analyze", files=files)

            # Nettoyage
            temp_path.unlink()

            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Erreur lors de l'analyse: {response.text}")
                return None
        except Exception as e:
            st.error(f"Erreur de connexion: {str(e)}")
            return None

    def get_example_document(self) -> Path:
        """Retourne le chemin vers le document exemple."""
        return Path(__file__).parent.parent / "data" / "examples" / "sample.txt"

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

        # Colonnes pour l'upload et l'exemple
        col1, col2 = st.columns(2)
        
        with col1:
            uploaded_file = st.file_uploader(
                "Choisissez un fichier à analyser",
                type=['txt', 'md', 'rst']
            )

        with col2:
            if st.button("Utiliser le document exemple"):
                example_path = analyzer.get_example_document()
                uploaded_file = open(example_path, "rb")

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
                            title="Métriques de qualité",
                            template="plotly_white"
                        )
                        st.plotly_chart(fig, use_container_width=True)

                    # Recommandations
                    st.markdown("### 🎯 Recommandations")
                    if "recommendations" in result:
                        for rec in result["recommendations"]:
                            st.info(rec)

    # Onglet Métriques
    with tabs[1]:
        st.markdown("""
        ### Métriques globales
        Visualisez les statistiques d'utilisation et les tendances.
        """)
        
        # Métriques dans une grille
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            #### Documents analysés
            """)
            st.metric("Total", "1,234", "↑ 12%")
        
        with col2:
            st.markdown("""
            #### Tokens traités
            """)
            st.metric("Total", "1.2M", "↑ 8%")
        
        with col3:
            st.markdown("""
            #### Temps moyen
            """)
            st.metric("Analyse", "2.3s", "↓ 15%")

        # Graphique de tendance
        chart_data = pd.DataFrame({
            'Date': pd.date_range(start='2024-01-01', periods=30),
            'Documents': [100 + i * 10 + i * i for i in range(30)]
        })
        
        fig = px.line(
            chart_data,
            x='Date',
            y='Documents',
            title="Évolution du nombre de documents analysés",
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)

    # Onglet Aide
    with tabs[2]:
        st.markdown("""
        ### Guide d'utilisation

        #### 1. Préparation des documents
        - **Formats supportés**: .txt, .md, .rst
        - **Taille maximale**: 10MB
        - **Encodage**: UTF-8 recommandé

        #### 2. Processus d'analyse
        L'analyse prend en compte plusieurs facteurs:
        - Complexité du texte
        - Structure du document
        - Qualité des métadonnées
        - Cohérence thématique
        - Potentiel d'extraction

        #### 3. Interprétation des résultats
        - **Métriques générales**: Données quantitatives sur le document
        - **Estimation des coûts**: Projection des coûts d'utilisation
        - **Visualisations**: Représentation graphique des métriques
        - **Recommandations**: Suggestions d'amélioration

        #### 4. Bonnes pratiques
        - Structurez clairement vos documents
        - Évitez les répétitions inutiles
        - Incluez des métadonnées pertinentes
        - Maintenez une longueur de document appropriée
        """)

if __name__ == "__main__":
    main()
