"""ShelfScan — Application Streamlit pour l'inventaire de bibliothèque."""

import streamlit as st


def main():
    """Point d'entrée de l'application ShelfScan."""
    st.set_page_config(
        page_title="ShelfScan",
        page_icon="\U0001f4da",
        layout="wide",
    )

    st.title("ShelfScan — Inventaire de bibliothèque")
    st.markdown("Uploadez une photo d'étagère pour identifier les livres.")

    uploaded_file = st.file_uploader(
        "Choisir une image",
        type=["jpeg", "jpg", "png"],
        help="Formats acceptés : JPEG, PNG",
    )

    if uploaded_file is not None:
        st.image(uploaded_file, caption="Image uploadée", use_container_width=True)

        st.subheader("Résultats")
        results_container = st.container()
        with results_container:
            st.info("Le pipeline d'analyse sera intégré dans les prochains milestones.")


if __name__ == "__main__":
    main()
